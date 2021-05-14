"""
Module for constructing token dictionary for tokenizer
"""
import sys

class TokenDictFactory():
    """
    Class for constructing token dictionaries for tokenizer
    """
    #=============  Old set of 52 C++ tokens  =================
    CPP52_OPERATORS = [
        "=", "+", "-", "*", "/",                  #Assignment and arithmetic operators
        "%", "&", "|", "^", "~", "<<", ">>",      #Bitwise Operators
        "+=", "-=", "*=", "/=", "%=", "++", "--", #Compound arithmetic assignment operators
        "&=", "|=", "^=", "<<=", ">>=",           #Compound bitwise assignment operators
        "==", "!=", "<", "<=", ">", ">=",         #Comparison operators
        "&&", "||", "!",                          #Logical operators
        "(", ")", "{", "}", "[", "]", "->"]             #Others
    CPP52_KEYWORDS  = ["if", "else", "for", "while",
                       "switch", 
                       "int", "char", "short", "long",
                       "float", "double", "bool"]
   
    #============  Extended set of C++ tokens =================
    #Old name CPPNew, now renamed to CPP54
    #Added tokens: ?, enum
    CPP54_OPERATORS = [
        "=", "+", "-", "*", "/",                  #Assignment and arithmetic operators
        "%", "&", "|", "^", "~", "<<", ">>",      #Bitwise Operators
        "+=", "-=", "*=", "/=", "%=", "++", "--", #Compound arithmetic assignment operators
        "&=", "|=", "^=", "<<=", ">>=",           #Compound bitwise assignment operators
        "==", "!=", "<", "<=", ">", ">=",         #Comparison operators
        "?", "&&", "||", "!",                          #Logical operators
        "(", ")", "{", "}", "[", "]", "->"]             #Others    
    CPP54_KEYWORDS  = ["if", "else", "for", "while",
                     "switch", 
                     "enum", "int", "char", "short", "long",
                     "float", "double", "bool"]

    #=========== Extended set of C++ tokens ================
    #Added tokens: '?', 'enum', ';', ','
    CPP56_OPERATORS = [
        "=", "+", "-", "*", "/",                  #Assignment and arithmetic operators
        "%", "&", "|", "^", "~", "<<", ">>",      #Bitwise Operators
        "+=", "-=", "*=", "/=", "%=", "++", "--", #Compound arithmetic assignment operators
        "&=", "|=", "^=", "<<=", ">>=",           #Compound bitwise assignment operators
        "==", "!=", "<", "<=", ">", ">=",         #Comparison operators
        "?", "&&", "||", "!",                     #Logical operators
        "(", ")", "{", "}", "[", "]", "->",
        ";", ","]                                 #Others    
    CPP56_KEYWORDS  = ["if", "else", "for", "while",
                     "switch", 
                     "enum", "int", "char", "short", "long",
                     "float", "double", "bool"]
    
    CPP_SYNONYMS = {"and": "&&", "or": "||", "not": "!"}

    #=========== Reduced set of C++ tokens ================
    #Removed << and >> as they overloaded with CPP input and output
    #Added tokens: '?', 'enum', ';', ','
    CPPreducedOPERATORS = [
        "=", "+", "-", "*", "/",                  #Assignment and arithmetic operators
        "%", "&", "|", "^", "~",                  #Bitwise Operators
        "+=", "-=", "*=", "/=", "%=", "++", "--", #Compound arithmetic assignment operators
        "&=", "|=", "^=", "<<=", ">>=",           #Compound bitwise assignment operators
        "==", "!=", "<", "<=", ">", ">=",         #Comparison operators
        "?", "&&", "||", "!",                     #Logical operators
        "(", ")", "{", "}", "[", "]",
        ";", ","]                                 #Others    
    CPPreducedKEYWORDS  = [
        "if", "else", "for", "while", "switch", 
        "enum", "int", "char", "short", "long",
        "float", "double", "bool"]
    #=========== Large set of C++ tokens ================
    #Added tokens: '?', 'enum', ';', ','
    CPPlarge_OPERATORS = [
        "=", "+", "-", "*", "/",                  #Assignment and arithmetic operators
        "%", "&", "|", "^", "~", "<<", ">>",      #Bitwise Operators
        "+=", "-=", "*=", "/=", "%=", "++", "--", #Compound arithmetic assignment operators
        "&=", "|=", "^=", "<<=", ">>=",           #Compound bitwise assignment operators
        "==", "!=", "<", "<=", ">", ">=",         #Comparison operators
        "?", "&&", "||", "!",                     #Logical operators
        "(", ")", "{", "}", "[", "]", "->",       #Others 
        ";", ",",
        ":", "."]                                 #Others added 
    CPPlarge_KEYWORDS  = ["if", "else", "for", "while", "switch", 
        "enum", "int", "char", "short", "long", "float", "double", "bool",
        "unsigned", "signed", "const", "static", "typedef", "sizeof", 
        "true", "false",
        "case", "default", "break", "continue", "return", "do",
        "void", "struct", "extern", "new", "delete", "class",
        "goto", "inline", "register"]
    #============================================================ 
    #Set of Java tokens
    JAVA_OPERATORS = [
        "=", "+", "-", "*", "/",           #Assignment and arithmetic operators
        "%", "&", "|", "^", "~",           #Bitwise Operators
        "<<", ">>", ">>>",                 #Shift operators                            
        "+=", "-=", "*=", "/=", "%=",      #Compound arithmetic assignment operators
        "++", "--",                        #Increment and decrement operators
        "&=", "|=", "^=",                  #Compound bitwise assignment operators
        "<<=", ">>=", ">>>=",              #Compound shift assignment operators
        "==", "!=", "<", "<=", ">", ">=",  #Comparison operators
        "?", "&&", "||", "!",              #Logical operators
        "(", ")", "{", "}", "[", "]", "->", #Others
        ".*", ",", ".", ":", ";", "...", "@", "::"]   #added
    
    JAVA_KEYWORDS  = ["if", "else", "for", "while",
                      "switch", "do",
                      "enum", "int", "char", "byte",
                      "short", "long",
                      "float", "double", "boolean",
                      "null", "case", "this", "new",        #added
                      "return", "interface", "implements",
                      "finally", "static"]  #added
    #============================================================ 
    #Experimental set of Java tokens
    JAVA_OPERATORS_EXP = [
        "=", "+", "-", "*", "/",           #Assignment and arithmetic operators
        "%", "&", "|", "^", "~",           #Bitwise Operators
        "<<", ">>", ">>>",                 #Shift operators                            
        "+=", "-=", "*=", "/=", "%=",      #Compound arithmetic assignment operators
        "++", "--",                        #Increment and decrement operators
        "&=", "|=", "^=",                  #Compound bitwise assignment operators
        "<<=", ">>=", ">>>=",              #Compound shift assignment operators
        "==", "!=", "<", "<=", ">", ">=",  #Comparison operators
        "?", "&&", "||", "!",              #Logical operators
        "(", ")", "{", "}", "[", "]", "->", #Others
        ".*", ",", ".", ":", ";", "...", "@", "::"]   #added
    
    JAVA_KEYWORDS_EXP  = ["if", "else", "for", "while",
                          "switch", "do",
                          "enum", "int", "char", "byte",
                          "short", "long",
                          "float", "double", "boolean",
                          "null", "case", "this", "new",        #added
                          "return", "interface", "implements",
                          "finally", "static",
        "try", "catch", "break", "throw", "default", "assert"]  #added for experiment
    #=========== Set of python tokens ================
    PYTHON_OPERATORS = [
        "=", "+", "-", "*", "**", "/", "//",       #Assignment and arithmetic operators
        "%", "&", "|", "^", "~", "<<", ">>",      #Bitwise Operators
        "+=", "-=", "*=", "/=", "%=", "//=", "**=", #Compound arithmetic assignment operators
        "&=", "|=", "^=", "<<=", ">>=",           #Compound bitwise assignment operators
        "==", "!=", "<", "<=", ">", ">=",         #Comparison operators
        "and", "or", "not", "is", "is not", "in", "not in",   #Logical operators
        "(", ")", "{", "}", "[", "]",             #Others 
        ";", ",", ":", "."]                       #Others

    PYTHON_KEYWORDS  = ["if", "else", "elif", "for", "while", "with", "from",
        "True", "False", "None",
        "def", "lambda", "break", "continue", "return", "yield",
        "try", "raise", "assert", "except", "finally", "class"]
    #============================================================  
  
    #Dictionary of sets of tokens
    #Key:   name of token set
    #Value: 3-tuple defining sets of operators and keywords, and
    #       dictionary of synonym tokens (either operators or keywords)
    #       If it is none no synonyms exist
    token_sets = {
        "CPP52" : (CPP52_OPERATORS, CPP52_KEYWORDS, None),
        "CPP54":  (CPP54_OPERATORS, CPP54_KEYWORDS, None),
        "CPP56":  (CPP56_OPERATORS, CPP56_KEYWORDS, None),
        "CPP56X": (CPP56_OPERATORS, CPP56_KEYWORDS, CPP_SYNONYMS),
        "CPPreduced":  (CPPreducedOPERATORS, CPPreducedKEYWORDS, CPP_SYNONYMS),
        "CPPlarge":  (CPPlarge_OPERATORS, CPPlarge_KEYWORDS, CPP_SYNONYMS),
        "Java"  : (JAVA_OPERATORS, JAVA_KEYWORDS, None),
        "JavaExp": (JAVA_OPERATORS_EXP, JAVA_KEYWORDS_EXP, None),
        "python" :(PYTHON_OPERATORS, PYTHON_KEYWORDS, None)}

    def __init__(self):
        """
        Initialize object of factory of tokens dictionaries
        So far factory of token disctionaries has only class level API
        Parameters:
        """
        pass

    @classmethod
    def makeTokenDict(self, token_set):
        """
        Make dictionary for parsing tokenizer output
        Parameters:
        - token_set  -- name of set of tokens to use
        Returns:
        - Dictionary of tokens
          Key:   string representation of the token
          Value: numerical string representation of the token
        - Number of types of tokens, excluding synonyms
        """
        try:
            _operators, _keywords, _synonyms = self.token_sets[token_set]
        except KeyError:
            sys.exit(f"Token set {token_set} is unknown")
        _token_dict = {}
        for _i, _op in enumerate(_operators + _keywords):
            _token_dict[_op] = str(_i)
        _n_token_types = len(_token_dict)    
        if _synonyms:
            for _syn, _orig in _synonyms.items():
                _token_dict[_syn] = _token_dict[_orig]
        return _token_dict, _n_token_types
#------------- End of class TokenDictFactory -----------------------------

