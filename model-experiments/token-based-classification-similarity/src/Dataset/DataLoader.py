"""
Module for loading samples of tokenized source codes 
for constructing dataset for code classifiers and 
similarity checkers
The module has an absract base class for more specialized 
constructors of datasets

Loads tokenized samples of source codes 
corresponding to solution of programming problems.
Each file there contains all samples of 
one class of samples - tokenised source code files

Number of classes (lables) is defined automatically
"""
import sys
import os
import math
from abc import ABC, abstractmethod
import numpy as np
import random
import json
from DsUtilities import *

class WrongToken(Exception):
    """
    Exception on incorrect token
    """
    def __init__(self):
        pass

class SeqOfTokensLoader(ABC):
    """
    Abstract base class of classes for making datasets
    to train bag and sequence of tokens classifiers
    Provides basic functions for child classes

    Child classes should reimplement method makeSample
    transforming sequence of tokens into sample to classify
    """    
    def __init__(self, dir_name, min_n_solutions = 1,
                 problem_list = None, max_n_problems = None,
                 short_code_th = 4, long_code_th = None,
                 report_dir = "./dataset_statistics"):
        """
        Initialize SeqOfTokensLoader with files to process
        
        Parameters:
        - dir_name  -- directory with files of tokenized source code files
        - min_n_solutions -- min number of solutions of problem 
                             required to load that problem
        - problem_list    -- list of problem to process
                             If it is not defined the problem are
                             selected from all tokenized problems
                             using specified criteria
        - max_n_problems  -- number of problems to select from the dataset
                             The problems are selected from 
                             randomly shuffled list of all loaded problems
                             If max_n_problems is None all the specified 
                             problems are selected
        - short_code_th   -- minimum length of code to load
        - long_code_th    -- max length of solution code to load
                             if it is None sys.maxsize is used
        - report_dir      -- directory for writing reports on
                             loaded dataset
        """
        super(SeqOfTokensLoader, self).__init__()
        self.short_code_th = short_code_th
        if long_code_th:
            self.long_code_th = long_code_th
        else:
            self.long_code_th = sys.maxsize
        self.dir_name = dir_name
        self._min_n_solutions = min_n_solutions
        self._max_n_problems = max_n_problems
        self.report_dir = report_dir
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)        
        self.token_set, self.n_token_types = \
                    getTokensInfo(self.dir_name)
        print(f"Loading dataset tokenized with {self.token_set} " +
              f"token set having {self.n_token_types} tokens")
        #Compute list of problems to load
        if problem_list:
            self.problem_list = []
            _all_problems = getProblemSet(self.dir_name, 1, None)
            _all_problems = frozenset(tuple(zip(*_all_problems))[0])
            for _p in problem_list:
                if _p in _all_problems:
                    self.problem_list.append(_p)
                else:
                    print(f"there is no problem {_p} is dataset {self.dir_name}")
        else:
            self.problem_list = getProblemSet(self.dir_name, 
                                              self._min_n_solutions, None)
            self.problem_list, _ = zip(*self.problem_list)
            self.problem_list = list(self.problem_list)
        #Shuffle problems randomly
        DataRand.randUnordered(self.problem_list, "ALL_PROBLEM_SEED")
        if self._max_n_problems:
            if self._max_n_problems > len(self.problem_list):
                sys.exit(f"Cannot select required {self._max_n_problems} " +
                         f"because only {len(self.problem_list)} were loaded")
            #Select random subset of of problem and guarantee reproducebility
            self.problem_list = self.problem_list[: self._max_n_problems]
        #Computed maximum lengh of the code
        self.code_max_length = 0
        #Problem names of constructed dataset in order of their labels
        self.problems = []
        #Dictionary of problems: 
        #key is problem name, 
        #value is a pair <label, number of solutions)
        self.problem_dict = {}
        #Flag of errors in data samples
        self.bad_data = False
        #Dictionaries of problems with too long and too short solutions
        #Key:   problem name
        #Value: list of pairs, where each pair is 
        #       <solution name, its length>
        self._long_solutions = {}
        self._short_solutions = {}

    def _registerSolution(self, reg_dict, name, data):
        """
        Register problem solution
        Parameters:
        - reg_dict  -- dictionary where to register
                       Key: problem name. Value: data
        - name      -- problem name 
        - data      -- solution data
        """
        if name in reg_dict:
            reg_dict[name].append(data)
        else:
            reg_dict[name] = [data]

    def _writeSolutionsLengths(self, reg_dict, fout):
        """
        Print registered problem solutions and their lengths
        Parameters:
        - reg_dict  --  Dictionary with registered problems
                        Key:   problem name
                        Value: list of pairs, where each pair is
                        <solution name, its length>
        - fout      -- file to write
        """
        for _i, _item in enumerate(reg_dict.items()):
            _p, _data = _item
            _line = "{:3d} {:16s}".format(_i + 1, _p)
            _sep = ":"
            for _s, _l in _data:
                _line += f"{_sep} {_s}/{_l}"
                _sep = ","
                if len(_line) > 80:
                    fout.write(_line + '\n')
                    _line = " " * 5
                    _sep = ""
            if len(_line) > 5: fout.write(_line + '\n')

    def loadAllSamples(self):
        """
        Loads tokenized samples of all solutions of programming problems.

        Transforms each sample into bag or sequence of tokens
        Actual transformation is defined with child class
        Makes dataset of them to be used for machine learning

        Prints sizes of shortest solutions of each problem.

        Returns the following items:
        - list of loaded samples, made with makeSample  function
          Currently they are either:
          * bags of tokens or 
          * sequences of tokens of problem solutions
        - list of indices idicating, where sub-arrays of solutions 
          of each problem start and end in the above list
        - list of names of samples i.e. names of problem solutions
        """
        #list of samples (either bags or sequences of tokens)
        _samples = []
        #Names of samples i.e. names of problem solutions
        _sample_names = []
        #List of indices where solutions of problem #i starts/ends
        _problem_solutions  = [] 
        print(f"\nDataset has solutions for the following {len(self.problem_list)} problems:\n")
        print("Problem    Label    N      Aver      Min      Max  Shortest          Longest")
        print("file             samples   size     size     size    code              code")
        _i = 0  #Label counter
        for _problem in self.problem_list:
            _problem_solutions.append(len(_samples))
            try:
                _n_samples, _n_all_tokens, _min_n_tokens, \
                    _max_n_tokens, _short_solution, _long_solution = \
                    self.loadSolutions(_problem, _samples, _sample_names)
            except OSError:
                print(f"Failed to read file of problem {_problem} in directory {self.dir_name}")
                print("Probably the file does not exist")
                self.bad_data = True
                continue
            if not _n_samples:
                print(f"Problem {_problem} has 0 samples loaded")
                self.bad_data = True
                continue
            self.code_max_length = max(self.code_max_length, _max_n_tokens)
            self.problems.append(_problem)
            self.problem_dict[_problem] = (_i, _n_samples)
            print("{:10s}  {:2d}   {:5d}   {:6.1f}   {:6d}   {:6d}  {:16s}  {:16s}".
                  format(_problem, _i, _n_samples,
                         _n_all_tokens / _n_samples,
                         _min_n_tokens, _max_n_tokens,
                         _short_solution, _long_solution))
            _i += 1
        _problem_solutions.append(len(_samples))
        if self.bad_data == True:
            print("Warning: There are errors in data samples")
        print("-----------------------------------------------")
        if len(_samples) < 2 *_i or _i < 2:
            sys.exit(f"Error: Loaded only {len(_samples)} " + 
                     f"solutions of {len(self.problems)} problems")
        print(f"Successfully loaded {len(_samples)} code solutions " +
              f"for {_i} problems")
        print(f"Longest code has {self.code_max_length} tokens\n")
        self.reportWrongLengthCode()
        self.n_labels = len(self.problems)
        return _samples, _problem_solutions, _sample_names

    def reportWrongLengthCode(self):
        """
        Report too long and too short source code files
        """
        if self._short_solutions:
            print(f"There are {len(self._short_solutions)} " + 
                  "too short source code files")
            with open(f"{self.report_dir}/TooShortCode.lst", 'w') as _f:
                self._writeSolutionsLengths(self._short_solutions, _f)
        if self._long_solutions:
            print(f"There are {len(self._long_solutions)} " + 
                  "too long source code files")
            with open(f"{self.report_dir}/TooLongCode.lst", 'w') as _f:
                self._writeSolutionsLengths(self._long_solutions, _f)

    def getPartitionedSampes(self):
        """
        Load tokenized samples of all solutions of programming problems,
        transform each sample into bag or sequence of tokens, 
        Partition whole dataset into sublists of samples corresponding to 
        programming problems
        Returns:
        - list of sub-lists of samples 
          Each sub-list contains samples of one problem
          All sublists are part of the whole list of samples
        - list of sub-lists of sample names i.e. names of 
          problem solutions
          Each sub-list contains sample names of one problem
          All sublists are part of the whole list of sample names
        """
        _samples, _problem_sol_indices, _sample_names = \
            self.loadAllSamples()
        _named_samples = list(zip(_sample_names, _samples))
        _named_probl_sols = \
            [_named_samples[_problem_sol_indices[_i - 1] :
                            _problem_sol_indices[_i]]
             for _i in range(1, len(_problem_sol_indices))]
        #Randomize order of solutions of each problem individually
        DataRand.setSeed("PROBLEM_SOLUTIONS_SEED")
        for _l in _named_probl_sols:
            _l.sort(key = lambda _s: _s[0])
            random.shuffle(_l)
        _sample_names, _samples = zip(*_named_samples)
        _sample_names = list(_sample_names)
        _samples = list(_samples)
        _problems_solutions = \
            [_samples[_problem_sol_indices[_i - 1] :
                      _problem_sol_indices[_i]]
             for _i in range(1, len(_problem_sol_indices))]
        _solution_names = \
            [_sample_names[_problem_sol_indices[_i - 1] :
                           _problem_sol_indices[_i]]
             for _i in range(1, len(_problem_sol_indices))]
        return _problems_solutions, _solution_names

    def getPartitionedSampesOld(self):
        """
        Load tokenized samples of all solutions of programming problems,
        transform each sample into bag or sequence of tokens, 
        Partition whole dataset into sublists of samples corresponding to 
        programming problems
        Returns:
        - list of samples
        - list of sub-lists of samples 
          Each sub-list contains samples of one problem
          All sublists are part of the whole list of samples
        - list of names of samples i.e. names of problem solutions
        """
        _samples, _problem_sol_indices, _sample_names = \
            self.loadAllSamples()
        _named_samples = list(zip(_sample_names, _samples))
        _named_probl_sols = \
            [_named_samples[_problem_sol_indices[_i - 1] :
                            _problem_sol_indices[_i]]
             for _i in range(1, len(_problem_sol_indices))]
        #Randomize order of solutions of each problem individually
        DataRand.setSeed("PROBLEM_SOLUTIONS_SEED")
        for _l in _named_probl_sols:
            _l.sort(key = lambda _s: _s[0])
            random.shuffle(_l)
        _problems_solutions = \
            [_samples[_problem_sol_indices[_i - 1] :
                      _problem_sol_indices[_i]]
             for _i in range(1, len(_problem_sol_indices))]    
        return _samples, _problems_solutions, _sample_names

    def getShuffledLabeledSamples(self):
        """
        Load tokenized samples of all solutions of programming problems,
        transform each sample into bag or sequence of tokens, 
        create samples labels corresponding to the programming problems,
        make shuffled dataset of them to be used for machine learning

        Returns:
        - shuffled list of samples
        - shulled list of labels
        - shuffled list of names of samples,
          i.e. names of problem solutions

        Same shuffling is produced by using same random seed
        """
        _samples, _problem_sol_indices, _sample_names = \
            self.loadAllSamples()
        #Randomize order of solutions of each problem individually
        _named_samples = list(zip(_sample_names, _samples))
        _named_probl_sols = \
            [_named_samples[_problem_sol_indices[_i - 1] :
                            _problem_sol_indices[_i]]
             for _i in range(1, len(_problem_sol_indices))]
        DataRand.setSeed("PROBLEM_SOLUTIONS_SEED")
        for _l in _named_probl_sols:
            _l.sort(key = lambda _s: _s[0])
            random.shuffle(_l)
        _sample_names, _samples = zip(*_named_samples)
        _sample_names = list(_sample_names)
        _samples = list(_samples)
        #Create class labels
        _labels = []
        for _i in range(len(_problem_sol_indices) - 1):
            _labels.extend([_i] * (_problem_sol_indices[_i + 1] - 
                                   _problem_sol_indices[_i]))
        #Randomize all samples, their labels and sample names
        DataRand.randPreordered(_samples, "ALL_SOLUTIONS_SEED")
        DataRand.randPreordered(_labels, "ALL_SOLUTIONS_SEED")
        DataRand.randPreordered(_sample_names, "ALL_SOLUTIONS_SEED")
        return _samples, _labels, _sample_names

    def getShuffledLabeledSamplesOld(self):
        """
        Load tokenized samples of all solutions of programming problems,
        transform each sample into bag or sequence of tokens, 
        create samples labels corresponding to the programming problems,
        make shuffled dataset of them to be used for machine learning

        Returns:
        - shuffled list of samples
        - shulled list of labels
        - shuffled list of names of samples,
          i.e. names of problem solutions

        Same shuffling is produced by using same random seed
        """
        _samples, _problems_solutions, _sample_names = \
            self.getPartitionedSampes()
        _labels = [_j for _j, _solutions 
                   in enumerate(_problems_solutions) 
                   for _ in range(len(_solutions))]
        #Randomize all samples, their labels and sample names
        DataRand.randPreordered(_samples, "ALL_SOLUTIONS_SEED")
        DataRand.randPreordered(_labels, "ALL_SOLUTIONS_SEED")
        DataRand.randPreordered(_sample_names, "ALL_SOLUTIONS_SEED")
        return _samples, _labels, _sample_names

    def loadSolutions(self, problem, samples, sample_names):
        """
        Load tokenized code samples of one class
        i.e. source code files solving one programming problem
        
        The loaded samples are appended to given sample list
        The names of samples i.e. names of problem solutions
        are appended to given list of sample names

        Parameters:
        - problem      -- name of problem to load tokenized solutions
        - samples      -- list to add samples
        - sample_names -- names of samples,
                          i.e. names of problem solutions

        Returns tuple of the following items:
        - number of samples (solutions) loaded
        - total number of tokens in all code samples
        - min number of tokens of code samples
        - max number of tokens of code samples
        - name of shortest solution
        - name of longest solution
        """
        _full_fn = self.dir_name + '/' + problem + ".tkn"
        _short_solution = None
        _long_solution  = None
        with open(_full_fn) as _f:
            _n_solutions = 0
            _n_all_tokens = 0
            _min_n_tokens = sys.maxsize
            _max_n_tokens = 0
            for _line in _f:
                try:
                    _tokens, _solution = self._seqOfTokens(_line)
                    _n_tokens = len(_tokens)
                except WrongToken:
                    print("Failed parsing the tokenization of solution " +
                          f"{_solution} of problem {problem}")
                    print("Tokenized code is: \n", repr(_line))
                    self.bad_data = True
                    continue
                if _n_tokens < self.short_code_th:
                    self._registerSolution(self._short_solutions,
                                    problem, (_solution, _n_tokens))
                    continue
                if _n_tokens > self.long_code_th:
                    self._registerSolution(self._long_solutions,
                                    problem, (_solution, _n_tokens))
                    continue
                _n_solutions += 1
                _n_all_tokens += _n_tokens
                _min_n_tokens = min(_min_n_tokens, _n_tokens)
                if(_min_n_tokens == _n_tokens):
                    _short_solution = _solution
                _max_n_tokens = max(_max_n_tokens, _n_tokens)
                if(_max_n_tokens == _n_tokens):
                    _long_solution  = _solution
                samples.append(self.makeSample(_tokens))
                sample_names.append(_solution)
        return _n_solutions, _n_all_tokens, _min_n_tokens, \
            _max_n_tokens, _short_solution, _long_solution

    #!!!This is used in clustering experiments.
    #!!!However it should be updated to reflect changes in API of self.loadSolutions
    def loadProblem(self, fn):
        """
        Load tokenized code samples of one class
        i.e. source code files solving one programming problem
        Parameters:
        - fn       -- name of problem
        Returns tuple of the following items:
        - list of samples (bags or sequence of tokens) of 
          source code solutions
        - number of samples (solutions) loaded
        - total number of tokens in all code samples
        - min number of tokens of code samples
        - max number of tokens of code samples
        """
        _solutions = []
        _n_solutions, _n_all_tokens, _min_n_tokens, \
            _max_n_tokens, _short_solution = \
            self.loadSolutions(fn + ".tkn", _solutions)
        return _solutions, _n_solutions, _n_all_tokens, \
            _min_n_tokens, _max_n_tokens

    def _seqOfTokens(self, line):
        """
        Load sequence of tokens for solution source code
        Transforms string representation into int
        Parameters:
        - line -- description of solution code of programming task
                  as string in the following form;
                  <name of solution>:<sequence of tokens separtated with ','>
        Returns:
        - sequence of source code tokens
        - name of solution
        """
        _solution, _tokens = line.split(":")
        _tokens = _tokens.split(',')
        try:
            _tokens = list(map(int, _tokens))
        except ValueError:
            print(f"Not all tokens are valid numbers")
            self.bad_data = True
            raise WrongToken()
        if any(_tok >= self.n_token_types for _tok in _tokens):
            print(
                f"Token of source code {_solution} exceeds " +
                f"maximum {self.n_token_types}")
            raise WrongToken(line)
            self.bad_data = True
        return _tokens, _solution

    @abstractmethod
    def makeSample(self, tokens):
        """
        Abstract method for computing data sample 
        from list of tokens
        Parameters:
        - tokens list of tokens as int values
        Returns:
        - data sample as numpy object 
        """
        raise NotImplementedError()

    def problemFromLabel(self, label):
        """
        Get problem name corresponding to a given label
        """
        return self.problems[label]

    def labelFromProblem(self, problem):
        """
        Get label number for a given problem
        """
        return self.problem_dict[problem][0]

    def makeBagOfTokens(self, tokens):
        """
        Compute bag of tokens from list of tokens
        where <bag of tokens> is a vector of tokens frequences

        Parameters:
        - tokens list of tokens as int values
        Returns:
        - bag of tokens as numpy object 
        """
        _code_signature = np.zeros(self.n_token_types,
                                   dtype = np.float32)
        for _tok in tokens:
            _code_signature[_tok] += 1
        _v = math.sqrt(np.dot(_code_signature, _code_signature))
        np.divide(_code_signature, _v, out = _code_signature)
        return _code_signature
#---------------- End of class SeqOfTokensLoader -----------------------------

