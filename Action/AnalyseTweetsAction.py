from Action.Action import Action
from Database.TwitterDB import TwitterDB
import math
import networkx as nx

from Entity.User import User


class AnalyseTweetsAction(Action):
    GRAPH_METRIC_KEYS = [
        'closeness_centrality',
        'betweenness_centrality',
        'pagerank',
        'input_edges_count',
        'retweet_count',
        'unique_retweet_count',

    ]
    NON_GRAPH_METRIC_KEYS = [
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
        'max_following_count',
        'input_edges_count_with_minimum_5_retweets',
        'input_edges_count_with_minimum_10_retweets',
    ]
    METRIC_KEYS = GRAPH_METRIC_KEYS + NON_GRAPH_METRIC_KEYS

    def __init__(self):
        self.db = TwitterDB.instance

    def get_retweets_graph_metrics_by_userid(self):
        user_retweet_nodes = self.db.get_retweets_graph_edges(threshold=1)
        G = nx.Graph()
        for retweet_node in user_retweet_nodes:
            retweet_node['input_edges_count_with_minimum_5_retweets'] = 0
            retweet_node['input_edges_count_with_minimum_10_retweets'] = 0
            for retweet_edge in retweet_node['data']:
                G.add_edge(
                    retweet_node['_id']['userid'],
                    retweet_edge['retweeting_userid'],
                    weight=1/retweet_edge['retweet_count']
                )
                if retweet_edge['retweet_count'] >= 5:
                    retweet_node['input_edges_count_with_minimum_5_retweets'] += 1
                if retweet_edge['retweet_count'] >= 10:
                    retweet_node['input_edges_count_with_minimum_10_retweets'] += 1

        print(f'Liczba krawędzi: {nx.number_of_edges(G)}')
        print(f'Liczba wierzchołków: {nx.number_of_nodes(G)}')
        # print(f'Radius: {nx.radius(G)}')
        # print(f'Diameter: {nx.diameter(G)}')
        # print(f'Average shortest path: {nx.average_shortest_path_length(G)}')
        # print(f'k_components: {nx.k_components(G)}')
        print(f'number_connected_components: {nx.number_connected_components(G)}')
        closeness_centrality = nx.closeness_centrality(G)
        print('Computed closeness_centrality')
        betweenness_centrality = nx.betweenness_centrality(G)
        print('Computed betweenness_centrality')
        pagerank = nx.pagerank(G)
        print('Computed pagerank')

        for user_retweet_node in user_retweet_nodes:
            userid = user_retweet_node['_id']['userid']
            user_retweet_node['closeness_centrality'] = closeness_centrality[userid]
            user_retweet_node['betweenness_centrality'] = betweenness_centrality[userid]
            user_retweet_node['pagerank'] = pagerank[userid]
            user_retweet_node['input_edges_count'] = nx.degree(G, nbunch=userid)
            user_retweet_node['output_edges_count'] = 0

        return dict([(
            retweet_node['_id']['userid'],
            {
                'closeness_centrality': retweet_node['closeness_centrality'],
                'betweenness_centrality': retweet_node['betweenness_centrality'],
                'pagerank': retweet_node['pagerank'],
                'input_edges_count': retweet_node['input_edges_count'],
                'output_edges_count': retweet_node['output_edges_count'],
                'input_edges_count_with_minimum_5_retweets': retweet_node['input_edges_count_with_minimum_5_retweets'],
                'input_edges_count_with_minimum_10_retweets': retweet_node['input_edges_count_with_minimum_10_retweets'],
            }
        ) for retweet_node in user_retweet_nodes])


    def calc_user_medians(self, user_data):
        favorite_values = sorted(user_data['favorite_values'])
        retweet_values = sorted(user_data['retweet_values'])
        lower_index = math.floor((len(favorite_values)-1)/2)
        upper_index = math.ceil((len(favorite_values)-1)/2)
        favorite_median = (favorite_values[lower_index]+favorite_values[upper_index])/2
        retweet_median = (retweet_values[lower_index]+retweet_values[upper_index])/2
        user_data['med_favorite'] = favorite_median
        user_data['med_retweet'] = retweet_median
        if user_data['avg_favorite'] == 0:
            user_data['med_to_avg_fav_ratio'] = 0
        else:
            user_data['med_to_avg_fav_ratio'] = favorite_median/user_data['avg_favorite']
        return user_data


    def execute(self):
        user_metrics = self.db.get_user_metrics(6, 1, 5)
        print('Number of users:', len(user_metrics))
        user_metrics = list(map(self.calc_user_medians, user_metrics))
        retweet_metrics_by_userid = self.get_retweets_graph_metrics_by_userid()
        for user_metric in user_metrics:
            userid = user_metric['_id']['userid']
            user_edge = retweet_metrics_by_userid[userid] if userid in retweet_metrics_by_userid else None
            if user_edge:
                user_metric['closeness_centrality'] = user_edge['closeness_centrality']
                user_metric['betweenness_centrality'] = user_edge['betweenness_centrality']
                user_metric['pagerank'] = user_edge['pagerank']
                user_metric['input_edges_count'] = user_edge['input_edges_count']
                user_metric['output_edges_count'] = user_edge['output_edges_count']
                user_metric['input_edges_count_with_minimum_5_retweets'] = user_edge['input_edges_count_with_minimum_5_retweets']
                user_metric['input_edges_count_with_minimum_10_retweets'] = user_edge['input_edges_count_with_minimum_10_retweets']
            else:
                user_metric['closeness_centrality'] = 0
                user_metric['betweenness_centrality'] = 0
                user_metric['pagerank'] = 0
                user_metric['input_edges_count'] = 0
                user_metric['output_edges_count'] = 0
                user_metric['input_edges_count_with_minimum_5_retweets'] = 0
                user_metric['input_edges_count_with_minimum_10_retweets'] = 0

        metric_lists = []
        for key in self.METRIC_KEYS:
            metric_lists.append(sorted(user_metrics, key=lambda i: i[key], reverse=True))

        self.save_users(self.METRIC_KEYS, metric_lists, user_metrics)

    def save_users(self, metric_keys, metric_lists, user_metrics):
        metrics_max_values = {}
        for metric_key in metric_keys:
            metrics_max_values[metric_key] = max(map(
                lambda metric: metric[metric_key] if metric_key in metric else 0,
                user_metrics
            ))
        for j, metric in enumerate(user_metrics):
            metrics = {}
            original_metrics = {}
            for metric_key in metric_keys:
                metric_value = metric[metric_key]
                original_metrics[metric_key] = metric_value
                normalized_metric_value = metric_value / metrics_max_values[metric_key]
                metrics[metric_key] = normalized_metric_value

            user_id = metric['_id']['userid']
            metrics_order = {}
            for (key, metric_list) in zip(metric_keys, metric_lists):
                for metric_order, user in enumerate(metric_list, start=1):
                    if user_id == user['_id']['userid']:
                        metrics_order[key] = metric_order
            if metric['aliasForUsersCollection']:
                user = self.db.find_user(user_id)
                user.metrics = metrics
                user.original_metrics = original_metrics
                user.metrics_order = metrics_order
            else:
                user = User(
                    id=user_id,
                    screen_name=metric['username'],
                    metrics=metrics,
                    original_metrics=original_metrics,
                    metrics_order=metrics_order
                )
            self.db.save_user(user)


