from datetime import datetime

import pymongo as pymongo
from bson import ObjectId

from Database.TwitterDB import TwitterDB
import os

from Entity.Search import Search
from Entity.User import User


class MongoTwitterDB(TwitterDB):
    TWEET_DATETIME_FORMAT = '%a %b %d %X %z %Y'

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

    def get_user_metrics(self, threshold=2, favorite_weight=1, retweet_weight=5, split_date=None):
        include_only_split_date = [] if split_date is None else\
            [
                {"$addFields": {
                    "date": {
                        "$dateFromString": {"dateString": "$created_at"}
                    }
                }},
                {"$match": {
                    "date": {
                        "$gte": split_date[0],
                        "$lte": split_date[1]
                    }
                }}
            ]
        threshold = threshold if split_date is None else threshold

        best_twitterers = list(self.db.twitts.aggregate(
            [
                *include_only_split_date,
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
            ],
            allowDiskUse=True
        ))

        if split_date is None:
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
                {"$match": {"_id.userid": {"$ne": "_id.retweeting_userid"}}},
                {"$match": {"retweet_count": {"$gte": threshold}}},
                {"$lookup":
                    {
                        "from": "users",
                        "localField": "_id.retweeting_userid",
                        "foreignField": "id",
                        "as": "aliasForRetweetingUsersCollection"
                    }
                },
                {"$match": {"aliasForRetweetingUsersCollection._id": {"$exists": True}}},
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
                {"$match": {"aliasForUsersCollection._id": {"$exists": True}}},

            ],
            allowDiskUse=True
        ))

    def save_user(self, user):
        if self.exist_user(user.id):
            self.update_user(user)
        else:
            self.add_user(user)

    def add_user(self, user):
        self.db.users.insert_one(user.__dict__)

    def exist_user(self, user_id):
        return False if self.db.users.find_one({'id': user_id}) is None else True

    def find_user(self, user_id):
        return User(**self.db.users.find_one({'id': user_id}))

    def update_user(self, user):
        self.db.users.update_one(
            {'id': user.id},
            {
                '$set': user.__dict__,
            },
            upsert=True
        )

    def find_all_users(self):
        fetched_users = self.db.users.find(
            {"metrics_order": {"$exists": True}},
        )
        return [User(**fetched_user) for fetched_user in fetched_users]

    def find_all_users_with_metrics(self, minimum_tweet_count_metric=0):
        fetched_users = self.db.users.find(
            {"metrics.tweet_count": {"$gte": minimum_tweet_count_metric}},
        )
        return [User(**fetched_user) for fetched_user in fetched_users]

    def find_first_tweet_date(self):
        tweet = self.db.twitts.find().sort('id', 1).limit(1)
        return datetime.strptime(tweet[0]['created_at'], self.TWEET_DATETIME_FORMAT)

    def find_last_tweet_date(self):
        tweet = self.db.twitts.find().sort('id', -1).limit(1)
        return datetime.strptime(tweet[0]['created_at'], self.TWEET_DATETIME_FORMAT)
    #
    # def get_user_metrics_splitted(self, split_dates, threshold=2, favorite_weight=1, retweet_weight=5):
    #     user_metrics = {}
    #     for split_date in split_dates:
    #         for user_period_metric in self.get_user_metrics(threshold, favorite_weight, retweet_weight, split_date.split_date):
    #             userid = user_period_metric['_id']['userid']
    #             if userid not in user_metrics:
    #                 user_metrics[userid] = {}
    #             user_metrics[userid][split_date.name_date_splits] = user_period_metric
    #
    #     return user_period_metrics
