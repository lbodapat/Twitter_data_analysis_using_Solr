import tweepy
import time

class Twitter:
    def __init__(self):
        self.auth = tweepy.OAuthHandler("UFKPrZYXM1K4d7ePghFdSRS45", "9bQKv3CrRehpY0hUTM3eZ9DnbaRr8xEjBPqQdXQWVSmp6rD6Y3")
        self.auth.set_access_token("1432544818358538241-fLcn8NmPWrtjUNTRZlHPA4bN4rAJ4f", "hRlaOyH3Mw1AY10luh2zlM74X0l6uH2ihGq85o0z4uC2Z")
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
                    if(tweet.retweeted and retweeted_count< round(input_count*0.15)):
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
            for tweet in self.limit_handled(tweepy.Cursor(self.api.search,q=keyword,count=input_count,lang=input_language,tweet_mode="extended")):
                try:
                    if(tweet.retweeted and retweeted_count< round(input_count*0.15)):
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

    def get_replies2(self,ip_tweet,tweet_id):
            total_replies_count=0
            required_replies_count=2
            poi_list=self.get_poi_list()
            name=ip_tweet.author.screen_name
            if any(srchstr in name for srchstr in poi_list):
                required_replies_count=11
            replies=[]
            for tweet in tweepy.Cursor(self.api.search,q='to:'+name, result_type='recent',tweet_mode="extended").items(1000):
                if hasattr(tweet, 'in_reply_to_status_id_str') and total_replies_count<required_replies_count:
                    if (tweet.in_reply_to_status_id_str==tweet_id):
                        replies.append(tweet.full_text)
                        total_replies_count=total_replies_count+1
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
                        'वैश्विकमहामारी',
                        'oxygen',
                        'सुरक्षित रहें',
                        'stayhomestaysafe',
                        'covid19',
                        'quarantine',
                        'मास्क',
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
                        'कोविड मृत्यु',
                        'स्वयं चुना एकांत',
                        'stay safe',
                        '#deltavariant',
                        'covid symptoms',
                        'sarscov2',
                        'covidiots',
                        'brote',
                        'alcohol en gel',
                        'disease',
                        'asintomático',
                        'टीकाकरण',
                        'encierro',
                        'covidiot',
                        'covidappropriatebehaviour',
                        'fever',
                        'pandemia de covid-19',
                        'wearamask',
                        'flatten the curve',
                        'oxígeno',
                        'desinfectante',
                        'super-spreader',
                        'ventilador',
                        'coronawarriors',
                        'quedate en casa',
                        'mascaras',
                        'mascara facial',
                        'trabajar desde casa',
                        'संगरोध',
                        'immunity',
                        'स्वयं संगरोध',
                        'डेल्टा संस्करण',
                        'mask mandate',
                        'health',
                        'dogajkidoori',
                        'travelban',
                        'cilindro de oxígeno',
                        'covid',
                        'staysafe',
                        'variant',
                        'yomequedoencasa',
                        'doctor',
                        'एंटीबॉडी',
                        'दूसरी लहर',
                        'distancia social',
                        'मुखौटा',
                        'covid test',
                        'अस्पताल',
                        'covid deaths',
                        'कोविड19',
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
                        'transmisión',
                        'सैनिटाइज़र',
                        'indiafightscorona',
                        'surgical mask',
                        'facemask',
                        'desinfectar',
                        'वायरस',
                        'संक्रमण',
                        'symptoms',
                        'सामाजिक दूरी',
                        'covid cases',
                        'ppe',
                        'sars',
                        'autocuarentena',
                        'प्रक्षालक',
                        'breakthechain',
                        'stayhomesavelives',
                        'coronavirusupdates',
                        'sanitize',
                        'covidinquirynow',
                        'कोरोना',
                        'workfromhome',
                        'outbreak',
                        'flu',
                        'sanitizer',
                        'distanciamientosocial',
                        'variante',
                        'कोविड 19',
                        'कोविड-19',
                        'covid pneumonia',
                        'कोविड',
                        'pandemic',
                        'icu',
                        'वाइरस',
                        'contagios',
                        'वेंटिलेटर',
                        'washyourhands',
                        'n95',
                        'stayhome',
                        'lavadodemanos',
                        'fauci',
                        'रोग प्रतिरोधक शक्ति',
                        'maskmandate',
                        'डेल्टा',
                        'कोविड महामारी',
                        'third wave',
                        'epidemia',
                        'fiebre',
                        'मौत',
                        'travel ban',
                        'फ़्लू',
                        'muerte',
                        'स्वच्छ',
                        'washhands',
                        'enfermedad',
                        'contagio',
                        'infección',
                        'faceshield',
                        'self-quarantine',
                        'remdesivir',
                        'oxygen cylinder',
                        'mypandemicsurvivalplan',
                        'कोविड के केस',
                        'delta variant',
                        'wuhan virus',
                        'लक्षण',
                        'corona',
                        'maskup',
                        'gocoronago',
                        'death',
                        'curfew',
                        'socialdistance',
                        'second wave',
                        'máscara',
                        'stayathome',
                        'positive',
                        'lockdown',
                        'propagación en la comunidad',
                        'तीसरी लहर',
                        'aislamiento',
                        'rtpcr',
                        'coronavirus',
                        'variante delta',
                        'distanciasocial',
                        'cubrebocas',
                        'घर पर रहें',
                        'socialdistancing',
                        'covidwarriors',
                        'प्रकोप',
                        'covid-19',
                        'stay home',
                        'संक्रमित',
                        'jantacurfew',
                        'cowin',
                        'कोरोनावाइरस',
                        'virus',
                        'distanciamiento',
                        'cuarentena',
                        'indiafightscovid19',
                        'healthcare',
                        'natocorona',
                        'मास्क पहनें',
                        'delta',
                        'ऑक्सीजन',
                        'wearmask',
                        'कोरोनावायरस',
                        'ventilator',
                        'pneumonia',
                        'maskupindia',
                        'ppe kit',
                        'sars-cov-2',
                        'testing',
                        'fightagainstcovid19',
                        'महामारी',
                        'नियंत्रण क्षेत्र',
                        'who',
                        'mask',
                        'pandemia',
                        'deltavariant',
                        'वैश्विक महामारी',
                        'रोग',
                        'síntomas',
                        'work from home',
                        'antibodies',
                        'masks',
                        'confinamiento',
                        'flattening the curve',
                        'मुखौटा जनादेश',
                        'thirdwave',
                        'mascarilla',
                        'usacubrebocas',
                        'covidemergency',
                        'inmunidad',
                        'cierre de emergencia',
                        'self-isolation',
                        'स्वास्थ्य सेवा',
                        'सोशल डिस्टन्सिंग',
                        'isolation',
                        'cases',
                        'community spread',
                        'unite2fightcorona',
                        'oxygencrisis',
                        'containment zones',
                        'homequarantine',
                        'स्पर्शोन्मुख',
                        'लॉकडाउन',
                        'hospitalización',
                        'incubation period']
        return keywords_list