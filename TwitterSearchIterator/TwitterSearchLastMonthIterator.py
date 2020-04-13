from datetime import datetime, timedelta
from TwitterSearchIterator.TwitterSearchIterator import TwitterSearchIterator
import searchtweets


class TwitterSearchLastMonthIterator(TwitterSearchIterator):
    def __init__(self, search_query):
        self.premium_search_args = searchtweets.load_credentials()
        self.rule = searchtweets.gen_rule_payload(
            search_query.query,
            to_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        )
        try:
            self.iter = iter(searchtweets.collect_results(self.rule, result_stream_args=self.premium_search_args))
        except Exception:
            self.iter = iter([])

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.iter)

