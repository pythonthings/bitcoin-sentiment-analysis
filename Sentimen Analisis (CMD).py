from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import os
import twitter_credentials
import perbaikan_singkatan
import StopwordsID
import pandas as pd
import numpy as np
from textblob import TextBlob
import re
import string
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory, StopWordRemover, ArrayDictionary
from PIL import Image


####################################################################################
# - - - CRAWLING DATA SECTION
####################################################################################

class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth

class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """
    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords:
        stream.filter(track=hash_tag_list)

class TwitterListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                       tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)

class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """

    def clean_tweet(self, tweet):

        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w +:\/\/ \S +)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        an = TextBlob(self.clean_tweet(tweet))
        analysis = an.translate(from_lang = 'in',to='en')

        if analysis.sentiment.polarity > 0:
            return "Positif"
        elif analysis.sentiment.polarity == 0:
            return "Netral"
        else:
            return "Negatif"

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])

        df['id'] = np.array([tweet.id_str for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['lang'] = np.array([tweet.lang for tweet in tweets])
        df['place'] = np.array([tweet.place for tweet in tweets ])

        return df

###########################################################################################



####################################################################################
# - - - MAIN SECTION
####################################################################################

if __name__ == '__main__':

####################################################################################
# - - - FUNCTION FOR PREPROCESS
####################################################################################

    def remove_punct(text):

        neg_pattern = re.compile(r'\b(' + '|'.join(perbaikan_singkatan.negations_dic.keys()) + r')\b')
        #hapus simbol
        text = text.lower()
        text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',text)
        text = re.sub('rt @[^\s]+',' ', text)
        text = re.sub('@[^\s]+',' ',text)
        text = re.sub(r'[^\x00-\x7F]+',' ', text)
        #Remove additional white spaces
        text = re.sub('[\s]+', ' ', text)
        #Replace #word with word
        neg_handled = neg_pattern.sub(lambda x: perbaikan_singkatan.negations_dic[x.group()], text)
        text = re.sub(r'#([^\s]+)', r'\1', neg_handled)
        #trim
        text = text.strip('\'"')
        text  = "".join([char for char in text if char not in string.punctuation])
        #text = re.sub('[0-9]+', '', text)

        return text

####################################################################################
# - - - FUNCTION FOR MENU
####################################################################################

    def inputNumber(prompt):
        while True:
                try:
                        num = float(input(prompt))
                        break
                except ValueError:
                        pass
        return num

    def displayMenu(options):
            for i in range(len(options)):
                    print("{:d}. {:s}".format(i+1, options[i]))

            choice = 0
            while not(any(choice == np.arange(len(options))+1)):
                    choice = inputNumber("Masukkan Pilihan: ")

            return choice


########################################################################################################

    menuItems = np.array(["Tampilkan Data Twitter", "Tampilkan Histogram","Tampilkan Piechart", "Tampilkan Word Cloud Positif", "Tampilkan Wordcloud Netral", "Tampilkan Wordcloud Negatif", "Simpan Data",  "Keluar"])
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    os.system('cls')
    print("\t\t\tPROGRAM SENTIMEN ANALISIS")
    print("\n\t\tBy : - Mohammad Idham Fachrurrozi \n\t\t     - Sunu Ilham Pradika")
    pilihan = input("\nIngin Menggunakan Data Offline? (y/n) : ")
    if pilihan == "y":
        print("\n1. Indihome \n2. Myindihome \n3. Usee TV \n4. Wifi.id")
        produk = input("\nPilih Produk : ")
        if produk == "1":
            os.chdir('Indihome')
            csv_file = input("Masukkan nama file :")
            keyword = "Indihome"
            df = pd.read_csv(csv_file)
        elif produk == "2":
            csv_file = input("Masukkan nama file :")
            keyword = "Myindihome"
            df = pd.read_csv(csv_file)
            os.chdir('Myindihome')
        elif produk == "3":
            csv_file = input("Masukkan nama file :")
            keyword = "Usee TV"
            df = pd.read_csv(csv_file)
            os.chdir('Indihome')
        elif produk == "4":
            csv_file = input("Masukkan nama file :")
            keyword = "Wifi Id"
            df = pd.read_csv(csv_file)
            os.chdir('Wifi id')
    else:
        keyword = input("Sentimen Apa ? (eX:indihome) :")
        jumlah = input("Berapa banyak data : ")

        api = twitter_client.get_twitter_client_api()

        print("Sedang melakukan pengambilan data . . .")
        tweets = api.search(keyword, count=jumlah)
        print("Selesai!")

        print("Tunggu Sebentar . . .")                                                                     # - - - crawling data

        df = tweet_analyzer.tweets_to_data_frame(tweets)
        df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])

        df['tweet_bersih'] = df['tweets'].apply(lambda x: remove_punct(x))                                              # - - - applying preprocess

    df = df.drop_duplicates(['tweet_bersih'])                                                                               # - - - applying preprocess
    df = df.set_index("source")                                                                                             # - - - applying preprocess
    df = df.drop("Sociomedio Pro Telkom", axis=0)                                                                           # - - - applying preprocess

    # - - - Divide tweets to positive, negative, and neutral
    df_positif = df[df['sentiment'] == 'Positif']
    df_negatif = df[df['sentiment'] == 'Negatif']
    df_netral = df[df['sentiment'] == 'Netral']

    sentimen_count = df['sentiment'].value_counts()
    sentimen_count

    words_positif = ' '.join(df_positif['tweet_bersih'])
    words_negatif = ' '.join(df_negatif['tweet_bersih'])
    words_netral = ' '.join(df_netral['tweet_bersih'])

    # MORE STOPWORDS
    stop_factory = StopWordRemoverFactory().get_stop_words()
    more_stopword = StopwordsID.more_stopword

    # Merge stopword
    data = stop_factory + more_stopword

    dictionary = ArrayDictionary(data)
    StopWordRemover(dictionary)
    stopwords = data

    mask = np.array(Image.open("shape.png"))

########################################################################################################

    while True:

        choice = displayMenu(menuItems)

        if choice == 1:
            print(df)

        elif choice == 2:
            objects = sentimen_count.index
            y_pos = np.arange(len(objects))
            performance = sentimen_count

            plt.bar(y_pos, performance, align='center', alpha=0.5)
            plt.xticks(y_pos, objects)
            plt.ylabel('Jumlah dalam tweets')
            plt.title('Sentiment Topik ' + keyword)

            plt.ion()
            plt.show()

        elif choice == 3:
            labels = sentimen_count.index
            sizes = sentimen_count
            colors = ['steelblue', 'red', 'gray']
            explode = (0.2, 0.1, 0.1)  # explode 1st slice

            # Plot
            plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
            plt.axis('equal')
            plt.ion()
            plt.show()

        elif choice == 4:
            wordcloud = WordCloud(stopwords = stopwords, background_color='white', height = 2000, width = 2000, max_words = 50, font_path='lucidasansdemibold.ttf', prefer_horizontal=0.70, colormap='winter', mask=mask).generate(words_positif)
            plt.imshow(wordcloud, interpolation = "bilinear")
            plt.axis('off')
            plt.ion()
            plt.show()

            # Save the image
            wordcloud.to_file("wordcloud_positif.png")
            print("wordcloud positif tersimpan")

        elif choice == 5:
            wordcloud = WordCloud(stopwords = stopwords, background_color='white', height = 2000, width = 2000, max_words = 50, font_path='lucidasansdemibold.ttf', prefer_horizontal=0.70, colormap='winter', mask=mask).generate(words_netral)
            plt.imshow(wordcloud, interpolation = "bilinear")
            plt.axis('off')
            plt.ion()
            plt.show()

            # Save the image
            wordcloud.to_file("wordcloud_netral.png")
            print("wordcloud netral tersimpan")

        elif choice == 6:
            wordcloud = WordCloud(stopwords = stopwords, background_color='white', height = 2000, width = 2000, max_words = 50, font_path='lucidasansdemibold.ttf', prefer_horizontal=0.70, colormap='winter', mask=mask).generate(words_negatif)
            plt.imshow(wordcloud, interpolation = "bilinear")
            plt.axis('off')
            plt.ion()
            plt.show()

            # Save the image
            wordcloud.to_file("wordcloud_negatif.png")
            print("wordcloud negatif tersimpan")

        elif choice == 7:
            df.to_csv("Data.csv")
            df.to_excel("Data.xlsx")

        elif choice == 8:
            break
