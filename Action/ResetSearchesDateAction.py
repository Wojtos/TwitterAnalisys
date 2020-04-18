from Action.Action import Action
from Database.TwitterDB import TwitterDB


class ResetSearchesDateAction(Action):
    def __init__(self, until, since_id):
        self.db = TwitterDB.instance
        self.until = until
        self.since_id = since_id

    def execute(self):
        for search in self.db.find_all_searches():
            search.until = self.until
            search.since_id = self.since_id
            self.db.update_search(search)

