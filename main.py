from TwitterSearch import *
import json
from Database.MongoTwitterDB import MongoTwitterDB
from dotenv import load_dotenv

load_dotenv()

try:
    tso = TwitterSearchOrder()  # create a TwitterSearchOrder object
    tso.set_keywords(['Guttenberg', 'Doktorarbeit'])  # let's define all words we would like to have a look for
    tso.set_language('de')  # we want to see German tweets only
    tso.set_include_entities(False)  # and don't give us all those entity information

    # it's about time to create a TwitterSearch object with our secret tokens
    ts = TwitterSearch(
        consumer_key='aaabbb',
        consumer_secret='cccddd',
        access_token='111222',
        access_token_secret='333444'
    )

    # this is where the fun actually starts :)
    for tweet in ts.search_tweets_iterable(tso):
        print('@%s tweeted: %s' % (tweet['user']['screen_name'], tweet['text']))

except TwitterSearchException as e:  # take care of all those ugly errors if there are some
    print(e)

mongo_db = MongoTwitterDB()
mongo_db.test_connection()
mongo_db.create_database()

with open('example_twitt.json') as file:
    example_twitt = json.load(file)

print(example_twitt)

if not mongo_db.twitt_exists(example_twitt['id']):
    mongo_db.add_twitt(example_twitt)

print(mongo_db.find_twitts_count())
