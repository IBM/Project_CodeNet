"""
Module with base class for analysis of confusion information
"""
import os
from abc import ABC, abstractmethod
import numpy as np
import sklearn.metrics as metrics

class ConfusionAnalysis(ABC):
    """
    Base class for analysis of confusion information
    It performs intialization common for child classes
    and provides utility functions for them
    """
    @classmethod
    def writeLargeMatrixInt(cls, m, f):
        """
        Write large matrix to file
        Parameters:
        - m      -- matrix to write as numpy array of floats
        - f      -- file to write the matrix
        """
        _n = m.shape[0]
        _s = "     "
        for _i in range(_n):
            _s += "{:5d} ".format(_i)
        f.write(_s + "\n")
        for _i in range(_n):
            _s = "{:3d} ".format(_i)
            for _j in range(_n):
                _s += "{:5d} ".format(m[_i, _j])
            f.write(_s + "\n")

    @classmethod
    def writeLargeMatrixPct(cls, m, f, scale):
        """
        Write large matrix to file
        Parameters:
        - m      -- matrix to write as numpy array of floats
        - f      -- file to write the matrix
        - scale  -- multiplier to scale elements of matrix
        """
        _n = m.shape[0]
        _s = "     "
        for _i in range(_n):
            _s += "{:4d} ".format(_i)
        f.write(_s + "\n")
        for _i in range(_n):
            _s = "{:3d} ".format(_i)
            for _j in range(_n):
                _s += "{:4.1f} ".format(scale * m[_i, _j])
            f.write(_s + "\n")

    def __init__(self, probabilities, labels, solutions, 
                 problems, extreme):
        """
        Initialize base class
        for analysis and reporting confusion information
        Parameters:
        - probabilities - classification probabilities as numpy array
        - labels        - labels of samples as numpy array
        - solutions     - list of sub-lists of file names of problem solutions
                          Each sub-list contains sample names of one problem
                          All sublists are part of the whole list of sample names
        - problems      - list of names of problems
        - extreme       - specification of number of cases to be reported 
                          as extreme ones;
                          * if extreme < 1.0 it is a fraction of number of problems
                          * if extreme >= 1  it is the number of problems  
        """
        super(ConfusionAnalysis, self).__init__()
        self.probabilities = probabilities
        self.labels  = labels
        self._n_samples = self.labels.shape[0]
        self.problems  = problems
        self._n_problems = len(self.problems)
        self.extreme = extreme
        #Number of problems to reports as the best or worst
        self._n_extreme_cases = int(extreme) if extreme >= 1 else \
            max(2, int(extreme * float(self._n_problems)))
        self.solutions = solutions
        #Directory for writing confusion reports to
        self.report_dir = "confusion_report"
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
        #Name of file to write large confusion matrices
        self._conf_mat_fn = "confusion_matrix.lst"
        self.predictions = self.getPredictions()
        self.conf_mat = metrics.confusion_matrix(
            self.labels, self.predictions)

    @abstractmethod
    def getPredictions(self):
        """
        Abstract method for getting classification predictions
        Returns:  classification predictions  
        """
        raise NotImplementedError()
#---------------- End of class  ConfusionAnalysis ----------------------    
