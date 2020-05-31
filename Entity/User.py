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
             ):
        if metrics is None:
            metrics = {}
        if original_metrics is None:
            original_metrics = {}
        if metrics_order is None:
            metrics_order = {}
        self.id = id
        self.screen_name = screen_name
        self.category = category
        self.subcategory = subcategory
        self.comment = comment
        self.label = label
        self.metrics = metrics
        self.original_metrics = original_metrics
        self.metrics_order = metrics_order
        if _id is not None:
            self._id = _id

    def get_metrics_as_array(self, metric_keys):
        return [self.metrics[metric_key] for metric_key in metric_keys]
