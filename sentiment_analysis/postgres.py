import psycopg2
from psycopg2.extras import Json


def database_credentials():
    return psycopg2.connect(database="media_analysis",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")


def create_tables():
    conn = database_credentials()

    table_channels = "channels"
    table_posts = "posts"
    table_comments = "comments"
    table_comments_duplicates = "comments_duplicates"

    cursor = conn.cursor()
    cursor.execute("select * from information_schema.tables where table_name = '{0}'".format(table_channels))
    if not (bool(cursor.rowcount)):
        print(f'No table ${table_channels}. Creating table')
        cursor.execute("CREATE TABLE {0} ("
                "channel_id int PRIMARY KEY,"
                "type VARCHAR(45),"
                "name VARCHAR(45),"
                "posts_count int,"
                "channel_sentiment jsonb,"
                "post_sentiment jsonb,"
                "comment_sentiment jsonb,"
                "reaction_sentiment jsonb)".format(table_channels))

    cursor.execute("select * from information_schema.tables where table_name = '{0}'".format(table_posts))
    if not (bool(cursor.rowcount)):
        print(f'No table ${table_posts}. Creating table')
        cursor.execute("CREATE TABLE {0} ("
                   "id SERIAL PRIMARY KEY,"
                   "channel_id int REFERENCES channels(channel_id),"
                   "post_id int,"
                   "text TEXT,"
                   "activity_time VARCHAR(45),"
                   "isMedia BOOLEAN,"
                   "comments_count int,"
                   "view_count int,"
                   "reactions jsonb)".format(table_posts))
        
    cursor.execute("select * from information_schema.tables where table_name = '{0}'".format(table_comments))
    if not (bool(cursor.rowcount)):
        print(f'No table ${table_comments}. Creating table')
        cursor.execute("CREATE TABLE {0} ("
                   "id SERIAL PRIMARY KEY,"
                   "post_id int REFERENCES posts(id),"
                   "comment_id int,"
                   "text TEXT,"
                   "activity_time VARCHAR(45),"
                   "user_id VARCHAR(45))".format(table_comments))

    cursor.execute("select * from information_schema.tables where table_name = '{0}'".format(table_comments_duplicates))
    if not (bool(cursor.rowcount)):
        print(f'No table ${table_comments_duplicates}. Creating table')
        cursor.execute("CREATE TABLE {0} ("
                "id SERIAL PRIMARY KEY,"
                "text TEXT,"
                "duplicates jsonb)".format(table_comments_duplicates))

    conn.commit()
    cursor.close()
    conn.close()


def add_channel(channel_id, channel_type, name, posts_count):
    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO channels (channel_id, type, name, posts_count) VALUES (%s, %s, %s, %s)',
                   (channel_id, channel_type, name, posts_count))
    conn.commit()
    cursor.close()
    conn.close()


def add_post(channel_id, post_id, text, activity_time, isMedia, comments_count, view_count, reactions):
    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (channel_id, post_id, text, activity_time, isMedia, comments_count,"
                   " view_count, reactions) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                   (channel_id, post_id, text, activity_time, isMedia, comments_count, view_count, reactions))
    conn.commit()
    cursor.close()
    conn.close()


def add_comment(channel_id, post_id, comment_id, text, activity_time, user_id):
    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute("select * from posts where channel_id = '{0}' and post_id = '{1}'".format(channel_id, post_id))
    rows = cursor.fetchall()
    post = rows[0][0]
    cursor.execute("INSERT INTO comments (post_id, comment_id, text, activity_time, user_id) VALUES (%s, %s, %s, %s, %s)",
                   (post, comment_id, text, activity_time, user_id))
    conn.commit()
    cursor.close()
    conn.close()


def add_comment_duplicates(text, duplicates):
    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO comments_duplicates (text, duplicates) VALUES (%s, %s)',
                    (text, duplicates))
    conn.commit()
    cursor.close()
    conn.close()

def update_channel(channel_id, channel_sentiment, post_sentiment, comment_sentiment, reaction_sentiment):
    conn = database_credentials()
    cursor = conn.cursor()
    
    # Wrap the channel_sentiment dictionary with Json
    channel_sentiment_json = Json(channel_sentiment)
    post_sentiment_json = Json(post_sentiment)
    comment__sentiment_json = Json(comment_sentiment)
    reaction_sentiment_json = Json(reaction_sentiment)
    
    cursor.execute('UPDATE channels SET channel_sentiment = %s, post_sentiment = %s, comment_sentiment = %s, reaction_sentiment  = %s WHERE channel_id = %s',
                   (channel_sentiment_json, post_sentiment_json, comment__sentiment_json, reaction_sentiment_json, channel_id))
    
    conn.commit()
    cursor.close()
    conn.close()


def update_comment_duplicates(text, statistics):
    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute("SELECT * from comments_duplicates WHERE text = '{0}'".format(text))
    rows = cursor.fetchall()
    comment = rows[0][0]
    cursor.execute(f'UPDATE comments_duplicates SET duplicates = %s WHERE id = %s',
                   (statistics, comment))
    conn.commit()
    cursor.close()
    conn.close()


def get_comments_duplicate_data(comment_text):
    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute("SELECT * from comments_duplicates WHERE text = '{0}'".format(comment_text))
    rows = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return rows


def exist_channel(channel_id):
    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute("select * from channels where channel_id = '{0}'".format(channel_id))
    return bool(cursor.rowcount)


def exist_post(channel_id, post_id):
    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute("select * from posts where channel_id = '{0}' and post_id = '{1}'".format(channel_id, post_id))
    return bool(cursor.rowcount)


def exist_comment(post_id, comment_id):
    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute("select * from comments where post_id = '{0}' and comment_id = '{1}'".format(post_id, comment_id))
    return bool(cursor.rowcount)


def exist_comment_text(text):
    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute("select * from comments where text = '{0}'".format(text))
    return bool(cursor.rowcount)


