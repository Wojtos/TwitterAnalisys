from Action.Action import Action
from Database.TwitterDB import TwitterDB
from Entity.Search import Search


class AddSearchFileAction(Action):
    def __init__(self, query_file, until, since_id, lang):
        self.query_file = query_file
        self.until = until
        self.since_id = since_id
        self.lang = lang
        self.twitter_db = TwitterDB.instance

    def execute(self):
        print(self.query_file.closed)
        return [self.add_search(query.strip()) for query in self.query_file.readlines()]

    def add_search(self, query):
        if self.twitter_db.search_exist_by_query(query):
            print(f'Search with query: {query} has already been added!')
            return None
        else:
            print(f'Adding search with query: {query}!')
            search = Search(
                query=query,
                until=self.until,
                since_id=self.since_id,
                lang=self.lang
            )
            self.twitter_db.add_search(search)
            return search