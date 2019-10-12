
import csv

from textblob import TextBlob
import tweepy
import sys, os, csv
from tweepy import OAuthHandler
import twitter_credentials
import numpy as np
import pandas as pd





def authenticate_twitter_api():
    auth=OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
    auth.secure = True
    auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
    tweepyApi = tweepy.API(auth, parser=tweepy.parsers.JSONParser() \
                           , wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    return tweepyApi
# with open('list.txt', 'r') as targets_file:
with open('twitter_user_names.txt', 'r') as targets_file:
     targets_list = targets_file.readlines()

usernames = []

for item in targets_list:
     usernames.append(item.strip('\n'))
# print(usernames)



def socialReputation(feature_dict):

    rep = np.log ( (1+feature_dict['followers_count']) * \
                  (1+feature_dict['followers_count']) ) + \
                np.log(1 + feature_dict['statuses_count'] ) \
                - np.log(1 + feature_dict['friends_count'])
    total_soc_score=rep
    return total_soc_score


def context_reputation(feature_dict):
    mean_value = (np.mean([feature_dict["retweet_ratio"], \
                           feature_dict["liked_ratio"], \
                           feature_dict["hashtag_ratio"],
                           feature_dict["urls_ratio"]]) *\
                  feature_dict["orig_content_ratio"])
    # print('mean value',mean_value)
    return mean_value


def hIndex(scores):
    if len(scores) == 0:
        return 0
    sortedScores = sorted(scores, reverse = True)
    i = 0
    for i, x in enumerate(sortedScores):
        if x < i+1:
            return i
    return len(scores)-1




def content_reputation(mentions):

    tweet_list_text = []
    for twet in mentions[0]:
        # print(twet)
        tweet_list_text.append(twet['text'])
    # print(tweet_list_text)
    neutral = 0
    positive = 0
    negative = 0
    polarity = 0
    for tweet in tweet_list_text:
        analyze=TextBlob(tweet)
        polarity+=analyze.sentiment.polarity
        # print("Analysis",polarity)
        if analyze.sentiment.polarity==0.00:
            neutral+=1
        if analyze.sentiment.polarity<0.00:
            negative+=1
        if analyze.sentiment.polarity>0.00:
            positive+=1
    neutral=neutral/len(tweet_list_text)
    positive = positive / len(tweet_list_text)
    negative = negative / len(tweet_list_text)
    total_score=(((positive+neutral)-negative))
    return total_score


def compute_features(tweets, mentions):

    feature_dict = {}
    user_data = mentions[0][0]['user']
    feature_dict["id_str"] = user_data["id_str"]
    feature_dict["screen_name"] = user_data["screen_name"]
    feature_dict["followers_count"] = user_data["followers_count"]
    feature_dict["friends_count"] = user_data["friends_count"]
    feature_dict["listed_count"] = user_data["listed_count"]
    feature_dict["statuses_count"] = user_data["statuses_count"]
    feature_dict["has_url"] = 0 if not user_data["url"] else 1


    # print('mentions',mentions)
    retweetedOthersTweets = 0
    retweetCountList = []  # used to compute retweet_index
    # liked by others
    likedByOtherCountList = []

    totalReplies = 0
    tweets_with_mentions = 0
    tweets_with_hashtags = 0
    tweets_with_symbols = 0
    tweets_with_urls = 0

    total_tweets = len(mentions[0])
    #
    for tweet in mentions[1]:
        if 'retweeted_status' in tweet:
            retweetedOthersTweets += 1
        elif int(tweet['retweet_count']) > 0:
            retweetCountList.append(int(tweet['retweet_count']))

        if len(tweet["entities"]["user_mentions"]):
            tweets_with_mentions += 1
        if len(tweet["entities"]["hashtags"]):
            tweets_with_hashtags += 1
    for tweet in mentions[0]:


        if int(tweet['favorite_count']) > 0:
            likedByOtherCountList.append(int(tweet['favorite_count']))

        if tweet["in_reply_to_status_id"] or tweet["in_reply_to_user_id"] or tweet["in_reply_to_screen_name"]:
            totalReplies += 1
        if len(tweet["entities"]["symbols"]):
            tweets_with_symbols += 1
        if len(tweet["entities"]["urls"]):
            tweets_with_urls += 1

    feature_dict["mention_by_others"] = len(mentions[1])
    feature_dict["retweet_ratio"] = float(len(retweetCountList)) / total_tweets
    feature_dict["liked_ratio"] = float(len(likedByOtherCountList)) / total_tweets
    feature_dict["orig_content_ratio"] = (total_tweets - float(retweetedOthersTweets)) / total_tweets
    feature_dict["hashtag_ratio"] = float(tweets_with_hashtags) / total_tweets
    feature_dict["urls_ratio"] = float(tweets_with_urls) / total_tweets
    feature_dict["symbols_ratio"] = float(tweets_with_symbols) / total_tweets
    feature_dict["mentions_ratio"] = float(tweets_with_mentions) / total_tweets

    feature_dict["Social_reputation"] =  socialReputation(feature_dict)
    feature_dict["retweet_hindex"] = hIndex(retweetCountList)
    feature_dict["like_hindex"] = hIndex(likedByOtherCountList)
    feature_dict["Content_Score"]=content_reputation(mentions)
    feature_dict["Context_score"]=context_reputation(feature_dict)
    feature_dict["Reputation_score"]=np.mean([feature_dict["Content_Score"],feature_dict["Context_score"],feature_dict["Social_reputation"],feature_dict["retweet_hindex"],feature_dict["like_hindex"]])
    print(feature_dict)
    return feature_dict




def get_all_tweets(screen_name):

    api = authenticate_twitter_api()

    #initialize a list to hold all the tweepy Tweets
    alltweets = []

    #make initial request for most recent tweets (200 is the maximum   allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name,count=200)

    #save most recent tweets
    alltweets.extend(new_tweets)

    #save the id of the oldest tweet less one
    oldest = alltweets[-1]["id"] - 1


    while len(new_tweets) > 0:  

        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

        #save most recent tweets
        alltweets.extend(new_tweets)
        # print(alltweets[-1]['id'])
        #update the id of the oldest tweet less one
        oldest = alltweets[-1]["id"] - 1


    user_data = alltweets[0]["user"]
    # print('UD',user_data)
    screen_name = user_data['screen_name']
    # print('SN',screen_name)
    # print("screen name",screen_name)
    search = api.search(screen_name, count=200)
    # print("search",search)
    mentions = search["statuses"]
    # print('mentions',mentions)
    # print('all tweets',alltweets)
    return alltweets, mentions

    # pass
from datetime import datetime

start_time = datetime.now()
print("start",start_time)
# "the code you want to test stays here"
if __name__ == '__main__':

    #pass in the username of the account you want to download
    all_fet = []
    for x in usernames:
        print(x)
        user_info=get_all_tweets(x)
        all_fet.append(compute_features(x,user_info))
    #
    columns= ['id_str', 'screen_name', 'statuses_count', 'followers_count', 'listed_count', 'friends_count', 'has_url', \
                  'mention_by_others', 'retweet_ratio', 'liked_ratio', 'orig_content_ratio', 'hashtag_ratio',
                  'urls_ratio', 'symbols_ratio', 'mentions_ratio', 'Social_reputation', 'retweet_hindex', 'like_hindex', "Content_Score", "Context_score", "Reputation_score"]

    df = pd.DataFrame(all_fet,columns=columns)

    export_csv = df.to_csv('Dataset Path', index=False)

time_elapsed = datetime.now() - start_time

print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
