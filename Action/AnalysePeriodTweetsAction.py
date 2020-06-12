from Action.Action import Action
from Database.TwitterDB import TwitterDB
import math
import networkx as nx

from Entity.User import User


class AnalysePeriodTweetsAction(Action):
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
    ]
    METRIC_KEYS = GRAPH_METRIC_KEYS + NON_GRAPH_METRIC_KEYS

    def __init__(self, date_splits=None):
        self.db = TwitterDB.instance
        self.date_splits = date_splits

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
        for date_split, name_date_split in zip(self.date_splits.date_splits, self.date_splits.name_date_splits):
            user_metrics = self.db.get_user_metrics(6, 1, 5, date_split)
            print('Number of users-periods:', len(user_metrics))
            user_metrics = list(map(self.calc_user_medians, user_metrics))
            metric_lists = []
            for key in self.NON_GRAPH_METRIC_KEYS:
                metric_lists.append(sorted(user_metrics, key=lambda i: i[key], reverse=True))

            self.save_users(self.NON_GRAPH_METRIC_KEYS, user_metrics, name_date_split)

    def save_users(self, metric_keys, user_metrics, name_date_split):
        metrics_max_values = {}
        for metric_key in metric_keys:
            metrics_max_values[metric_key] = max(map(
                lambda metric: metric[metric_key] if metric_key in metric else 0,
                user_metrics
            ))
        for j, metric in enumerate(user_metrics):
            user_id = metric['_id']['userid']
            if metric['aliasForUsersCollection']:
                metrics = {}
                original_metrics = {}
                for metric_key in metric_keys:
                    metric_value = metric[metric_key]
                    original_metrics[metric_key] = metric_value
                    normalized_metric_value = metric_value / metrics_max_values[metric_key]
                    metrics[metric_key] = normalized_metric_value

                    user = self.db.find_user(user_id)
                    user.add_date_split_metrics(self.date_splits.name, name_date_split, metrics)
                    user.add_date_split_original_metrics(self.date_splits.name, name_date_split, original_metrics)
                    self.db.save_user(user)


