from Action.Action import Action
from Database.TwitterDB import TwitterDB


class RunAction(Action):
    def __init__(self):
        self.db = TwitterDB.instance

    def execute(self):
        for search in self.db.find_all_searches():
            print(search)