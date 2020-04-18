from datetime import date, timedelta, datetime

from TwitterSearch import TwitterSearchException

from Action.Action import Action
from Database.TwitterDB import TwitterDB
from Entity.Search import Search
from TwitterSearchHelpers.SearchStatistics import SearchStatistics
from TwitterSearchIterator.TwitterSearchSwitchableIterator import TwitterSearchSwitchableIterator


class SearchAction(Action):
    def __init__(self, search):
        self.db = TwitterDB.instance
        self.search = search if isinstance(search, Search) else self.db.find_one_search(search)
        print(self.search.__dict__)

    def execute(self):
        statistics = self.do()
        self.update_search()
        return statistics

    def do(self):
        twitter_search_iterator = TwitterSearchSwitchableIterator(self.search)
        statistics = SearchStatistics()

        try:
            for tweet in twitter_search_iterator:
                if not self.db.twitt_exists(tweet['id']):
                    self.db.add_twitt(tweet)
                    statistics.saved_entites_amount += 1
                statistics.fetched_entites_amount += 1
                self.search.since_id = tweet['id']
            if self.search.until < date.today():
                self.search.until = self.search.until + timedelta(days=1)
            print(self.search.until)
            return statistics

        except Exception as e:
            print(e)
            statistics.wait = True
            return statistics

    def update_search(self):
        self.db.update_search(self.search)
