from turtle import clear
from nltk.corpus import twitter_samples
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk import FreqDist
from nltk import classify
from nltk import NaiveBayesClassifier
from nltk.tokenize import word_tokenize

stop_words = stopwords.words('english')

import re, string
import random


from nltk.corpus import twitter_samples
positive_tweets = twitter_samples.strings('positive_tweets.json')
negative_tweets = twitter_samples.strings('negative_tweets.json')
text = twitter_samples.strings('tweets.20150430-223406.json')
tweet_tokens = twitter_samples.tokenized('positive_tweets.json')

def lemmatize_sentence(tweet):
    lemmatizer = WordNetLemmatizer()
    lemmatized_sentences = []

    for word, tag in pos_tag(tweet):
        if tag.startswith('VB'):
            pos = 'v'
        elif tag.startswith('NN'):
            pos = 'n'
        else:
            pos = 'a'
        lemmatized_sentences.append(lemmatizer.lemmatize(word,pos))
    return lemmatized_sentences

def clear_tweet(tweet, stop_words = ()):
    cleaned_tweet = []
    for text, tag in pos_tag(tweet):
        text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', text)
        text = re.sub("(@[A-Za-z0-9_]+)","", text)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        text = lemmatizer.lemmatize(text, pos)

        if len(text) > 0 and text not in string.punctuation and text.lower() not in stop_words:
            cleaned_tweet.append(text.lower())
    return cleaned_tweet


positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')
positive_cleaned_tweets_list = []
negative_cleaned_tweets_list = []

for tweet in positive_tweet_tokens:
    positive_cleaned_tweets_list.append(clear_tweet(tweet, stop_words))

for tweet in negative_tweet_tokens:
    negative_cleaned_tweets_list.append(clear_tweet(tweet, stop_words))

def get_all_words_in_tweets(cleander_tweets_list):
    for tweets in cleander_tweets_list:
        for tweet in tweets:
            yield tweet

all_pos_words = get_all_words_in_tweets(positive_cleaned_tweets_list)
all_neg_words = get_all_words_in_tweets(negative_cleaned_tweets_list)

freq_dist_pos = FreqDist(all_pos_words)
freq_dist_neg = FreqDist(all_neg_words)

def get_tweets_for_model(cleaned_tweets_list):
    for tweet_tokens in cleaned_tweets_list:
        yield dict([token, True] for token in tweet_tokens)

positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tweets_list)
negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tweets_list)

positive_dataset = [(tweet_dict, "Positive")
                     for tweet_dict in positive_tokens_for_model]

negative_dataset = [(tweet_dict, "Negative")
                     for tweet_dict in negative_tokens_for_model]

dataset = positive_dataset + negative_dataset

random.shuffle(dataset)

train_data = dataset[:7000]
test_data = dataset[7000:]

classifier = NaiveBayesClassifier.train(train_data)

custom_tweet = "I ordered just once from TerribleCo, they screwed up, never used the app again."

custom_tokens = clear_tweet(word_tokenize(custom_tweet))

print(classifier.classify(dict([token, True] for token in custom_tokens)))