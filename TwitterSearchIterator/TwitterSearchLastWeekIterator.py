from TwitterSearch import TwitterSearch
from TwitterSearchIterator.TwitterSearchIterator import TwitterSearchIterator
import os


class TwitterSearchLastWeekIterator(TwitterSearchIterator):
    def __init__(self, search_query):
        self.search_query = search_query
        self.library = TwitterSearch(
            consumer_key=os.getenv("SEARCHTWEETS_CONSUMER_KEY"),
            consumer_secret=os.getenv("SEARCHTWEETS_CONSUMER_SECRET"),
            access_token=os.getenv("SEARCHTWEETS_ACCESS_TOKEN"),
            access_token_secret=os.getenv("SEARCHTWEETS_ACCESS_TOKEN_SECRET")
        )
        twitter_search_order = self.search_query.create_twitter_search_order()
        self.iter = iter(self.library.search_tweets_iterable(twitter_search_order))

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.iter)

