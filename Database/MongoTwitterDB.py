import pymongo as pymongo
from bson import ObjectId

from Database.TwitterDB import TwitterDB
import os

from Entity.Search import Search


class MongoTwitterDB(TwitterDB):
    def __init__(self):
        self.client = pymongo.MongoClient(os.getenv("MONGO_DB_HOST"))
        self.db = self.client.twitter
        self.create_database()

    def test_connection(self):
        try:
            self.client.server_info()
            return True
        except:
            return False

    def create_database(self):
        self.db.twitts.create_index('id', unique=True)
        self.db.searches.create_index('query', unique=True)

    def add_twitt(self, twitt):
        self.db.twitts.insert_one(twitt)

    def find_twitts_count(self):
        return self.db.twitts.count()

    def twitt_exists(self, twitt_id):
        return False if self.db.twitts.find_one({'id': twitt_id}) is None else True

    def add_search(self, search):
        self.db.searches.insert_one(search.__dict__)

    def update_search(self, search):
        if search._id is None:
            raise Exception(f'Search object can not be update, if does not have _id')
        self.db.searches.update_one(
            {'_id': search._id},
            {
                '$set': {
                    'until': search.until,
                    'since_id': search.since_id
                }
            }
        )

    def find_one_search(self, search_id):
        fetched_search = self.db.searches.find_one({'_id': ObjectId(search_id)})
        if fetched_search is None:
            raise Exception(f'Search object with id {search_id} not found!')
        return Search(**fetched_search)

    def find_all_searches(self):
        fetched_searches = self.db.searches.find()
        return [Search(**fetched_search) for fetched_search in fetched_searches]

    def get_all_tweets(self):
        fetched_tweets = self.db.twitts.find()
        return list(fetched_tweets)

    def get_tweets_by_username(self, username):
        fetched_tweets = self.db.twitts.find({ "user.name": username})
        return list(fetched_tweets)

    def get_all_users(self):
        best_twitterers = list(self.db.twitts.aggregate(
            [
                {"$group":
                      {
                          "_id": {"userid": "$user.id"},
                          "username": {"$max": "$user.screen_name"},
                          "max_userfollowers_count": {"$max": "$user.followers_count"},
                          "avg_favorite": {"$avg": "$favorite_count"},
                          "avg_retweet": {"$avg": "$retweet_count"},
                          "tweet_count": {"$sum": 1}
                      }
                },
                 {"$sort": {"max_userfollowers_count": -1}}
            ]))
        return best_twitterers

    def search_exist_by_query(self, query):
        return False if self.db.searches.find_one({'query': query}) is None else True

