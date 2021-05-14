"""
Module for making dataset for similarity detection of 
of source codes by sequence or bag of tokens technique

Has two operation modes:
- Validiation on solutions of the same problems
- Valdiation on solutions of the problems different from 
  the ones seen at training
However, test datset is always constructed from the problems
that were used neither for training nor validation.

Loads tokenized samples of source codes 
corresponding to solution of programming problems.
Each file there contains all samples of 
one class of samples - tokenised source code files

The module has an absract base class for more specialized 
constructors of datasets
"""
import sys
import os
from abc import ABC, abstractmethod

import numpy as np
import math
import random
import csv

from DataLoader import SeqOfTokensLoader
from DsUtilities import DataRand

class SimilarityDSMaker(SeqOfTokensLoader):
    """
    Abstract class for making dataset for 
    source code similarity analysis by bag or sequence of Tokens technique

    Loads files of tokenized source code files from the given directory and
    Prepares datasets for Bag or Sequence Tokens code similarity detector
    Test datset is always constructed for problems that are not used 
    either for training or validation
    """
    def __init__(self, dir_name, min_n_solutions = 1,
                 problem_list = None, max_n_problems = None,
                 short_code_th = 4, long_code_th = None,
                 test = 0, labels01 = True):
        """
        Initialize Dataset maker
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
        - long_code_th    -- max length of solution code to load
                              if it is None sys.maxsize is used
        - test            -- amount of problems reserved for test dataset
                             if test = 0 no problems test dataset is not created
                             if test < 1 it defines fraction of all problems 
                             if test > 1 it defines number of all problems
        - labels01        -- label types flag:
                             True:   0/1 labels
                             Flase:  -1/+1 labels
        """
        super(SimilarityDSMaker, self).__init__(
            dir_name, min_n_solutions = min_n_solutions,
            problem_list = problem_list, max_n_problems = max_n_problems,
            short_code_th = short_code_th, long_code_th = long_code_th)
        self.labels01 = labels01
        #Size of the array used for selection of problem solutions
        #with probabilities proportional to the number 
        #of each problem solutions
        self.problems_solutions, self.solution_names = \
                                    self.getPartitionedSampes()
        self.n_problems = len(self.problems_solutions)
        self.n_test_problems = int(float(self.n_problems) * test) \
                               if test < 1 else int(test)
        if test and self.n_test_problems == 1:
            sys.exit(f"Too few {test} problems for test dataset")
        #Reserve problems for test dataset
        self.n_tran_ds_problems = self.n_problems - self.n_test_problems
        if self.n_test_problems > 0:
            self.test_problems = self.problems[-self.n_test_problems :]
            self.writeProblemList(self.test_problems, 
                                  "test_problems.txt")
            self.train_ds_problems = \
                    self.problems[: -self.n_test_problems]
            self.test_problem_solutions = \
                    self.problems_solutions[-self.n_test_problems :]
            self.train_ds_probl_solutions = \
                    self.problems_solutions[: -self.n_test_problems]
            print(f"Dataset of {self.n_problems} problems is split "+ 
                  f"into {self.n_test_problems} and " + 
                  f"{self.n_tran_ds_problems} for test and training with validation")
        else:
            self.test_problems = None
            self.train_ds_problems = self.problems
            self.test_problem_solutions = None
            self.train_ds_probl_solutions = self.problems_solutions
            print("No test dataset was defined")
        self._SEL_SIZE = 128 * 1024
        self.writeProblemList(self.train_ds_problems, 
                              "train_valid_problems.txt")
        self.writeProblemList(self.problems, "all_problems.txt")

    def trainValidDsSameProblems(self, val_train_split,
                                 val_size, train_size,
                                 similar_part):
        """
        Make datasets for training source code similarity analyser
        Both training and validation parts of dataset are made.

        The validation part is made from solutions of the same 
        problems that were used for making the training part 
        of the dataset.
        However, the test dataset is made from solutions of 
        the problems different from ones used here for training 
        and validation

        The function provides the following:
        - No same code samples (problem solutions) are used 
          for creation both validation and training datasets
        - Each problem is represented in both created datasets
          with the same fraction of its code samples
        - Number of samples of similar solutions of each problem
          is proportional to the number of all pairs of solutions 
          of that problem.
        - All pairs of similar solutions are constructed from
          different samples, i.e. no pair has same solution.
          No self similar solution is constructed.
          !!!Possibly this condition should be parameterized.
        - Pairs of dissimilar solutions are constructed such as
          each problem is selected with the probability 
          proportional to the number of its solutions.
        Similar samples are constructed as pairs of solutions
        of the same problem
        Dissimilar samples are constructed as pairs of solution
        of different problems
        Samples of each problem solutions are splitted individually.
        The obtained subsets of are used for constructing training 
        and validation datasets.

        Parameters:
        - val_train_split  -- Fraction of training samples that is used 
                              for constructing validation dataset.
                              It speciified as float
                              Samples of each problem solutions are splitted 
                              individually according to this parameters
        - val_size         -- Size of validation dataset to create
        - train_size       -- Size of training dataset to create
        - similar_part     -- Fraction of samples of the created dataset 
                              representing similar source code samples
        Returns:
        - validation and training datasets:
        Each of them has the following items:
        - constructed dataset 
          * either as single numpy array 
          * or list of 2 them 
          * or TF dataset
        - labels as numpy array
        - list of similarity samples in form of 4-tuples
          <problem1, solution1, problem2, solution2>
        """
        print("Constructing training and validation datasets " + 
              "from different solutions of the same problems")
        _val_problem_solutions = \
            [_solutions[: int(float(len(_solutions)) * 
                                   val_train_split)] 
             for _solutions in self.train_ds_probl_solutions]
        _train_problem_solutions = \
            [_solutions[int(float(len(_solutions)) * 
                                 val_train_split) :] 
             for _solutions in self.train_ds_probl_solutions]
        DataRand.setSeed("SIMIL_TRAIN_DS_SEED")
        self.train_ds = self._makeDs(0, _train_problem_solutions,
                                     train_size, similar_part)
        DataRand.setSeed("SIMIL_VALID_DS_SEED")
        self.val_ds = self._makeDs(0, _val_problem_solutions,
                                   val_size, similar_part)
        self.reportDatasetStatistics(0, self.n_tran_ds_problems, 
                                     self.val_ds[2], 
                                     0, self.n_tran_ds_problems, 
                                     self.train_ds[2])
        return self.val_ds, self.train_ds

    def trainValidDsDifferentProblems(self, val_train_split,
                                      val_size, train_size,
                                      similar_part):
        """
        Make datasets for training source code similarity analyser

        Both training and validation parts of dataset are made.

        The validation part is made from solutions of different 
        problems that were used for making the training part 
        of the dataset.
        Validation uses the problems of the beginning of the list
        Training uses problems that are between validation and test ones

        The function provides the following:
        - No same code samples (problems) are used 
          for creation both validation and training datasets
        - Validation and training datasets are created from 
          solutions of different problems
        - Number of samples of similar solutions of each problem
          is proportional to the number of all pairs of solutions 
          of that problem.
        - All pairs of similar solutions are constructed from
          different samples, i.e. no pair has same solution.
          No self similar solution is constructed.
          !!!Possibly this condition should be parameterized.
        - Pairs of dissimilar solutions are constructed such as
          each problem is selected with the probability 
          proportional to the number of its solutions.
        Similar samples are constructed as pairs of solutions
        of the same problem
        Dissimilar samples are constructed as pairs of solution
        of different problems
        All problem solutions are splitted for ones used 
        for training and ones used for validation. The solutions 
        of the resulted subsets of problems are used for 
        constructing training and validation datasets.

        Parameters:
        - val_train_split  -- Fraction of original probles used 
                              for constructing validation dataset.
                              It speciified as float
                              Set of all problem is splitted according
                              to this parameters
        - val_size         -- Size of validation dataset to create
        - train_size       -- Size of training dataset to create
        - similar_part     -- Fraction of samples of the created dataset 
                              representing similar source code samples
        Returns:
        - validation and training datasets:
        Each of them has the following items:
        - constructed dataset 
          * either as single numpy array 
          * or list of 2 them 
          * or TF dataset
        - labels as numpy array
        - list of similarity samples in form of 4-tuples
          <problem1, solution1, problem2, solution2>
        """
        print("Constructing training and validation datasets " + 
              "from solutions of different problems")
        _n_val_probls = int(float(self.n_tran_ds_problems) * 
                            val_train_split)
        print(f"Validation and training use {_n_val_probls} " + 
              f"and {self.n_tran_ds_problems - _n_val_probls} problems respectively")
        if _n_val_probls < 2 or self.n_tran_ds_problems - _n_val_probls < 2:
            sys.exit(f"Too few problems for training " + 
                     f"{self.n_tran_ds_problems - _n_val_probls} " + 
                     f"or validation {_n_val_probls}")
        _val_problem_solutions = \
                self.train_ds_probl_solutions[: _n_val_probls]
        _train_problem_solutions = \
                self.train_ds_probl_solutions[_n_val_probls :]
        self.writeProblemList(self.train_ds_problems[: _n_val_probls],
                              "validation_problems.txt")
        self.writeProblemList(self.train_ds_problems[_n_val_probls :],
                              "training_problems.txt")
        DataRand.setSeed("SIMIL_VALID_DS_SEED")
        self.val_ds = self._makeDs(0, _val_problem_solutions,
                                   val_size, similar_part)
        DataRand.setSeed("SIMIL_TRAIN_DS_SEED")
        self.train_ds = self._makeDs(_n_val_probls,
            _train_problem_solutions, train_size, similar_part)
        self.reportDatasetStatistics(0, _n_val_probls, self.val_ds[2], 
            _n_val_probls, self.n_tran_ds_problems - _n_val_probls, 
            self.train_ds[2])
        self.writeSamplesCsv(self.val_ds[2], "val_samples.csv")
        self.writeSamplesCsv(self.train_ds[2], "train_samples.csv")
        return self.val_ds, self.train_ds

    def testDataset(self, size, similar_part):
        """
        Make test dataset
        Test datset is always constructed from problems different 
        from ones used for training and validation
        It uses the last problems in the list
        More details are in comments to self.trainValidDsDifferentProblems

        Parameters:
        - size         -- Size of dataset to create
        - similar_part -- Fraction of samples of the created dataset 
                          representing similar source code samples
        Returns:
        - Test datasets having the following items:
        - constructed dataset 
          * either as single numpy array 
          * or list of 2 them 
          * or TF dataset
        - labels as numpy array
        - list of similarity samples in form of 4-tuples
          <problem1, solution1, problem2, solution2>
        """
        print("Constructing test dataset")
        if not self.test_problem_solutions:
            sys.exit("Test datset cannot be created as it was not defined.")
        DataRand.setSeed("SIMIL_TEST_DS_SEED")
        _start_problem = self.n_problems - self.n_test_problems
        self.test_ds = self._makeDs(_start_problem,
                        self.test_problem_solutions, size, similar_part) 
        with open(f"{self.report_dir}/TestDatasetStatistics.lst", 'w') as _f:
            _f.write("PROBLEM DISTRIBUTION IN TEST DATASET\n")
            self.writeProblemDistribution(_start_problem, 
                            self.n_test_problems, self.test_ds[2], _f)
        self.writeSamplesCsv(self.test_ds[2], "test_samples.csv")
        return self.test_ds

    def _makeDs(self, start_problem, problems_solutions,
                size, similar_part):
        """
        Make a dataset for source code similarity analyser
        Parameters:
        - start_problem      -- index of fist problem to use for samples 
        - problems_solutions -- source code problems solutions used
                                for constructing the dataset
        - size               -- Size of dataset to create
        - similar_part       -- Fraction of samples of the created dataset 
                                representing similar source code samples
        Returns:
        - constructed dataset 
          * either as single numpy array 
          * or list of 2 them 
          * or TF dataset
        - labels as numpy array
        - list of similarity samples in form of 4-tuples
          <problem1, solution1, problem2, solution2>
        """
        _annotations = []  #Similarity samples to construct
        _n_similar = int(float(size) * similar_part)

        #Add samples with similar solutions
        self._addSimilarSamples(_annotations, start_problem, 
                                problems_solutions,_n_similar)
        _n_similar_solutions = len(_annotations)
        self._addDisSimilarSamples(_annotations, start_problem, 
                                   problems_solutions,
                                   size - _n_similar_solutions)
        _n_samples = len(_annotations)
        _n_dissimilar_solutions = _n_samples - _n_similar_solutions
        random.shuffle(_annotations)
        _labels  = self._makeLabels(_annotations)
        _samples = self.makeSimDataset(_annotations, _labels)
        print(f"Similarity dataset of {_n_samples} samples is ready")
        print(f"Dataset has {_n_similar_solutions} samples with similar solutions" + 
              f" and {_n_dissimilar_solutions} samples with dissimilar solutions")
        return (_samples, _labels, _annotations)

    def _addSimilarSamples(self, ds, start_problem, problems_solutions, 
                           size):
        """
        Add samples with similar solutions of the problems
        to the given dataset
        Parameters:
        - ds                 -- dataset for adding samples to
        - start_problem      -- index of fist problem to use for samples
        - problems_solutions -- source code solutions for constructing 
                                samples of similar solutions
        - size               -- Size of dataset to create  
        """
        #Number of all pairs of similar solutions that can be constructed 
        #from the given data
        _n_pairs = \
            float(sum(map(lambda _array: len(_array) * (len(_array) -1), 
                          problems_solutions)))
        for _p, _solutions in enumerate(problems_solutions):
            if len(_solutions) <= 1:
                continue     #Cannot make any pair from 1 or 0 items
            #Number of pairs of similar solutions that can be constructed
            #from solutions of this problem
            _n_samples = \
                int((float(size) * 
                     float(len(_solutions) * (len(_solutions) -1)) / 
                     _n_pairs))
            for _i in range(_n_samples):
                while True:
                    _s1_idx = random.randint(0, len(_solutions) - 1)
                    _s2_idx = random.randint(0, len(_solutions) - 1)
                    if _s1_idx != _s2_idx: break
                _sample_annot = (start_problem + _p, _s1_idx, 
                                 start_problem + _p, _s2_idx)
                ds.append(_sample_annot)

    def _addDisSimilarSamples(self, ds, start_problem, 
                              problems_solutions, size):
        """
        Expand the given dataset with pairs of dissimilar solutions 
        Parameters:
        - ds                 -- dataset for adding samples to
        - start_problem      -- index of fist problem to use for samples
        - problems_solutions -- source code solutions for constructing 
                                samples of similar solutions
        - size               -- Size of dataset to create   
        """
        #Total number of problem solution
        _n_solutions = float(sum(map(len, problems_solutions)))
        #Probabilities of random selection of each problem solution
        _probl_probabilities = [float(len(_s)) / _n_solutions 
                                for _s in problems_solutions]
        #Utility array for selection of problem solutions with
        #probabilities proportional to the number of solutions
        #of each problem
        _selection = np.zeros(self._SEL_SIZE, dtype = int)
        _curr_probl_idx = 0
        for _i, _p in enumerate(_probl_probabilities):
            _next_probl_idx = int(float(_curr_probl_idx) + 
                                  _p * float(self._SEL_SIZE))
            _selection[_curr_probl_idx :_next_probl_idx] = _i
            _curr_probl_idx = _next_probl_idx
        _selection[_curr_probl_idx :] = _i
        #Constructing pairs of solutions of different problems
        for _ in range(size):
            #Select pair of different problems
            #with probabilities proportional to the number
            #of their solutions
            while True:
                _rand_idx = random.randint(0, self._SEL_SIZE - 1)
                _p1_idx = _selection[_rand_idx]
                _rand_idx = random.randint(0, self._SEL_SIZE - 1)
                _p2_idx = _selection[_rand_idx]
                #_p1_idx = random.choice(_selection)
                #_p2_idx = random.choice(_selection)
                if _p1_idx != _p2_idx: break
            _solutions1 = problems_solutions[_p1_idx]
            _solutions2 = problems_solutions[_p2_idx]
            #Selection of solution of each problem selected
            _s1_idx = random.randint(0, len(_solutions1) - 1)
            _s2_idx = random.randint(0, len(_solutions2) - 1)
            _sample_annot = (start_problem + _p1_idx, _s1_idx, 
                             start_problem + _p2_idx, _s2_idx)
            ds.append(_sample_annot)

    def _makeLabels(self, annotations):
        """
        Make lables from set of similarity samples
        Parameters:
        - annotations  -- list of similarity samples in form of 4-tuples
                          <problem1, solution1, problem2, solution2>
        Returns:
        - numpy array of lables
        """
        _dissimilar = 0 if self.labels01 else -1
        return np.asarray(tuple(map(
            lambda _a: 1 if _a[0] == _a[2] else _dissimilar,
            annotations)), dtype=np.int32) 
        
    def reportDatasetStatistics(self, val_start, n_val_problems, val_ds, 
                                train_start, n_train_problems, train_ds):
        """
        Write down report on statistics of generated dataset
        Parameters:
        - val_start        -- index of start problem for validation
        - n_val_problems   -- number of problems used for validation
        - val_ds           -- samples of validation dataset
        - train_start      -- index of start problem for training
        - n_train_problems -- number of problems used for training
        - train_ds         -- samples of training dataset
        """
        with open(f"{self.report_dir}/TrainDatasetStatistics.lst", 'w') as _f:
            _f.write("PROBLEM DISTRIBUTION IN VALIDATION DATASET\n")
            self.writeProblemDistribution(val_start, n_val_problems, 
                                          val_ds, _f)
            _f.write("\n\n")
            _f.write("PROBLEM DISTRIBUTION IN TRAINING DATASET\n")
            self.writeProblemDistribution(train_start, n_train_problems, 
                                          train_ds, _f)

    def writeProblemList(self, problems, fn):
        """
        Write problem list to file 
        to report test, train, validation problems
        Parameters:
        - problems  -- list of problems
        - fn        -- name of file 
        """
        with open(f"{self.report_dir}/{fn}", 'w') as _f:
            for _p in problems:
                _f.write(_p + "\n")

    def writeSamplesTxt(self, samples, fn):
        """
        Write dataset samples in plain text format
        to report test, train, validation datset
        Parameters:
        - samples  -- similarity samples in the form of 4-tuples
                      <problem1, solution1, problem2, solution2>
        - fn       -- name file to write down report
        """
        with open(f"{self.report_dir}/{fn}", 'w') as _f:
            _f.write("{:8s} {:12s} {:8s} {:12s}\n".
                format("problem1", "solution1", "problem2", "solution2"))
            _f.write("------------------------------------------------\n")
            for _sample in samples:
                _p1, _sol1, _p2, _sol2 = _sample
                _f.write("{:8s} {:12s} {:8s} {:12s}\n".
                         format(self.problems[_p1], 
                                self.solution_names[_p1][_sol1], 
                                self.problems[_p2], 
                                self.solution_names[_p2][_sol2]))

    def writeSamplesCsv(self, samples, fn):
        """
        Write dataset samples in csv format
        to report test, train, validation datset
        Parameters:
        - samples  -- similarity samples in the form of 4-tuples
                      <problem1, solution1, problem2, solution2>
        - fn       -- file to write down csv file
        """
        with open(f"{self.report_dir}/{fn}", 'w', newline='') as _f:
            _writer = csv.writer(_f, lineterminator=os.linesep)
            _writer.writerow(["problem1", "solution1",
                              "problem2", "solution2"])
            for _sample in samples:
                _p1, _sol1, _p2, _sol2 = _sample
                _writer.writerow([self.problems[_p1], 
                                  self.solution_names[_p1][_sol1], 
                                  self.problems[_p2], 
                                  self.solution_names[_p2][_sol2]])

    def writeProblemDistribution(self, start_problem, 
                                 n_problems, samples, f):
        """
        Compute and write problem distribution in samples
        The distribution is computed only for problems used 
        for constructing samples
        Parameters:
        - start_problem   -- index of fist problem used for samples
        - n_problems      -- number of problems used for samples    
        - samples         -- similarity samples in the form of 4-tuples
                             <problem1, solution1, problem2, solution2>
        - f               -- file to write down reports
        """
        _same_problems = [0] * n_problems
        _left_problems = [0] * n_problems
        _right_problems = [0] * n_problems
        _pair_cnt = np.zeros((n_problems, n_problems), dtype=float)
        for _p1, _, _p2, _ in samples:
            _pair_cnt[_p1 - start_problem, _p2 - start_problem] += 1
            if _p1 == _p2:
                _same_problems[_p1 - start_problem] += 1
            else:
                _left_problems[_p1 - start_problem] += 1
                _right_problems[_p2 - start_problem] += 1
        _max_pair = _pair_cnt.max(axis=1)
        _min_pair = _pair_cnt.min(axis=1)
        _mean_pair = _pair_cnt.mean(axis=1)
        _median_pair = np.median(_pair_cnt, axis=1)
        _std_pair  = _pair_cnt.std(axis=1)
        _min_problem = np.argmin(_pair_cnt, axis=1)
        _max_problem = np.argmax(_pair_cnt, axis=1)
        _n_fully_omitted = 0
        _n_same_omitted = 0
        _n_left_omitted = 0
        _n_right_omitted = 0
        _n_different_omitted = 0
        _n_samples = len(samples)
        f.write(
            "Probl  Same  Same%   Left  Left%  Right Right% Min N  Max N  Median Mean N Std N  Problem   Pare  Often\n" + 
            "Index    samples       sample       samples    pairs  pairs  pairs  pairs  pairs  name    problem Problem\n")
        f.write(
            "---------------------------------------------------------------------------------------------------------\n")
        for _i in range(n_problems):        
            if (_same_problems[_i] + _left_problems[_i] + 
                _right_problems[_i]) == 0:
                _n_fully_omitted += 1
                continue
            f.write("{:4d} {:6d} {:5.2f}  {:6d} {:5.2f}  {:6d} {:5.2f} {:6f} {:6f} {:6f} {:8.1f} {:6.2f} {:7s} {:7s} {:7s} \n".
                format(_i + start_problem, _same_problems[_i],
                       (100.0 * float(_same_problems[_i])) / float(_n_samples),
                       _left_problems[_i],
                       100.0 * float(_left_problems[_i]) / float(_n_samples),
                       _right_problems[_i],
                       100.0 * float(_right_problems[_i]) / float(_n_samples),
                       _min_pair[_i], _max_pair[_i], _median_pair[_i],
                       _mean_pair[_i], _std_pair[_i],
                       self.problems[_i + start_problem], 
                       self.problems[_min_problem[_i] + start_problem] \
                       if _min_pair[_i] > 0 else "   -   ", 
                       self.problems[_max_problem[_i] + start_problem] \
                       if _max_pair[_i] > 0 else "   -   "))
            if _same_problems[_i] == 0: _n_same_omitted += 1
            if _left_problems[_i] == 0: _n_left_omitted += 1
            if _right_problems[_i] == 0: _n_right_omitted += 1
            if _left_problems[_i] + _right_problems[_i] == 0:
                _n_different_omitted += 1
        f.write("-------------------------------------------\n")
        f.write(f"{_n_fully_omitted} problems are not present in ANY samples\n")
        f.write(f"Among the other {n_problems - _n_fully_omitted} problems:")
        f.write(f"  - {_n_same_omitted} problems are not present in SAME samples\n")
        f.write(f"  - {_n_different_omitted} problems are not present in DIFFERENT samples\n")
        f.write(f"  - {_n_left_omitted} problems are not present in left side of DIFFERENT samples\n")
        f.write(f"  - {_n_right_omitted} problems are not present in right side of DIFFERENT samples\n")

    @abstractmethod
    def makeSimDataset(samples, labels):
        """
        Make similarity dataset in the form of numpy arrays of
        tensorflow datasets
        Parameters:
        - samples             -- list of dataset samples
                                 Each sample is represented as 4-tuple
                                 <problem 1, solution 1, problem 2, solution 2>,
                                 where problems and solutions are their indices
        - labels              -- labels as numpy array
                                 used only in implementations constructing 
                                 TF datasets
        Returns:
        - constructed dataset 
          * either as single numpy array 
          * or tuple of them 
          * or TF dataset
        """
        raise NotImplementedError()
#---------------- End of class SimilarityDSMaker ----------------------------
        
