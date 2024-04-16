#import nltk
import json
from transformers import pipeline
import postgres
from psycopg2.extras import Json 
import os


analyze_sentiment = pipeline("sentiment-analysis", model="cardiffnlp/twitter-xlm-roberta-base-sentiment") 
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
    path = "src/"+ current_file
    with open(path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    reaction_sentiment_cache = {}

    # adjust these weights as needed
    # the bigger the weight, the bigger it's impact on channel sentiment analysis
    post_weight = 0.4
    comment_weight = 0.4
    reactions_weight = 0.2

    for item in data:
        channel_id = item['id']
        channel = item['title']
        posts = item['posts']
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
                
                # now push reaction_sentiment (likes/dislikes) for this post
                
            ratio_normalization(sentiments) # return ratio, push it too

        channel_sentiment = calculate_channel_sentiment(posts_sentiment_aggregated, comments_sentiment_aggregated, reactions_sentiment_aggregated, post_weight, comment_weight, reactions_weight)

        postgres.update_channel(channel_id, channel_sentiment, posts_sentiment_aggregated, comments_sentiment_aggregated, reactions_sentiment_aggregated)

        print(f"channel sentiment: {channel_sentiment}")

        # now push posts_quantity, channel_sentiment for this channel

def calculate_channel_sentiment(posts_sentiment_aggregated, comments_sentiment_aggregated, reactions_sentiment_aggregated, post_weight, comment_weight, reactions_weight):
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

    channel_sentiment = {
        "positive": round(
            ratio_normalization(posts_sentiment_aggregated)["positive"] * post_weight +
            ratio_normalization(comments_sentiment_aggregated)["positive"] * comment_weight +
            ratio_normalization(reactions_sentiment_aggregated)["positive"] * reactions_weight, 3
        ),
        "negative": round(
            ratio_normalization(posts_sentiment_aggregated)["negative"] * post_weight +
            ratio_normalization(comments_sentiment_aggregated)["negative"] * comment_weight +
            ratio_normalization(reactions_sentiment_aggregated)["negative"] * reactions_weight, 3
        ),
        "neutral": round(
            ratio_normalization(posts_sentiment_aggregated)["neutral"] * post_weight +
            ratio_normalization(comments_sentiment_aggregated)["neutral"] * comment_weight +
            ratio_normalization(reactions_sentiment_aggregated)["neutral"] * reactions_weight, 3
        ),
    }

    return channel_sentiment


def count(current_file):
    path = "src/"+ current_file

    with open(path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    for item in data:
        channel_id = item['id']
        channel = item['title']
        posts = item['posts']
        print(f"channel: {channel} channel_id {channel_id}")

        posts_quantity = len(item['posts'])

        if not(postgres.exist_channel(channel_id)):
            print(f'{channel_id} does not exist, adding...')
            postgres.add_channel(channel_id, "Telegram", channel, posts_quantity) 

        for post in posts:
            post_id = post['post_id']
            post_text = post['text']

            if not post_text == None:
                adapt_post_text = post_text.replace("'", "''")
            else: 
                post_text = ""
                adapt_post_text = post_text

            if not (postgres.exist_post(channel_id, post_id)):
                all_comments = post['comments']
                comments_quantity = len(all_comments)
                all_reactions = Json(post["reactions"])
                postgres.add_post(channel_id, post_id, adapt_post_text, post['datetime'], post['media_in_post'], 
                                  comments_quantity, post['views'], all_reactions)

                for comment in all_comments:
                    check_comment(comment)
                    user = comment['from_user']
                    user_id = user["uid"]
                    comment_text = comment['text']
                    adapt_comment_text = comment_text.replace("'", "''")
                    postgres.add_comment(channel_id, post_id, comment['id'], adapt_comment_text, comment['datetime'], user_id)
            else:
                print(f'Post {post_id} exists. Skipping')


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
    get_basic_stats()
    get_sentiment()


if __name__ == "__main__":
    main()
