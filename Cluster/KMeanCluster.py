from Cluster.Cluster import Cluster
from sklearn.cluster import KMeans


class KMeanCluster(Cluster):
    def fit(self, user_metrics):
        kmeans = KMeans(n_clusters=self.clusters_amount)
        return kmeans.fit_predict(user_metrics)

    def get_name(self):
        return KMeans.__name__
