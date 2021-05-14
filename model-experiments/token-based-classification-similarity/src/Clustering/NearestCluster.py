"""
"""
import sys
import os
import math
import numpy as np
from VectorKMeans import VectorsClustered

class NearestClusterClassifier(object):
    """
    """
    def __init__(self, train_samples, val_samples):
        """
        """
        self._val_samples = val_samples
        self._min_n_class_samples = min(map(len, train_samples))
        print("_min_n_class_samples: ", self._min_n_class_samples)
        self._classes = [VectorsClustered(_samples) 
                         for _samples in train_samples]
        self.n_classes = len(self._classes)

    def nClustersTrain(self, n_clusters):
        """
        """
        for _class in self._classes:
            _class.kmeansCluster(n_clusters)

    def scaledClustersTrain(self, n_clusters):
        """
        """
        for _class in self._classes:
            _scale = _class.n_samples // self._min_n_class_samples
            print("Scale: ", _scale)
            _class.kmeansCluster(n_clusters * _scale)
            
    def classify(self, sample):
        """
        """
        _min_d = sys.maxsize
        _classification = None
        for _i, _class in enumerate(self._classes):
            _class_dist = _class.distanceToCenters(sample)
            if _class_dist < _min_d:
                _min_d = _class_dist
                _classification = _i
        return _classification

    def validate(self):
        """
        """
        return self.test(self._val_samples)

    def test(self, val_samples):
        """
        """
        _n_correct_list = []
        _acc_list = []
        _n_val_samples = sum(map(len, val_samples))
        print(_n_val_samples)
        for _i, _val_class_samples in enumerate(val_samples):
            _n_correct = 0
            for _sample in _val_class_samples:
                if _i == self.classify(_sample):
                    _n_correct += 1
            _n_correct_list.append(_n_correct)
            _acc_list.append(float(_n_correct) / 
                             float(len(_val_class_samples)))
        _n_correct = sum(_n_correct_list)
        print("Accuracy of classes: ", _acc_list)
        return float(_n_correct) / float(_n_val_samples)
            
