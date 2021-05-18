"""
Module for constracting dataset of sequence of tokens
for similarity analysis
Loads tokenized samples of source codes solving programming 
problems and constructs data set of sampleas for similarity 
analysis.
Each sample is a pair of problem solutions.

This implementation of does not support creation of test datset 
"""
import sys
import os
import math

import numpy as np

from TokensSimilDS import SimilarityDSMaker

class SeqTok2WaySimDS(SimilarityDSMaker):
    """
    Class for making datasets
    to train source code similarity analyser 
    by sequence of tokens technique
    Specializes parent class with functions 
    computing sequence of tokens
    """
    def __init__(self, dir_name, min_n_solutions = 1,
                 problem_list = None, max_n_problems = None,
                 short_code_th = 4, long_code_th = None,
                 max_seq_length = None, test = 0):
        """
        Initialize object SeqTok2WaySimDS
        
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
        - test            -- amount of problems reserved for test dataset
                             if test = 0 no problems test dataset is not created
                             if test < 1 it defines fraction of all problems 
                             if test > 1 it defines number of all problems
        """
        super(SeqTok2WaySimDS, self).__init__(
            dir_name, min_n_solutions = min_n_solutions,
            problem_list = problem_list, max_n_problems = max_n_problems,
            short_code_th = short_code_th, long_code_th = long_code_th,
            test = test)
        self.seq_length =  \
            self.code_max_length if max_seq_length is None \
            else max_seq_length        

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

    def _fillInOneHot(self, ds, sample_idx, seq):
        """
        !!!OBSOLETE FUNCTION, RETAINED AS AN EXAMPLE!!!
        Fill in dataset numpy array with one solution
        using one hot coding
        Parameters:
        - ds          -- numpy array of to fill in with one part 
                         of similary sample
        - sample_idx  -- index of the similarity sample
        - seq         -- sequence of tokens of solution source code
        """
        _l = min(len(seq), self.seq_length)
        for _i, _tok in enumerate(seq[0 : _l]):
            ds[sample_idx, _i, _tok] = 1.0

    def _fillInCategorical(self, ds, sample_idx, seq):
        """
        Fill in dataset numpy array with one solution
        using categorical coding
        Parameters:
        - ds          -- numpy array of to fill in with one part 
                         of similary sample
        - sample_idx  -- index of the similarity sample
        - seq         -- sequence of tokens of solution source code
        """
        _l = min(len(seq), self.seq_length)
        for _i, _tok in enumerate(seq[0 : _l]):
            ds[sample_idx, _i] = _tok


    def makeSimDataset(self, samples, labels):
        """
        Make similarity dataset 
        in the form of a pair of numpy arrays
        with one hot token coding of each token and 
        fixed length of sequences
        Parameters:
        - samples             -- list of dataset samples
                                 Each sample is represented as 4-tuple
                                 <problem 1, solution 1, problem 2, solution 2>,
                                 where problems and solutions are their indices
        - labels              -- labels as dummy parameter,
                                 which is not used here
        Returns:
        - list of two datasets in numpy form ready for processing with DNN,
          where each sequence of tokens is an array slice,
          and tokens are represented with one hot coding
        """
        _np_ds1 = np.zeros(shape=(len(samples), self.seq_length), 
                           dtype=np.int32)
        _np_ds2 = np.zeros(shape=(len(samples), self.seq_length), 
                           dtype=np.int32)            
        for _i, _s in enumerate(samples):
            _p1_idx, _s1_idx, _p2_idx, _s2_idx = _s
            _seq1 = self.problems_solutions[_p1_idx][_s1_idx]
            _seq2 = self.problems_solutions[_p2_idx][_s2_idx]
            self._fillInCategorical(_np_ds1, _i, _seq1)
            self._fillInCategorical(_np_ds2, _i, _seq2)
        return [_np_ds1, _np_ds2]
#---------------- End of class SeqTok2WaySimDS -----------------------------

