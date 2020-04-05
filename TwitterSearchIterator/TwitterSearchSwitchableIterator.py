from datetime import datetime, timedelta

from TwitterSearchIterator.TwitterSearchIterator import TwitterSearchIterator
import searchtweets

from TwitterSearchIterator.TwitterSearchLastMonthIterator import TwitterSearchLastMonthIterator
from TwitterSearchIterator.TwitterSearchLastWeekIterator import TwitterSearchLastWeekIterator


class TwitterSearchSwitchableIterator(TwitterSearchIterator):
    def __init__(self, search_query):
        self.search_query = search_query
        self.last_month_iterator = TwitterSearchLastMonthIterator(search_query)
        self.last_week_iterator = None
        self.week_ago = (datetime.now() - timedelta(days=7)).date()

    def __iter__(self):
        return self

    def __next__(self):
        if self.search_query.until < self.week_ago:
            try:
                return next(self.last_month_iterator)
            except StopIteration:
                pass
        if self.last_week_iterator is None:
            self.search_query.until = self.week_ago
            self.last_week_iterator = TwitterSearchLastWeekIterator(self.search_query)
        return next(self.last_week_iterator)



