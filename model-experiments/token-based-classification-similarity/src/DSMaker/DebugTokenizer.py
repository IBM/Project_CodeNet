"""
Module for debugging tokenizer
nd tokenized source code
"""
import csv

class DebugTokenizer:
    """
    Class for debugging tokenizer
    """
    #Operators to catch
    catch_operators = frozenset([])
    #Keywords to catch
    catch_keywords  = frozenset([])
    #Tokens to catch
    catch_tokens    = frozenset([".*"])
    #catch_tokens    = frozenset([">>>", "and", "or", "not"])
    def __init__(self, debug, report_dir):
        """
        Initialize debugging
        Paramneters:
        - debug    -- flag to debug tokenization
                      If it is False no debugging is performed
        - report_dir -- directory to write the report to
        """
        self.debug = debug
        if not self.debug: return
        self.too_short_files = {}
        self.too_long_files  = {}
        self.strange_token_files   = {}
        self.strange_operator_files   = {}
        self.strange_keyword_files   = {}
        self.debug_number = 0
        self.fout = open(f"{report_dir}\DebugTokenization.lst", 'w')

    def debugFile(self, source_fn, tok_fn):
        """
        Check tokenized file
        Parameters:
        - source_fn  -- file name of source code
        - tok_fn     -- file name of tokenizer output
        """
        if not self.debug: return
        _strange_tokens = set()
        with open(tok_fn, newline='',
                  encoding="ISO-8859-1") as _csvfile:
            _token_reader = csv.reader(_csvfile)
            _token_reader.__next__() #Skip csv header
            for _, _, _tok_class, _tok_value in _token_reader:
                if _tok_class == "operator" or _tok_class == "keyword":
                    if _tok_value in self.catch_tokens:
                        _strange_tokens.add(_tok_value)
        if _strange_tokens:
            self.debug_number += 1
            _t = ", ".join(_strange_tokens)
            self.fout.write(f"{self.debug_number:3d}  {source_fn}\n")
            self.fout.write(f"   Unexpected tokens: {_t}\n")

    def endDebug(self):
        """
        Complete debugging
        """
        if not self.debug: return
        self.fout.close()

        
        

