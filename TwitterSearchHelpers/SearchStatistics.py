class SearchStatistics:
    def __init__(self, search):
        self.until = search.until.date()
        self.since_id = search.since_id
        self.fetched_entites_amount = 0
        self.saved_entites_amount = 0
        self.wait = False
