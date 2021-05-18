"""
Module for constracting dataset of bag of tokens
of problem solutions of source code.

Provides it capability of computing bag of tokens
to parent module TokensClassifDS

Test dataset is not created and is not supported
"""
import sys
import os

import numpy as np
import math
from TokensClassifDS import *

class BagTokDataset(ClassifDSMaker):
    """
    Class for making datasets
    to train bag of tokens classifiers of source code
    Specializes parent class with functions computing bag of tokens
    """
    def __init__(self, dir_name, min_n_solutions = 3,
                 problem_list = None, max_n_problems = None,
                 short_code_th = 4, long_code_th = None,
                 test_part = 0, balanced_split = False):
        """
        Initialize object BagTokDataset with files to process
        
        Parameters:
       - dir_name  -- directory with files of tokenized source code files
        - min_n_solutions -- min number of solutions of problem 
                             required to load that problem
        - problem_list    -- list of problem to process
                             If it is not defined the problem are
                             selected from all tokenized problems
                             using specified criteria
        - max_n_problems  -- maximum number of problems to load
                             If it is None 
                             all the specified problems are loaded
        - short_code_th   -- minimum length of code to load
        - long_code_th     -- max length of solution code to load
                              if it is None sys.maxsize is used
        - test_part       -- fraction of data reserved for test set
        - balanced_split  -- flag to make training/validation/test split
                             of the dateset fully balanced, it means that
                             each problem has the same fraction of solutions
        """
        super(BagTokDataset, self).__init__(
            dir_name, min_n_solutions = min_n_solutions,
            problem_list = problem_list, 
            max_n_problems = max_n_problems,
            short_code_th = short_code_th, 
            long_code_th = long_code_th, test_part = test_part,
            balanced_split = balanced_split)
        #Names and lables of validation samples,
        #computed at the time of validation set construction
        #Required for confusion analysis
        self.val_ds  = None
        self.train_ds = None
        #!!!Used by obsolete function trainValNumPyDs
        self.val_labels = None

    def makeSample(self, tokens):
        """
        Compute bag of tokens from list of tokens
        where <bag of tokens> is a vector of tokens frequences.
        Uses function of parent class

        Parameters:
        - tokens list of tokens as int values
        Returns:
        - bag of tokens as numpy object 
        """
        return self.makeBagOfTokens(tokens)

    #!!! Obsolete function
    def trainValNumPyDs(self, valpart):
        """
        Get training and validation numpy type datasets
        constructed by splitting loaded data set
        Additionally computes names of validation samples
        Parameter:
        - valpart  -- Fraction of dataset samples used for validation
                      as float
        - show     -- Flag to print distribution of sample lables
        Returns:
        - pair of <validation dataset>, <training dataset>
          Each data set is a pair of samples and lables
          in the form of numpy arrays 
        """
        _val_len = int(float(len(self.labels)) * valpart)
        self.labels = np.asarray(self.labels, dtype = np.int32)
        self.samples = np.stack(self.samples)
        _val_ds = self.samples[: _val_len],   \
                  self.labels[: _val_len]
        self.val_labels = _val_ds[1]
        self.val_names = self.sample_names[: _val_len]
        _train_ds = self.samples[_val_len :], \
                    self.labels[_val_len :]
        return _val_ds, _train_ds

    def trainValidDs(self, valpart, batch_size):
        """
        Make training and validation datasets by 
        splitting loaded data set
        Parameters:
        - valpart    -- Fraction of dataset samples used for validation
                        as float
        - batch_size -- size for training dataset
        Returns:
        - <validation dataset>
        - <training dataset>
          Each data set is a pair of samples and lables
          in the form of numpy arrays 
        """
        _train_len, _val_len = self.trainValDsSize(valpart, batch_size)
        self.val_ds = ClassDataset(self, 0, _val_len,
                                   "validation", self.report_dir)
        self.train_ds = ClassDataset(self, _val_len, _train_len,
                                     "training", self.report_dir)
        self.writeLabelDistribution()
        _train_samples, _train_labels, _, _ = self.train_ds.rawDS(batch_size)
        _train_ds = (np.stack(_train_samples),
                     np.asarray(_train_labels, dtype = np.int32))
        _val_samples, _val_labels, _, _ = self.val_ds.rawDS(batch_size)
        _val_ds = (np.stack(_val_samples),
                   np.asarray(_val_labels, dtype = np.int32))
        memoryUsage("After DS made")
        return _val_ds, _train_ds

    def testDS(self, batch_size):
        """
        Make test tf.dataset
        The tf.data.dataset is constructed from_generator
        Parameters:
        - batch_size -- batch size

        Returns:
        - <validation dataset>
        - <test dataset> as a pair of samples and lables 
          in the form of numpy arrays 
        - list of labels
        - list of sample names 
        - list of label names
        """
        if not self.test_ds:
            sys.exit("Cannot make test dataset because it was not defined")
        _samples, _labels, _sample_names, _label_names = \
                                    self.test_ds.rawDS(batch_size)
        _test_ds = (np.stack(_samples),
                     np.asarray(_labels, dtype = np.int32))
        return _test_ds, _labels, _sample_names, _label_names
#---------------- End of class BagOfTokensLoader ---------------------
