import datetime

from Database.TwitterDB import TwitterDB


class TweetsDateSplit:
    def __init__(self, days_interval, name):
        self.db = TwitterDB.instance
        self.days_interval = days_interval
        self.name = name
        self.date_splits = list(self.compute_date_splits())
        self.name_date_splits = list(map(
            lambda x: f'{x[0].strftime("%d.%m.%Y")} - {x[1].strftime("%d.%m.%Y")}',
            self.date_splits
        ))

    def compute_date_splits(self):
        start_date = self.db.find_first_tweet_date()
        end_date = self.db.find_last_tweet_date()
        next_week = start_date
        while next_week <= end_date:
            previous_week = next_week
            next_week += datetime.timedelta(days=self.days_interval)
            yield previous_week, next_week
