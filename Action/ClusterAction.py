from bson import ObjectId

from Action.Action import Action
from sklearn.cluster import KMeans
import numpy as np
from matplotlib import pyplot as plt
import operator


from Database.TwitterDB import TwitterDB


class ClusterAction(Action):
    METRIC_KEYS_TO_CLUSTERING = [
         'tweet_count', 'med_retweet', 'sum_favorite', 'avg_retweet_to_followers_count'

    ]

    ALL_METRICS = [
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
            'max_following_count',
            'avg_favorite_to_followers_count',
            'avg_retweet_to_followers_count',
            'closeness_centrality',
            'betweenness_centrality',
            'pagerank',
            'input_edges_count'
        ]

    COLORS = [
        'red',
        'blue',
        'green',
        'black',
        'yellow',
        'pink'
    ]

    def __init__(self):
        self.db = TwitterDB.instance

    def execute(self):
        users = self.db.find_all_users()
        users = [user for user in users if bool(user.metrics) and isinstance(user._id, ObjectId)]
        user_metrics = np.array([user.get_metrics_as_array(self.METRIC_KEYS_TO_CLUSTERING) for user in users])
        user_original_metrics = np.array([user.get_original_metrics_as_array(self.METRIC_KEYS_TO_CLUSTERING) for user in users])
        #user_metrics = np.concatenate([user.get_date_split_metrics_as_array(self.METRIC_KEYS_TO_CLUSTERING) for user in users], axis=0)
        #user_metrics =[]
        #for user in users:
        #    date_split_metrics_array = user.get_date_split_metrics_as_array(self.METRIC_KEYS_TO_CLUSTERING)
        #    if date_split_metrics_array is not None:
        #        for user_week in date_split_metrics_array:
        #            user_metrics.append(user_week)
        #user_metrics = np.array(user_metrics)
        #user_original_metrics = []
        #for user in users:
        #    date_split_metrics_array = user.get_date_split_original_metrics_as_array(self.METRIC_KEYS_TO_CLUSTERING)
        #    if date_split_metrics_array is not None:
        #        for user_week in date_split_metrics_array:
        #            user_original_metrics.append(user_week)
        #user_original_metrics = np.array(user_original_metrics)
        #all_user_metrics = np.array([user.get_metrics_as_array(self.ALL_METRICS) for user in users])

        #a=min(users[0].metrics_order, key=users[0].metrics_order.get)
        #print(users[0].metrics_order[a])
        #exit()


        users_p = np.array([list(user.metrics.values()) for user in users if user.category == "p"])
        users_m = np.array([list(user.metrics.values()) for user in users if user.category == "m"])
        users_d = np.array([list(user.metrics.values()) for user in users if user.category == "d"])
        users_i = np.array([list(user.metrics.values()) for user in users if user.category == "i"])
        users_n = np.array([list(user.metrics.values()) for user in users if user.category == None])

        means_p = np.mean(users_p, axis=0)
        means_m = np.mean(users_m, axis=0)
        means_d = np.mean(users_d, axis=0)
        means_i = np.mean(users_i, axis=0)
        means_n = np.mean(users_n, axis=0)

        #np.set_printoptions(suppress=True)
        #with open('usr_stats_metrics_none.txt', 'w') as file:
        #    file.write(str(means_p))
        #    file.write('\n')
        #    file.write(str(means_m))
        #    file.write('\n')
        #    file.write(str(means_d))
        #    file.write('\n')
        #    file.write(str(means_i))
        #    file.write('\n')
        #    file.write(str(means_n))

        kmeans = KMeans(n_clusters=len(self.COLORS), verbose=1)
        print('prediction')
        labels = kmeans.fit_predict(user_metrics)
        print('predicted')
        #for user, label in zip(users, labels):
        #    user.label = int(label)
        #    self.db.save_user(user)
        #user_weeks = []
        #for u in users:
        #    uweeks = u.get_user_weeks()
        #    if uweeks is not None:
        #        for uweek in uweeks:
        #            user_weeks.append((u, uweek))
        labeled_users = list(zip(users, user_metrics, labels, user_original_metrics))
        #print(labeled_users[0])
        #print(labeled_users[0][0])

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        print('plotting 3D')
        for index, user_metric in enumerate(user_metrics[:5000]):
            ax.scatter(
                user_metric[0],
                user_metric[1],
                user_metric[2],
                c=self.COLORS[labels[index]]
            )

        ax.set_xlabel(self.METRIC_KEYS_TO_CLUSTERING[0])
        ax.set_ylabel(self.METRIC_KEYS_TO_CLUSTERING[1])
        ax.set_zlabel(self.METRIC_KEYS_TO_CLUSTERING[2])
        plt.savefig('cluster.png')
        print('plotted 3D')

        print('writing results to file')
        output=[]
        output.append("group, color, count, percentage, top_50, top_10, p, m, d, i, ")
        output.append(", , , , , , , , , , ")
        for i in self.METRIC_KEYS_TO_CLUSTERING:
            output[0] += i+', , , , '
            output[1] += 'mean, min, max, std, '

        count_p = sum(map(lambda us : us.category=="p", users))
        count_m = sum(map(lambda us : us.category=="m", users))
        count_d = sum(map(lambda us : us.category=="d", users))
        count_i = sum(map(lambda us : us.category=="i", users))

        for i, color in enumerate(self.COLORS):
            this_users = [t[0] for t in labeled_users if t[2] == i]
            this_user_metrics = np.array([t[3] for t in labeled_users if t[2] == i])
            means = np.mean(this_user_metrics, axis = 0)
            mins = np.amin(this_user_metrics, axis = 0)
            maxes = np.amax(this_user_metrics, axis = 0)
            stds = np.std(this_user_metrics, axis = 0)

            assigned_count = 0
            for us in this_users:
                if us.category != None:
                    assigned_count += 1
            percentage = len([label for label in labels if label == i]) / len(labels) * 100
            perc_p = 100*sum(map(lambda us : us.category=="p", this_users))/len(this_users)
            perc_m = 100*sum(map(lambda us : us.category=="m", this_users))/len(this_users)
            perc_d = 100*sum(map(lambda us : us.category=="d", this_users))/len(this_users)
            perc_i = 100*sum(map(lambda us : us.category=="i", this_users))/len(this_users)

            perc_top_50 = 100*sum(map(lambda us : us.metrics_order[min(us.metrics_order, key=us.metrics_order.get)] <= 50, this_users))/len(this_users)
            perc_top_10 = 100*sum(map(lambda us : us.metrics_order[min(us.metrics_order, key=us.metrics_order.get)] <= 10, this_users))/len(this_users)
            metric_scores = ""
            for (mean, _min, _max, std) in zip(means, mins, maxes, stds):
                metric_scores+=str(mean)+", "+str(_min)+", "+str(_max)+", "+str(std)+", "
            output.append(f'{i}, {color}, {len(this_users)}, {percentage}, {perc_top_50}, {perc_top_10}, {perc_p}, {perc_m}, {perc_d}, {perc_i}, {metric_scores}')

        with open('clusters_stats.txt', 'w') as file:
            for line in output:
                file.write(line)
                file.write('\n')


