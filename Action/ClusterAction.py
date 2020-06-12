from bson import ObjectId

from Action.Action import Action
import numpy as np
from matplotlib import pyplot as plt


from Database.TwitterDB import TwitterDB


class ClusterAction(Action):
    METRIC_KEYS_TO_CLUSTERING = [
        'max_followers_count',
        'weighed_sum',
        'tweet_count',
        # 'betweenness_centrality'
    ]

    COLORS = [
        'red',
        'blue',
        'green',
        'black',
        'yellow',
        'pink'
    ]

    def __init__(self, cluster):
        self.db = TwitterDB.instance
        self.cluster = cluster

    def execute(self):
        users = self.db.find_all_users()
        users = [user for user in users if bool(user.metrics) and isinstance(user._id, ObjectId)]
        user_metrics = np.array([user.get_metrics_as_array(self.METRIC_KEYS_TO_CLUSTERING) for user in users])
        labels = self.cluster.fit(user_metrics)
        for user, label in zip(users, labels):
            int_label = int(label)
            user.label = int_label
            user.labels[self.cluster.get_name()] = int_label
            self.db.save_user(user)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for index, user_metric in enumerate(user_metrics):
            ax.scatter(
                user_metric[0],
                user_metric[1],
                user_metric[2],
                c=self.COLORS[labels[index]]
            )

        ax.set_xlabel(self.METRIC_KEYS_TO_CLUSTERING[0])
        ax.set_ylabel(self.METRIC_KEYS_TO_CLUSTERING[1])
        ax.set_zlabel(self.METRIC_KEYS_TO_CLUSTERING[2])
        plt.savefig(f'cluster{self.cluster.get_name()}.png')

        for i, color in enumerate(self.COLORS):
            percentage = len([label for label in labels if label == i]) / len(labels) * 100
            print(f'Group: {i}, color: {color}, percentage: {percentage}%')


