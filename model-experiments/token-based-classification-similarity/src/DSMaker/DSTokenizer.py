"""
Module for updating dataset with tokenized solutions of given problems.

- Tokenized representations of all solutions of one problem are 
  placed in a single file.
- The files with tokenized solutions of problems are added into existing 
  directory.
- Each tokenized source code file is represented in the following form:
     <Name of code file>:<String of tokens separated with commas (',')>'\n'
- The program can select for tokenisation solutions having 
  the specified status. 
  If the specified status is 'All' all solutions are tokenized.
- The program selects problems having not fewer tokenizable solutions 
  than the specified parameter.
- There is a parameter specifying the limit of 
  the number problems to tokenize. If that number is None 
  all existing problems satisfying to selection criteria 
  are tokenized.
"""
import sys
import os
from os import path
from abc import ABC, abstractmethod
import json
import csv

from DebugTokenizer import DebugTokenizer
from TokenSets      import TokenDictFactory

class BaseTokenizer(ABC):
    """
    Base abstract class for tokenizing one file of source code
    """
    #Name of temporary file for tokenized source code
    TMP_TOKENIZATION = "./t_o_k_e_n_s.o_u_t"
    #Flags specifing program langiages for Geert's tokenizer 
    LANG_FLAGS = {"Java": "j", "C++": "", "C": ""}
    
    def __init__(self, lang, verbose, no_macro):
        """
        Initialize tokenizer object
        Parameters:
        - lang     -- language of the solution code written in:
                      either C++ or Java
        - verbose  -- flag to print tokenizer warning
        - no_macro -- flag not to tokenize macro definitions
        """
        self.lang = lang
        self.tokenize_cmd = self.makeTokenizerCmd(
            self.lang, verbose = verbose, no_macro = no_macro)
        
    def makeTokenizerCmd(self, language, verbose = False, 
                        no_macro = False):
        """
        Make command for tokenizing source code
        Parameters:
        - language  -- programming language of code written in
                       either C++ or Java
        - verbose   -- flag to pring tonezer warnings
        - no_macro  -- flag to ignor macro definitions in C C++ code
        Returns: tokenization commend as a string
        """
        _w = "" if verbose else "w"
        if language == "python":
            return f"pytokenize -{_w}mcsv "
        try:
            _l = self.LANG_FLAGS[language]
        except KeyError:
            sys.exit(f"Programming language {language} cannot be tokenized")    
        _c = "c" if no_macro else ""
        return f"tokenize -{_w}{_c}{_l}mcsv "
        
    @abstractmethod
    def tokenizeFile(self, in_fn):
        """
        Tokenize source code file
        Parameters:
        - in_fn  -- name of input file with code to tokenize
        Returns:
        - either string of tokens if tokenization is successful
        - or None if it failed
        """
        raise NotImplementedError()

    @abstractmethod
    def tokensReport(self):
        """
        Print report on tokens and 
        their occurrence in processed files
        and write down info on tokens to tokenized dataset
        """
        raise NotImplementedError()
#------------- End of class BaseTokenizer  -----------------------------

class TokClass17Tokenizer(BaseTokenizer):
    """
    Class for tokenizing one file of source code
    The tokenization is represented with 17 token classes 
    """
    def __init__(self, lang, verbose, no_macro):
        """
        Initialize tokenizer object
        Parameters:
        - lang     -- language of the solution code
        - verbose  -- flag to print tokenizer warning
        - no_macro -- flag not to tokenize macro definitions
        """
        super(TokClass17Tokenizer, self).__init__(
            lang, verbose, no_macro)
        self.filter_cmd = self.makeFilterCmd()
        self.n_tokens = 17

    def makeFilterCmd(self):
        """
        Make command for tokenizing source code
        Returns: string as for command pipe with awk filter 
                 postprocessing output of tokenizer
        """
        return f"| filter.awk > {self.TMP_TOKENIZATION};" + \
            "exit ${PIPESTATUS[0]}"

    def tokenizeFile(self, in_fn):
        """
        Tokenize source code file
        Parameters:
        - in_fn  -- name of input file with code to tokenize
        Returns:
       - either string of tokens if tokenization is successful
       - or None if it failed
        """
        _rc =  os.system(self.tokenize_cmd + in_fn + 
                         self.filter_cmd)
        if _rc: return None
        with open(self.TMP_TOKENIZATION) as _f:
            _tokens = _f.read().rstrip('\n').replace('\n',',')
        return _tokens

    def tokensReport(self):
        """
        - Print report on tokens and 
          their occurrence in processed files
        - 17 classes tokenizer does not collect tokens statistics
        """
        print("\nTokenization was performed with 17 classes of tokens")
#------------- End of class BaseTokenizer  -----------------------------

class DetailedTokenizer(BaseTokenizer):
    """
    Class for tokenizing source code file
    The resulted sequence reprersents all operator and keyword tokens
    Uses file cls.TMP_TOKENIZATION for temporary results 
    """
    def __init__(self, lang, verbose, no_macro,
                 token_set, tok_debugger):
        """
        Initialize tokenizer object
        Parameters:
        - lang       -- language of the solution code
        - verbose    -- flag to print tokenizer warning
        - no_macro   -- flag not to tokenize macro definitions
        - token_set  -- name of set of tokens to use
        - tok_debugger -- object for debugging tokeinizer
        """
        super(DetailedTokenizer, self).__init__(
            lang, verbose, no_macro)
        self.tokenize_cmd += f" -o{self.TMP_TOKENIZATION} "
        self.token_dict, self.n_tokens = \
            TokenDictFactory.makeTokenDict(token_set)
        #Set of unrecognized operators and keywords
        self.unknow_tokens = set()
        #Set of found operators and keywords
        self.found_tokens = set() 
        self.tok_debugger = tok_debugger

    def tokenizeFile(self, in_fn):
        """
        Tokenize source code file
        Parameters:
        - in_fn  -- name of input file with code to tokenize
        Returns:
        - either string of tokens if tokenization is successful
        - or None if it failed
        """
        if os.system(self.tokenize_cmd + in_fn):
            return None
        self.tok_debugger.debugFile(in_fn, 
                                    self.TMP_TOKENIZATION)
        _tokens = []
        with open(self.TMP_TOKENIZATION, newline='',
                  encoding="ISO-8859-1") as _csvfile:
            _token_reader = csv.reader(_csvfile)
            _token_reader.__next__() #Skip csv header
            for _, _, _tok_class, _tok_value in _token_reader:
                if _tok_class == "operator" or _tok_class == "keyword":
                    try:
                        _tokens.append(self.token_dict[_tok_value])
                        self.found_tokens.add(_tok_value)
                    except KeyError:
                        self.unknow_tokens.add(_tok_value)
        return  ','.join(_tokens)

    def tokensReport(self):
        """
        Print report on tokens and 
        their occurrence in processed files
        """
        self.printTokenDict()
        self.printUnknownTokens()
        self.printNonexistentTokens()

    def printTokenDict(self):
        """
        Print tokens used for tokenization
        """
        print(f"\nTokenization used {len(self.token_dict)} tokens")
        print("#   Token       Tok idx")
        print("-----------------------")
        for _i, _t in enumerate(
                sorted(self.token_dict.keys())):
            print("{:3d} {:10s}  {:s}".
                  format(_i + 1, _t, self.token_dict[_t]))

    def printUnknownTokens(self):
        """
        Print tokens that were not recognized
        """
        if not self.unknow_tokens: return
        print("\nUnrecognized tokens")
        print("-------------------")
        for _i, _t in enumerate(self.unknow_tokens):
            print("{:3d}  {:s}".format(_i + 1, _t))

    def printNonexistentTokens(self):
        """
        Print tokens not found in any of the processed files
        """
        _not_found = [_t for _t in self.token_dict.keys() 
                      if _t not in self.found_tokens]
        if _not_found:
            print("\nTokens not present in processed files")
            for _i, _t in enumerate(_not_found):
                print(f"{_i + 1:2d}  {_t}")
        else:
            print("\nAll tokens present in processed files")
#------------- End of class DetailTokenizer -----------------------------

class BaseDsTokenizer:
    """
    Base class for tokenizing solutions of all problems
    and writing down tokenized solution code to dataset
    Defines data and functions common for all tokenizers
    Does not rely on any metadada or directory structure
    of source code files to be tokenized
    """
    #Working directory for writing down reports and temporary files
    WORK_DIR = "./TokenizerWorkDir"
    #File name for reporting problem solutions that are not found
    NOT_FOUND_SOLUTIONS = f"{WORK_DIR}/not_found_solutions.lst"
    #File name for reporting problem solutions with tokenization errors
    FAILED_TOKENIZATIONS = f"{WORK_DIR}/tokenization_errors.lst"
    #File name for reporting problem solutions without interesting tokens
    NO_TOKENS = f"{WORK_DIR}/no_interesting_tokens.lst"
    #File name for reporting tokenized problems
    TOKENIZED_PROBLEMS = f"{WORK_DIR}/tokenized_problems.lst"
    #File for reporting distribution of 
    #lengths (number of tokens) of problem solutions
    SOL_LENGTH_DISTR = f"{WORK_DIR}/distr_solution_lengths.lst"
    #File for writing report on tokenized problems
    PROBLEMS_REPORT = f"{WORK_DIR}/tokenization_report.lst"
    #Name of temporary file for tokenized source code
    TMP_TOKENIZATION = f"{WORK_DIR}/t_o_k_e_n_s.o_u_t"

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
        if not os.path.exists(ds):
            sys.exit(f"Directory {ds} to write down tokenized solutions is not found")
        if not os.path.exists(data):
            sys.exit(f"Directory {data} with data files of dataset is not found")
        if not os.path.exists(self.WORK_DIR):
            os.makedirs(self.WORK_DIR)
        #Set name of the temporary file for output of tokenization program
        BaseTokenizer.TMP_TOKENIZATION = self.TMP_TOKENIZATION
        self.ds = ds
        self.data = data
        self.update = update
        self.lang = lang
        self.token_set = token_set
        if self.token_set == "17classes":
            self.tok_debugger = DebugTokenizer(False, self.WORK_DIR)
            self.file_tokenizer = \
                TokClass17Tokenizer(lang, verbose, no_macro)
        else:
            self.tok_debugger = DebugTokenizer(debug, self.WORK_DIR)
            self.file_tokenizer = \
                DetailedTokenizer(lang, verbose, no_macro, 
                                  token_set, self.tok_debugger)
        #Dictionary for accumulating distribution of solution length
        #Key number of tokens
        #Value a pair <number of solutions, name of one sample>
        self.sol_len_distr = {}
        #Dictionary of tokenized problems:
        #Key: number of solutions. Value list of problems
        self.tokenized_problems = {}
        #List of source code files not found
        self.not_found = []
        #List of source code files failed to tokenize 
        self.failed_tokenized = []
        #List of source files having no interesting tokens
        self.without_tokens = []
        self.n_all_tokenized_sol = 0
        #List of correctly tokenized problems
        self.valid_problems = {}

    def tokenizeFile(self, file2tokenize, solution, fout,
                     failed, without_tokens):
        """
        Tokenize file, write down tokenization, and 
        update accumulated statistics
        Parameters:
        - file2tokenize  -- file name to tokenize
        - solution       -- name of problem solution represented by this file
        - fout           -- file to write down tokenization to
        - failed         -- list accumalting names of files failed
        - without_tokens -- list accumalting names of files 
                            without interesting tokens
        Returns:
        - 1  --  if tokenization is successuly written down 
        - 0  -- if tokenization is not written down
        """
        _tokens = self.file_tokenizer.tokenizeFile(file2tokenize)
        if _tokens:
            fout.write(f"{solution}:{_tokens}\n")
            n_tok = (len(_tokens) +1) // 2
            try:
                self.sol_len_distr[n_tok][0] += 1
            except KeyError:
                self.sol_len_distr[n_tok] = [1, file2tokenize]
            return 1
        if _tokens is None:
            failed.append(file2tokenize)
        else:
            without_tokens.append(file2tokenize)
            print(f"WARNING: File {file2tokenize} is skipped. " +
                  "It has no interesting tokens")
        return 0

    def writeInfo(self):
        """
        Write information on tokenization into the dataset
        """
        _fn_info = self.ds + "/" + "info.json"
        _info = {"token_set": self.token_set,
                 "n_tokens": self.file_tokenizer.n_tokens}
        with open(_fn_info, 'w') as _out_json:
            json.dump(_info, _out_json)        

    def printReport(self):
        """
        Print report on performed tokenization
        """
        self.file_tokenizer.tokensReport()
        self.writeProblemsReport(self.valid_problems)
        self.writeSolLenDistr()
        print(f"It was tokenized {self.n_all_tokenized_sol} solutions " + 
              f"of {len(self.tokenized_problems)} problems")
        print(f"There were {len(self.failed_tokenized)} " + 
              "files failed tokenization")
        print(f"There were {len(self.not_found)} files not found")
        print(f"There were {len(self.without_tokens)} files" + 
              " without interesting tokens")
        with open(self.NOT_FOUND_SOLUTIONS, 'w') as _f:
            _f.write('\n'.join(self.not_found) + '\n')
        with open(self.FAILED_TOKENIZATIONS, 'w') as _f:
            _f.write('\n'.join(self.failed_tokenized) + '\n')
        with open(self.NO_TOKENS, 'w') as _f:
            _f.write('\n'.join(self.without_tokens) + '\n')
        with open(self.TOKENIZED_PROBLEMS, 'w') as _f:
            _f.write("Problem    N solutions\n")
            _f.write("----------------------\n")
            for _p, _n in self.tokenized_problems.items():
                _f.write("{:10} {:7d}\n".format(_p, _n))

    def writeSolLenDistr(self):
        """
        Write distribution of problem solutions
        """
        with open(self.SOL_LENGTH_DISTR, 'w') as _f:
            _f.write("  N       N        %%      Tot N    Distr %  One example\n")
            _f.write("tok-s  sol-ns    sol-ns    sol-ns   sol-ns   of solution\n")
            _f.write("--------------------------------------------------------\n")
            _acc_n_sol = 0
            for _l, _n in sorted(self.sol_len_distr.items()):
                _acc_n_sol += _n[0]
                _f.write("{:5d}  {:6d}  {:7.3f}%  {:8d}  {:7.3f}%  {}\n".
                         format(_l, _n[0], 
                                100.0 * _n[0] / self.n_all_tokenized_sol,
                                _acc_n_sol, 
                                100.0 * _acc_n_sol / self.n_all_tokenized_sol,
                                _n[1]))

    def writeProblemsReport(self, problems):
        """
        Print report on processed problems
        sorted according to their number of solutions
        Parameters:
        - problems  -- dictionary of processed problems
           Key:   number of solutions
           Value: list of problems with so many solutions
        """
        with open(self.PROBLEMS_REPORT, 'w') as _f:
            _f.write("Number of  Number of  Count of   Names of problems\n")
            _f.write("solutions  problems   problems                    \n")
            _f.write("--------------------------------------------------\n")
            _total = 0
            for _n in sorted(problems.keys(), reverse = True):
                _total += len(problems[_n])
                _problems = ', '.join(problems[_n])
                _f.write("{:8d}     {:6d}     {:6d}   {}\n".
                         format(_n, len(problems[_n]), 
                                _total, _problems))
        print(f"\nIt was considered {_total} problems " +
              f"with solutions in {self.lang}")
#------------- End of class BaseDsTokenizer  -----------------------------

class DsTokenizer(BaseDsTokenizer):
    """
    Class for tokenizing solutions of all given problems
    of CodeNet dataset
    and writing down tokenized solution code to dataset
    """
    def __init__(self, ds, data, mdata, lang, 
                 verbose, no_macro, update = True, 
                 token_set = "17classes", debug = False):
        """
        Initialize tokenizer object
        Parameters:
        - ds       -- Directory to write down tokenized solutions
        - data     -- Directory with source code of problem solutions
        - mdata    -- Directory with metadata describing the dataset
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
        super(DsTokenizer, self).__init__(ds, data, lang, 
                        verbose, no_macro, update = update, 
                        token_set = token_set, debug = debug)
        if not os.path.exists(mdata):
            sys.exit(f"Directory {mdata} with metadata of dataset is not found")
        self._mdata = mdata

    def tokenizeProblem(self, sol_dir, problem_mdata, out_fn):
        """
        Tokenize solution files of given problem 
        and combine results in a single file,
        collect statistics about tokenized problems 
        and their solutions
        Tokenization of each file is represented in the following format:
        <Name of code file>:<String of tokens seprated with commas (',')>'\n'
        
        Parameters:
        - sol_dir       -- directory with solutions to tokenize
        - problem_mdata -- name of the file with problem metadata
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
        with open(problem_mdata, newline='') as _mdata_csv, \
             open(out_fn, 'w') as _fout:
            _reader = csv.DictReader(_mdata_csv)
            for _row in _reader:
                if _row["language"] != self.lang or \
                   _row["status"] != "Accepted":
                    continue
                _n_files_analyzed += 1
                _solution = \
                    f"{_row['submission_id']}.{_row['filename_ext']}"
                _file2tokenize = \
                    f"{sol_dir}/{_solution}"
                if not os.path.exists(_file2tokenize):
                    _not_found.append(_file2tokenize)
                    continue
                _tokens = \
                    self.file_tokenizer.tokenizeFile(_file2tokenize)
                if _tokens:
                    _fout.write(f"{_solution}:{_tokens}\n")
                    _n_files_tokenized += 1
                    _n_tok = (len(_tokens) +1) // 2
                    try:
                        self.sol_len_distr[_n_tok][0] += 1
                    except KeyError:
                        self.sol_len_distr[_n_tok] = [1, file2tokenize]
                elif _tokens is None:
                    _failed.append(_file2tokenize)
                else:
                    _without_tokens.append(_file2tokenize)
                    print(f"WARNING: File {_file2tokenize} is skipped. " +
                          "It has no interesting tokens")
                #os.system(f"rm {self.TMP_TOKENIZATION}")
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
    #------------- End of function DsTokenizer.tokenizeProblem  -----------

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
            _solution_dir = f"{self.data}/{_problem}/{self.lang}"
            _problem_mdata = f"{self._mdata}/{_problem}.csv"
            if not os.path.exists(_solution_dir):
                sys.exit(f"Directory {_solution_dir} with source code files is not found")
            if not os.path.exists(_problem_mdata):
                sys.exit(f"File {_problem_mdata} with problem metadata is not found")
            _n_tokenized_sols = self.tokenizeProblem(
                _solution_dir, _problem_mdata, _output_fn)
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
#------------- End of class DsTokenizer -----------------------------
