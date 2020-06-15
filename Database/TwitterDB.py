class TwitterDB:
    instance = None

    def test_connection(self):
        return False

    def create_database(self):
        pass

    def add_twitt(self, twitt):
        pass

    def find_twitts_count(self):
        return None

    def twitt_exists(self, twitt_id):
        return False

    def add_search(self, search):
        pass

    def update_search(self, search):
        pass

    def find_one_search(self, search_id):
        return None

    def find_all_searches(self):
        return []

    def get_tweets_by_username(self, username):
        return []

    def get_all_users(self):
        return []

    def search_exist_by_query(self, query):
        return False

    def get_retweets_graph_edges(self, threshold=10):
        return []

    def save_user(self, user):
        pass

    def add_user(self, user):
        pass

    def exist_user(self, user_id):
        return False

    def update_user(self, user):
        pass

    def find_all_users(self):
        return []

    def find_all_users_with_metrics(self):
        return []

    def find_first_tweet_date(self):
        return None

    def find_last_tweet_date(self):
        return None


