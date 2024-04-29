# WIP

Packages required (you can install them via 'pip install'):

'
ntlk
transformers
sentencepiece
numpy
torch
requests
'

Install them with:
```
pip install -r requirements.txt
```
Update postgres credentials in file postgres.py if needed
```
Put json files to analyse into /src folder
```
Now simply run the code:
```
python3 main.py
```

The code is far from complete, but, by far it analyzes:
1. Post sentiment, number of posts
2. Average comments sentiment for a particular post, number of comments for this post
3. Average reactions sentiment per post (which can be correlated to comments sentiment)
4. Aggregated channel sentiment
5. Checks comments for duplicates

Code also puts collected data to postgres.
Credentials should be updated to users credentials or inquired from the team lead.

Important: all the sentiments can be represented as diagrams in front-end

The main issue encountered now is huge overhead -- thanks to slow sentiment analysis, but this model is by far the best for slavic languages like Ukrainian and russian. Also the code will be further optimized with parallelization, batching etc. 