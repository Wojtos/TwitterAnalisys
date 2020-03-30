from datetime import date, timedelta, datetime

from TwitterSearch import TwitterSearchException

from Action.Action import Action
from TwitterSearchHelpers.AuthenticatedTwitterSearch import AuthenticatedTwitterSearch
from Database.TwitterDB import TwitterDB
from Entity.Search import Search
from TwitterSearchHelpers.SearchStatistics import SearchStatistics


class SearchAction(Action):
    def __init__(self, search):
        self.db = TwitterDB.instance
        self.search = search if isinstance(search, Search) else self.db.find_one_search(search)
        print(self.search.__dict__)

    def execute(self):
        statistics = self.do()
        self.update_search(statistics)
        return statistics

    def do(self):
        twitter_search = AuthenticatedTwitterSearch()
        twitter_search_order = self.search.create_twitter_search_order()
        statistics = SearchStatistics(self.search.until.date())

        try:
            while True:
                twitter_search_order.set_until(statistics.until)
                for tweet in twitter_search.search_tweets_iterable(twitter_search_order):
                    if not self.db.twitt_exists(tweet['id']):
                        self.db.add_twitt(tweet)
                        statistics.saved_entites_amount += 1
                    statistics.fetched_entites_amount += 1
                    statistics.since_id = tweet['id']
                if statistics.until == date.today():
                    return statistics
                statistics.until = statistics.until + timedelta(days=1)
                print(statistics.until)

        except Exception as e:
            print(e)
            return statistics

    def update_search(self, statistics):
        self.search.since_id = statistics.since_id
        self.search.until = datetime.combine(statistics.until, datetime.min.time())
        self.db.update_search(self.search)
