"""
Program for updating dataset with tokenized solutions of given problems.

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
from os import path
import argparse
import json

main_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([f"{main_dir}/Dataset"])
from DsUtilities import getProblemSet
from DSTokenizer import BaseDsTokenizer

def makeProblemList(ds, source):
    """
    Analyze source code dataset and 
    write down list of problems to tokenized dataset
    Parameters:
    - ds      -- directory of tokenized datset to be constructed
    - source  -- directory with source code files of problem solutions
    """
    _problems = os.listdir(source)
    if not _problems:
        sys.exit(f"Directory {source}  of source code dataset is empty")
    problem_dict = {}
    volume_hist = {}
    print(f"Analyzing source code dataset with {len(_problems)} problems")
    _n_problems = 0
    _n_all_solutions = 0
    for _p in _problems:
        _sol_dir = source + '/' + _p
        _solutions = os.listdir(_sol_dir)
        if not _solutions:
            print(f"Directory {_sol_dir} has no source code files")
            continue
        _n_problems += 1
        _n_solutions = len(_solutions)
        _n_all_solutions += _n_solutions
        problem_dict[_p] = _n_solutions
        try: 
            volume_hist[_n_solutions] += 1 
        except KeyError: 
            volume_hist[_n_solutions] = 1
    out_fn = ds + '/' + "problems.json"
    with open(out_fn, 'w') as out_json:
        json.dump(problem_dict, out_json)
    print(f"Imported {_n_problems} problems with {_n_all_solutions} solutions")
    #------------- End of function makeProblemList  -----------

class ImportDsTokenizer(BaseDsTokenizer):
    """
    Class for tokenizing solutions of all problems
    of imported datset, which is different from CodeNet
    and writing down tokenized solution code to dataset
    """
    def __init__(self, ds, data, lang, 
                 verbose, no_macro, update = True, 
                 token_set = "17classes", debug = False):
        """
        Initialize tokenizer object
        Parameters:
        - ds       -- Directory to write down tokenized solutions
        - data     -- Directory with source code of problem solutions
        - lang     -- language of the solution code
        - verbose  -- flag to print tokenizer warning
        - no_macro -- flag not to tokenize macro definitions
        - update   -- flag to update tokenized problems in constructed dataset
        - token_set -- name of set of tokens to use:
                      - either "17classes" for combined tokens into 17 classes.
                      - name of sets language operators and keywords 
                        for detailed operational mode
        - debug    -- flag to debug tokenization
        """
        super(ImportDsTokenizer, self).__init__(ds, data, lang, 
                        verbose, no_macro, update =update, 
                        token_set = token_set, debug = debug)

    def tokenizeProblem(self, sol_dir, out_fn):
        """
        Tokenize solution files of given problem 
        and combine results in a single file,
        collect statistics about tokenized problems 
        and their solutions
        Tokenization of each file is represented in the following format:
        <Name of code file>:<String of tokens seprated with commas (',')>'\n'
        
        Parameters:
        - sol_dir       -- directory with solutions to tokenize
        - out_fn       -- Name of output file to write tokenized code
        Returns:
        - number of files tokenized
        Updates:
        - self.sol_len_distr distribution of solution lengths
        """
        _not_found = []
        _failed = []
        _without_tokens = []
        _n_files_analyzed = 0
        _n_files_tokenized = 0
        _solutions = os.listdir(sol_dir)
        with open(out_fn, 'w') as _fout:
            for _s in _solutions:
                _n_files_analyzed += 1
                _solution = _s.rpartition('.')[0]
                _file2tokenize = f"{sol_dir}/{_s}"
                if not os.path.exists(_file2tokenize):
                    _not_found.append(_file2tokenize)
                    continue
                _n_files_tokenized += self.tokenizeFile(
                    _file2tokenize, _solution, _fout, _failed, _without_tokens)
        self.not_found += _not_found
        self.failed_tokenized += _failed
        self.without_tokens += _without_tokens
        print(f"Problem {sol_dir} was tokenized into {out_fn}")
        print(f"   Number of files analyzed:  {_n_files_analyzed}")
        print(f"   Number of files tokenized: {_n_files_tokenized}")
        if _not_found:
            print(f"   Number of files not found: {len(_not_found)}")
        if _failed:
            print(f"   Number of files failed to tokenize: {len(_failed)}")
        if _without_tokens:
            print(f"   Number of files without intertesting tokens: {len(_without_tokens)}")
        return _n_files_tokenized

    def tokenizeAllProblems(self, problem_list):
        """
        Tokenize all problems
        Parameters:
        - problem_list -- problems to tokenize their solutions
        """
        #Dictionary for distribution of solution length
        self.sol_len_distr = {}
        #Dictionary of tokenized problems:
        #Key: number of solutions. 
        #Value list of problems
        self.tokenized_problems = {}
        #List of source code files not found
        self.not_found = []
        #List of source code files failed to tokenize 
        self.failed_tokenized = []
        #List of source files having no interesting tokens
        self.without_tokens = []
        self.n_all_tokenized_sol = 0
        self.valid_problems = {}
        for _i, _p_data in  enumerate(problem_list):
            _problem, _n_solutions = _p_data
            _output_fn = f"{self.ds}/{_problem}.tkn"
            if not self.update and os.path.exists(_output_fn):
                print(f"#{_i + 1}: Problem {_problem} is skipped. " + 
                      "The tokenized dataset already has it")
                continue
            print(f"#{_i + 1}: " + 
                  f"Tokenize problem {_problem} with {_n_solutions} solutions")
            _solution_dir = f"{self.data}/{_problem}"
            if not os.path.exists(_solution_dir):
                sys.exit(f"Directory {_solution_dir} with source code files is not found")
            _n_tokenized_sols = self.tokenizeProblem(
                _solution_dir, _output_fn)
            if _n_tokenized_sols:
                self.n_all_tokenized_sol += _n_tokenized_sols
                self.tokenized_problems[_problem] = _n_tokenized_sols
                try:
                    self.valid_problems[_n_tokenized_sols].append(_problem)
                except KeyError:
                    self.valid_problems[_n_tokenized_sols] = [_problem]
            else:
                os.system(f"rm {_output_fn}")
                print(f"Problem {_problem} with solutions in {_solution_dir} " + 
                      "has no tokenized solutions")
        self.tok_debugger.endDebug()
        self.printReport()
        self.writeInfo()
#------------- End of class ImportDsTokenizer -----------------------------

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
    if not os.path.exists(args.source):
        sys.exit(f"Directory {args.source} of source code dataset is not found")
    makeProblemList(args.ds, args.source)
    _problem_list = getProblemSet(args.ds, args.size, 
                                  args.n_problems)
    if not _problem_list:
        sys.exit(f"No problems have required number {args.size} of solutions")
    tokenizer = ImportDsTokenizer(args.ds, args.source,
                                  args.language, args.verbose,
                                  args.no_macro, args.update,
                                  args.tok_set, args.debug)
    tokenizer.tokenizeAllProblems(_problem_list)
#------------- End of function main -----------------------------

################################################################################
# Command line arguments are described below
################################################################################
if __name__ == '__main__':
    print("\nTOKENIZING IMPORTED DATASET")
    #Command-line arguments
    parser = argparse.ArgumentParser(
        description = "Make tokenized dataset from imported data")
    parser.add_argument("ds", type=str,
                        help="Directory to construct tokenized dataset")
    parser.add_argument("--source", type=str, 
                        default="/Volume1/AI4CODE/POJ-104/raw/ProgramData", 
                        help="Path to source code dataset")
    parser.add_argument("--language", type=str, 
                        default="C++", choices=["C", "C++", "Java", "python"],
                        help="programming language: either C, C++, Java or python")
    parser.add_argument("--tok_set", type=str,  default="CPP56X", 
        help=("name of token set: " + 
              "17classes, CPP52, CPP54, CPP56, CPP56X, Java, etc."))
    parser.add_argument('--size', default=1, type=int,
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
