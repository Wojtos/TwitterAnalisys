from Action.Action import Action
from Database.TwitterDB import TwitterDB


class AnalyseTweetsAction(Action):
    def __init__(self):
        self.db = TwitterDB.instance
        pass

    def print_metrics(self, metric_keys, metric_lists):
        for i, (key, metric_list) in enumerate(zip(metric_keys, metric_lists)):
            print(key)
            for j, user in enumerate(metric_list):
                print(user['_id']['userid'], end='\t')
                print(user['username'], end='\t')
                print(user['name'], end='\t')
                print(user['aliasForUsersCollection'][0]['category'], end='\t')
                print(user['aliasForUsersCollection'][0]['comment'], end='\t')
                print(user[key], end='\t')
                print(user['max_followers_count'], end='\t')
                print(user['tweet_count'], end='\t')
                for k, (other_metric_key, other_metric_list) in enumerate(zip(metric_keys, metric_lists)):
                    if i != k:
                        for l, other_user in enumerate(other_metric_list):
                            if user['username'] == other_user['username']:
                                print(other_metric_key, l + 1, end='\t')
                print('')
            print('')

    def execute(self):
        #tweets = self.db.get_tweets_by_user_screen_name('TheNationNews')
        #for t in tweets:
        #    print(t)

        by_user = self.db.get_all_users()

        limit = 50

        metric_keys = ['max_followers_count', 'tweet_count', 'avg_favorite', 'avg_retweet', 'sum_retweet', 'sum_retweet']
        metric_lists = []
        for key in metric_keys:
            metric_lists.append(sorted(by_user, key=lambda i: i[key], reverse=True)[:limit])

        self.print_metrics(metric_keys, metric_lists)