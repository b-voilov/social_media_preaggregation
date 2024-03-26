import json
import dynamo
import uuid
import postgres

# dynamo.create_tables()

# REPLACE LATER
positive_reactions_list = ['👍', '❤', '🎉', '😁', '👍']
negative_reactions_list = ['😡']
neutral_reactions_list = ['🤔', '😢']


# REPLACE WITH API LATER
def get_data(input_file):
    with open(input_file, "r", encoding="utf-8") as json_file:
        content = json.load(json_file)
    return content


# LATER REPLACE WITH DATA FROM DB
def get_comments_data():
    return {}
    # return get_json("results/new_text_comments.json")


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
    comments_count = get_comments_data()
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
        # dynamo.put_new_comment(comment_id, comment, count, users)  # LATER UPDATE FOR EXISTING COMMENTS AND ADD NEW


# postgres.create_tables()
# get_first_telegram_stats()
# upd_comments_duplicates(file, "@ssternenko", "Telegram")
# upd_comments_duplicates(get_data("src/comments.json"), "@ssternenko", "Youtube")
