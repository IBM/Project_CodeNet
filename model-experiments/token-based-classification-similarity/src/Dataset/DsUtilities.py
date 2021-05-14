"""
Module of utility functiosn and constants for Dataset functionality
"""
import sys
import os
import math
from abc import ABC, abstractmethod
import numpy as np
import random
import json
import tensorflow as tf

def getProblemSet(ds, n_solutions_th, max_n_problems):
    """
    Get list of problems satisfying required criteria:
    - number of solutions is not less than threshold
    - number of problems is not more than required
    Parameters:
    - ds             - directory with tokenized dataset
    - n_solutions_th - min number of solutions required for 
                       selecting problems
    - max_n_problems - max number of problems to return
                       If it is None or 0 return all problems 
                       with sufficiently many solutions
    Returns: Sorted list of pairs:
             <problem, number of its solutions>,
             sorted according to the number of problem solutions
             If there are more problems with required number of 
             solutions, the problems with more solutions are returned
    """
    _problem_data = f"{ds}/problems.json"
    if not os.path.exists(_problem_data):
        sys.exit(f"File {_problem_data} " + 
                 "with a list of problems is not found")
    with open(_problem_data, 'r') as _problem_json:
        _all_problems = json.load(_problem_json)
    _problems = [_p for _p in _all_problems.items() 
                 if int(_p[1]) >= n_solutions_th]
    if _problems:
        _problems.sort(key = lambda _x: int(_x[1]), reverse=True)
        if max_n_problems:
            _problems = _problems[: max_n_problems]
    return _problems

def getTokensInfo(ds):
    """
    Get name of the token set and number of tokens used
    for tokenization of problem solutions
    Parameters:
    - ds             - directory with tokenized dataset
    Returns:
    - Name of token set
    - Number of tokens
    """
    _info_fn = f"{ds}/info.json"
    with open(_info_fn, 'r') as _info_json:
        _info = json.load(_info_json)
    return _info["token_set"], _info["n_tokens"]

def makeShardOptions(policy = "OFF"):
    """
    Make Dataset options: 
    currently they are chard options for multi GPU mode
    Parameters:
    - policy  -- policy to shard dataset:
                 * "OFF"    -- AutoShardPolicy.OFF
                * "DATA" -- AutoShardPolicy.DATA
Returns: dataset options
    """
    #Setting TF sharding policy for multi GPU mode. 
    #It should be either OFF or DATA
    _options = tf.data.Options()
    if policy == "OFF":
        _options.experimental_distribute.auto_shard_policy = \
            tf.data.experimental.AutoShardPolicy.OFF
    elif policy == "DATA":
        _options.experimental_distribute.auto_shard_policy = \
            tf.data.experimental.AutoShardPolicy.OFF
    else:
        sys.exit(f"Invalid shard policy {policy}")
    return _options
#------------- End of utility functions -------------------

class DataRand:
    """
    Class for randomization of data samples
    Provides random seeds for randomization of datasets
    """

    #Random seeds for repeatable randomization of data samples
    #Seed for random shaffling all problems
    seeds ={
        #Shuffle list of problems
        "ALL_PROBLEM_SEED": 1812, #+ 1001,
        #Shuffle solutions of each problem
        "PROBLEM_SOLUTIONS_SEED": 1870,
        #Shuffle all solution samples
        "ALL_SOLUTIONS_SEED": 1905,
        #Make similarity training dataset
        "SIMIL_TRAIN_DS_SEED": 1917,
        #Make similarity validation dataset
        "SIMIL_VALID_DS_SEED": 1937,
        #Make similarity test dataset
        "SIMIL_TEST_DS_SEED":  1941,
        #Shuffle balanced test datsset
        "TEST_SHUFFLE_SEED" :  1945,
        #Shuffle balanced validation dataset seed
        "VALID_SHUFFLE_SEED":  1961,
        #Shuffle balanced training dataset seed
        "TRAIN_SHUFFLE_SEED":  1980}

    @classmethod
    def setDsSeeds(cls, seed):
        """
        Setup all seeds used in dataset construction
        Function should be executed only once before making all datasets
        Parameters:
        - seed   -- starting value of all dataset related seeds
        """
        for _k in cls.seeds.keys():
            cls.seeds[_k] += seed
        
    @classmethod
    def setSeed(cls, seed_name):
        """
        Set seed for current randomization procedure
        Parameters:
        - seed_name  -- name of the seed
        """
        random.seed(cls.seeds[seed_name])

    @classmethod
    def randPreordered(cls, l, seed):
        """
        Randomize list of ordered elements by shuffling it in place
        It is assumed that the elements are in order 
        which is the same for all runs
        Parameters:
        l    -- list of elements 
                usually names of problems or solutions)
        seed -- name of the predefined seed for random shuffling 
        """
        _state = random.getstate()
        random.seed(cls.seeds[seed])
        random.shuffle(l)
        random.setstate(_state)
    
    @classmethod
    def randUnordered(cls, l, seed):
        """
        Randomize list of unordered elements by shuffling it in place
        It is assumed that the elements are in some random order,
        which need not be the same from run to run
        Therefroe for repeatability it is required to order them
        Parameters:
        l    -- list of unordered elements
        seed -- name of the predefined seed for random shuffling 
        """
        l.sort()
        cls.randPreordered(l, seed)
        
        
