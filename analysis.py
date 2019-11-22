import nltk
import json
import pandas as pd
from pandas.io.json import json_normalize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sid = SentimentIntensityAnalyzer()

inputfile = 'reviews.json'

df = pd.read_json(inputfile)

df['scores'] = df['text'].apply(lambda review:sid.polarity_scores(review))

df['compound'] = df['scores'].apply(lambda d:d['compound'])

df['score'] = df['compound'].apply(lambda score: 'pos' if score >=0 else 'neg')

# final output with text and sentiment score
df[['text','score']].to_csv('data.csv')