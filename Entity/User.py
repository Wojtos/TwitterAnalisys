class User:
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
        self.id = id
        self.screen_name = screen_name
        self.category = category
        self.subcategory = subcategory
        self.comment = comment
        self.label = label
        self.metrics = metrics
        self.original_metrics = original_metrics
        self.metrics_order = metrics_order
        self.date_split_metrics = date_split_metrics
        self.date_split_original_metrics = date_split_original_metrics
        if _id is not None:
            self._id = _id

    def get_metrics_as_array(self, metric_keys):
        return [self.metrics[metric_key] for metric_key in metric_keys]

    def add_date_split_metrics(self, period_name, date_split_name, value):
        if period_name not in self.date_split_metrics:
            self.date_split_metrics[period_name] = {}
        self.date_split_metrics[period_name][date_split_name] = value

    def add_date_split_original_metrics(self, period_name, date_split_name, value):
        if period_name not in self.date_split_original_metrics:
            self.date_split_original_metrics[period_name] = {}
        self.date_split_original_metrics[period_name][date_split_name] = value
