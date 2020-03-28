import pymongo as pymongo
from Database.TwitterDB import TwitterDB
import os

class MongoTwitterDB(TwitterDB):
    def __init__(self):
        self.client = pymongo.MongoClient(os.getenv("MONGO_DB_HOST"))
        self.db = self.client.twitter

    def test_connection(self):
        try:
            self.client.server_info()
            return True
        except:
            return False

    def create_database(self):
        self.db.twitts.create_index('id', unique=True)

    def add_twitt(self, twitt):
        self.db.twitts.insert_one(twitt)

    def find_twitts_count(self):
        return self.db.twitts.count()

    def twitt_exists(self, twitt_id):
        return False if self.db.twitts.find_one({'id': twitt_id}) is None else True
