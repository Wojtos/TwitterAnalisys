import argparse
from datetime import datetime, date, timedelta

from Action.ActionParser import ActionParser
from Action.AddSearchAction import AddSearchAction
from Action.RunSearchAction import RunSearchAction
from Action.SearchAction import SearchAction


class ArgumentActionParser(ActionParser):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--action', default='run', type=str)
        self.parser.add_argument('--query', type=str)
        self.parser.add_argument(
            '--until',
            type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
            default=datetime.now() - timedelta(days=7),
            help="Date in the format YYYY-mm-dd"
        )
        self.parser.add_argument('--since_id', type=int)
        self.parser.add_argument('--lang', type=str, default='pl')
        self.parser.add_argument('--search_id', type=str)
        self.args = self.parser.parse_args()

    def parse(self):
        if self.args.action == 'add_search':
            if self.args.query is None:
                raise Exception('Option --query must be defined')
            add_search = AddSearchAction(
                query=self.args.query,
                until=self.args.until,
                since_id=self.args.since_id,
                lang=self.args.lang
            )
            return add_search
        elif self.args.action == 'search':
            if self.args.search_id is None:
                raise Exception('Option --search_id must be defined')

            return SearchAction(self.args.search_id)
        elif self.args.action == 'run_search':
            return RunSearchAction()
        else:
            raise Exception('Wrong Command')

