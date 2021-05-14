"""
Module for constructing dataset for similarity analysis
by bag of tokens technique.

Loads tokenized samples of source codes 
corresponding to solution of programming problems.
Each file there contains all samples of 
one class of samples - tokenised source code files

Number of classes (lables) is defined automatically
"""
import sys
import os

import numpy as np
import math
import random

from TokensSimilDS import SimilarityDSMaker

class BagTokSimilarityDS(SimilarityDSMaker):
    """
    Dataset maker for source coode similarity analyser
    using Bag of Tokens technique

    Loads files of tokenized source code files from the given directory and
    Prepares data set for simple Bag or Tokens code similarity detector
    """
    def __init__(self, dir_name, min_n_solutions = 1,
                 problem_list = None, max_n_problems = None,
                 short_code_th = 4, long_code_th = None, test = 0):
        """
        Initize Dataset maker
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
        - test            -- amount of problems reserved for test dataset
                             if test = 0 no problems test dataset is not created
                             if test < 1 it defines fraction of all problems 
                             if test > 1 it defines number of all problems
        """
        super(BagTokSimilarityDS, self).__init__(
            dir_name, min_n_solutions = min_n_solutions,
            problem_list = problem_list, max_n_problems = max_n_problems,
            short_code_th = short_code_th, long_code_th = long_code_th,
            test = test)

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

    '''
    !!!Obsolete function. Delete after confirming.
    def completeSimilDataset(self, ds):
        """
        Complete similarity dataset
        by converting it from compact pythonic form to 
        numpy array
        Parameters: 
        - ds -- list of data samples,
                 where data sample is a concatenated pair of bag of tokens,
        Returns: 
        - numpy array of input list items
        """
        return np.stack(ds)
    '''

    def makeSimDataset(self, samples, labels):
        """
        Make similarity dataset in the form of numpy array
        Parameters:
        - samples             -- list of dataset samples
                                 Each sample is represented as 4-tuple
                                 <problem 1, solution 1, problem 2, solution 2>,
                                 where problems and solutions are their indices
        - labels              -- labels as dummy parameter,
                                 which is not used here
        Returns:
        numpy array of the constructed dataset
        """
        _np_ds = np.zeros(shape=(len(samples), self.n_token_types * 2))
        for _i, _s in enumerate(samples):
            _p1_idx, _s1_idx, _p2_idx, _s2_idx = _s
            _np_ds[_i] = \
                np.concatenate((self.problems_solutions[_p1_idx][_s1_idx],
                                self.problems_solutions[_p2_idx][_s2_idx]))
        return _np_ds    
#---------------- End of class BagTokSimilarityDS -----------------------------
