"""
"""
import sys
import os
import math
import numpy as np
from sklearn.cluster import KMeans

sys.path.extend(["../BagOfTokens"])
from DatasetLoader import BagOfTokensLoader

def distance(x, y):
    """
    Distance between two vectors
    """
    return np.linalg.norm(x - y)

def sampleToSetDistance(s, sset):
    """
    Distance from sample to set of vectors
    """
    return np.min(np.linalg.norm(sset - s, axis=1))
    
def setSeparation(s1, s2):
    """
    Separation of two sets of vectors
    """
    return min([sampleToSetDistance(s1[_i], s2)
                for _i in range(s1.shape[0])])
#--------------End of utility functions------------------------------

class VectCluster(object):
    """
    Cluster of vectors
    """
    def __init__(self, samples, center = None, inertia = None):
        """   
        """
        self.samples = samples if isinstance(samples, np.ndarray) \
                       else np.stack(samples)
        self.n_samples = self.samples.shape[0]
        self.vect_len = self.samples.shape[1]
        self.centroid = center if center is not None else \
                        self.compCentroid()
        self.inertia = inertia if inertia is not None else \
                       self.compInertia()
        self.rmsRadius = self.compRmsRadius()
        self.max_radius = self.compMaxRadius()
        self.aver_radius = self.compAvrRadius()
        self.diameter = self.compDiameter()

    def getStat(self):
        """
        """
        return (self.n_samples, self.inertia, self.rmsRadius, 
                self.max_radius, self.aver_radius, self.diameter)

    def compCentroid(self):
        """
        """
        _l = self.samples.shape[0]
        _v_dim = self.samples.shape[1]
        _c = np.zeros(_v_dim)
        for _i in range(_v_dim):
            _c[_i] = np.sum(self.samples[:, _i])/_l
        return np.stack(_c)

    def compInertia(self):
        """
        """
        return np.sum(np.linalg.norm(
            self.samples - self.centroid, axis=1) ** 2)

    def compRmsRadius(self):
        """
        """
        return math.sqrt(self.inertia / self.n_samples)

    def compMaxRadius(self):
        """
        """    
        return np.max(np.linalg.norm(
            self.samples - self.centroid, axis=1))

    def compAvrRadius(self):
        """
        """
        #print("Checking np.linalg.norm\n")
        #print(np.linalg.norm(
        #    self.samples - self.centroid, axis=1))
        #print("End of np.linalg.norm\n")
        return np.average(np.linalg.norm(
            self.samples - self.centroid, axis=1))

    def compDiameter(self):
        """
        """
        _d = 0
        for _i in range(self.n_samples):
            _d = max(_d, np.max(np.linalg.norm(
                self.samples - self.samples[_i], axis=1)))
        return _d
#---------------- End of class VectCluster -----------------------------

class SetOfClusters(object):
    """
    """
    def __init__(self, clusters, centers = None, inertia = None):
        """
        """
        self.clusters = \
            [VectCluster(_cluster, center = 
                         centers[_i] if centers is not None else None)
             for _i, _cluster in enumerate(clusters)]
        self.clust_centers = centers if centers is not None \
            else np.stack([_cluster.centroid for _cluster in self.clusters])
        self.n_clusters = len(self.clusters)
 
    def _clustCentersSeparation(self, i, j):
        """
        Distance between centers of two clusters
        """
        return distance(self.clust_centers[i], 
                        self.clust_centers[j])

    def _clustToCenterSeparation(self, i, j):
        """
        Distance from center of one cluster to other cluster
        """
        return sampleToSetDistance(self.clusters[i].centroid,
                                   self.clusters[j].samples)

    def _clustSeparation(self, i, j):
        """
        """
        if self.clusters[i].n_samples > self.clusters[j].n_samples:
            i,j = j,i
        return setSeparation(self.clusters[i].samples,
                             self.clusters[j].samples)

    def printClustCentersDistr(self):
        """
        """
        print("\nDistances between cluster centers")
        print("----------------------------")
        self._printClustersDistr(self._clustCentersSeparation)

    def printClustToCentersDistr(self):
        """
        """
        print("\nDistances between centers of clusters to other clusters")
        print("----------------------------")
        self._printClustersDistr(self._clustToCenterSeparation)

    def printClustersDistr(self):
        """
        """
        print("\nDistances between clusters")
        print("----------------------------")
        self._printClustersDistr(self._clustSeparation)


    def _printClustersDistr(self, dist_func):
        """
        """
        _title = (" " + "   {:2d}" * self.n_clusters). \
                 format(*range(self.n_clusters))
        print(_title + '\n')
        _max_sep = 0
        _min_sep = sys.maxsize
        _avr_sep = 0
        for _i in range(self.n_clusters):
            _line = "{:2d}: ".format(_i)
            for _j in range(self.n_clusters):
                _sep = dist_func(_i, _j)
                _line += "{:4.2f} ".format(_sep)
                _max_sep = max(_max_sep, _sep)
                if _i != _j:
                    _min_sep = min(_min_sep, _sep)
                    _avr_sep += _sep
            print(_line)
        _avr_sep = _avr_sep / float((self.n_clusters - 1) ** 2)
        print("Separations: " + 
              f"min = {_min_sep:.4f}, average = {_avr_sep:.4f}, max = {_max_sep:.4f}\n")

    def printClustersStat(self):
        """
        """
        print("Characteristics of clusters\n") 
        print("Num    N    Inert    RMS    Max    Avr   Diameter")
        print("Clus points        Radius Radius  Radius        \n")
        _big_cluster = None
        _max_size = 0
        _small_cluster = None
        _min_size = sys.maxsize
        _wide_cluster = None
        _max_width = 0
        _compact_cluster = None
        _min_width = float(sys.maxsize)
        for _i, _cluster in enumerate(self.clusters):
            print("{:3d}  {:4d}  {:7.3f}  {:5.3f}  {:5.3f}  {:5.3f}   {:5.3f}".
                  format(_i, *_cluster.getStat()))
            if _max_size < _cluster.n_samples:
                _big_cluster = _i
                _max_size = _cluster.n_samples
            if _min_size > _cluster.n_samples:
                _small_cluster = _i
                _min_size = _cluster.n_samples
            if _max_width < _cluster.diameter:
                _wide_cluster = _i
                _max_width = _cluster.diameter
            if _min_width > _cluster.diameter:
                _compact_cluster = _i
                _min_width = _cluster.diameter
        print(f"Largest cluster #{_big_cluster} has {_max_size} samples")
        print(f"Smallest cluster #{_small_cluster} has {_min_size} samples")
        print(f"Widest cluster #{_wide_cluster} is {_max_width:.4f} wide")
        print(f"Most compact cluster #{_compact_cluster} is {_min_width:.4f} wide")

    def makeClustersStat(self):
        """
        """
        pass
#---------------- End of class SetOfClusters -----------------------------
            
class VectorsClustered(VectCluster):
    """
    Clustered source code of problem solutions 
    """
    def __init__(self, samples):
        """
        """
        super(VectorsClustered, self).__init__(samples)
        self._random_seed = 0

    def kmeansCluster(self, n_clusters):
        """
        Cluster samples into n clusters
        Parameters:
        - n  -- number of clusters
        """
        _kmeans = KMeans(n_clusters = n_clusters, 
                         random_state =
                         self._random_seed).fit(self.samples)
        self._kmeans_inertia = _kmeans.inertia_
        self.clust_centers = _kmeans.cluster_centers_
        self.n_clusters = n_clusters
        self.labels = _kmeans.labels_
        self.clusters = SetOfClusters(self.clustersFromLabels(),
                                      self.clust_centers)

    def clustersFromLabels(self):
        """
        """
        _cluster_list = [[] for _in in range(self.n_clusters)]
        for _i in range(self.n_samples):
            _cluster_list[self.labels[_i]].append(self.samples[_i])
        return _cluster_list
            
    def printClustersStat(self):
        """
        """
        self.clusters.printClustersStat()
        self.clusters.printClustCentersDistr()
        self.clusters.printClustToCentersDistr()
        self.clusters.printClustersDistr()

    def printClustCenters(self):
        """
        """
        print("Centers of clusters\n", self.clusters.clust_centers)

    def distanceToCenters(self, sample):
        """
        """
        return sampleToSetDistance(sample, self.clust_centers)
#---------------- End of class SolutionsClustered -----------------------------
