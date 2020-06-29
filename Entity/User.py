class User:
    unique_periods = [
        '04.03.2020 - 11.03.2020',
        '11.03.2020 - 18.03.2020',
        '18.03.2020 - 25.03.2020',
        '25.03.2020 - 01.04.2020',
        '01.04.2020 - 08.04.2020',
        '08.04.2020 - 15.04.2020',
        '15.04.2020 - 22.04.2020',
        '22.04.2020 - 29.04.2020',
        '29.04.2020 - 06.05.2020',
        '06.05.2020 - 13.05.2020',
        '13.05.2020 - 20.05.2020',
        '20.05.2020 - 27.05.2020',
        '27.05.2020 - 03.06.2020'
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
    def __init__(self,
                 id,
                 screen_name=None,
                 category=None,
                 subcategory=None,
                 comment=None,
                 _id=None,
                 metrics=None,
                 label=None,
                 original_metrics=None,
                 metrics_order=None,
                 date_split_metrics=None,
                 date_split_original_metrics=None,
                 labels=None
             ):
        if metrics is None:
            metrics = {}
        if original_metrics is None:
            original_metrics = {}
        if metrics_order is None:
            metrics_order = {}
        if date_split_metrics is None:
            date_split_metrics = {}
        if date_split_original_metrics is None:
            date_split_original_metrics = {}
        if 'weeks' not in date_split_original_metrics:
            date_split_original_metrics['weeks'] = {}
        for period in self.unique_periods:
            if period not in date_split_original_metrics['weeks']:
                date_split_original_metrics['weeks'][period] = {}
                for key in self.NON_GRAPH_METRIC_KEYS:
                    date_split_original_metrics['weeks'][period][key] = 0
        if labels is None:
            labels = {}
        self.id = id
        self.screen_name = screen_name
        self.category = category
        self.subcategory = subcategory
        self.comment = comment
        self.label = label
        self.labels = labels
        self.metrics = metrics
        self.original_metrics = original_metrics
        self.metrics_order = metrics_order
        self.date_split_metrics = date_split_metrics
        self.date_split_original_metrics = date_split_original_metrics
        if _id is not None:
            self._id = _id

    def get_metrics_as_array(self, metric_keys):
        return [self.metrics[metric_key] for metric_key in metric_keys]

    def get_original_metrics_as_array(self, metric_keys):
        return [self.original_metrics[metric_key] for metric_key in metric_keys]

    def get_date_split_metrics_as_array(self, metric_keys):
        if self.date_split_metrics == None:
            return None
        return [[self.date_split_metrics['weeks'][week[0]][metric_key] for metric_key in week[1]] for week in self.date_split_metrics['weeks'].items()]

    def get_date_split_original_metrics_as_array(self, metric_keys):
        if self.date_split_original_metrics == None:
            return None
        return [[self.date_split_original_metrics['weeks'][week[0]][metric_key] for metric_key in week[1]] for week in self.date_split_original_metrics['weeks'].items()]

    def get_user_weeks(self):
        if self.date_split_original_metrics == None:
            return None
        return self.date_split_metrics['weeks'].keys()
    def add_date_split_metrics(self, period_name, date_split_name, value):
        if period_name not in self.date_split_metrics:
            self.date_split_metrics[period_name] = {}
        self.date_split_metrics[period_name][date_split_name] = value

    def add_date_split_original_metrics(self, period_name, date_split_name, value):
        if period_name not in self.date_split_original_metrics:
            self.date_split_original_metrics[period_name] = {}
        self.date_split_original_metrics[period_name][date_split_name] = value
