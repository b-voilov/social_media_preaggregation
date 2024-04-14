import json
import uuid
import postgres
from psycopg2.extras import Json 
import os


# REPLACE WITH API LATER
def get_data(input_file):
    with open(input_file, "r", encoding="utf-8") as json_file:
        content = json.load(json_file)
    return content

# CLEAN UP LATER
def get_json(input_file):
    with open(input_file, "r", encoding="utf-8") as json_file:
        content = json.load(json_file)
    return content

# LATER REPLACE WITH DATA FROM DB
def get_comments_data(input_file):
    return get_json(input_file)


#  FILL FIRST DATA TO TRY IN GRAFANA
def get_first_telegram_stats():
    channel_type = "Telegram"
    tg_file = get_data("src/example_data.json")
    for x in tg_file.keys():
        postgres.add_channel(channel_type, x, len(tg_file[x]))
        for y in tg_file[x]:
            channel = x
            text = y["post_text"]
            activity_time = y["datetime"]
            postgres.add_post(channel, text, activity_time)
            comments_count = len(y["comments"])
            negative_reactions = 0
            positive_reactions = len(y["reactions"])
            neutral_reactions = 0
            postgres.add_post_activity(activity_time, comments_count, negative_reactions, positive_reactions,
                                       neutral_reactions)


# WORK IN PROGRESS
def get_first_youtube_stats():
    channels = get_data("src/channels.json")
    comments = get_data("src/comments.json")
    videos = get_data("src/videos.json")


def get_telegram_comments_count(input_file, channel_name):
    config = input_file[channel_name]
    comments_count = get_comments_data("results/new_text_comments.json")
    # Looking through each post
    for x in config:
        if "comments" in x:
            comments = x.get("comments")
            for y in comments:
                comment_users = {}
                current_comment = {}
                comment_text = y.get("text")
                user_id = y.get("from_user")
                # check if there was a comment like that before
                if comment_text in comments_count:
                    current_comment = comments_count[comment_text]
                    current_comment["comment_number"] += 1
                    comment_users = current_comment["users"]
                    if user_id in comment_users:
                        comment_users[user_id] += 1
                    else:
                        comment_users[user_id] = 1
                    current_comment["users"] = comment_users
                else:
                    current_comment["comment_number"] = 1
                    comment_users[user_id] = 1
                    current_comment["users"] = comment_users
                comments_count[comment_text] = current_comment
    return comments_count


def get_youtube_comments_count(input_file):
    config = input_file
    comments_count = get_comments_data()
    for x in config:
        comment_video = {}
        current_comment = {}
        comment_text = x.get("textDisplay")
        video_id = x.get("videoId")
        if comment_text in comments_count:
            current_comment = comments_count[comment_text]
            current_comment["comment_number"] += 1
            comment_video = current_comment["videos"]
            if video_id in comment_video:
                comment_video[video_id] += 1
            else:
                comment_video[video_id] = 1
            current_comment["videos"] = comment_video
        else:
            current_comment["comment_number"] = 1
            comment_video[video_id] = 1
            current_comment["videos"] = comment_video
        comments_count[comment_text] = current_comment
    return comments_count


def upd_comments_duplicates(input_file, channel_name, channel_type):
    if channel_type == "Youtube":
        comments_count = get_youtube_comments_count(input_file)
    else:
        comments_count = get_telegram_comments_count(input_file, channel_name)

    # SAVE TO JSON FOR TEST PURPOSES
    with open("results/new_text_comments_1.json", mode="w", encoding='utf-8') as new_file:
        json.dump(comments_count, new_file, ensure_ascii=False)

    # NEED TO CHECK AND UPDATE ONLY COMMENTS WITH 2 AND MORE DUPLICATES
    for x in comments_count.keys():
        current_comment = comments_count[x]
        comment = x
        count = current_comment.get("comment_number")
        users = current_comment.get("users")
        comment_id = str(uuid.uuid4())


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
            postgres.add_channel(channel_id, "Telegram", channel, posts_quantity) #TYPE CHECK

        for post in posts:
            post_id = post['post_id']
            post_text = post['text']

            if not post_text == None:
                adapt_post_text = post_text.replace("'", "''")
            else: 
                post_text = ""
                adapt_post_text = post_text

            if not (postgres.exist_post(channel_id, post_id)):
                comments_quantity = len(post['comments'])
                all_reactions = Json(post["reactions"])
                postgres.add_post(channel_id, post_id, adapt_post_text, post['datetime'], post['media_in_post'], 
                                  comments_quantity, post['views'], all_reactions)
            else:
                print(f'Post {post_id} exists. Skipping')


def main():
    postgres.create_tables()
    arr = os.listdir("src")
    for file in arr:
        count(file)
     
     
if __name__ == "__main__":
    main()