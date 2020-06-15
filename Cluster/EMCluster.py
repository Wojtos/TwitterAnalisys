from sklearn.mixture import GaussianMixture

from Cluster.Cluster import Cluster
from sklearn.cluster import KMeans


class EMCluster(Cluster):
    def fit(self, user_metrics):
        em = GaussianMixture(n_components=self.clusters_amount)
        return em.fit_predict(user_metrics)

    def get_name(self):
        return GaussianMixture.__name__
