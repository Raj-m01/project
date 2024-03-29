import regex as re
import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from analyze import analyzer
import emoji

import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


from nltk.stem import WordNetLemmatizer


from nltk.tokenize import word_tokenize
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")

def extract_emojis(s):
        return ''.join(c for c in s if c in emoji.UNICODE_EMOJI['en'])

if uploaded_file is not None:
    # analyzer.analyze()
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)

    if st.sidebar.button("Show Analysis"):

        # Sentiment Analysis
        sia = SentimentIntensityAnalyzer()
        df['sentiment'] = df['message'].apply(lambda x: sia.polarity_scores(x)['compound'])


        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(str(num_messages)+"+")
        with col2:
            st.header("Total Words")
            st.title(str(words)+"+")
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'],color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1,col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user,df)
        fig,ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x,new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values,color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # Add TOPIC MODELLING 
        # Convert messages to a list of strings

        messages = df['message'].tolist()
        # Create a CountVectorizer object to convert text to a matrix of word counts
        vectorizer = CountVectorizer(stop_words='english')
        # Convert the messages to a matrix of word counts
        word_counts = vectorizer.fit_transform(messages)
        # Set the number of topics to be identified
        num_topics = 5
        # Create a LatentDirichletAllocation object to perform topic modeling
        lda = LatentDirichletAllocation(n_components=num_topics, random_state=0)
        # Fit the model to the word counts
        lda.fit(word_counts)
        # Get the top 10 words for each topic
        num_top_words = 10
        vocab = vectorizer.get_feature_names()
        topics = []
        print("topic modelling")
        for i, topic in enumerate(lda.components_):
            top_words = [vocab[j] for j in topic.argsort()[:-num_top_words - 1:-1]]
            topics.append(', '.join(top_words))
            print(f"Topic {i+1}: {', '.join(top_words)}")
        # Add a new column to the dataframe with the topic for each message
        topic_values = lda.transform(word_counts)
        fetched_topics = topic_values.argmax(axis=1)

        # Print the vectors with the added topic column
        print(fetched_topics)

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user,df)
        fig,ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # most common words
        most_common_df = helper.most_common_words(selected_user,df)

        fig,ax = plt.subplots()

        ax.barh(most_common_df[0],most_common_df[1])
        plt.xticks(rotation='vertical')

        st.title('Most commmon words')
        st.pyplot(fig)



        # emoji analysis
        emoji_df = helper.emoji_helper(selected_user,df)
        st.title("Emoji Analysis")

        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig,ax = plt.subplots()
            ax.pie(emoji_df[1].head(),labels=emoji_df[0].head(),autopct="%0.2f")
            st.pyplot(fig)

        
        # create a new column to store the extracted emojis
        df['emojis'] = df['message'].apply(extract_emojis)
        # group the DataFrame by "user" and count the number of emojis sent by each user
        # emoji_counts = df.groupby('user')['emojis'].apply(lambda x: ''.join(x)).apply(lambda x: len(re.findall(r'[\U0001F600-\U0001F64F]', x)))
        emoji_counts = df.groupby('user')['emojis'].apply(lambda x: ''.join(x)).apply(lambda x: len(re.findall(r'[\U0001F600-\U0001F64F]', x))).sort_values(ascending=False)

        st.write("Users emojis count")
        st.dataframe(emoji_counts)
        
        

        # Sentiment Analysis Results
        sentiment_df = df.groupby('user')['sentiment'].mean().reset_index()
        st.title("Sentiment Analysis")
        fig, ax = plt.subplots(figsize=(20,20))
        ax.bar(sentiment_df['user'], sentiment_df['sentiment'], color='blue')
        plt.xticks(rotation='vertical')
        plt.subplots_adjust(bottom=0.7)
        ax.set_xlabel('User', fontsize=10)
        ax.set_ylabel('Sentiment Score', fontsize=14)
        ax.set_title('Sentiment Analysis', fontsize=16)
        st.pyplot(fig)


        

#  ************************** Message Classification 


       
        # Define categories and keywords for each category
        categories = {
            'questions': ['?', 'what', 'why', 'how', 'when', 'who'],
            'announcements': ['announcement', 'important', 'urgent', 'reminder'],
            'greetings': ['hi', 'hello', 'hey', 'morning', 'evening'],
            'media': ['image', 'video', 'gif', 'media'],
            'links': ['link', 'url', 'website']
        }

   
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()

        def preprocess_text(text):
            words = word_tokenize(text.lower())
            words = [w for w in words if not w in stop_words and w.isalpha()]
            words = [lemmatizer.lemmatize(w) for w in words]
            return ' '.join(words)

        df['processed_message'] = df['message'].apply(preprocess_text)

        # Assign categories to each message
        def categorize_message(text):
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword in text:
                        return category
            return 'other'

        df['category'] = df['processed_message'].apply(categorize_message)

        # Train a Random Forest classifier for message classification
        X_train, X_test, y_train, y_test = train_test_split(df['processed_message'], df['category'], test_size=0.2, random_state=42)
        vectorizer = CountVectorizer()
        X_train = vectorizer.fit_transform(X_train)
        X_test = vectorizer.transform(X_test)
        clf = RandomForestClassifier(n_estimators=100, random_state=42)

        clf.fit(X_train, y_train)

        # y_pred = clf.predict(X_test)
        # accuracy = accuracy_score(y_test, y_pred)
        # print('@@@@@@@@@@@@@@@@@@@@@@@@@Accuracy:', accuracy)
        # df['category_pred'] = y_pred
        # print(df[['message', 'category_pred']])

        X = vectorizer.transform(df['processed_message'])
        categories_pred = clf.predict(X)
        df['category_pred'] = categories_pred

        # Print the classified result
        print(df[['message', 'category_pred']])








 # ************************** new feat

'''
# CHAT SUMMARY

        # tokenize and preprocess the messages
        lemmatizer = WordNetLemmatizer()
        stop_words = stopwords.words('english')
        df['processed'] = df['message'].apply(lambda x: [lemmatizer.lemmatize(w) for w in nltk.word_tokenize(x.lower()) if w.isalpha() and w not in stop_words])

        # create a bag-of-words representation of the messages
        cv = CountVectorizer(tokenizer=lambda x: x, preprocessor=lambda x: x)
        cv.fit(df['processed'])
        bow = cv.transform(df['processed'])

        # train LDA model to identify topics
        lda_model = LatentDirichletAllocation(n_components=10, max_iter=10, learning_method='online', random_state=42)
        lda_model.fit(bow)

        # print topics identified by LDA model
        print("Topics found via LDA:")
        for idx, topic in enumerate(lda_model.components_):
            print(f"Topic {idx}:")
            print([cv.get_feature_names()[i] for i in topic.argsort()[:-11:-1]])
            print('\n')

        # identify topic for each message
        df['topic'] = lda_model.transform(bow).argmax(axis=1)

        # extract most representative message for each topic
        summary = ''
        for i in range(lda_model.n_components):
            topic_messages = df.loc[df['topic'] == i, 'message']
            if not topic_messages.empty:
                top_message = topic_messages.value_counts().index[0]
                summary += f"Topic {i}: {top_message}\n\n"

        # print chat summary
        print("Chat Summary:")
        print(summary)
        '''

