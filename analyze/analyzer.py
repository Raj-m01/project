from flask import Flask, request, render_template
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

app = Flask(__name__)

def analyze():
    if request.method == 'POST':
        file = request.files['file']
        data = file.read().decode("utf-8")
        df = preprocessor.preprocess(data)

        user = request.form['user']

        # Sentiment Analysis
        sia = SentimentIntensityAnalyzer()
        df['sentiment'] = df['message'].apply(lambda x: sia.polarity_scores(x)['compound'])

        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(user, df)
        stats_html = f"<h2>Top Statistics</h2><p>Total Messages: {num_messages}</p><p>Total Words: {words}</p><p>Media Shared: {num_media_messages}</p><p>Links Shared: {num_links}</p>"

        # Monthly Timeline
        timeline = helper.monthly_timeline(user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        timeline_html = f"<h2>Monthly Timeline</h2><img src='{fig_to_uri(fig)}'>"

        # Daily Timeline
        daily_timeline = helper.daily_timeline(user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        daily_timeline_html = f"<h2>Daily Timeline</h2><img src='{fig_to_uri(fig)}'>"

        # Activity Map
        busy_day = helper.week_activity_map(user, df)
        fig, ax = plt.subplots()
    pass
