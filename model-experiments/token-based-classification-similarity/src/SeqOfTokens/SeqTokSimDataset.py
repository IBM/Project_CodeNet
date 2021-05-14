"""
Module for constracting dataset of sequence of tokens
for similarity analysis
The samples are coded as 2 concatenated vectors 
representing tokens by one-hot coding

Number of classes (lables) is defined automatically

This implementation of does not support creation of test datset 
"""
import sys
import os

import numpy as np
import math
from TokensSimilDS import SimilarityDSMaker

class SeqTokSimilarityDS(SimilarityDSMaker):
    """
    Class for making datasets
    to train source code similarity analyser of sequence of tokens
    Specializes parent class withcomputing sequence of tokens
    """
    def __init__(self, dir_name, min_n_solutions = 1,
                 problem_list = None, max_n_problems = None,
                 short_code_th = 4, long_code_th = None,
                 max_seq_length = None,
                 test = 0):
        """
        Initialize object SeqTokSimilarityDS with files to process
        
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
        super(SeqTokSimilarityDS, self).__init__(
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
        return list(tokens)

    def _fillInSimDataset(self, ds, sample_idx, seq, sol_idx):
        """
        Fill in similarity dataset with one solution
        Parameters:
        - ds          -- numpy array of to fill in with one part 
                         of similary sample
        - sample_idx  -- index of the similarity sample
        - seq         -- sequence of tokens of solution source code
        - sol_idx     -- index of the solution in similarity sample
        """
        _displacement = sol_idx * self.n_token_types
        _l = min(len(seq), self.seq_length)
        for _i, _tok in enumerate(seq[0 : _l]):
            ds[sample_idx, _i, _tok + _displacement] = 1.0
        
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
        _np_ds = np.zeros(shape=(len(samples), self.seq_length, 
                                 self.n_token_types * 2), dtype=np.float32)
        for _i, _s in enumerate(samples):
            _p1_idx, _s1_idx, _p2_idx, _s2_idx = _s
            _seq1 = self.problems_solutions[_p1_idx][_s1_idx]
            _seq2 = self.problems_solutions[_p2_idx][_s2_idx]
            self._fillInSimDataset(_np_ds, _i, _seq1, 0)
            self._fillInSimDataset(_np_ds, _i, _seq2, 1)
        return _np_ds
#---------------- End of class SeqTokSimilarityDS -----------------------------

