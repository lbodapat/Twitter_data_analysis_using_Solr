import tweepy
import time

class Twitter:
    def __init__(self):
#     Add them....
        self.auth = tweepy.OAuthHandler("", "")
        self.auth.set_access_token("", "")
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def _meet_basic_tweet_requirements(self):
        '''
        Add basic tweet requirements logic, like language, country, covid type etc.
        :return: boolean
        '''
        raise NotImplementedError

    def get_tweets_by_poi_screen_name(self,screen_name,input_count):
        '''
        Use user_timeline api to fetch POI related tweets, some postprocessing may be required.
        :return: List
        '''
        tweets_array=[]
        re_tweets_array=[]
        poi_covid_tweets_array=[]
        try:
            print("Getting POI Tweets")
            retweeted_count=0
            covid_related_tweets_count=0
            for tweet in self.limit_handled(tweepy.Cursor(self.api.user_timeline,id=screen_name,tweet_mode="extended").items(input_count)):
                try:
                    if('RT @' in tweet.full_text and retweeted_count< round(input_count*0.1)):
                        re_tweets_array.append(tweet)
                        retweeted_count=retweeted_count+1
                    elif(not tweet.retweeted and 'RT @' not in tweet.full_text):
                        if(covid_related_tweets_count<51 and self.is_keywords_present_in_tweet_text(tweet.full_text)) :
                            poi_covid_tweets_array.append(tweet)
                            covid_related_tweets_count=covid_related_tweets_count+1
                        else:
                            tweets_array.append(tweet)
                except tweepy.TweepError as exp:
                    print(exp.reason)
                except StopIteration:
                    print("Breaking Interation")
                    break
        except:
            print("Passing...")
            pass
        return tweets_array,re_tweets_array,poi_covid_tweets_array

    def get_tweets_by_lang_and_keyword(self,keyword,input_count,input_language):
        '''
        Use search api to fetch keywords and language related tweets, use tweepy Cursor.
        :return: List
        '''
        tweets_array=[]
        re_tweets_array=[]
        try:
            retweeted_count=0
            for tweet in self.limit_handled(tweepy.Cursor(self.api.search,q=keyword,lang=input_language,tweet_mode="extended").items(input_count)):
                try:
                    if('RT @' in tweet.full_text and retweeted_count< round(input_count*0.07)):
                        re_tweets_array.append(tweet)
                        retweeted_count=retweeted_count+1
                    elif(not tweet.retweeted and 'RT @' not in tweet.full_text):
                        tweets_array.append(tweet)
                except tweepy.TweepError as exp:
                    print(exp.reason)
                except StopIteration:
                    break
        except:
            pass
        print("For the Keywork and Language",keyword," : ",input_language," the number of total tweets: ",len(tweets_array),
        " and Retweets: ",len(re_tweets_array))
        return tweets_array,re_tweets_array

    def get_replies(self,reply_tweet_id):
        '''
        Get replies for a particular tweet_id, use max_id and since_id.
        For more info: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/guides/working-with-timelines
        :return: List
        '''
        reply_tweet_text=[]
        if(reply_tweet_id != None):
            tweets = self.api.search(q=reply_tweet_id)
            for tweet in tweets:
                reply_tweet_text.append(tweet)

        print(reply_tweet_text)
        return reply_tweet_text

    def get_replies2(self,ip_tweet,tweet_id,poi_reply_flag):
            items_count=200
            total_replies_count=0
            required_replies_count=2
            if(poi_reply_flag==1):
                items_count=1000
                required_replies_count=12
            name=ip_tweet.author.screen_name
            replies=[]
            for tweet in tweepy.Cursor(self.api.search,q='to:'+name, result_type='recent',tweet_mode="extended").items(items_count):
                if hasattr(tweet, 'in_reply_to_status_id_str') and total_replies_count<required_replies_count:
                    if (tweet.in_reply_to_status_id_str==tweet_id):
                        replies.append(tweet.full_text)
                        total_replies_count=total_replies_count+1
            print("# Replies Collected for name: ",name," are: ",len(replies))
            return replies

    def check_rate_limit_error(self,tweets):
        print("Checking Rate Limit Error: ")
        try:
            while True:
                yield tweets.next()
        except:
            print("Rate limit reached, sleeping for 15*60 secs")
            time.sleep(15*60)

    def limit_handled(self,cursor):
        while True:
            try:
                yield next(cursor)
            except tweepy.RateLimitError:
                print("RL reached, sleeping for 15*60 secs")
                time.sleep(15*60)

    def is_keywords_present_in_tweet_text(self,tweet_text):
        covid_keyword_list=self.get_covid_keyword_list()
        if any(srchstr in tweet_text for srchstr in covid_keyword_list):
            return True
        else:
            return False

    def get_poi_list(self):
        poi_list=['narendramodi',
                   'PMOIndia',
                   'ShashiTharoor',
                   'mansukhmandviya',
                   'AyushmanNHA',
                   'RahulGandhi',
                   'EPN',
                   'FelipeCalderon',
                   'lopezobrador_',
                   'JoseNarroR',
                   'Claudiashein',
                   'JoeBiden',
                   'POTUS',
                   'CDCgov',
                   'BarackObama',
                   'SecBecerra']
        return poi_list

    def get_covid_keyword_list(self):
        keywords_list=['quarentena',
                        'hospital',
                        'covidresources',
                        'rt-pcr',
                        '??????????????????????????????????????????',
                        'oxygen',
                        '???????????????????????? ????????????',
                        'stayhomestaysafe',
                        'covid19',
                        'quarantine',
                        '???????????????',
                        'face mask',
                        'covidsecondwaveinindia',
                        'flattenthecurve',
                        'corona virus',
                        'wuhan',
                        'cierredeemergencia',
                        'autoaislamiento',
                        'sintomas',
                        'covid positive',
                        'casos',
                        '??????????????? ??????????????????',
                        '??????????????? ???????????? ???????????????',
                        'stay safe',
                        '#deltavariant',
                        'covid symptoms',
                        'sarscov2',
                        'covidiots',
                        'brote',
                        'alcohol en gel',
                        'disease',
                        'asintom??tico',
                        '?????????????????????',
                        'encierro',
                        'covidiot',
                        'covidappropriatebehaviour',
                        'fever',
                        'pandemia de covid-19',
                        'wearamask',
                        'flatten the curve',
                        'ox??geno',
                        'desinfectante',
                        'super-spreader',
                        'ventilador',
                        'coronawarriors',
                        'quedate en casa',
                        'mascaras',
                        'mascara facial',
                        'trabajar desde casa',
                        '??????????????????',
                        'immunity',
                        '??????????????? ??????????????????',
                        '?????????????????? ?????????????????????',
                        'mask mandate',
                        'health',
                        'dogajkidoori',
                        'travelban',
                        'cilindro de ox??geno',
                        'covid',
                        'staysafe',
                        'variant',
                        'yomequedoencasa',
                        'doctor',
                        '????????????????????????',
                        '??????????????? ?????????',
                        'distancia social',
                        '??????????????????',
                        'covid test',
                        '?????????????????????',
                        'covid deaths',
                        '???????????????19',
                        'muvariant',
                        'susanadistancia',
                        'personal protective equipment',
                        'remdisivir',
                        'quedateencasa',
                        'asymptomatic',
                        'social distancing',
                        'distanciamiento social',
                        'cdc',
                        'transmission',
                        'epidemic',
                        'social distance',
                        'herd immunity',
                        'transmisi??n',
                        '??????????????????????????????',
                        'indiafightscorona',
                        'surgical mask',
                        'facemask',
                        'desinfectar',
                        '???????????????',
                        '?????????????????????',
                        'symptoms',
                        '????????????????????? ????????????',
                        'covid cases',
                        'ppe',
                        'sars',
                        'autocuarentena',
                        '???????????????????????????',
                        'breakthechain',
                        'stayhomesavelives',
                        'coronavirusupdates',
                        'sanitize',
                        'covidinquirynow',
                        '??????????????????',
                        'workfromhome',
                        'outbreak',
                        'flu',
                        'sanitizer',
                        'distanciamientosocial',
                        'variante',
                        '??????????????? 19',
                        '???????????????-19',
                        'covid pneumonia',
                        '???????????????',
                        'pandemic',
                        'icu',
                        '???????????????',
                        'contagios',
                        '???????????????????????????',
                        'washyourhands',
                        'n95',
                        'stayhome',
                        'lavadodemanos',
                        'fauci',
                        '????????? ??????????????????????????? ???????????????',
                        'maskmandate',
                        '??????????????????',
                        '??????????????? ?????????????????????',
                        'third wave',
                        'epidemia',
                        'fiebre',
                        '?????????',
                        'travel ban',
                        '???????????????',
                        'muerte',
                        '??????????????????',
                        'washhands',
                        'enfermedad',
                        'contagio',
                        'infecci??n',
                        'faceshield',
                        'self-quarantine',
                        'remdesivir',
                        'oxygen cylinder',
                        'mypandemicsurvivalplan',
                        '??????????????? ?????? ?????????',
                        'delta variant',
                        'wuhan virus',
                        '???????????????',
                        'corona',
                        'maskup',
                        'gocoronago',
                        'death',
                        'curfew',
                        'socialdistance',
                        'second wave',
                        'm??scara',
                        'stayathome',
                        'positive',
                        'lockdown',
                        'propagaci??n en la comunidad',
                        '??????????????? ?????????',
                        'aislamiento',
                        'rtpcr',
                        'coronavirus',
                        'variante delta',
                        'distanciasocial',
                        'cubrebocas',
                        '?????? ?????? ????????????',
                        'socialdistancing',
                        'covidwarriors',
                        '??????????????????',
                        'covid-19',
                        'stay home',
                        '????????????????????????',
                        'jantacurfew',
                        'cowin',
                        '?????????????????????????????????',
                        'virus',
                        'distanciamiento',
                        'cuarentena',
                        'indiafightscovid19',
                        'healthcare',
                        'natocorona',
                        '??????????????? ???????????????',
                        'delta',
                        '?????????????????????',
                        'wearmask',
                        '?????????????????????????????????',
                        'ventilator',
                        'pneumonia',
                        'maskupindia',
                        'ppe kit',
                        'sars-cov-2',
                        'testing',
                        'fightagainstcovid19',
                        '?????????????????????',
                        '???????????????????????? ?????????????????????',
                        'who',
                        'mask',
                        'pandemia',
                        'deltavariant',
                        '????????????????????? ?????????????????????',
                        '?????????',
                        's??ntomas',
                        'work from home',
                        'antibodies',
                        'masks',
                        'confinamiento',
                        'flattening the curve',
                        '?????????????????? ??????????????????',
                        'thirdwave',
                        'mascarilla',
                        'usacubrebocas',
                        'covidemergency',
                        'inmunidad',
                        'cierre de emergencia',
                        'self-isolation',
                        '??????????????????????????? ????????????',
                        '???????????? ?????????????????????????????????',
                        'isolation',
                        'cases',
                        'community spread',
                        'unite2fightcorona',
                        'oxygencrisis',
                        'containment zones',
                        'homequarantine',
                        '????????????????????????????????????',
                        '?????????????????????',
                        'hospitalizaci??n',
                        'incubation period']
        return keywords_list