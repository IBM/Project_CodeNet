"""
Module for making dataset for classifier 
of source codes by sequence or bag of tokens technique
The module has an absract base class for more specialized 
constructors of datasets

Loads tokenized samples of source codes 
corresponding to solution of programming problems.
Each file there contains all samples of 
one class of samples - tokenised source code files

Token sequences are codeconverted into samples by
the function provided with child class

Number of classes (lables) is defined automatically
"""
import sys
import os
from abc import ABC, abstractmethod
import numpy as np
import csv

import tensorflow as tf

from DataLoader   import SeqOfTokensLoader
from Utilities    import memoryUsage
from DsUtilities  import *

class ClassDatasetBase():
    """
    Base class for classes specifying classification datasets
    """
    #Filenames for dumping datasets
    fn_ds_dump = {"whole":       "WholeDataset",
                  "training":    "TrainingDataset",
                  "validation":  "ValidationDataset",
                  "test":        "TestDataset",
                  "train_val":   "TrainAndValidDataset"}

    def __init__(self, ds, purpose, report_dir, 
                 dump = False, csv = True):
        """
        Initialize base object of classification dataset
        Parameters:
        - ds            -- object of loaded dataset
        - purpose       -- purpose of dataset:
                           "whole" -- whole dataset
                           "training" -- training dataset
                           "validation" -- validation dataset
                           "test"       -- testing dataset
        - report_dir    -- directory to write reports about dataset
        - dump          -- flag to dump the dataset to file
        - csv           -- flag to dump the dataset to csv file
        """
        self.label_names = ds.problems
        self.report_dir = report_dir
        if dump:
            self.dumpDataset(f"{self.report_dir}/{self.fn_ds_dump[purpose]}.lst")
        if csv:
            self.csvDataset(f"{self.report_dir}/{self.fn_ds_dump[purpose]}.csv")
            
    @property
    def size(self):
        return len(self.samples)
        
    def dumpDataset(self, fn):
        """
        Dump classification dataset
        Parameters:
        - fn  -- name of file to write to
        """
        with open(fn, 'w') as _f:
            _f.write("#         Label  Solution  Problem\n")
            _f.write("------------------------------------\n")
            for _i in range(len(self.labels)):
                _f.write("{:8d}  {:5d}  {:8s} {:s}\n".
                         format(_i, self.labels[_i], self.sample_names[_i], 
                                self.label_names[self.labels[_i]]))
                
    def csvDataset(self, fn):
        """
        Write down classification dataset in csv form
        Parameters:
        - fn  -- name of file to write to
        """
        with open(fn, 'w', newline='') as _f:
            _writer = csv.writer(_f, lineterminator=os.linesep)
            _writer.writerow(["Problem", "Solution"])
            for _i in range(len(self.labels)):
                _writer.writerow([self.label_names[self.labels[_i]],
                                  self.sample_names[_i]])
                
    def labelDistr(self):
        """
        Compute label distribution
        Parameters:
        - labels   - list of sample labels
        - n_labels - number of labels
        """
        _lab_distr = [0] * len(self.label_names)
        for _l in self.labels:
            _lab_distr[_l] += 1
        return _lab_distr

    def samplesDsFromGenerator(self, samples, batch_size):
        """
        Make batched TF dataset of samples froms samples generator
        Samples are defined with list of sequences
        Parameters:
        - samples    -- list of samples
        - batch_size -- batch size
        Returns: TF dataset
        """
        _s = tf.data.Dataset.from_generator(
            lambda: samples, output_signature=(
                tf.TensorSpec(shape=([None]), dtype=tf.int32)))
        _s = _s.padded_batch(batch_size, padding_values = 0,
                             drop_remainder=True)
        return _s

    def dsFromGenerator(self, batch_size, shard = "OFF"):
        """
        Make batched TF dataset from samples generator,
        Samples are defined with list of sequences
        Drop samples to make the dataset to be multiple of batch size
        Parameters:
        - batch_size -- batch size
        - shard      -- option to shard dataset:
                        * "OFF"  -- AutoShardPolicy.OFF
                        " "DATA" -- AutoShardPolicy.DATA
        Returns: 
        - TF dataset
        - list of sample labels (indices of problems)
        - list of sample names (names of solutions)
        - list of label names (name of problems)
        """
        _ds_size = (len(self.labels) // batch_size) * batch_size
        _s = self.samplesDsFromGenerator(self.samples[: _ds_size], batch_size)
        _s = _s.unbatch()
        _t_labels  = tf.convert_to_tensor(
            np.asarray(self.labels[: _ds_size], dtype=np.int32))
        _l = tf.data.Dataset.from_tensor_slices(_t_labels)
        _ds = tf.data.Dataset.zip((_s, _l))
        _ds_options = makeShardOptions(policy = shard)
        _ds = _ds.batch(batch_size).with_options(_ds_options)
        return (_ds, self.labels[: _ds_size],
                self.sample_names[: _ds_size], self.label_names)
    
    def rawDS(self, batch_size):
        """
        Make raw dataset having length multiple to batch size 
        Samples are defined with list of sequences
        Parameters:
        - batch_size -- batch size
        Returns: 
        - list of samples 
        - list of sample labels (indices of problems)
        - list of sample names (names of solutions)
        - list of label names (name of problems)
        """
        _ds_size = (len(self.labels) // batch_size) * batch_size
        return (self.samples[: _ds_size], self.labels[: _ds_size],
                self.sample_names[: _ds_size], self.label_names)
#---------------- End of class ClassDatasetBase -----------------------------

class ClassDataset(ClassDatasetBase):
    """
    Classification Dataset that is initialized by carving a part 
    of array of samples
    the resulted dataset is unbalanced in terms of solutions of each 
    problem
    Class of objects representing a classification dataset
    Currently works for samples represented with sequences of tokens
    """
    def __init__(self, ds, start_idx, length,
                 purpose, report_dir, dump = True, csv = True):
        """
        Initialize object of classification dataset
        Parameters:
        - ds            -- object of loaded dataset
        - start_idx     -- start index for selecting dataset 
                           from all data samples
        - length        -- length of dataset
        - purpose       -- purpose of dataset:
                           "whole" -- whole dataset
                           "training" -- training dataset
                           "validation" -- validation dataset
                           "test"       -- testing dataset
        - report_dir    -- directory to write reports about dataset
        - dump          -- flag to dump the dataset to file
        - csv           -- flag to dump the dataset to csv file
        """
        self.samples = ds.samples[start_idx: start_idx + length]
        self.sample_names = ds.sample_names[start_idx: start_idx + length]
        self.labels = ds.labels[start_idx: start_idx + length]
        #__init__ of base class is postponed till here to prepare the datasets
        super(ClassDataset, self).__init__(ds, purpose, 
                                report_dir, dump = dump, csv = csv)
#---------------- End of class ClassDataset -----------------------------

class BalancedClassDataset(ClassDatasetBase):
    """
    Balanced classification Dataset where is problem has proportionally 
    correct number of solutions
    Class of objects representing a classification dataset
    Currently works for samples represented with sequences of tokens
    """
    #Seeds for shuffling datasets
    shuffle_seeds = {"training"  : "TRAIN_SHUFFLE_SEED",
                     "validation": "VALID_SHUFFLE_SEED",
                     "test"      : "TEST_SHUFFLE_SEED"}

    def __init__(self, ds, samples, sample_names, labels,
                 purpose, report_dir, 
                 dump = True, csv = True):
        """
        Initialize object of classification dataset
        Parameters:
        - ds            -- object of loaded dataset
        - samples       -- dataset samples
        - sample_names  -- names of dataset samples
        - labels        -- labels of dataset samples loaded ???
        - report_dir    -- directory to write reports about dataset
        - purpose       -- purpose of dataset:
                           "whole" -- whole dataset
                           "training" -- training dataset
                           "validation" -- validation dataset
                           "test"       -- testing dataset
        - dump          -- flag to dump the dataset to file
        """
        self.samples = samples
        self.sample_names = sample_names
        self.labels = labels
        try:
            _seed = self.shuffle_seeds[purpose]
            DataRand.randPreordered(self.samples, _seed)
            DataRand.randPreordered(self.sample_names, _seed)
            DataRand.randPreordered(self.labels, _seed)
        except KeyError:
            pass
        #__init__ of base class is postponed till here to prepare the datasets
        super(BalancedClassDataset, self).__init__(ds, purpose, 
                            report_dir, dump = dump, csv = csv)
#---------------- End of class BalancedClassDataset -------------------------

class ClassifDSMaker(SeqOfTokensLoader):
    """
    Dataset maker
    Loads files of tokenized source code files from the given directory and
    Prepares data set for classifier of source codes
    """
    def __init__(self, dir_name, min_n_solutions = 1,
                 problem_list = None, max_n_problems = None,
                 short_code_th = 4, long_code_th = None,
                 test_part = 0, balanced_split = False):
        """
        Initialize Dataset maker with files to process
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
        - test_part       -- fraction of data reserved for test set
        - balanced_split  -- flag to make training/validation/test split
                             of the dateset fully balanced, it means that
                             each problem has the same fraction of solutions
        """
        super(ClassifDSMaker, self).__init__(
            dir_name, min_n_solutions = min_n_solutions,
            problem_list = problem_list, max_n_problems = max_n_problems,
            short_code_th = short_code_th, long_code_th = long_code_th)
        self.test_part = test_part
        self.balanced_split = balanced_split
        if self.balanced_split:
            self.test_ds, self.train_val_ds, self.whole_ds = \
                self.balancedTestTrain()
            print("Constructed balanced split of problem solutions for testing and training")
        else:
            self.test_ds, self.train_val_ds, self.whole_ds = \
                self.splitShuffledSamples() 
            print("Shuffled samples are splited for testing and training")
        self.val_ds = None
        self.train_ds = None
        print(f"Dataset with {len(self.whole_ds.samples)} samples is loaded")
        memoryUsage("After ClassifDSMaker.__init__")

    def balancedTestTrain(self):
        """
        Devide solutions of each problem evenly between test and,
        training and test datasets
        Returns:
        - test dataset
        - training/validation dataset
        Computes:
        - list of number of solutions of each problem reserved 
          for training and validation
        """
        self.probl_solutions, self.sol_names = \
                                self.getPartitionedSampes()
        _test_samples = []
        _test_sample_names = []
        _test_labels = []
        _train_samples = []
        _train_sample_names = []
        _train_labels = []
        _all_samples = []
        _all_sample_names = []
        _all_labels = []
        self.train_valid_solutions = []
        for _i in range(len(self.probl_solutions)):
            _n_solutions = len(self.probl_solutions[_i])
            if _n_solutions < 3:
                sys.exit(f"Number of solutions of problem {self.problems[_i]} " +
                         "is only {_n_solutions}\n" + 
                         "It is not enough for training and testing")
            _n_test_solutions = max(1, int(_n_solutions * self.test_part))
            _n_train_solutions = _n_solutions - _n_test_solutions
            _test_samples.extend(self.probl_solutions[_i][_n_train_solutions :])
            _test_sample_names.extend(self.sol_names[_i][_n_train_solutions :])
            _test_labels.extend([_i] * _n_test_solutions)
            _train_samples.extend(self.probl_solutions[_i][: _n_train_solutions])
            _train_sample_names.extend(self.sol_names[_i][: _n_train_solutions])
            _train_labels.extend([_i] * _n_train_solutions)
            self.train_valid_solutions.append(_n_train_solutions)
            _all_samples.extend(self.probl_solutions[_i])
            _all_sample_names.extend(self.sol_names[_i])
            _all_labels.extend([_i] * _n_solutions)
        _test_ds = BalancedClassDataset(
            self, _test_samples, _test_sample_names, _test_labels, 
            "test", self.report_dir)
        _train_val_ds = BalancedClassDataset(
            self, _train_samples, _train_sample_names, _train_labels,
            "train_val", self.report_dir)
        #Make dataset with all samples
        _whole_ds = BalancedClassDataset(
            self, _all_samples, _all_sample_names, _all_labels, 
            "whole", self.report_dir)
        return _test_ds, _train_val_ds, _whole_ds
      
    def splitShuffledSamples(self):
        """
        Split array of shaffled samples straight forward way into 
        test and, train and validation
        Returns:
        - test dataset
        - training/validation dataset
        - whole dataset
        Computes: 
        - size of test and training/validation dataset
        """
        self.samples, self.labels, self.sample_names = \
            self.getShuffledLabeledSamples()
        #Make dataset with all samples
        _whole_ds = ClassDataset(self, 0, len(self.samples),
                                 "whole", self.report_dir)
        #Reserve samples for test set
        self.test_size = int(len(self.samples) * self.test_part)
        self.train_val_size = len(self.samples) - self.test_size
        _test_ds = ClassDataset(
            self, len(self.samples) - self.test_size,
            self.test_size, "test", self.report_dir) \
            if self.test_size else None
        _train_val_ds = ClassDataset(self, 0, self.train_val_size,
                                    "train_val", self.report_dir)
        return _test_ds, _train_val_ds, _whole_ds

    def balancedValTrain(self, valpart):
        """
        Devide solutions of each problem evenly between 
        validation and training datasets
        Parameters:
        - valpart    -- Fraction of dataset samples used 
                        for validation as float
        Returns:
        - validation and training datsets
        """
        _val_samples = []
        _val_sample_names = []
        _val_labels = []
        _train_samples = []
        _train_sample_names = []
        _train_labels = []
        for _i, _n_solutions in enumerate(self.train_valid_solutions):
            if _n_solutions < 2:
                sys.exit(f"Number of solutions of problem {self.problems[_i]} is " +
                         "only {_n_solutions}\n" + 
                         "It is not enough for training and validation")
            _n_val_solutions = max(1, int(_n_solutions * valpart))
            _val_samples.extend(self.probl_solutions[_i][: _n_val_solutions])
            _val_sample_names.extend(self.sol_names[_i][: _n_val_solutions])
            _val_labels.extend([_i] * _n_val_solutions)
            _train_samples.extend(
                self.probl_solutions[_i][_n_val_solutions : _n_solutions])
            _train_sample_names.extend(
                self.sol_names[_i][_n_val_solutions : _n_solutions])
            _train_labels.extend([_i] * (_n_solutions - _n_val_solutions))
        _val_ds = BalancedClassDataset(
            self, _val_samples, _val_sample_names, _val_labels, 
            "validation", self.report_dir)
        _train_ds = BalancedClassDataset(
            self, _train_samples, _train_sample_names, _train_labels,
            "training", self.report_dir)
        return _val_ds, _train_ds

    def testDS(self, batch_size):
        """
        Make test tf.dataset
        The tf.data.dataset is constructed from_generator
        Parameters:
        - batch_size -- batch size

        Returns: 
        - TF dataset and 
        - list of labels
        - list of sample names 
        - list of lable names
        """
        if self.test_ds:
            return self.test_ds.dsFromGenerator(batch_size)
        else:
            sys.exit("Cannot make test dataset because it was not defined")

    def trainValidDs(self, valpart, batch_size, dump = True):
        """
        Make training and validation tf.datasets by 
        splitting loaded data set
        The tf.data.dataset is constructed from_generator
        Additionally computes names of validation samples
        Parameters:
        - valpart    -- Fraction of dataset samples used for validation
                        as float
        - batch_size -- size for training dataset
        Returns:
        - pair of <validation dataset>, <training dataset>
          Both training and validation dataset are tensorflow Datasets
        """
        if self.balanced_split:
            self.val_ds, self.train_ds = self.balancedValTrain(valpart)
        else:
            _train_len, _val_len = self.trainValDsSize(valpart, batch_size)
            self.val_ds = ClassDataset(self, 0, _val_len,
                                       "validation", self.report_dir)
            self.train_ds = ClassDataset(self, _val_len, _train_len,
                                         "training", self.report_dir)
        self.writeLabelDistribution()
        _train_ds = self.train_ds.dsFromGenerator(batch_size)
        _val_ds = self.val_ds.dsFromGenerator(batch_size)
        memoryUsage("After DS made")
        return _val_ds, _train_ds

    def trainValDsSize(self, valpart, batch_size):
        """
        Compute sizes of training and validation datasets 
        rounded to batch size
        Use only samples left after reserving samples for testb set
        Parameters:
        - valpart    -- Fraction of dataset samples used for validation
                        as float
        - batch_size -- size for training dataset
        Returns:
        - sizes of training and validation datasets
        """
        _val_len = int(float(self.train_val_size) * valpart)
        _train_len = self.train_val_size - _val_len
        return _train_len, _val_len

    def writeLabelDistribution(self):
        """
        Write down distribution of datasets lables
        """
        _whole_distr = self.whole_ds.labelDistr()
        _train_distr = self.train_ds.labelDistr()
        _val_distr   = self.val_ds.labelDistr()
        _test_distr  = self.test_ds.labelDistr() if self.test_ds else None
        print(f"Whole dataset has {self.whole_ds.size} samples")
        print(f"Training dataset has {self.train_ds.size} samples")
        print(f"Validation dataset has {self.val_ds.size} samples")
        print(f"Test dataset has {self.test_ds.size} samples")
        with open(f"{self.report_dir}/SampleDistribution.lst", 'w') as _f:
            _f.write("Problem    Label      N     %%        N      %%       N       %%    N     %%\n")
            _f.write("                 in whole dataset  in training DS   in valid DS   in test DS\n")
            for _i in range(len(self.problems)): 
                _whole_pct = 100.0 * float(_whole_distr[_i]) / self.whole_ds.size
                _train_pct = 100.0 * float(_train_distr[_i]) / self.train_ds.size
                _val_pct = 100.0 * float(_val_distr[_i]) / self.val_ds.size
                _test_num, _test_pct = (_test_distr[_i], 
                        100.0 * float(_test_distr[_i]) / self.test_ds.size) \
                        if self.test_ds else (0, 0)
                _f.write("{:10s}   {:3d}  {:7d}  {:6.2f}  {:7d}  {:6.2f}  {:7d}  {:6.2f}  {:7d}  {:6.2f}\n".
                    format(self.problems[_i], _i, 
                           _whole_distr[_i], _whole_pct,
                           _train_distr[_i], _train_pct, 
                           _val_distr[_i], _val_pct,
                           _test_num, _test_pct))
#---------------- End of class ClassifDSMaker ----------------------------------
