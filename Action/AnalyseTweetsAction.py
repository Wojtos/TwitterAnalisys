from Action.Action import Action
from Database.TwitterDB import TwitterDB


class AnalyseTweetsAction(Action):
    def __init__(self):
        self.db = TwitterDB.instance
        pass

    def execute(self):
        #tweets = self.db.get_tweets_by_username('Tygodnik NIE')
        #for t in tweets:
        #    print(t['text'])
        by_user = self.db.get_all_users()
        print('Most followed:')
        for user in by_user[:10]:
            for col in user.items():
                print(col, end='\t')
            print('')
        print('Most tweets:')
        for user in sorted(by_user, key=lambda i: i['tweet_count'], reverse=True)[:10]:
            for col in user.items():
                print(col, end='\t')
            print('')
        print('Most favorites:')
        for user in sorted(by_user, key=lambda i: i['avg_favorite'], reverse=True)[:10]:
            for col in user.items():
                print(col, end='\t')
            print('')
        print('Most retweets:')
        for user in sorted(by_user, key=lambda i: i['avg_retweet'], reverse=True)[:10]:
            for col in user.items():
                print(col, end='\t')
            print('')
