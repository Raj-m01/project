from flask import Flask, render_template, request
import regex as re
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import emoji

nltk.download('vader_lexicon')

app = Flask(__name__)


@app.route('/', methods=['POST'])
def analyze():
    uploaded_file = request.files['file']
    bytes_data = uploaded_file.read()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user = request.form['user']

    # Sentiment Analysis
    sia = SentimentIntensityAnalyzer()
    df['sentiment'] = df['message'].apply(lambda x: sia.polarity_scores(x)['compound'])

    # Stats Area
    num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,df)

    # monthly timeline
    timeline = helper.monthly_timeline(selected_user,df)
    fig,ax = plt.subplots()
    ax.plot(timeline['time'], timeline['message'],color='green')
    plt.xticks(rotation='vertical')
    plt.savefig('static/monthly_timeline.png')
    plt.close()

    # daily timeline
    daily_timeline = helper.daily_timeline(selected_user, df)
    fig, ax = plt.subplots()
    ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
    plt.xticks(rotation='vertical')
    plt.savefig('static/daily_timeline.png')
    plt.close()

    # activity map
    busy_day = helper.week_activity_map(selected_user,df)
    fig,ax = plt.subplots()
    ax.bar(busy_day.index,busy_day.values,color='purple')
    plt.xticks(rotation='vertical')
    plt.savefig('static/busy_day.png')
    plt.close()

    busy_month = helper.month_activity_map(selected_user, df)
    fig, ax = plt.subplots()
    ax.bar(busy_month.index, busy_month.values,color='orange')
    plt.xticks(rotation='vertical')
    plt.savefig('static/busy_month.png')
    plt.close()

    user_heatmap = helper.activity_heatmap(selected_user,df)
    fig,ax = plt.subplots()
    ax = sns.heatmap(user_heatmap)
    plt.savefig('static/user_heatmap.png')
    plt.close()

    # finding the busiest users in the group(Group level)
    if selected_user == 'Overall':
        x,new_df = helper.most_busy_users(df)
        fig, ax = plt.subplots()
        ax.bar(x.index, x.values,color='red')
        plt.xticks(rotation='vertical')
        plt.savefig('static/most_busy_users.png')
        plt.close()

    # WordCloud
    df_wc = helper.create_wordcloud(selected_user,df)
    fig,ax = plt.subplots()
    ax.imshow(df_wc)
    plt.savefig('static/wordcloud.png')
    plt.close()

    # most common words
    most_common_df = helper.most_common_words(selected_user,df)
    fig,ax = plt.subplots()
    ax.barh(most_common_df[0],most_common_df[1])
    plt.xticks(rotation='vertical')
    plt.savefig('static/most_common_words.png')
    plt.close()
