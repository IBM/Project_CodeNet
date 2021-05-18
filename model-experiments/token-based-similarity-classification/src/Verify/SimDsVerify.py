"""
Program for verification of downloaded classification datsets.
"""
import sys
import os
from os import path
import argparse
import csv

class DsProblemStat:
    """
    Statistics on problems usage in dataset
    """
    def __init__(self):
        self.similar_left = set()
        self.similar_right = set()
        self.n_similar_left = 0
        self.n_similar_right = 0
        self.left = set()
        self.n_left = 0
        self.right = set() 
        self.n_right = 0

    def update_similar(self, s1, s2):
        """
        Update statistics for similarity sample
        Parameters:
        s1, s2 -- solutions used in similarity sample
        """
        self.similar_left.add(s1)
        self.similar_right.add(s2)
        self.n_similar_right += 1
        self.n_similar_left += 1
 
    def update_left(self, s):
        """
        Update statistics for dissimilarity sample
        """
        self.left.add(s)
        self.n_left += 1           

    def update_right(self, s):
        """
        Update statistics for dissimilarity sample
        """
        self.right.add(s)
        self.n_right += 1
#-------End of class DsProblemStat ------------------------

class SamplePartStat:
    """
    Statistics of the part of set of samples:
    similar, left or right
    """
    def __init__(self):
        """
        Initialize statistics of the part of sample:
        similar, left or right
        """
        self.min_fract_sol_used = 1
        self.max_fract_sol_used = 0
        self.min_uniqueness     = 1
        self.max_uniqueness     = 0
        self.sols_used          = 0
        self.n_total            = 0

    def update(self, n_unique, n_used, n_total):
        """
        Update statistics of the part of sample 
        with data on solutions of one problem
        Parameters:
        - n_unique  -- number of unique problem solutions used in samples
        - n_used    -- number of total problem solutions used in samples
        - n_total   -- number of all problem solutions existed
        """
        #Fraction of all problem solutions used in samples
        _fract_used = float(n_unique) / float(n_total)
        self.min_fract_sol_used = min(self.min_fract_sol_used, _fract_used)
        self.max_fract_sol_used = max(self.max_fract_sol_used, _fract_used)
        #Ratio of number of problem solutions are used in sample to 
        #number of cases where the problem is used in samples
        #Indicator how unique is usage of solution in the samples
        _uniqueness = float(n_unique) / float(n_used)
        self.min_uniqueness = min(self.min_uniqueness, _uniqueness)
        self.max_uniqueness = max(self.max_uniqueness, _uniqueness)
        #Number of cases where problem is used in the samples
        self.sols_used += n_unique
        self.n_total += n_total

    def report(self, title):
        """
        Report statistics
        """
        print(title)
        print(f"Total {self.sols_used} from all {self.n_total} " +
              "of problem solutions are used")
        print("Fraction of used problem solutions varies from " + 
              f"{self.min_fract_sol_used:5.3f} to {self.max_fract_sol_used:5.3f} ")
        print("Uniqueness of used problem solutions varies from " + 
              f"{self.min_uniqueness:7.5f} to {self.max_uniqueness:7.5f}")
#-------End of class SamplePartStat ------------------------

class DsStat:
    """
    Class defining statistics of dataset: test validation or training
    """
    def __init__(self):
        self.simil_left_stat = SamplePartStat()
        self.simil_right_stat = SamplePartStat()
        self.left_stat  = SamplePartStat()
        self.right_stat = SamplePartStat()
        self.total_sols = 0
        self.min_sols = 999999999
        self.min_problem = None
        self.max_sols = 0
        self.max_problem = None
        self.n_problems = 0

    def update(self, problem, problem_stat, n_total):
        """
        Update statistics of problem solutions usage
        Parameters:
        - problem       -- problem name
        - problem_stat  -- Statistics of problem solutions
                           in the form of DsProblemStat object
        - n_total       -- Total number of solutions of the problem
        """
        self.simil_left_stat.update(len(problem_stat.similar_left), 
                                    problem_stat.n_similar_left, 
                                    n_total)
        self.simil_right_stat.update(len(problem_stat.similar_right), 
                                    problem_stat.n_similar_right, 
                                    n_total)
        self.left_stat.update(len(problem_stat.left), 
                                    problem_stat.n_left, 
                                    n_total)
        self.right_stat.update(len(problem_stat.right), 
                                    problem_stat.n_right, 
                                    n_total)
        #Number of all problem solutions existed
        self.total_sols += n_total
        #Minimum number of problem solutions
        if n_total < self.min_sols:
            self.min_sols = n_total
            self.min_problem = problem
        #Maximum number of problem solutions
        if n_total > self.max_sols:
            self.max_sols = n_total
            self.max_problem = problem
        self.n_problems += 1

    def update_solutions(self, n_total):
        """
        Update statistics of dataset problem solutions
        with data on solutions of one problem
        - n_total  -- number of all problem solutions existed
        """
        #Number of all problem solutions existed
        self.total_sols += n_total
        #Minimum number of problem solutions
        self.min_sols = min(self.min_sols, n_total)
        #Maximum number of propblem solutions
        self.max_sols = max(self.max_sols, n_total)
        self.n_problems += 1

    def report(self, title):
        """
        Printing report of dataset statistics
        Parameters:
        - title  -- title of the report
        """
        print(title)
        print(f"Dataset uses {self.n_problems} problems " +
              f"having total {self.total_sols} solutions")
        print("Average number of problem solutions " + 
              f"is {float(self.total_sols) / float(self.n_problems)}")
        print(f"Problem {self.min_problem} has lowest " + 
              f"number {self.min_sols} of solutions")
        print(f"Problem {self.max_problem} has highest " + 
              f"number {self.max_sols} of solutions")
        self.simil_left_stat.report("Statistics of left side of similarity samples:")
        self.simil_right_stat.report("Statistics of right side of similarity samples:")
        self.left_stat.report("Statistics of left side of dissimilarity samples:")
        self.right_stat.report("Statistics of right side of dissimilarity samples:")
        print("\n")
#-------End of class DsStat ------------------------
 
def readDsProblems(fname):
    """
    Read problems of the dataset
    Parameters:
    -fname  -- file name
    Returns: 
    - initialized dictionary
       * key    - problem name
       * value  - dictionary of number of problem used 
                  in similar and dissimilar samples as right and left one
    - number of errors found
    """
    if not os.path.exists(fname):
        sys.exit(f"File {fname} of problems of datset is not found")
    _problem_dict = {}
    _n_errors = 0
    with open(fname) as _f:
        for _p in _f:
            _p = _p.rstrip('\n')
            if _p in _problem_dict:
                print(f"Error: multiple occurrences of problem {_p} in file{fname}")
                _n_errors +=1
            else:
                _problem_dict[_p] = DsProblemStat()
    return _problem_dict, _n_errors

def readDsSamples(cvs_file, problems):
    """
    Read samples of dataset
    Parameters;
    - cvs_file  -- csv file defining dataset
    - problems  -- dictionary of problems of the dataset
                   key:    problem name
                   value:  Statistics of problem usage 
                           in the form of DsProblemStat
    Fills in problems(dictionary of problems of the dataset)
    Returns:
    - number of samples in the loaded datasets
    - number of similar samples
    - number of dissimilar samples
    - number of errors found
    """
    _n_errors = 0
    if not os.path.exists(cvs_file):
        sys.exit(f"File {cvs_file} with datset is not found")
    _n_samples = 0
    _n_similar = 0
    _n_disssimilar = 0
    with open(cvs_file, newline='') as _:
        _reader = csv.reader(_)
        next(_reader)
        for _p1, _s1, _p2, _s2 in _reader:
            _n_samples += 1
            if _p1 not in problems:
                print(f"Error: problem {_p1} occurred in file {cvs_file} " +
                      "is not among problems of that dataset")
                _n_errors +=1
            if _p2 != _p1 and _p2 not in problems:
                print(f"Error: problem {_p2} occurred in file {cvs_file} " +
                      "is not among problems of that dataset")
                _n_errors +=1
            if _p1 == _p2:
                _n_similar += 1
                problems[_p1].update_similar(_s1, _s2)
            else:
                _n_disssimilar += 1
                problems[_p1].update_left(_s1)
                problems[_p2].update_right(_s2)             
    return _n_samples, _n_similar, _n_disssimilar, _n_errors

def checkNoCommonProblems(ds1, ds2, fname1, fname2):
    """
    Check that no common problems in two datasets
    Parameters:
    - ds1     -- 1-st dataset as dictionary of its problems
                 dictionary of problems of the dataset
                   key:    problem name
                   value:  Statistics of problem usage as DsProblemStat
    - ds2     -- 2-nd dataset as dictionary of its problems
                 similar to ds1
    - fname1  -- file name of 1-st dataset
    - fname2  -- file name of 2-nd dataset
    Returns number of errors found
    """
    _n_errors = 0
    _common_problems = frozenset(ds1.keys()).intersection(ds2.keys())
    if _common_problems:
        _n_errors = len(_common_problems)
        print(f"Error datasets {fname1} and {fname2} " +
              "have following {_n_errors} common problems:")
        print(_common_problems)
    return _n_errors

def checkDsSolVsDir(problem, solutions, ds_fn, ds_dir, fn_extension):
    """
    Check that all solutiosn of a given problem are in dataset
    Parameters:
    - problem   -- problem to check
    - solutions -- set of solutions to check
    - ds_fn     -- file name of dataset whose problem 
                   and solutions are checked 
    - ds_dir    -- directory with source dataset
    - fn_extension -- extensions of source code files of problem solutions
    Returns number of errors
    """
    _n_errors = 0
    for _s in solutions:
        if not os.path.exists(f"{ds_dir}/{problem}/{_s}.{fn_extension}"):
            print(f"Solution {_s}.{fn_extension} occurring in file {ds_fn} " +
                  f"is not in problem directory {ds_dir}/{problem}")
            _n_errors +=1
    return _n_errors

def checkDsVsDir(ds, ds_dir, ds_fn, fn_extension):
    """
    Check loaded dataset with respect to source dataset directory
    Parameters:
    - ds      -- dictionary defining dataset to be checked
                   key:    problem name
                   value:  Statistics of problem usage as DsProblemStat
    - ds_dir  -- directory with source dataset
    - ds_fn     -- file name of dataset whose problem 
                   and solutions are checked
    - fn_extension -- extensions of source code files of problem solutions
    Returns:
    - number of errors found
    """
    _n_errors = 0
    for _p, _samples in ds.items():
        if not os.path.exists(f"{ds_dir}/{_p}"):
            print(f"Problem {_p} is not in dataset directory {ds_dir}")
            _n_errors +=1
        _n_errors += checkDsSolVsDir(
            _p, _samples.similar_right, ds_fn, ds_dir, fn_extension)
        _n_errors += checkDsSolVsDir(
            _p, _samples.similar_left, ds_fn, ds_dir, fn_extension)
        _n_errors += checkDsSolVsDir(
            _p, _samples.right, ds_fn, ds_dir, fn_extension)
        _n_errors += checkDsSolVsDir(
            _p, _samples.left, ds_fn, ds_dir, fn_extension)
    return _n_errors

def checkDirVsDatasets(source, train, val, test):
    """
    Check that all problems from source dataset directory are in one 
    of datasets
    Parameters:
    - source  -- directory with source dataset
    - train   -- dictionary defining training dataset to be checked
                   key:    problem name
                   value:  Statistics of problem usage as DsProblemStat
    - val     -- dictionary defining validation dataset to be checked
                 similar to train
    - test    -- dictionary defining test dataset to be checked
                 similar to train
    Returns:
    - number of problems in source dataset directory
    - number of solutions in source dataset directory
    - number of errors found
    """
    _test_stat  = DsStat()
    _val_stat   = DsStat()
    _train_stat = DsStat()
    
    _problems = os.listdir(source)
    _n_total_solutions = 0
    _n_errors = 0
    if not _problems:
        sys.exit(f"Directory {source} of source code dataset is empty")
    for _p in _problems:
        _solutions = os.listdir(f"{source}/{_p}")
        _n_solutions = len(_solutions)
        if not _solutions:
            print(f"Error: Directory {source}/{_p} of source code dataset is empty")
            _n_errors += 1
            continue
        _n_total_solutions += _n_solutions
        if _p in test:
            _test_stat.update(_p, test[_p], _n_solutions)
        elif _p in train:
            _train_stat.update(_p, train[_p], _n_solutions)
        elif _p in val:
            _val_stat.update(_p, val[_p], _n_solutions)
        else:
            print(f"Error: problem {_p} is not present in any datasets")
            _n_errors +=1
    print("\n")
    _train_stat.report("Statistics of training dataset")
    _val_stat.report("Statistics of validation dataset")
    _test_stat.report("Statistics of test dataset")
    return len(_problems), _n_total_solutions, _n_errors
#------------- End of functions -----------------------------

def main(args):
    """
    Main function of program for verifying dataset

    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    if not os.path.exists(args.ds):
        sys.exit(f"Directory {args.source} of source code dataset is not found")
    n_total_errors = 0
    train_problems, _n_errors = readDsProblems(args.train_problems)
    n_total_errors += _n_errors
    val_problems, _n_errors = readDsProblems(args.val_problems)
    n_total_errors += _n_errors
    test_problems, _n_errors = readDsProblems(args.test_problems)
    n_total_errors += _n_errors

    n_trains, n_train_similars, n_train_dissimilars, _n_errors = \
                    readDsSamples(args.train_samples, train_problems)
    n_total_errors += _n_errors
    n_vals, n_val_similars, n_val_dissimilars, _n_errors = \
                    readDsSamples(args.val_samples, val_problems)
    n_total_errors += _n_errors
    n_tests, n_test_similars, n_test_dissimilars, _n_errors = \
                    readDsSamples(args.test_samples, test_problems)
    n_total_errors += _n_errors

    n_total_errors += checkNoCommonProblems(train_problems, val_problems, 
                                            args.train_problems, 
                                            args.val_problems)
    n_total_errors += checkNoCommonProblems(train_problems, test_problems, 
                                            args.train_problems, 
                                            args.test_problems)
    n_total_errors += checkNoCommonProblems(test_problems, val_problems, 
                                            args.test_problems, 
                                            args.val_problems)

    n_total_errors += checkDsVsDir(train_problems, args.ds, 
                                   args.train_samples, args.sol_ext)
    n_total_errors += checkDsVsDir(val_problems, args.ds, 
                                   args.val_samples, args.sol_ext)
    n_total_errors += checkDsVsDir(test_problems, args.ds, 
                                   args.test_samples, args.sol_ext)

    print(f"Training dataset has {n_trains} samples: " +
          f"{n_train_similars} similar and {n_train_dissimilars} " +
          f"dissimilar ones built on {len(train_problems)} problems")
    print(f"Validation dataset has {n_vals} samples: " +
          f"{n_val_similars} similar and {n_val_dissimilars} " +
          f"dissimilar ones built on {len(val_problems)} problems")
    print(f"Test dataset has {n_trains} samples: " +
          f"{n_test_similars} similar and {n_test_dissimilars} " +
          f"dissimilar ones built on {len(test_problems)} problems")

    n_source_problems, n_source_solutions, _n_errors = checkDirVsDatasets(
        args.ds, train_problems, val_problems, test_problems)
    print(f"Source dataset directory has {n_source_problems} problems " +
          f"with {n_source_solutions} total solutions")
    
    if n_total_errors:
        print(f"There were found {n_total_errors} errors in datasets")
    else:
        print("No errors were found in test and training datasets")
#------------- End of function main -----------------------------

################################################################################
# Command line arguments are described below
################################################################################
if __name__ == '__main__':
    print("\nVERIFYING CONSISTENCY OF TESTING, VALIDATION AND TRAINING SIMILARITY DATASETS")
    #Command-line arguments
    parser = argparse.ArgumentParser(
        description = "Verication of testing, validation and training datsets " +
        "of similarity analysis")
    parser.add_argument("ds", type=str,
                        help="Directory with source dataset")
    parser.add_argument("--test_samples", type=str, 
                        help="file with samples of test dataset")
    parser.add_argument("--val_samples", type=str, required=True,
                        help="file with samples of validation dataset")
    parser.add_argument("--train_samples", type=str, required=True,
                        help="file with samples of training datset")
    parser.add_argument("--test_problems", type=str, required=True,
                        help="file with problems of test dataset")
    parser.add_argument("--val_problems", type=str, required=True,
                        help="file with problems of validation dataset")
    parser.add_argument("--train_problems", type=str, required=True,
                        help="file with problems of training datset")
    parser.add_argument("--sol_ext", type=str, default="cpp",
                        help="extentions of files with solutions")

    args = parser.parse_args()

    print("Parameter settings used:")
    for k,v in sorted(vars(args).items()):
        print("{}: {}".format(k,v))

    main(args)
