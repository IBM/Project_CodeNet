"""
Program for creating or updating dataset with tokenized solutions 
of given problems.

- Tokenized representations of all solutions of each 
  problem are placed in a single file.
- The files with tokenized solutions of problems are 
  added into existing  directory.
- Each tokenized source code file is represented in 
  the following form:
     <Name of code file>:<String of tokens separated with commas (',')>'\n'
- The program can select for tokenisation solutions having 
  the specified status. If the specified status is 'All',
  all problem solutions are tokenized.
- The program selects problems having not fewer tokenizable 
  solutions than the specified parameter.
- The program has parameter specifying the limit of 
  the number problems to tokenize. If that number is 
  None all existing problems satisfying to the selection 
  criteria are tokenized.
"""
import sys
import os
import argparse
import csv
import json

main_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([f"{main_dir}/Dataset", 
                 f"{main_dir}/CommonFunctions"])
from DsUtilities import getProblemSet
from Utilities import makeFilePath
from DSTokenizer import DsTokenizer

def getProblemNumber(metadir, pid,  lang):
    """
    Get number of accepted solutions of a required problem
    Parameters:
    - metadir  -- path to directory with metadata
    - pid      -- problem id
    - lang     -- language
    """

    problem_data_fn = makeFilePath(metadir, pid + ".csv", 
                        m = "File with problem metadata")
    n_accepted = 0
    with open(problem_data_fn, newline='') as mdata_csv:
        reader = csv.DictReader(mdata_csv)
        for row in reader:
            if row["language"] == lang and \
               row["status"] == "Accepted":
                n_accepted += 1
    return n_accepted

def makeProblemList(out_ds_fn, mdata_dir, source, lang):
    """
    Make problem list if it i does not exist and
    write it down to directory for tokenized dataset
    Parameters:
    - out_ds_fn  -- tokenized datset to write problem list to
    - mdata_dir  -- path to directory with metadata
    - source     -- source of problems: either AIZU or AtCoder
    - lang       -- language
    """
    _out_fn = makeFilePath(out_ds_fn, "problems.json")
    if os.path.exists(_out_fn):
        print(f"Tokenized dataset {out_ds_fn} already has problem list")
        print("The dataset be updated with tokenized source code files")
        return
    _problem_list_fn = makeFilePath(
        mdata_dir, "/problem_list.csv",
        m = "File with dataset problem list")
    _problem_dict = {}
    _volume_hist = {}
    with open(_problem_list_fn, newline='') as _plist_csv:
        _reader = csv.DictReader(_plist_csv)
        for _row in _reader:
            if _row["dataset"] != source: continue
            _problem_id = _row["id"]
            _n = getProblemNumber(mdata_dir, _problem_id, lang)
            if _n:
                _problem_dict[_problem_id] = _n
                try: 
                    _volume_hist[_n] += 1 
                except KeyError: 
                    _volume_hist[_n] = 1
    with open(_out_fn, 'w') as _out_json:
        json.dump(_problem_dict, _out_json)        

def main(args):
    """
    Main function of program for making dataset
    with tokenized solutions of given problem

    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    if not os.path.exists(args.ds):
        os.makedirs(args.ds)
    _mdata_dir = makeFilePath(args.codenet,"/metadata",
                    m = "Directory with dataset metadata")
    _data_dir = makeFilePath(args.codenet, "/data",
                    m = "Directory with dataset data")
    makeProblemList(args.ds,_mdata_dir, args.source, 
                    args.language)
    _problem_list = getProblemSet(args.ds, args.size, 
                                  args.n_problems)
    if not _problem_list:
        sys.exit(f"No problems have required number {args.size} of solutions")
    tokenizer = DsTokenizer(args.ds,_data_dir, _mdata_dir,
                            args.language, args.verbose,
                            args.no_macro, args.update,
                            args.tok_set, args.debug)
    tokenizer.tokenizeAllProblems(_problem_list)
#------------- End of function main -----------------------------

################################################################################
# Command line arguments are described below
################################################################################
if __name__ == '__main__':
    print("\nMAKING TOKENIZED DATASET")
    #Command-line arguments
    parser = argparse.ArgumentParser(
        description = "Adding tokenized solutions to dataset")
    parser.add_argument("ds", type=str,
                        help='Directory to construct tokenized dataset')
    parser.add_argument("--codenet", type=str,
                        default = "/Volume1/AI4CODE/CodeNet_AtCoder",
                        help="path to dataset directory")
    parser.add_argument("--source", type=str, 
                        default="AIZU", choices=["AIZU", "AtCoder"],
                        help="source of data: either AIZU or AtCoder")
    parser.add_argument("--language", type=str, 
                        default="C++", choices=["C", "C++", "Java", "python"],
                        help="programming language: either C, C++, Java or python")
    parser.add_argument("--tok_set", type=str,  default="CPP56X", 
        help=("name of token set: " + 
              "17classes, CPP52, CPP54, CPP56, CPP56X, Java, etc."))
    parser.add_argument('--size', default=100, type=int,
                        help='number of files with solutions of source code')
    parser.add_argument('--n_problems', default=None, type=int,
                        help='number of problems to tokenize solutions')
    parser.add_argument('--update', default=False, action='store_true',
                        help="rewrite existing files with tokenized solutions")
    parser.add_argument('--verbose', default=False, action='store_true',
                        help="report tokenization warnings")
    parser.add_argument('--no_macro', default=False, action='store_true',
                        help="do not tokenize macro definitions")
    parser.add_argument('--debug', default=False, action='store_true',
                        help="run in debug mode")

    args = parser.parse_args()

    print("Parameter settings used:")
    for k,v in sorted(vars(args).items()):
        print("{}: {}".format(k,v))

    main(args)
