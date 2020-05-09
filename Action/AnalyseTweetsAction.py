from Action.Action import Action
from Database.TwitterDB import TwitterDB
import statistics
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sn


class AnalyseTweetsAction(Action):
    def __init__(self):
        self.db = TwitterDB.instance
        pass

    def correlations(self, keys, users):
        df = pd.DataFrame(users)
        plt.figure(figsize=(10, 8))
        sn.heatmap(df.corr(), annot=True)
        plt.yticks(rotation=70)
        plt.xticks(rotation=20)
        plt.savefig('correlation_matrix.png')
        plt.clf()


    def print_line(self, file, line_elements, end='\n'):
        s = ''
        for el in range(len(line_elements)-1):
            s += str(line_elements[el]) + ' '
        s += str(line_elements[-1]) + end
        file.write(s)

    def print_metric_stats(self, users, key, f):
        self.print_line(f, ['\tmean:\t', statistics.mean([u[key] for u in users])])
        self.print_line(f, ['\tmedian:\t', statistics.median([u[key] for u in users])])
        self.print_line(f, ['\tpopulation std dev:\t', statistics.pstdev([u[key] for u in users])])
        quantiles_n=100
        quantiles = statistics.quantiles([u[key] for u in users], n=quantiles_n)
        quantile_intervals = [(i+1)*100/quantiles_n for i in range(quantiles_n-1)]
        self.print_line(f, ['\tquantile intervals:\t', quantile_intervals[int(quantiles_n/10)-1::int(quantiles_n/10)]])
        self.print_line(f, ['\tquantiles:\t', quantiles[int(quantiles_n/10)-1::int(quantiles_n/10)]])
        plt.bar(quantile_intervals, quantiles)
        plt.savefig(key+'_quantile_bar.png')
        plt.clf()

    def print_metrics(self, metric_keys, metric_lists, limit=50):
        with open('results.txt', 'w', encoding="utf-8") as f:
            self.print_line(f, ['nr\tid\tscreen_name\tname\tcategory\tsubcategory\tcomment\tmetric score\tfollowers\ttweets\toccurences on other lists'])
            for i, (key, metric_list) in enumerate(zip(metric_keys, metric_lists)):
                self.print_line(f, [key])
                self.print_metric_stats(metric_list, key, f)
                for j, user in enumerate(metric_list[:limit]):
                    self.print_line(f, [j+1], end='\t')
                    self.print_line(f, [user['_id']['userid']], end='\t')
                    self.print_line(f, [user['username']], end='\t')
                    self.print_line(f, [user['name']], end='\t')
                    if len(user['aliasForUsersCollection'])>0:
                        self.print_line(f, [user['aliasForUsersCollection'][0]['category']], end='\t')
                        self.print_line(f, [user['aliasForUsersCollection'][0]['subcategory']], end='\t')
                        self.print_line(f, [user['aliasForUsersCollection'][0]['comment']], end='\t')
                    else:
                        self.print_line(f, ['?'], end='\t')
                        self.print_line(f, ['?'], end='\t')
                        self.print_line(f, ['?'], end='\t')
                    self.print_line(f, [user[key]], end='\t')
                    self.print_line(f, [user['max_followers_count']], end='\t')
                    self.print_line(f, [user['tweet_count']], end='\t')
                    for k, (other_metric_key, other_metric_list) in enumerate(zip(metric_keys, metric_lists)):
                        if i != k:
                            for l, other_user in enumerate(other_metric_list[:limit]):
                                if user['username'] == other_user['username']:
                                    self.print_line(f, [other_metric_key, l + 1], end='\t')
                    self.print_line(f, [''])
                self.print_line(f, [''])

    def execute(self):
        by_user = self.db.get_user_metrics(6, 1, 5)
        print('Number of users:', len(by_user))

        limit = 50

        metric_keys = [
            'max_followers_count',
            'tweet_count',
            'avg_favorite',
            'avg_retweet',
            'sum_favorite',
            'sum_retweet',
            'weighed_sum',
            'weighed_sum_with_cost',
            'unique_retweet_count'
        ]
        metric_lists = []
        for key in metric_keys:
            # self.print_metric_stats(by_user, key)
            metric_lists.append(sorted(by_user, key=lambda i: i[key], reverse=True))
            # print('Prepared metric:', key)

        self.correlations(metric_keys, by_user)
        self.print_metrics(metric_keys, metric_lists, limit)
