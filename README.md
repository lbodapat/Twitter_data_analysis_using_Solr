# Twitter Data Scraper Project



## Requirements

Use the package manager [pip3](https://pip.pypa.io/en/stable/) to install the requirements.

```bash
pip3 install pandas numpy tweepy pysolr tweet-preprocessor demoji -q
```

## Files and Tasks

**Files** | **Description** | 
--- | --- | --- |
`twitter.py` | Interacts with Twitter API 
`indexer.py` | Interacts with Solr 
`tweet_preprocesssor.py` | For processing Tweets 
`scraper.py` | Main orchestration code 

## Authentication

Please add the following details in `twitter.py` as shown below:

```python
class Twitter:
    def __init__(self):
        self.auth = tweepy.OAuthHandler("<consumer_api_key>", "<consumer_api_token>")
        self.auth.set_access_token("<access_token>", "<access_token_secret>")
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
````

## Core Creation

Please run `indexer.py` using the command `python3 indexer.py` only once. It will create the Solr core for you.  **[Caution]** RUNNING this command more than once will be delete your core and create a new core.
## Configuration

`config.json` is not automatically created, create config.json under `project1` directory.

An example configuration file.

```json
{
  "pois": [
    {
      "id": 1,
      "screen_name": "JoeBiden",
      "country": "USA",
      "count": 500,
      "finished": 0,
      "reply_finished": 0
    }
  ],
  "keywords": [
    {
      "id": 1,
      "name": "covid vaccine",
      "count": 100,
      "lang": "en",
      "country": "USA",
      "finished": 0
    }
  ]
}
```

#### Fields

- `pois[0].id`: Very IMPORTANT attribute, data files are created using this.
- `pois[0].screen_name` : Screen name of the POI, get it from `twitter.com` .
- `pois[0].country` : Country of the POI.
- `pois[0].count` : The number of tweets that you want to collect for a POI.
- `pois[0].finished`: The status of tweet collection, after data collection and indexing is completed it will be changed to `1` and saved in `config.json`.
- `pois[0].reply_finished`: Status of reply collection, you have to implement the logic.
- `keywords[0].name`: Keyword name.
- `keywords[0].count`: Self explanatory.
- `keywords[0].language`: Language of the tweets you want to collect for a particular keyword.
- `keywords[0].country`:Self explanatory.
- `keywords[0].finished`:Self explanatory.

## Data Files

Under `project1/data/` all the POIs, Keywords tweets will be stored in pickle format, use these files to collect replies.

## Running the Scraper

`python3 scraper.py`
