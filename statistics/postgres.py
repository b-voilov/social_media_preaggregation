import psycopg2


def create_tables():
    conn = psycopg2.connect(database="media_analysis",
                            host="DummyHost",
                            user="postgres",
                            password="DummyPassword",
                            port="5432")

    cursor = conn.cursor()
    cursor.execute("CREATE TABLE comments_duplicates("
                   "id SERIAL PRIMARY KEY,"
                   "comment VARCHAR(45),"
                   "duplicates INT)")

    cursor.execute("CREATE TABLE botlike_users("
                   "id SERIAL PRIMARY KEY,"
                   "type VARCHAR(45),"
                   "comment int REFERENCES comments_duplicates(id))")

    cursor.execute("CREATE TABLE channels("
                   "channel_id SERIAL PRIMARY KEY,"
                   "type VARCHAR(45),"
                   "name VARCHAR(45),"
                   "posts_count int)")

    cursor.execute("CREATE TABLE posts("
                   "post_id SERIAL PRIMARY KEY,"
                   "channel_id int REFERENCES channels(channel_id),"
                   "text TEXT,"
                   "activity_time VARCHAR(45))")

    cursor.execute("CREATE TABLE post_activity("
                   "activity_id SERIAL PRIMARY KEY,"
                   "post_id int REFERENCES posts(post_id),"
                   "comments_count int,"
                   "negative_reactions int,"
                   "positive_reactions int,"
                   "neutral_reactions int)")

    conn.commit()
    cursor.close()
    conn.close()


def add_channel(channel_type, name, posts_count):
    conn = psycopg2.connect(database="media_analysis",
                            host="DummyHost",
                            user="postgres",
                            password="DummyPassword",
                            port="5432")

    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO channels (type, name, posts_count) VALUES (%s, %s, %s)',
                   (channel_type, name, posts_count))
    conn.commit()
    cursor.close()
    conn.close()


def add_post(channel, text, activity_time):
    conn = psycopg2.connect(database="media_analysis",
                            host="DummyHost",
                            user="postgres",
                            password="DummyPassword",
                            port="5432")

    cursor = conn.cursor()
    cursor.execute("SELECT * from channels WHERE name = '{0}'".format(channel))
    rows = cursor.fetchall()
    channel_id = rows[0][0]
    print(channel_id)
    cursor.execute("INSERT INTO posts (channel_id, text, activity_time) VALUES (%s, %s, %s)",
                   (channel_id, text, activity_time))
    conn.commit()
    cursor.close()
    conn.close()


def add_post_activity(activity_time, comments_count, negative_reactions, positive_reactions, neutral_reactions):
    conn = psycopg2.connect(database="media_analysis",
                            host="DummyHost",
                            user="postgres",
                            password="DummyPassword",
                            port="5432")

    cursor = conn.cursor()
    cursor.execute("SELECT * from posts WHERE activity_time = '{0}'".format(activity_time))
    rows = cursor.fetchall()
    post_id = rows[0][0]
    print(post_id)

    cursor.execute(f'INSERT INTO post_activity (post_id, comments_count, negative_reactions, '
                   f'positive_reactions, neutral_reactions) VALUES (%s, %s, %s, %s, %s)',
                   (post_id, comments_count, negative_reactions, positive_reactions, neutral_reactions))

    conn.commit()
    cursor.close()
    conn.close()


#  TODO
def update_activity():
    conn = psycopg2.connect(database="media_analysis",
                            host="DummyHost",
                            user="postgres",
                            password="DummyPassword",
                            port="5432")

    cursor = conn.cursor()
    conn.commit()
    cursor.close()
    conn.close()


#  TODO
def update_channel():
    conn = psycopg2.connect(database="media_analysis",
                            host="DummyHost",
                            user="postgres",
                            password="DummyPassword",
                            port="5432")

    cursor = conn.cursor()
    conn.commit()
    cursor.close()
    conn.close()


#  TODO
def update_comments():
    conn = psycopg2.connect(database="media_analysis",
                            host="DummyHost",
                            user="postgres",
                            password="DummyPassword",
                            port="5432")

    cursor = conn.cursor()
    conn.commit()
    cursor.close()
    conn.close()


