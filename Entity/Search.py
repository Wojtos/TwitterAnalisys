import datetime

from TwitterSearchHelpers.ExtendedTwitterSearchOrder import ExtendedTwitterSearchOrder


class Search:
    def __init__(self, query, until, since_id, lang, _id=None):
        self.query = query
        self.until = until.date() if isinstance(until, datetime.datetime) else until
        self.since_id = since_id
        self.lang = lang
        if _id is not None:
            self._id = _id

    def create_twitter_search_order(self):
        twitter_search_order = ExtendedTwitterSearchOrder()
        twitter_search_order.add_keyword(self.query)
        twitter_search_order.set_language(self.lang)
        twitter_search_order.set_include_entities(False)
        twitter_search_order.set_result_type('recent')
        twitter_search_order.set_until(self.until)
        if self.since_id is not None:
            twitter_search_order.set_since_id(self.since_id)
        return twitter_search_order
