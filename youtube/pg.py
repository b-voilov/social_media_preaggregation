import psycopg2
# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(
  host="media-analysis.ctswok4gi0gq.us-east-1.rds.amazonaws.com",
  port=5432,
  user="postgres",
  password="5T2FkWFcR49k",
  database="media_analysis"
)
def add_channel(channel):
  cursor = conn.cursor()
  cursor.execute('''
    INSERT INTO youtube_channels (
      id,
      title,
      description_channel,
      custom_url,
      published_at,
      default_language,
      country,
      view_count,
      subscriber_count,
      video_count
    ) VALUES (
      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )  ON CONFLICT DO NOTHING
  ''', (
    channel['id'],
    channel['title'],
    channel['descriptionChannel'],
    channel['customUrl'],
    channel['publishedAt'],
    channel['defaultLanguage'],
    channel['country'],
    channel['viewCount'],
    channel['subscriberCount'],
    channel['videoCount']
  ))
  conn.commit()
  cursor.close()

def add_video(video):
  cursor = conn.cursor()
  cursor.execute('''
    INSERT INTO youtube_videos (
      id,
      published_at,
      channel_id,
      channel_title,
      title,
      description_video,
      duration,
      definition_video,
      default_audio_language,
      view_count,
      like_count,
      dislike_count,
      favorite_count,
      comment_count,
      recording_date,
      speech_text,
      title_pos_sentiment,
      title_neg_sentiment,
      description_pos_sentiment,
      description_neg_sentiment
    ) VALUES (
      %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
  ) ON CONFLICT DO NOTHING''', (
    video['id'],
    video['publishedAt'],
    video['channelId'],
    video['channelTitle'],
    video['title'],
    video['descriptionVideo'],
    video['duration'],
    video['definitionVideo'],
    video['defaultAudioLanguage'],
    video['viewCount'],
    video['likeCount'],
    video['dislikeCount'],
    video['favoriteCount'],
    video['commentCount'],
    video['recordingDate'],
    video['speechText'],
    video['titlePosSentiment'],
    video['titleNegSentiment'],
    video['descriptionPosSentiment'],
    video['descriptionNegSentiment']
  ))

  conn.commit()
  cursor.close()

def add_comment(comments):
  cursor = conn.cursor()

  for comment in comments: 
    cursor.execute('''
      INSERT INTO youtube_comments (
        id,
        text_display,
        like_count,
        published_at,
        updated_at,
        parent_id,
        video_id,
        pos_sentiment,
        neg_sentiment
      ) VALUES (
        %s,%s,%s,%s,%s,%s,%s,%s,%s
      ) ON CONFLICT DO NOTHING
    ''', (
      comment['id'],
      comment['textDisplay'],
      comment['likeCount'],
      comment['publishedAt'],
      comment['updatedAt'],
      comment['parentId'],
      comment['videoId'],
      comment['posSentiment'],
      comment['negSentiment']
    ))

  conn.commit()
  cursor.close()

def init_db():
  
  cursor = conn.cursor()
  
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS youtube_channels (
      id VARCHAR(255) PRIMARY KEY,
      title VARCHAR(255),
      description_channel TEXT,
      custom_url VARCHAR(255),
      published_at TIMESTAMP,
      default_language VARCHAR(255),
      country VARCHAR(255),
      view_count BIGINT,
      subscriber_count INTEGER,
      video_count INTEGER
    )
  ''')

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS youtube_videos (
      id VARCHAR(255) PRIMARY KEY,
      published_at TIMESTAMP,
      channel_id VARCHAR(255),
      channel_title VARCHAR(255),
      title VARCHAR(255),
      description_video TEXT,
      duration VARCHAR(255),
      definition_video VARCHAR(255),
      default_audio_language VARCHAR(255),
      view_count BIGINT,
      like_count INTEGER,
      dislike_count INTEGER,
      favorite_count INTEGER,
      comment_count INTEGER,
      recording_date TIMESTAMP,
      speech_text TEXT,
      title_pos_sentiment INTEGER,
      title_neg_sentiment INTEGER,
      description_pos_sentiment INTEGER,
      description_neg_sentiment INTEGER
    )
  ''')

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS youtube_comments (
      id VARCHAR(255) PRIMARY KEY,
      text_display TEXT,
      like_count INTEGER,
      published_at TIMESTAMP,
      updated_at TIMESTAMP,
      parent_id VARCHAR(255),
      video_id VARCHAR(255),
      pos_sentiment INTEGER,
      neg_sentiment INTEGER
    )
  ''')
  
  conn.commit()
  cursor.close()

