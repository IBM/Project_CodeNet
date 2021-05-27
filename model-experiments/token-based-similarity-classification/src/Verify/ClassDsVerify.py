"""
Program for verification of downloaded classification datsets.
"""
import sys
import os
from os import path
import argparse
import csv

def readDataset(cvs_file):
    """
    Read datset problems and solutions from csv file
    Parameters;
    - cvs_file  -- csv file defining dataset
    Returns:
    - dictionary defining loaded datsets
    - number of samples in the loaded datasets
    - number of errors found
    """
    _n_errors = 0
    if not os.path.exists(cvs_file):
        sys.exit(f"File {cvs_file} with datset is not found")
    _problem_dict = {}
    _n_samples = 0
    with open(cvs_file, newline='') as _:
        _reader = csv.reader(_)
        next(_reader)
        for _p, _s in _reader:
            _n_samples += 1
            try:
                if _s in _problem_dict[_p]:
                    print(f"Error: multiple occrrences of solution {_s} of problem {_p} occurred file {cvs_file}")
                    _n_errors +=1
                _problem_dict[_p].add(_s)
            except KeyError:
                _problem_dict[_p] = {_s}
    return _problem_dict, _n_samples, _n_errors

def compareDatasets(test, train):
    """
    Compare training and testing datasets
    Parameters:
    - test   -- dictionary defining test dataset
    - train  -- dictionary defining training dataset
    Returns:
    - minimal value of test fraction of samples
    - maximal value of test fraction of samples
    - number of errors found
    """
    _max_test = 0
    _min_test = 1.0
    _n_errors = 0
    for _p, _test_sols in test.items():
        try:
            _train_sols = train[_p]
            _common_sols = _test_sols & _train_sols
            if _common_sols:
                print(f"Error: common solutions of problem {_p} in test and train datasets")
                _n_errors +=1
            _test_part = float(len(_test_sols)) / float(len(_train_sols))
            _max_test = max(_max_test, _test_part)
            _min_test = min(_min_test, _test_part)
        except KeyError:
            print(f"Problem {_p} is only in test dataset but not in training one")
            _n_errors +=1
    for _p, _sols in train.items():
        if _p not in test:
            print(f"Problem {_p} is only in training dataset but not in test one")
            _n_errors +=1
    return _min_test, _max_test, _n_errors

def checkDsVsDir(ds, ds_dir):
    """
    Check loaded dataset with respect to source datset directory
    Parameters:
    - ds      -- dictionary defining dataset to be checked
    - ds_dir  -- directory with source dataset
    Returns:
    - number of errors found
    """
    _n_errors = 0
    for _p, _sols in ds.items():
        if not os.path.exists(f"{ds_dir}/{_p}"):
            print(f"Problem {_p} is not in dataset directory {ds_dir}")
            _n_errors +=1
            for _s in _sols:
                if not os.path.exists(f"{ds_dir}/{_p}/{_s}"):
                    print(f"Solution {_s} is not in problem directory {ds_dir}/{_p}")
                    _n_errors +=1
    return _n_errors

def checkDirVsDatasets(source, test, train):
    """
    Check source dataset directory with respect to loaded test and training datasets
    Parameters:
    - source  -- directory with source dataset
    - test    -- dictionary defining test dataset to be checked
    - train   -- dictionary defining training dataset to be checked
    Returns:
    - number of problems in source dataset directory
    - total number of solutions (samples) in source dataset directory
    - number of errors found
    """
    _problems = os.listdir(source)
    _n_solutions = 0
    _n_errors = 0
    if not _problems:
        sys.exit(f"Directory {source} of source code dataset is empty")
    for _p in _problems:
        if _p not in test:
            print(f"Error: problem {_p} is not in test dataset")
            _n_errors +=1
        if _p not in train:
            print(f"Error: problem {_p} is not in train dataset")
            _n_errors +=1
        _solutions = os.listdir(f"{source}/{_p}")
        _n_solutions += len(_solutions)
        if not _solutions:
            sys.exit(f"Directory {source}/{_p} of source code dataset is empty")
            for _s in _solutions:
                if (_s not in test[_p]) or (_s not in train[_p]):
                    print(f"Error: solution {_s} of problem {_p} is neither in test not in training dataset")

                    _n_errors +=1
    return len(_problems), _n_solutions, _n_errors
#------------- End of functions -----------------------------

def main(args):
    """
    Main function of program for verifying dataset

    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    if not os.path.exists(args.ds):
        sys.exit(f"Directory {args.ds} of source code dataset is not found")
    n_total_errors = 0
    test_ds, test_size, n_errors = readDataset(args.test)
    n_total_errors += n_errors
    train_ds, train_size, n_errors = readDataset(args.train)
    n_total_errors += n_errors
    min_test, max_test, n_errors = compareDatasets(test_ds, train_ds)
    n_errors = checkDsVsDir(test_ds, args.ds)
    n_total_errors += n_errors
    n_errors = checkDsVsDir(train_ds, args.ds)
    n_total_errors += n_errors
    n_source_problems, n_source_solutions, n_errors = \
            checkDirVsDatasets(args.ds, test_ds, train_ds)
    n_total_errors += n_errors
    print(f"Source dataset directory has {n_source_problems} problems with {n_source_solutions} total solutions")
    print(f"Test dataset has {test_size} samples, which are solutions of {len(test_ds)} problems")
    print(f"Training dataset has {train_size} samples, which are solutions of {len(train_ds)} problems")
    print(f"Test fraction varies from {min_test *100}% to {max_test*100}% of number of training solutions of each problem")
    if n_total_errors:
        print(f"There were found {n_total_errors} errors in datasets")
    else:
        print("No errors were found in test and training datasets")
#------------- End of function main -----------------------------

################################################################################
# Command line arguments are described below
################################################################################
if __name__ == '__main__':
    print("\nVERIFYING CONSISTENSY OF TESTING AND TRAINING CLASSIFICATION DATASETS")
    #Command-line arguments
    parser = argparse.ArgumentParser(
        description = "Verication of testing and trainingg classification datsets")
    parser.add_argument("ds", type=str,
                        help="Directory with source dataset")
    parser.add_argument("test", type=str, 
                        help="file with test dataset")
    parser.add_argument("train", type=str, 
                        help="file with training and validation datset")

    args = parser.parse_args()

    print("Parameter settings used:")
    for k,v in sorted(vars(args).items()):
        print("{}: {}".format(k,v))

    main(args)
