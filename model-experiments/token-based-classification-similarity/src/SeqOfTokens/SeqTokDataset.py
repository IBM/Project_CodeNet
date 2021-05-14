"""
Module for constracting dataset for classifying code of problem solution
The problem solutions are represented with sequences of source code tokens

Extends module TokensClassifDS with 
capability of computing samples of sequence of tokens 
"""
import sys
import os

import numpy as np
import math
from TokensClassifDS import ClassifDSMaker

class SeqTokDataset(ClassifDSMaker):
    """
    Class for making datasets
    to train sequence of tokens classifiers
    Specializes parent class with 
    functions computing samples as sequences of tokens
    """
    def __init__(self, dir_name, min_n_solutions = 1,
                 problem_list = None, max_n_problems = None,
                 short_code_th = 4, long_code_th = None,
                 max_seq_length = None, test_part = 0,
                 balanced_split = False):
        """
        Initialize object SeqTokDataset with files to process

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
        - max_seq_length  -- maximum length of token sequences
                             to pad or truncate.
                             If it is none all sequences are padded
                             to maximum length of tokenized code samples.
        - test_part       -- fraction of data reserved for test set   
        - balanced_split  -- flag to make training/validation/test split
                             of the dateset fully balanced, it means that
                             each problem has the same fraction of solutions
        """
        self.seq_length = max_seq_length        
        super(SeqTokDataset, self).__init__(
            dir_name, min_n_solutions = min_n_solutions,
            problem_list = problem_list, 
            max_n_problems = max_n_problems,
            short_code_th = short_code_th, 
            long_code_th = long_code_th,
            test_part = test_part,
            balanced_split = balanced_split)
        
    def makeSample(self, tokens):
        """
        Compute sequence of tokens from list of tokens
        No actual computation requires as the parent class 
        did everything correctly
        Parameters:
        - tokens list of tokens as int values
        Returns:
        - sequence of tokens as python list
        """
        return list(map(lambda _tok: _tok + 1, tokens))

    def _makeOneHot(self, samples):
        """
        Make one hot coding samples
        !!!DEPRECATED FUNCTION RETAINED AS AN EXAMPLE!!!
        Parameters:
        - samples  -- samples as list of sequences of tokens
        Returns:
        - numpy array of samples ready for DNN

        All sequences of tokens are made either of the same length
        by padding and possibly truncating
        """
        _samples = \
            np.zeros(shape=(len(samples), self.seq_length, 
                            self.n_token_types), dtype=np.float32)
        for _i, _seq in enumerate(samples):
            for _j, _tok in enumerate(_seq[0 : min(len(_seq), 
                                                   self.seq_length)]):
                _samples[_i, _j, _tok] = 1.0
        return _samples

    def _makeCategorical(self, samples):
        """
        Make samples with categorical coding 
        Parameters:
        - samples  -- samples as list of sequences of tokens
        Returns:
        - numpy array of samples ready for DNN

        All sequences of tokens are made either of the same length
        by padding and possibly truncating
        """
        _samples = \
            np.zeros(shape=(len(samples), self.seq_length),
                            dtype=np.int32)
        for _i, _seq in enumerate(samples):
            for _j, _tok in enumerate(
                    _seq[0 : min(len(_seq), self.seq_length)]):
                     _samples[_i, _j] = _tok + 1
        return _samples

    def makeShuffledSamples(self, samples):
        """
        Makes shuffled samples (sequence of tokens) ready for DNN

        Parameters:
        - samples  -- samples as list of sequences of tokens
        Returns:
        - numpy array of samples ready for DNN

        All sequences of tokens are made either of the same length
        by padding and possibly truncating
        """
        if self.seq_length is None:
            self.seq_length = self.code_max_length        
        _samples =  self._makeCategorical(samples)
        return _samples
#---------------- End of class BagOfTokensLoader -----------------------------

