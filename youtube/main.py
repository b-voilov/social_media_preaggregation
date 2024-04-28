import requests
import json
import datetime
from polyglot.text import Text
from pg import init_db, add_channel, add_video, add_comment
import time
url = "https://youtube-team-b.vercel.app/api/channels"

response = requests.get(url)
data = response.json()

def lang(text):
  if any(char in text for char in ['і','І','ї', 'Є','є','ґ','Ґ']): 
    return 'uk'
  elif any(ord(c) > 127 for c in text):
    return 'ru'
  else:
    return 'en'
    

def get_sentiment(text):
  if len(text) == 0:
    return (0,0)
  text = Text(text, hint_language_code=lang(text))
  pos_sent = 0
  neg_sent = 0
  for w in text.words:
    if w.polarity > 0:
      pos_sent += w.polarity.item()
    elif w.polarity < 0:
      neg_sent += w.polarity.item()
  return (pos_sent/len(text.words), neg_sent/len(text.words))
# print(json.dumps(data, indent=4,ensure_ascii=False))

for channel in data:
  # Calculate the date one week ago

  start_date = (datetime.datetime.now()- datetime.timedelta(weeks=3)).strftime("%Y-%m-%d 00:00:00")
  end_date = (datetime.datetime.now()- datetime.timedelta(weeks=0)).strftime("%Y-%m-%d 23:59:59")

  videos_url = f"https://youtube-team-b.vercel.app/api/channels/videos?channelId={channel['id']}&startDate={start_date}&endDate={end_date}"
  videos = requests.get(videos_url).json()
  print(json.dumps(channel, indent=4, ensure_ascii=False))
  add_channel(channel)
  for idx,video in enumerate(videos):
    text = Text(video['title'], hint_language_code='en')
    print(channel['title'],idx,len(videos),video['title'])
    titleSentiment = get_sentiment(video['title'])
    video['titlePosSentiment'] = titleSentiment[0]
    video['titleNegSentiment'] = titleSentiment[1]
    descriptionSentiment = get_sentiment(video['descriptionVideo'])
    video['descriptionPosSentiment'] = descriptionSentiment[0]
    video['descriptionNegSentiment'] = descriptionSentiment[1]
    print(titleSentiment)
    speechSentiment = get_sentiment(video['speechText'])
    print("SPEECH SENTIMENT:",len(video['speechText']), speechSentiment)
    video['speechPosSentiment'] = speechSentiment[0]
    video['speechNegSentiment'] = speechSentiment[1]
    comments_url = f"https://youtube-team-b.vercel.app/api/channels/comments?videoId={video['id']}&startDate={start_date}&endDate={end_date}"
    comments = requests.get(comments_url).json()
    #print(json.dumps(video, indent=4, ensure_ascii=False))
    add_video(video)
    print(f"commets {len(comments)}")
    for comment in comments:
      sentiment = get_sentiment(comment['textDisplay'])
      comment['posSentiment'] = sentiment[0]
      comment['negSentiment'] = sentiment[1]
    start_time = time.time()
    add_comment(comments)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"add_comments {len(comments)} execution time: {execution_time} seconds")
