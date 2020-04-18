from Action.Action import Action
from Database.TwitterDB import TwitterDB


class AnalyseTweetsAction(Action):
    def __init__(self):
        self.db = TwitterDB.instance
        pass

    def execute(self):
        tweets = self.db.get_tweets_by_user_screen_name('TheNationNews')
        for t in tweets:
            print(t)
        by_user = self.db.get_all_users()

        limit = 50
        most_followed = by_user[:limit]
        most_tweets = sorted(by_user, key=lambda i: i['tweet_count'], reverse=True)[:limit]
        most_avg_fav = sorted(by_user, key=lambda i: i['avg_favorite'], reverse=True)[:limit]
        most_avg_ret = sorted(by_user, key=lambda i: i['avg_retweet'], reverse=True)[:limit]
        most_sum_fav = sorted(by_user, key=lambda i: i['sum_favorite'], reverse=True)[:limit]
        most_sum_ret = sorted(by_user, key=lambda i: i['sum_retweet'], reverse=True)[:limit]

        print('Most followed:')
        for user in most_followed:
            print(user['_id']['userid'], end='\t')
            print(user['username'], end='\t')
            print(user['name'], end='\t')
            print(user['max_userfollowers_count'], end='\t')
            print(user['max_userfollowers_count'], end='\t')
            print(user['tweet_count'], end='\t')
            for i, u2 in enumerate(most_tweets):
                if user['username'] == u2['username']:
                    print('most_tweets', i+1, end='\t')
            for i, u2 in enumerate(most_avg_fav):
                if user['username'] == u2['username']:
                    print('most_avg_fav', i+1, end='\t')
            for i, u2 in enumerate(most_avg_ret):
                if user['username'] == u2['username']:
                    print('most_avg_ret', i+1, end='\t')
            for i, u2 in enumerate(most_sum_fav):
                if user['username'] == u2['username']:
                    print('most_sum_fav', i+1, end='\t')
            for i, u2 in enumerate(most_sum_ret):
                if user['username'] == u2['username']:
                    print('most_sum_ret', i+1, end='\t')
            #for col in user.items():
            #    print(col, end='\t')
            print('')
        print('')
        print('Most tweets:')
        for user in most_tweets:
            print(user['_id']['userid'], end='\t')
            print(user['username'], end='\t')
            print(user['name'], end='\t')
            print(user['tweet_count'], end='\t')
            print(user['max_userfollowers_count'], end='\t')
            print(user['tweet_count'], end='\t')
            for i, u2 in enumerate(most_followed):
                if user['username'] == u2['username']:
                    print('most_followed', i+1, end='\t')
            for i, u2 in enumerate(most_avg_fav):
                if user['username'] == u2['username']:
                    print('most_avg_fav', i+1, end='\t')
            for i, u2 in enumerate(most_avg_ret):
                if user['username'] == u2['username']:
                    print('most_avg_ret', i+1, end='\t')
            for i, u2 in enumerate(most_sum_fav):
                if user['username'] == u2['username']:
                    print('most_sum_fav', i+1, end='\t')
            for i, u2 in enumerate(most_sum_ret):
                if user['username'] == u2['username']:
                    print('most_sum_ret', i+1, end='\t')
            print('')
        print('')
        print('Most avg favorites:')
        for user in most_avg_fav:
            print(user['_id']['userid'], end='\t')
            print(user['username'], end='\t')
            print(user['name'], end='\t')
            print(int(user['avg_favorite']), end='\t')
            print(user['max_userfollowers_count'], end='\t')
            print(user['tweet_count'], end='\t')
            for i, u2 in enumerate(most_followed):
                if user['username'] == u2['username']:
                    print('most_followed', i+1, end='\t')
            for i, u2 in enumerate(most_tweets):
                if user['username'] == u2['username']:
                    print('most_tweets', i+1, end='\t')
            for i, u2 in enumerate(most_avg_ret):
                if user['username'] == u2['username']:
                    print('most_avg_ret', i+1, end='\t')
            for i, u2 in enumerate(most_sum_fav):
                if user['username'] == u2['username']:
                    print('most_sum_fav', i+1, end='\t')
            for i, u2 in enumerate(most_sum_ret):
                if user['username'] == u2['username']:
                    print('most_sum_ret', i+1, end='\t')
            print('')
        print('')
        print('Most avg retweets:')
        for user in most_avg_ret:
            print(user['_id']['userid'], end='\t')
            print(user['username'], end='\t')
            print(user['name'], end='\t')
            print(int(user['avg_retweet']), end='\t')
            print(user['max_userfollowers_count'], end='\t')
            print(user['tweet_count'], end='\t')
            for i, u2 in enumerate(most_followed):
                if user['username'] == u2['username']:
                    print('most_followed', i+1, end='\t')
            for i, u2 in enumerate(most_tweets):
                if user['username'] == u2['username']:
                    print('most_tweets', i+1, end='\t')
            for i, u2 in enumerate(most_avg_fav):
                if user['username'] == u2['username']:
                    print('most_avg_fav', i+1, end='\t')
            for i, u2 in enumerate(most_sum_fav):
                if user['username'] == u2['username']:
                    print('most_sum_fav', i+1, end='\t')
            for i, u2 in enumerate(most_sum_ret):
                if user['username'] == u2['username']:
                    print('most_sum_ret', i+1, end='\t')
            print('')
        print('')
        print('Most favorites:')
        for user in most_sum_fav:
            print(user['_id']['userid'], end='\t')
            print(user['username'], end='\t')
            print(user['name'], end='\t')
            print(user['sum_favorite'], end='\t')
            print(user['max_userfollowers_count'], end='\t')
            print(user['tweet_count'], end='\t')
            for i, u2 in enumerate(most_followed):
                if user['username'] == u2['username']:
                    print('most_followed', i+1, end='\t')
            for i, u2 in enumerate(most_tweets):
                if user['username'] == u2['username']:
                    print('most_tweets', i+1, end='\t')
            for i, u2 in enumerate(most_avg_fav):
                if user['username'] == u2['username']:
                    print('most_avg_fav', i+1, end='\t')
            for i, u2 in enumerate(most_avg_ret):
                if user['username'] == u2['username']:
                    print('most_avg_ret', i+1, end='\t')
            for i, u2 in enumerate(most_sum_ret):
                if user['username'] == u2['username']:
                    print('most_sum_ret', i+1, end='\t')
            print('')
        print('')
        print('Most retweets:')
        for user in most_sum_ret:
            print(user['_id']['userid'], end='\t')
            print(user['username'], end='\t')
            print(user['name'], end='\t')
            print(user['sum_retweet'], end='\t')
            print(user['max_userfollowers_count'], end='\t')
            print(user['tweet_count'], end='\t')
            for i, u2 in enumerate(most_followed):
                if user['username'] == u2['username']:
                    print('most_followed', i+1, end='\t')
            for i, u2 in enumerate(most_tweets):
                if user['username'] == u2['username']:
                    print('most_tweets', i+1, end='\t')
            for i, u2 in enumerate(most_avg_fav):
                if user['username'] == u2['username']:
                    print('most_avg_fav', i+1, end='\t')
            for i, u2 in enumerate(most_avg_ret):
                if user['username'] == u2['username']:
                    print('most_avg_ret', i+1, end='\t')
            for i, u2 in enumerate(most_sum_fav):
                if user['username'] == u2['username']:
                    print('most_sum_fav', i+1, end='\t')
            print('')