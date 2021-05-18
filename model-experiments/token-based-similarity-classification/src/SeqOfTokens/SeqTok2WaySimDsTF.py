"""
Module for constracting TF dataset of sequence of tokens
for similarity analysis
Loads tokenized samples of source codes solving programming 
problems and 
constructs data set of samples for similarity analysis.
Each sample is a pair of problem solutions.
"""
import sys
import os
import math

from TokensSimilDS import SimilarityDSMaker
from DoubleSeqTfDS import DoubleSeqTfDataset

class SeqTok2WaySimDsTF(SimilarityDSMaker):
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
                 max_seq_length = None, test = 0,
                 labels01 = True, batch = 512):
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
        - labels01        -- label types flag:
                             True:   0/1 labels
                             Flase:  -1/+1 labels
        - batch           -- batch size for TF dataset
        """
        super(SeqTok2WaySimDsTF, self).__init__(
            dir_name, min_n_solutions = min_n_solutions,
            problem_list = problem_list, max_n_problems = max_n_problems,
            short_code_th = short_code_th, long_code_th = long_code_th,
            test = test, labels01 = labels01)
        self.seq_length =  \
            self.code_max_length if max_seq_length is None \
            else max_seq_length
        self.batch_size = batch

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

    def makeSimDataset(self, samples, labels):
        """
        Make similarity dataset in the form of 
        TensorFlow  Datasets of from_generator type
        Parameters:
        - samples             -- list of dataset samples
                                 Each sample is represented as 4-tuple
                                 <problem 1, solution 1, problem 2, solution 2>,
                                 where problems and solutions are their indices
        - labels              -- labels as numpy array
                                 If labels is None, the dataset is test dataset
        Returns:
        - Tensorflow dataset combined from 
          * two tensorflow datasets representing each sequence of tokens; and
          * tensorflow dataset rezenting labels 
        """
        _seq1 = [self.problems_solutions[_s[0]][_s[1]] for _s in samples]
        _seq2 = [self.problems_solutions[_s[2]][_s[3]] for _s in samples]
        _ds =  DoubleSeqTfDataset.makeDoubleSeqDataset(
            _seq1, _seq2, labels, self.batch_size)
        return _ds
#---------------- End of class SeqTok2WaySimDsTF -------------------------

