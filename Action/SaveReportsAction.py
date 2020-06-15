from Action.Action import Action
from Action.AnalyseTweetsAction import AnalyseTweetsAction
from Database.TwitterDB import TwitterDB
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sn
import statistics


class SaveReportsAction(Action):
    def __init__(self):
        self.db = TwitterDB.instance

    def execute(self):
        users = self.db.find_all_users()
        user_metrics = list(map(
            lambda user: user.original_metrics,
            users
        ))
        print(user_metrics[0])
        self.correlations(user_metrics)

        metric_lists = []
        for key in AnalyseTweetsAction.METRIC_KEYS:
            # self.print_metric_stats(by_user, key)
            metric_lists.append(sorted(users, key=lambda i: i.metrics_order[key]))
            # print('Prepared metric:', key)
        LIMIT = 50
        self.print_metrics(AnalyseTweetsAction.METRIC_KEYS, metric_lists, LIMIT)

    def correlations(self, users):
        df = pd.DataFrame(users)
        plt.figure(figsize=(10, 8))
        sn.heatmap(df.corr(), annot=True)
        plt.yticks(rotation=70)
        plt.xticks(rotation=20)
        plt.savefig('correlation_matrix.png')
        plt.clf()

    def print_metrics(self, metric_keys, metric_lists, limit=50):
        with open('results.txt', 'w', encoding="utf-8") as f:
            self.print_line(f, ['nr\tid\tscreen_name\tcategory\tsubcategory\tcomment\tlabel k-means\tlabel em\tmetric score\tfollowers\ttweets\toccurences on other lists'])
            for i, (key, metric_list) in enumerate(zip(metric_keys, metric_lists)):
                self.print_line(f, [key])
                self.print_metric_stats(metric_list, key, f)
                for j, user in enumerate(metric_list[:limit]):
                    self.print_line(f, [j+1], end='\t')
                    self.print_line(f, [user.id], end='\t')
                    self.print_line(f, [user.screen_name], end='\t')
                    self.print_line(f, [user.category if user.category is not None else '?'], end='\t')
                    self.print_line(f, [user.subcategory if user.subcategory is not None else '?'], end='\t')
                    self.print_line(f, [user.comment if user.comment is not None else '?'], end='\t')
                    self.print_line(f, [user.labels['KMeans'] if 'KMeans' in user.labels is not None else '?'], end='\t')
                    self.print_line(f, [user.labels['GaussianMixture'] if 'GaussianMixture' in user.labels is not None else '?'], end='\t')
                    self.print_line(f, [user.original_metrics[key]], end='\t')
                    self.print_line(f, [user.original_metrics['max_followers_count']], end='\t')
                    self.print_line(f, [user.original_metrics['tweet_count']], end='\t')
                    for k, (other_metric_key, other_metric_list) in enumerate(zip(metric_keys, metric_lists)):
                        if i != k:
                            for l, other_user in enumerate(other_metric_list[:limit]):
                                if user.screen_name == other_user.screen_name:
                                    self.print_line(f, [other_metric_key, l + 1], end='\t')
                    self.print_line(f, [''])
                self.print_line(f, [''])

    def print_line(self, file, line_elements, end='\n'):
        s = ''
        for el in range(len(line_elements)-1):
            s += str(line_elements[el]) + ' '
        s += str(line_elements[-1]) + end
        file.write(s)

    def print_metric_stats(self, users, key, f):
        self.print_line(f, ['\tmean:\t', statistics.mean([u.original_metrics[key] for u in users])])
        self.print_line(f, ['\tmedian:\t', statistics.median([u.original_metrics[key] for u in users])])
        self.print_line(f, ['\tpopulation std dev:\t', statistics.pstdev([u.original_metrics[key] for u in users])])
        quantiles_n=100
        quantiles = statistics.quantiles([u.original_metrics[key] for u in users], n=quantiles_n)
        quantile_intervals = [(i+1)*100/quantiles_n for i in range(quantiles_n-1)]
        self.print_line(f, ['\tquantile intervals:\t', quantile_intervals[int(quantiles_n/10)-1::int(quantiles_n/10)]])
        self.print_line(f, ['\tquantiles:\t', quantiles[int(quantiles_n/10)-1::int(quantiles_n/10)]])
        plt.bar(quantile_intervals, quantiles)
        plt.savefig(key+'_quantile_bar.png')
        plt.clf()
