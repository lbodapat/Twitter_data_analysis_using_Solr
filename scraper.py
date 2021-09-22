import json
import datetime
import pandas as pd
from twitter import Twitter
from tweet_preprocessor import TWPreprocessor
from indexer import Indexer

reply_collection_knob = False


def read_config():
    with open("config.json") as json_file:
        data = json.load(json_file)
    return data


def write_config(data):
    with open("config.json", 'w') as json_file:
        json.dump(data, json_file)


def save_file(data, filename):
    df = pd.DataFrame(data)
    df.to_pickle("data/" + filename)


def read_file(type, id):
    return pd.read_pickle(f"data/{type}_{id}.pkl")


def main():
    config = read_config()
    indexer = Indexer()
    twitter = Twitter()

    pois = config["pois"]
    keywords = config["keywords"]

    total_covid=0
    total_rt=0
    total_tweets_poi=0
    total_tweets_non_poi_vac=0

    print(pois)
    for i in range(len(pois)):
        if pois[i]["finished"] == 0:
            poi_name_flag=1
            print(f"---------- collecting tweets for poi: {pois[i]['screen_name']}")
            raw_tweets = twitter.get_tweets_by_poi_screen_name(pois[i]['screen_name'],pois[i]['count'])  # pass args as needed
            print("For the POI ",pois[i]['screen_name'],"the number of total tweets: ",len(raw_tweets[0])," covid related tweets: ",
                    len(raw_tweets[2])," and Retweets: ",len(raw_tweets[1]))
            processed_tweets = []
            for tw in raw_tweets[0]:
                processed_tweets.append(TWPreprocessor.preprocess(tw,pois[i]['country'],twitter,poi_name_flag))
            for tw in raw_tweets[1]:
                processed_tweets.append(TWPreprocessor.preprocess(tw,pois[i]['country'],twitter,poi_name_flag))
            for tw in raw_tweets[2]:
                processed_tweets.append(TWPreprocessor.preprocess(tw,pois[i]['country'],twitter,poi_name_flag))
#             indexer.create_documents(processed_tweets)

            pois[i]["finished"] = 1
            pois[i]["collected"] = len(processed_tweets)
            write_config({
                "pois": pois, "keywords": keywords
            })

            total_covid=total_covid+len(raw_tweets[2])
            total_rt=total_rt+len(raw_tweets[1])
            total_tweets_poi=total_tweets_poi+len(raw_tweets[0])

            save_file(processed_tweets, f"poi_{pois[i]['id']}.pkl")
            print("------------ process complete -----------------------------------")

    for i in range(len(keywords)):
        if keywords[i]["finished"] == 0:
            poi_name_flag=0
            print(f"---------- collecting tweets for keyword: {keywords[i]['name']}")
            raw_tweets = twitter.get_tweets_by_lang_and_keyword(keywords[i]['name'],keywords[i]['count'],keywords[i]['lang'])  # pass args as needed
            print("For the Keyword ",keywords[i]['name'],"the number of total tweets: ",len(raw_tweets[0])," and Retweets: ",len(raw_tweets[1]))
            processed_tweets = []
            for tw in raw_tweets[0]:
                processed_tweets.append(TWPreprocessor.preprocess(tw,keywords[i]['country'],twitter,poi_name_flag))
            for tw in raw_tweets[1]:
                processed_tweets.append(TWPreprocessor.preprocess(tw,keywords[i]['country'],twitter,poi_name_flag))
            print("In scrapper, Processed tweets count: ",len(processed_tweets))

#             indexer.create_documents(processed_tweets)

            keywords[i]["finished"] = 1
            keywords[i]["collected"] = len(processed_tweets)
            write_config({
                "pois": pois, "keywords": keywords
            })

            total_rt=total_rt+len(raw_tweets[1])
            total_tweets_non_poi_vac=total_tweets_non_poi_vac+len(raw_tweets[0])

            save_file(processed_tweets, f"keywords_{keywords[i]['id']}.pkl")
            print("------------ process complete -----------------------------------")
            print("------------ Total tweets collected of POI -----------------------------------",total_tweets_poi)
            print("------------ Total tweets collected of NON POI Vaccine related -----------------------------------",total_tweets_non_poi_vac)
            print("------------ Total @RT retweets collected -----------------------------------",total_rt)
            print("------------ Total Covid general POI tweets collected -----------------------------------",total_covid)

    if reply_collection_knob:
        # Write a driver logic for reply collection, use the tweets from the data files for which the replies are to collected.
        raise NotImplementedError

if __name__ == "__main__":
    main()
