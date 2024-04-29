import json
from transformers import pipeline
import postgres
from psycopg2.extras import Json 
import os
import boto3
import pysftp

analyze_sentiment = pipeline("sentiment-analysis", model="cardiffnlp/twitter-xlm-roberta-base-sentiment")


def receive_messages():
    client = boto3.client('sqs', region_name='', aws_access_key_id='', aws_secret_access_key='')
    url = ""
    while True:
        response = client.receive_message(QueueUrl=url, MaxNumberOfMessages=1, AttributeNames=["All"])
        print(response)
        message = response['Messages'][0]
        response_body = message['Body'].replace("\n", "")
        print(response_body)
        response_body = json.loads(response_body.replace("\n", ""))
        channels = response_body['channels']
        files = response_body['files']

        print(f'channels are: {channels}, files are: {files}')

        hkey = pysftp.CnOpts()
        hkey.hostkeys = None
        conn = pysftp.Connection(host='', port=0000, username='', password='', cnopts=hkey)
        conn.get(files[0], 'src/file.json')
        arr = os.listdir("src")
        for path in arr:
            with open('src/' + path, 'r', encoding="utf-8") as file:
                data = json.load(file)
        conn.close()
        print(data)
        get_basic_stats()
        get_sentiment()


# paper: https://arxiv.org/abs/2104.12250

# WIP!!
# TODO: 
#   Analyze comments in batches rather than one by one, we may lose some accuracy tho
#   Parallelize the code
#   Find some faster models in: https://huggingface.co/models
#   Write in DynamoDB
#   May add number of reactions per post, but, so far it's replaced with reactions sentiment (both per post and per channel)


# normalize the feedback ratio for additional stats
def ratio_normalization(sentiments):
    total = sentiments['positive'] + sentiments['negative'] + sentiments['neutral']
    if total != 0:
        positives_percentage = round((sentiments['positive'] / total) * 100, 3)
        negatives_percentage = round((sentiments['negative'] / total) * 100, 3)
        neutrals_percentage = round((sentiments['neutral'] / total) * 100, 3)
    else:
        positives_percentage = 0
        negatives_percentage = 0
        neutrals_percentage = 0
        print(f"positives: {positives_percentage}; negatives {negatives_percentage}; neutrals: {neutrals_percentage}")
    
    return {"positive": positives_percentage, "negative": negatives_percentage, "neutral": neutrals_percentage}


def analyse(current_file):
    path = "src/" + current_file
    with open(path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    reaction_sentiment_cache = {}

    # adjust these weights as needed
    # the bigger the weight, the bigger it's impact on channel sentiment analysis
    post_weight = 0.4
    comment_weight = 0.4
    reactions_weight = 0.2

    channel_id = data['id']
    channel = data['title']
    posts = data['posts']
    post_sentiments = []
    comment_sentiments = []
    print(f"channel: {channel}")

    posts_sentiment_aggregated = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    comments_sentiment_aggregated = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    reactions_sentiment_aggregated = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

    for post in posts:
        post_text = post['text']
        post_id = post['post_id']

        if post_text == None:
            post_text = ""

        if len(post_text) > 1500:
            post_sentiment = analyze_sentiment(post_text[:int(len(post_text) * 0.15)])
        else:
            post_sentiment = analyze_sentiment(post_text)

        print(f"\nanalyzing text and reactions for post: {post['datetime']}")
        posts_sentiment_aggregated[post_sentiment[0]['label']] += post_sentiment[0]['score'] # <- here,
        # if we'll keep adding new sentiments forever, at some point we'll obviously exceed the
        # bounds of float in python, but, considering that float is 64bit by default, and considering our
        # not big enough and finite analysis -- it's extremely unlikely that we will ever exceed these bounds

        # push post_sentiment

        print(f"post sentiment: {post_sentiment}")

        sentiments = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

        for comment in post.get('comments', []):
            comment_text = comment['text']

            if len(comment_text) > 1500:
                comment_sentiment = analyze_sentiment(comment_text[:int(len(comment_text) * 0.15)])
            else:
                comment_sentiment = analyze_sentiment(comment_text)
                
            comments_sentiment_aggregated[comment_sentiment[0]['label']] += comment_sentiment[0]['score']
            print(f"comment sentiment: {comment_sentiment}")

            label = comment_sentiment[0]['label']
            sentiments[label] += comment_sentiment[0]['score']
            comment_sentiment_data = {"comment_id": comment['id'], "sentiment": comment_sentiment}
            comment_sentiments.append(comment_sentiment_data)

                # now push comments_quantity for this post
                
        ratio_normalization(sentiments) # push sentiment ratio for comments now

        sentiments = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
        reactions = post['reactions'][:5] # analyzing only the first 5 reactions, which is enough for our estimate

        for reaction in reactions:
            reaction_type = reaction['emoticon']

            # cache reactions for better performance / unfortunately we cant cache messages ;(
            if reaction_type not in reaction_sentiment_cache:
                reaction_sentiment_cache[reaction_type] = analyze_sentiment(reaction_type)

            reaction_sentiment = reaction_sentiment_cache[reaction_type]
            reactions_sentiment_aggregated[reaction_sentiment[0]['label']] += reaction_sentiment[0]['score']

            print(f"reaction: {reaction_type} : {reaction['count']}; reaction sentiment: {reaction_sentiment}")
                    
            label = reaction_sentiment[0]['label']
            sentiments[label] += reaction_sentiment[0]['score'] * reaction['count']
                
        ratio_normalization(sentiments) # return ratio, push it too
        post_sentiment_data = {"post_id": post_id, "sentiment": post_sentiment, "comment_sentiments": comment_sentiments}
        post_sentiments.append(post_sentiment_data)

    channel_sentiment = calculate_channel_sentiment(channel_id, posts_sentiment_aggregated, comments_sentiment_aggregated, reactions_sentiment_aggregated,
                                                        post_weight, comment_weight, reactions_weight, post_sentiments)

    print(f"channel sentiment: {channel_sentiment}")
    # now push posts_quantity, channel_sentiment for this channel


def calculate_channel_sentiment(channel_id, posts_sentiment_aggregated, comments_sentiment_aggregated, reactions_sentiment_aggregated, 
                                post_weight, comment_weight, reactions_weight, post_sentiment_data):
    available_weights = []
    if any(posts_sentiment_aggregated.values()):
        available_weights.append(post_weight)
    else:
        post_weight = 0
    
    if any(comments_sentiment_aggregated.values()):
        available_weights.append(comment_weight)
    else:
        comment_weight = 0
    
    if any(reactions_sentiment_aggregated.values()):
        available_weights.append(reactions_weight)
    else:
        reactions_weight = 0

    # normalize weights if some sentiments are absent
    total_weight = sum(available_weights)
    if total_weight == 0:
        return {"positive": 0, "negative": 0, "neutral": 0}
    else:
        post_weight = post_weight / total_weight if post_weight else 0
        comment_weight = comment_weight / total_weight if comment_weight else 0
        reactions_weight = reactions_weight / total_weight if reactions_weight else 0

    post_positive_ratio = ratio_normalization(posts_sentiment_aggregated)["positive"]
    comments_positive_ratio = ratio_normalization(comments_sentiment_aggregated)["positive"]
    reactions_positive_ratio = ratio_normalization(reactions_sentiment_aggregated)["positive"]

    post_negative_ratio = ratio_normalization(posts_sentiment_aggregated)["negative"]
    comments_negative_ratio = ratio_normalization(comments_sentiment_aggregated)["negative"]
    reactions_negative_ratio = ratio_normalization(reactions_sentiment_aggregated)["negative"]

    post_neutral_ratio = ratio_normalization(posts_sentiment_aggregated)["neutral"]
    comments_neutral_ratio = ratio_normalization(comments_sentiment_aggregated)["neutral"]
    reactions_neutral_ratio = ratio_normalization(reactions_sentiment_aggregated)["neutral"]

    channel_sentiment = {
        "positive": round(
            post_positive_ratio * post_weight +
            comments_positive_ratio * comment_weight +
            reactions_positive_ratio * reactions_weight, 3
        ),
        "negative": round(
            post_negative_ratio * post_weight +
            comments_negative_ratio * comment_weight +
            reactions_negative_ratio * reactions_weight, 3
        ),
        "neutral": round(
            post_neutral_ratio * post_weight +
            comments_neutral_ratio * comment_weight +
            reactions_neutral_ratio * reactions_weight, 3
        ),
    }

    post_sentiments = {"positive": post_positive_ratio, "negative": post_negative_ratio, "neutral": post_neutral_ratio}
    comments_sentiments = {"positive": comments_positive_ratio, "negative": comments_negative_ratio, "neutral": comments_neutral_ratio}
    reactions_sentiments = {"positive": reactions_positive_ratio, "negative": reactions_negative_ratio, "neutral": reactions_neutral_ratio}

    postgres.update_channel(channel_id, channel_sentiment, post_sentiments, comments_sentiments, reactions_sentiments, post_sentiment_data)

    return channel_sentiment


def count(current_file):
    path = "src/" + current_file

    with open(path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    channel_id = data['id']
    channel = data['title']
    posts = data['posts']
    print(f"channel: {channel} channel_id {channel_id}")

    posts_quantity = len(data['posts'])

    if not(postgres.exist_channel(channel_id)):
        print(f'Channel {channel_id} does not exist, adding...')
        postgres.add_channel(channel_id, "Telegram", channel, posts_quantity)
    postgres.add_posts(channel_id, posts)


def check_comment(comment):
    comment_text = comment['text']
    adapt_comment_text = comment_text.replace("'", "''")
    comment_users = []
    user_data = comment["from_user"]
    user_id = user_data["uid"]
    comments_data = postgres.get_comments_duplicate_data(adapt_comment_text)

    if len(comments_data) > 0:
        comments_statistics = comments_data[0][2]
        comments_statistics["comment_count"] += 1
        comment_users = comments_statistics["users"]

        if not (user_id in comment_users):
            comments_statistics["users"].append(user_id)
            comments_statistics = Json(comments_statistics)
            postgres.update_comment_duplicates(adapt_comment_text, comments_statistics)
    else:
        comments_statistics = {}

        if postgres.exist_comment_text(adapt_comment_text):
            comments_statistics["comment_count"] = 2
            comments_statistics["users"] = [user_id]
            comments_statistics = Json(comments_statistics)
            postgres.add_comment_duplicates(adapt_comment_text, comments_statistics)


def get_basic_stats():
    arr = os.listdir("src")
    for file in arr:
        count(file)


def get_sentiment():
    arr = os.listdir("src")
    for file in arr:
        analyse(file)
   

def main():
    postgres.create_tables()
    postgres.update_tables()
    receive_messages()


if __name__ == "__main__":
    main()
