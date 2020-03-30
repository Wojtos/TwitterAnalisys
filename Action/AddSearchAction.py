from Action.Action import Action
from Database.TwitterDB import TwitterDB
from Entity.Search import Search


class AddSearchAction(Action):
    def __init__(self, query, until, since_id, lang):
        self.query = query
        self.until = until
        self.since_id = since_id
        self.lang = lang

    def execute(self):
        search = Search(
            query=self.query,
            until=self.until,
            since_id=self.since_id,
            lang=self.lang
        )
        TwitterDB.instance.add_search(search)
