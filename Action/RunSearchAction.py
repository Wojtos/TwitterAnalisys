from Action.Action import Action
from Action.SearchAction import SearchAction
from Database.TwitterDB import TwitterDB
from time import sleep
import logging
import logging.handlers
import os
from datetime import datetime


class RunSearchAction(Action):
    def __init__(self):
        self.db = TwitterDB.instance
        handler = logging.handlers.WatchedFileHandler(os.environ.get('LOG_FILE'))
        formatter = logging.Formatter(logging.BASIC_FORMAT)
        handler.setFormatter(formatter)
        root = logging.getLogger()
        root.setLevel('INFO')
        root.addHandler(handler)

    @staticmethod
    def get_formatted_current_datetime():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def execute(self):
        while True:

            for search in self.db.find_all_searches():
                search_action = SearchAction(search)
                start_datetime = self.get_formatted_current_datetime()
                statistics = search_action.execute()
                end_datetime = self.get_formatted_current_datetime()
                logging.info(f'Stared: {start_datetime}, '
                             f'ended:{end_datetime}, '
                             f'query: {search.query}, '
                             f'fetched tweets: {statistics.fetched_entites_amount}, '
                             f'saved tweets" {statistics.saved_entites_amount}')
            sleep(60)
