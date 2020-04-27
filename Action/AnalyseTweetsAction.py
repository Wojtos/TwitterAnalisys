from Action.Action import Action
from Database.TwitterDB import TwitterDB
import statistics


class AnalyseTweetsAction(Action):
    def __init__(self):
        self.db = TwitterDB.instance
        pass

    def print_metric_stats(self, users, key):
        print('\tmean:\t', statistics.mean([u[key] for u in users]))
        print('\tmedian:\t', statistics.median([u[key] for u in users]))
        print('\tpopulation std dev:\t', statistics.pstdev([u[key] for u in users]))
        quantiles_n=20
        print('\tquantile intervals:\t', [(i+1)*100/quantiles_n for i in range(quantiles_n-1)])
        print('\tquantiles:\t', statistics.quantiles([u[key] for u in users], n=quantiles_n))

    def print_metrics(self, metric_keys, metric_lists, users, limit=50):
        print('nr\tid\tscreen_name\tname\tcategory\tsubcategory\tcomment\tmetric score\tfollowers\ttweets\toccurences on other lists')
        for i, (key, metric_list) in enumerate(zip(metric_keys, metric_lists)):
            print(key)
            self.print_metric_stats(metric_list, key)
            for j, user in enumerate(metric_list[:limit]):
                print(j+1, end='\t')
                print(user['_id']['userid'], end='\t')
                print(user['username'], end='\t')
                print(user['name'], end='\t')
                if len(user['aliasForUsersCollection'])>0:
                    print(user['aliasForUsersCollection'][0]['category'], end='\t')
                    print(user['aliasForUsersCollection'][0]['subcategory'], end='\t')
                    print(user['aliasForUsersCollection'][0]['comment'], end='\t')
                else:
                    print('?', end='\t')
                    print('?', end='\t')
                print(user[key], end='\t')
                print(user['max_followers_count'], end='\t')
                print(user['tweet_count'], end='\t')
                for k, (other_metric_key, other_metric_list) in enumerate(zip(metric_keys, metric_lists)):
                    if i != k:
                        for l, other_user in enumerate(other_metric_list[:limit]):
                            if user['username'] == other_user['username']:
                                print(other_metric_key, l + 1, end='\t')
                print('')
            print('')

    def execute(self):
        tweets = self.db.get_tweets_by_user_screen_name('tvn24')
        min_id=1250097097543688192
        max_id=0
        for t in tweets:
            print(t)
            if t['id']<min_id:
                min_id=t['id']
            if t['id']>max_id:
                max_id=t['id']
        print(min_id)
        print(max_id)

        by_user = self.db.get_user_metrics(6, 1, 5)
        print('Number of users:', len(by_user))

        limit = 50

        metric_keys = ['max_followers_count', 'tweet_count', 'avg_favorite', 'avg_retweet', 'sum_favorite', 'sum_retweet', 'weighed_sum', 'weighed_sum_with_cost']
        metric_lists = []
        for key in metric_keys:
            #self.print_metric_stats(by_user, key)
            metric_lists.append(sorted(by_user, key=lambda i: i[key], reverse=True))
            #print('Prepared metric:', key)

        self.print_metrics(metric_keys, metric_lists, by_user, limit)