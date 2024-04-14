import psycopg2

# CLEAN UP AFTER DATABASE IS FILLED?
def create_tables():
    conn = psycopg2.connect(database="media_analysis",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")

    table_channels = "channels_test"
    table_posts = "posts_test"
    table_comments = "comments_duplicates_test"

    cursor = conn.cursor()
    cursor.execute("select * from information_schema.tables where table_name = '{0}'".format(table_channels))
    if not (bool(cursor.rowcount)):
        print(f'No table ${table_channels}. Creating table')
        cursor.execute("CREATE TABLE {0} ("
                "channel_id int PRIMARY KEY,"
                "type VARCHAR(45),"
                "name VARCHAR(45),"
                "posts_count int,"
                "channel_sentiment jsonb)".format(table_channels))

    cursor.execute("select * from information_schema.tables where table_name = '{0}'".format(table_posts))
    if not (bool(cursor.rowcount)):
        print(f'No table ${table_posts}. Creating table')
        cursor.execute("CREATE TABLE {0} ("
                   "id SERIAL PRIMARY KEY,"
                   "channel_id int REFERENCES channels_test(channel_id),"
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
                "text TEXT,"
                "duplicates jsonb)".format(table_comments))

    conn.commit()
    cursor.close()
    conn.close()


def add_channel(channel_id, channel_type, name, posts_count):
    conn = psycopg2.connect(database="media_analysis",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")

    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO channels_test (channel_id, type, name, posts_count) VALUES (%s, %s, %s, %s)',
                   (channel_id, channel_type, name, posts_count))
    conn.commit()
    cursor.close()
    conn.close()


def add_post(channel_id, post_id, text, activity_time, isMedia, comments_count, view_count, reactions):
    conn = psycopg2.connect(database="media_analysis",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")

    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts_test (channel_id, post_id, text, activity_time, isMedia, comments_count,"
                   " view_count, reactions) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                   (channel_id, post_id, text, activity_time, isMedia, comments_count, view_count, reactions))
    conn.commit()
    cursor.close()
    conn.close()


def add_comments(text, duplicates):
    conn = psycopg2.connect(database="media_analysis",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")

    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO comments_duplicates_test (text, duplicates) VALUES (%s, %s)',
                    (text, duplicates))
    conn.commit()
    cursor.close()
    conn.close()

def update_channel(channel_id, posts_count, channel_sentiment):
    conn = psycopg2.connect(database="media_analysis",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")

    cursor = conn.cursor()
    cursor.execute(f'UPDATE channels_test SET posts_count = %s, channel_sentiment = %s WHERE id = %s',
                   (posts_count, channel_sentiment, channel_id))
    conn.commit()
    cursor.close()
    conn.close()

# TO DO IF NEEDED
# def update_post(channel_id, post_id, text, activity_time, isMedia, comments_count, view_count, reactions):
#    conn = psycopg2.connect(database="media_analysis",
#                            host="localhost",
#                            user="postgres",
#                            password="postgres",
#                            port="5432")
#
#    cursor = conn.cursor()
#    cursor.execute("INSERT INTO posts (channel_id, post_id, text, activity_time, isMedia, comments_count,"
#                   " view_count, reactions) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
#                   (channel_id, post_id, text, activity_time, isMedia, comments_count, view_count, reactions))
#    conn.commit()
#    cursor.close()
#    conn.close()


def update_comments(text, statistics):
    conn = psycopg2.connect(database="media_analysis",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")

    cursor = conn.cursor()
    cursor.execute("SELECT * from comments_duplicates_test WHERE text = '{0}'".format(text))
    rows = cursor.fetchall()
    comment = rows[0][0]
    cursor.execute(f'UPDATE comments_duplicates_test SET duplicates = %s WHERE id = %s',
                   (statistics, comment))
    conn.commit()
    cursor.close()
    conn.close()


def get_comments_data(comment_text):
    conn = psycopg2.connect(database="media_analysis",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")

    cursor = conn.cursor()
    cursor.execute("SELECT * from comments_duplicates_test WHERE text = '{0}'".format(comment_text))
    rows = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return rows


def exist_channel(channel_id):
    conn = psycopg2.connect(database="media_analysis",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")

    cursor = conn.cursor()
    cursor.execute("select * from channels_test where channel_id = '{0}'".format(channel_id))
    return bool(cursor.rowcount)


def exist_post(channel_id, post_id):
    conn = psycopg2.connect(database="media_analysis",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")

    cursor = conn.cursor()
    cursor.execute("select * from posts_test where channel_id = '{0}' and post_id = '{1}'".format(channel_id, post_id))
    return bool(cursor.rowcount)

