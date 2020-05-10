from datetime import datetime

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
        search.until = datetime.combine(search.until, datetime.min.time())
        self.db.searches.insert_one(search.__dict__)

    def update_search(self, search):
        if search._id is None:
            raise Exception(f'Search object can not be update, if does not have _id')
        self.db.searches.update_one(
            {'_id': search._id},
            {
                '$set': {
                    'until': datetime.combine(search.until, datetime.min.time()),
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

    def get_tweets_by_user_screen_name(self, username):
        fetched_tweets = self.db.twitts.aggregate(
            [
                {"$match":
                    {"$and": [
                        {"user.screen_name": username},
                        {"retweeted_status": {"$exists": False}}
                    ]}
                },
                {"$sort": {"created_at": 1}}
            ]
        )
        return list(fetched_tweets)

    def get_user_retweets_mapped_by_userid(self):
        user_retweets = list(self.db.twitts.aggregate(
            [
                {"$group":
                    {
                        "_id": {
                            "userid": "$retweeted_status.user.id",
                            "retweeted_userid": "$user.id"
                        },
                        "retweet_count": {"$sum": 1}
                    }
                },
                {"$group":
                    {
                        "_id": {
                            "userid": "$_id.userid",
                        },
                        "unique_retweet_count": {"$sum": 1},
                        "retweet_count": {"$sum": "$retweet_count"},
                    }
                },

            ],
            allowDiskUse=True
        ))
        return dict([(user_retweet["_id"]['userid'], {"retweet_count": user_retweet["retweet_count"], "unique_retweet_count": user_retweet["unique_retweet_count"]})
                     for user_retweet in user_retweets])

    def get_user_metrics(self, threshold=2, favorite_weight=1, retweet_weight=5):
        best_twitterers = list(self.db.twitts.aggregate(
            [
                {"$match": {"retweeted_status": {"$exists": False}}},
                {"$group":
                    {
                        "_id": {"userid": "$user.id"},
                        "name": {"$max": "$user.name"},
                        "username": {"$max": "$user.screen_name"},
                        "max_followers_count": {"$max": "$user.followers_count"},
                        "max_following_count": {"$max": "$user.friends_count"},
                        "avg_favorite": {"$avg": "$favorite_count"},
                        "avg_retweet": {"$avg": "$retweet_count"},
                        "sum_favorite": {"$sum": "$favorite_count"},
                        "sum_retweet": {"$sum": "$retweet_count"},
                        "tweet_count": {"$sum": 1},
                        "favorite_values": {"$push": "$favorite_count"},
                        "retweet_values": {"$push": "$retweet_count"}
                    }
                },
                {"$addFields": {"weighed_sum": {"$add": [{"$multiply": ["$sum_retweet", retweet_weight]},
                                                         {"$multiply": ["$sum_favorite", favorite_weight]}]}}},
                {"$addFields": {"weighed_sum_with_cost": {"$divide": ["$weighed_sum", "$tweet_count"]}}},
                {"$addFields": {"avg_favorite_to_followers_count": {
                    "$cond": [{ "$eq": ["$max_followers_count", 0] }, 0, {"$divide": ["$avg_favorite", "$max_followers_count"]}]
                }}},
                {"$addFields": {"avg_retweet_to_followers_count": {
                    "$cond": [{"$eq": ["$max_followers_count", 0]}, 0,
                              {"$divide": ["$avg_retweet", "$max_followers_count"]}]
                }}},
                #{"$addFields": {"sum_vs_divided": {"$divide": ["$weighed_sum", "$tweet_count"]}}},
                {"$match": {"tweet_count": {"$gte": threshold}}},
                {"$sort": {"max_followers_count": -1}},
                {"$lookup":
                    {
                        "from": "users",
                        "localField": "_id.userid",
                        "foreignField": "id",
                        "as": "aliasForUsersCollection"
                    }
                },
                {"$match": {"aliasForUsersCollection.category": {"$ne": "x"}}},
                {"$match": {"aliasForUsersCollection.category": {"$ne": "x"}}}
            ]))

        user_retweet_mapped_by_userid = self.get_user_retweets_mapped_by_userid()
        best_twitterers = list(map(
            lambda user: dict(
                **user,
                **(user_retweet_mapped_by_userid[user["_id"]['userid']] if
                   user["_id"]['userid'] in user_retweet_mapped_by_userid else
                   {'retweet_count': 0, 'unique_retweet_count': 0})
            ),
            best_twitterers
        ))
        return best_twitterers

    def get_user_median(self, uid):
        best_twitterers = list(self.db.twitts.aggregate(
            [
                {"$match": {"retweeted_status": {"$exists": False}}},
                {"$group":
                             {
                                 "_id": {"userid": "$user.id"},
                                 "count": {"$sum": 1},
                                 "values": {"$push": "$favorite_count"}
                             }
                         }
            ]))
        return list(best_twitterers)

    def search_exist_by_query(self, query):
        return False if self.db.searches.find_one({'query': query}) is None else True

    def get_retweets_graph_edges(self, threshold=10):
        return list(self.db.twitts.aggregate(
            [
                {"$group":
                    {
                        "_id": {
                            "userid": "$retweeted_status.user.id",
                            "retweeting_userid": "$user.id"
                        },
                        "name": {"$max": "$retweeted_status.user.name"},
                        "username": {"$max": "$retweeted_status.user.screen_name"},
                        "retweeting_name": {"$max": "$user.name"},
                        "retweeting_username": {"$max": "$user.screen_name"},
                        "retweet_count": {"$sum": 1}
                    }
                },
                {"$match": {"_id.userid": {"$ne": "$data.retweeting_userid"}}},
                {"$match": {"retweet_count": {"$gte": threshold}}},
                {"$group": {
                    "_id": {
                        "userid": "$_id.userid",
                    },
                    "data": {"$push":
                         {
                             "retweeting_userid": "$_id.retweeting_userid",
                             "retweet_count": "$retweet_count",
                             "retweeting_name": {"$max": "$retweeting_name"},
                             "retweeting_username": {"$max": "$retweeting_username"},
                         }},
                    "name": {"$max": "$name"},
                    "username": {"$max": "$username"},
                }},
                {"$sort": {"retweet_count": -1}},
                {"$lookup":
                    {
                        "from": "users",
                        "localField": "_id.userid",
                        "foreignField": "id",
                        "as": "aliasForUsersCollection"
                    }
                },

            ],
            allowDiskUse=True
        ))
