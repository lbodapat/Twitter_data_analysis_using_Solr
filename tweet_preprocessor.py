import demoji, re, datetime
import preprocessor
import pandas as pd
import numpy as np
import itertools as it
import regex as re
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import string
import json

class TWPreprocessor:
    @classmethod
    def preprocess(cls, tweet,country,twitter_class_object,poi_name_flag):
        '''
        Do tweet pre-processing before indexing, make sure all the field data types are in the format as asked in the project doc.
        :param tweet:
        :return: dict
        '''
        print("Preprocessing: ",tweet.id_str)
        return createDictionary(tweet,country,twitter_class_object,poi_name_flag)

def createDictionary(tweet,country,twitter_class_object,poi_name_flag):
   #Chaging text_ln key based on language
    lang_specific_text=''
    if(tweet.lang=='en'):
        lang_specific_text='text_en'
    elif(tweet.lang=='es'):
        lang_specific_text='text_es'
    elif(tweet.lang=='hi'):
        lang_specific_text='text_hi'

    #Getting hashtags, mentions and tweet_urls
    hashtags=_get_entities(tweet,'hashtags')
    mentions=_get_entities(tweet,'mentions')
    tweet_urls=_get_entities(tweet,'urls')

    #Cleaning text- for all 3 langs
    text_cleaned_data=_text_cleaner(tweet.full_text,tweet.lang,hashtags,mentions,tweet_urls)

    #Formatting the date
    formatted_date=_get_tweet_date(tweet.created_at)

    #Fetching reply tweets
#     reply_tweet=''
    reply_tweet=fetch_reply_tweet(tweet,twitter_class_object)

    #Setting name and id - for POI and Non-POI
    poi_name=''
    poi_id=''
    if(poi_name_flag==1):
        poi_name=tweet.author.screen_name
        poi_id=tweet.author.id

    #Creating Dictionary
    keys = ['poi_name', 'poi_id', 'verified','country','id','replied_to_tweet_id','replied_to_user_id','reply_text','tweet_text','tweet_lang',lang_specific_text,'hashtags','mentions','tweet_urls','tweet_emoticons','tweet_date','geolocation']
    values=[poi_name,poi_id,tweet.author.verified,country,tweet.id_str,tweet.in_reply_to_status_id,tweet.in_reply_to_user_id,reply_tweet,tweet.full_text,tweet.lang,text_cleaned_data[0],hashtags,mentions,tweet_urls,text_cleaned_data[1],formatted_date,tweet.geo]
    createDictionary=dict(zip(keys, values))
    return createDictionary

def fetch_reply_tweet(tweet,twitter_class_object):
    print("Fetching replies.....")
    fetched_replies=twitter_class_object.get_replies2(tweet,tweet.id_str)
    return fetched_replies

def _get_entities(tweet, type=None):
    result = []
    if type == 'hashtags':
        hashtags = tweet.entities['hashtags']
        for hashtag in hashtags:
            result.append(hashtag['text'])
    elif type == 'mentions':
        mentions = tweet.entities['user_mentions']
        for mention in mentions:
            result.append(mention['screen_name'])
    elif type == 'urls':
        urls = tweet.entities['urls']
        for url in urls:
            result.append(url['url'])
    return result


def _text_cleaner(text,lang,hashtags,mentions,tweet_urls):
    emoticons_happy = list([
        ':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}',
        ':^)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D',
        '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P', ':-P', ':P', 'X-P',
        'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)',
        '<3'
    ])
    emoticons_sad = list([
        ':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<',
        ':-[', ':-<', '=\\', '=/', '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c',
        ':c', ':{', '>:\\', ';('
    ])
    all_emoticons = emoticons_happy + emoticons_sad

    emojis = list(demoji.findall(text).keys())
    clean_text = demoji.replace(text, '')

    for emo in all_emoticons:
        if (emo in clean_text):
            clean_text = clean_text.replace(emo, '')
            emojis.append(emo)
    #Data Cleaning for EN
    if(lang=='en'):
        clean_text = preprocessor.clean(text)
     #Data clean for ES and HI
    if(lang=='hi' or lang=='es'):
        clean_text="".join([i for i in text if i not in string.punctuation])
        clean_text="".join([i for i in text if i not in emojis])
        for ht in hashtags:
            temp=clean_text.replace(ht,'')
            clean_text=temp
        for men in mentions:
             temp=clean_text.replace(men,'')
             clean_text=temp
        for url in tweet_urls:
              temp=clean_text.replace(url,'')
              clean_text=temp
        for p in string.punctuation:
              temp=clean_text.replace(p,'')
              clean_text=temp
    return clean_text, emojis


def _get_tweet_date(tweet_date):
    final_val=_hour_rounder(convert((datetime.datetime.strftime(tweet_date, '%a %b %d %H:%M:%S +0000 %Y'))))
    return final_val.isoformat()

def convert(date_str):
    val=(datetime.datetime.strptime(date_str,'%a %b %d %H:%M:%S +0000 %Y'))
    return val

def _hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
    + datetime.timedelta(hours=t.minute // 30))

