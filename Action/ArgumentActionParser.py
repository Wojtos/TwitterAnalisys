import argparse
from datetime import datetime, date, timedelta

from Action.ActionParser import ActionParser
from Action.AddSearchAction import AddSearchAction
from Action.AddSearchFileAction import AddSearchFileAction
from Action.AnalyseTweetsAction import AnalyseTweetsAction
from Action.RunSearchAction import RunSearchAction
from Action.SearchAction import SearchAction


class ArgumentActionParser(ActionParser):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--action', default='run_search', type=str)
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
        self.parser.add_argument('--file', type=str)
        self.args = self.parser.parse_args()

    def parse(self):
        if self.args.action == 'add_search':
            if self.args.query is not None:
                return AddSearchAction(
                    query=self.args.query,
                    until=self.args.until,
                    since_id=self.args.since_id,
                    lang=self.args.lang
                )
            elif self.args.file is not None:
                try:
                    query_file = open(self.args.file, 'r')
                    return AddSearchFileAction(
                        query_file=query_file,
                        until=self.args.until,
                        since_id=self.args.since_id,
                        lang=self.args.lang
                    )
                except OSError:
                    raise Exception(f'Could not open {self.args.file}!')

            else:
                raise Exception('Option --query or --file must be defined')
        elif self.args.action == 'search':
            if self.args.search_id is None:
                raise Exception('Option --search_id must be defined')

            return SearchAction(self.args.search_id)
        elif self.args.action == 'run_search':
            return RunSearchAction()
        elif self.args.action == 'analyse':
            return AnalyseTweetsAction()
        else:
            raise Exception('Wrong Command')

