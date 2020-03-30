class SearchStatistics:
    def __init__(self, until):
        self.until = until
        self.since_id = None
        self.fetched_entites_amount = 0
        self.saved_entites_amount = 0