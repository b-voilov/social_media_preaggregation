import psycopg2
from psycopg2.extras import Json


table_channels = "channels"
table_posts = "posts"
table_comments = "comments"
table_comments_duplicates = "comments_duplicates"


def database_credentials():
    return psycopg2.connect(database="media_analysis",
                            host="localhost",
                            user="postgres",
                            password="postgress",
                            port="5432")


def create_tables():
    conn = database_credentials()

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
                   "channel_id int,"
                   "post_id int,"
                   "text TEXT,"
                   "activity_time VARCHAR(45),"
                   "isMedia BOOLEAN,"
                   "comments_count int,"
                   "view_count int,"
                   "reactions jsonb,"
                   "post_sentiment jsonb)".format(table_posts))
        
    cursor.execute("select * from information_schema.tables where table_name = '{0}'".format(table_comments))
    if not (bool(cursor.rowcount)):
        print(f'No table ${table_comments}. Creating table')
        cursor.execute("CREATE TABLE {0} ("
                   "id SERIAL PRIMARY KEY,"
                   "post_id int,"
                   "comment_id int,"
                   "text TEXT,"
                   "activity_time VARCHAR(45),"
                   "user_id VARCHAR(45),"
                   "comment_sentiment jsonb)".format(table_comments))

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


def update_tables():
    conn = database_credentials()
    cursor = conn.cursor()

    cursor.execute("select * from information_schema.tables where table_name = '{0}'".format(table_posts))
    if bool(cursor.rowcount):
        print(f'Updating ${table_posts}')
        cursor.execute("ALTER TABLE posts ADD COLUMN IF NOT EXISTS post_sentiment jsonb;")
        
    cursor.execute("select * from information_schema.tables where table_name = '{0}'".format(table_comments))
    if bool(cursor.rowcount):
        print(f'Updating ${table_comments}')
        cursor.execute("ALTER TABLE comments ADD COLUMN IF NOT EXISTS comment_sentiment jsonb;")

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

    
def add_posts(channel_id, posts):
    conn = database_credentials()
    cursor = conn.cursor()
    for post in posts:
        post_id = post['post_id']
        post_text = post['text']

        if not post_text == None:
            adapt_post_text = post_text.replace("'", "''")
        else: 
            post_text = ""
            adapt_post_text = post_text

        if not (exist_post(channel_id, post_id)):
                print(f'Post {post_id} does not exist, adding...')
                all_comments = post['comments']
                comments_quantity = len(all_comments)
                all_reactions = Json(post["reactions"])
            
                cursor.execute("INSERT INTO posts (channel_id, post_id, text, activity_time, isMedia, comments_count,"
                   " view_count, reactions) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                   (channel_id, post_id, adapt_post_text, post['datetime'], post['media_in_post'], 
                                  comments_quantity, post['views'], all_reactions))
                add_comments(post_id, post['comments'], cursor)
        else:
                print(f'Post {post_id} exists. Skipping')
                add_comments(post_id, post['comments'], cursor)

    conn.commit()
    cursor.close()
    conn.close()


def add_comments(post_id, comments, cursor):
    for comment in comments:
        if not (exist_comment(post_id, comment['id'])):
            user = comment['from_user']
            user_id = user["uid"]
            comment_text = comment['text']
            adapt_comment_text = comment_text.replace("'", "''")
            cursor.execute("INSERT INTO comments (post_id, comment_id, text, activity_time, user_id) VALUES (%s, %s, %s, %s, %s)",
                           (post_id, comment['id'], adapt_comment_text, comment['datetime'], user_id))
        else:
            print(f'Comment {comment['id']} exists. Skipping')


def add_comment_duplicates(text, duplicates):
    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO comments_duplicates (text, duplicates) VALUES (%s, %s)',
                    (text, duplicates))
    conn.commit()
    cursor.close()
    conn.close()


def update_channel(channel_id, channel_sentiment, agreggated_post_sentiment, agreggated_comment_sentiment, agreggated_reaction_sentiment,
                   posts_sentiment):
    conn = database_credentials()
    cursor = conn.cursor()
    print(f'Uploading data for channel ${channel_id} to the database')
    # Wrap the channel_sentiment dictionary with Json
    channel_sentiment_json = Json(channel_sentiment)
    post_sentiment_json = Json(agreggated_post_sentiment)
    comment_sentiment_json = Json(agreggated_comment_sentiment)
    reaction_sentiment_json = Json(agreggated_reaction_sentiment)
    
    cursor.execute('UPDATE channels SET channel_sentiment = %s, post_sentiment = %s, comment_sentiment = %s, reaction_sentiment  = %s WHERE channel_id = %s',
                   (channel_sentiment_json, post_sentiment_json, comment_sentiment_json, reaction_sentiment_json, channel_id))
    
    update_posts(channel_id, posts_sentiment, cursor)
    conn.commit()
    cursor.close()
    conn.close()


def update_posts(channel_id, post_sentiment, cursor):
    for post in post_sentiment:
        post_sentiment_json = Json(post['sentiment'])
        post_id = post['post_id']
        comment_sentiments = post['comment_sentiments']
        if (exist_post(channel_id, post_id)):
            print(f'Uploading data for post ${post_id} to the database')
            cursor.execute('UPDATE posts SET post_sentiment = %s WHERE channel_id = %s and post_id= %s',
                        (post_sentiment_json, channel_id, post_id))
            update_comments(post_id, comment_sentiments, cursor)
        else:
            print(f'Post ${post_id} does not exist, skipping')


def update_comments(post_id, comment_sentiment, cursor):
    for comment in comment_sentiment:
        comment_sentiment_json = Json(comment['sentiment'])
        comment_id = comment['comment_id']
        # if (exist_comment(post_id, comment_id)):
        cursor.execute('UPDATE comments SET comment_sentiment = %s WHERE post_id= %s and comment_id = %s',
                      (comment_sentiment_json, post_id, comment_id))


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


def post_sentiment_calculated(channel_id, post_id):
        conn = database_credentials()
        cursor = conn.cursor()
        cursor.execute("select * from posts where post_id = '{0}' and channel_id = '{1}'".format(post_id, channel_id))
        if (cursor.fetchall[0][9] is None):
            isCalculated = False
        else:
            isCalculated = True
        return isCalculated

