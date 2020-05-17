from Action.Action import Action
from Database.TwitterDB import TwitterDB
import statistics
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sn
import math
import networkx as nx

from Entity.User import User


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

    def get_retweets_graph_metrics_by_userid(self):
        user_retweet_edges = self.db.get_retweets_graph_edges(threshold=1)
        G = nx.Graph()
        for retweet_node in user_retweet_edges:
            for retweet_edge in retweet_node['data']:
                G.add_edge(
                    retweet_node['_id']['userid'],
                    retweet_edge['retweeting_userid'],
                    weight=1/retweet_edge['retweet_count']
                )
        print(f'Liczba krawędzi: {nx.number_of_edges(G)}')
        print(f'Liczba wierzchołków: {nx.number_of_nodes(G)}')
        # print(f'Radius: {nx.radius(G)}')
        # print(f'Diameter: {nx.diameter(G)}')
        # print(f'Average shortest path: {nx.average_shortest_path_length(G)}')
        # print(f'k_components: {nx.k_components(G)}')
        closeness_centrality = nx.closeness_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        pagerank = nx.pagerank(G)
        for user_retweet_edge in user_retweet_edges:
            user_retweet_edge['closeness_centrality'] = closeness_centrality[user_retweet_edge['_id']['userid']]
            user_retweet_edge['betweenness_centrality'] = betweenness_centrality[user_retweet_edge['_id']['userid']]
            user_retweet_edge['pagerank'] = pagerank[user_retweet_edge['_id']['userid']]
        return dict([(
            retweet_edge['_id']['userid'],
            {
                'closeness_centrality': retweet_edge['closeness_centrality'],
                'betweenness_centrality': retweet_edge['betweenness_centrality'],
                'pagerank': retweet_edge['pagerank'],
            }
        ) for retweet_edge in user_retweet_edges])


    def print_metrics(self, metric_keys, metric_lists, limit=50):
        with open('results.txt', 'w', encoding="utf-8") as f:
            self.print_line(f, ['nr\tid\tscreen_name\tname\tcategory\tsubcategory\tcomment\tlabel\tmetric score\tfollowers\ttweets\toccurences on other lists'])
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
                        self.print_line(f, [user['aliasForUsersCollection'][0]['label']], end='\t')
                    else:
                        self.print_line(f, ['?'], end='\t')
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


    def calc_user_medians(self, user_data):
        favorite_values = sorted(user_data['favorite_values'])
        retweet_values = sorted(user_data['retweet_values'])
        lower_index = math.floor((len(favorite_values)-1)/2)
        upper_index = math.ceil((len(favorite_values)-1)/2)
        favorite_median = (favorite_values[lower_index]+favorite_values[upper_index])/2
        retweet_median = (retweet_values[lower_index]+retweet_values[upper_index])/2
        user_data['med_favorite'] = favorite_median
        user_data['med_retweet'] = retweet_median
        if user_data['avg_favorite']==0:
            user_data['med_to_avg_fav_ratio'] = 0
        else:
            user_data['med_to_avg_fav_ratio'] = favorite_median/user_data['avg_favorite']
        return user_data


    def execute(self):
        by_user = self.db.get_user_metrics(6, 1, 5)
        for u in by_user:
            u = self.calc_user_medians(u)
        print('Number of users:', len(by_user))
        user_metrics = self.db.get_user_metrics(6, 1, 5)
        retweet_metrics_by_userid = self.get_retweets_graph_metrics_by_userid()
        for user_metric in user_metrics:
            userid = user_metric['_id']['userid']
            user_edge = retweet_metrics_by_userid[userid] if userid in retweet_metrics_by_userid else None
            if user_edge:
                user_metric['closeness_centrality'] = user_edge['closeness_centrality']
                user_metric['betweenness_centrality'] = user_edge['betweenness_centrality']
                user_metric['pagerank'] = user_edge['pagerank']
            else:
                user_metric['closeness_centrality'] = 0
                user_metric['betweenness_centrality'] = 0
                user_metric['pagerank'] = 0
        print('Number of users:', len(user_metrics))

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
            'med_favorite',
            'med_retweet',
            'unique_retweet_count',
            'max_following_count'
            'unique_retweet_count',
            'avg_favorite_to_followers_count',
            'avg_retweet_to_followers_count',
            'closeness_centrality',
            'betweenness_centrality',
            'pagerank'
        ]
        metric_lists = []
        for key in metric_keys:
            # self.print_metric_stats(by_user, key)
            metric_lists.append(sorted(user_metrics, key=lambda i: i[key], reverse=True))
            # print('Prepared metric:', key)

        self.correlations(metric_keys, user_metrics)
        self.print_metrics(metric_keys, metric_lists, limit)
        self.save_users(metric_keys, user_metrics)

    def save_users(self, metric_keys, user_metrics):
        metrics_max_values = {}
        for metric_key in metric_keys:
            metrics_max_values[metric_key] = max(map(
                lambda metric: metric[metric_key] if metric_key in metric else 0,
                user_metrics
            ))
        print(metrics_max_values)
        for j, metric in enumerate(user_metrics):
            metrics = {}
            for metric_key in metric_keys:
                metric_value = metric[metric_key]
                normalized_metric_value = metric_value / metrics_max_values[metric_key]
                metrics[metric_key] = normalized_metric_value
            if metric['aliasForUsersCollection']:
                earlier_user = metric['aliasForUsersCollection'][0]
                user = User(
                    id=earlier_user['id'],
                    screen_name=earlier_user['screen_name'],
                    label=earlier_user['label'],
                    metrics=metrics,
                )
            else:
                user = User(
                    id=metric['_id']['userid'],
                    screen_name=metric['username'],
                    metrics=metrics
                )
            self.db.save_user(user)


