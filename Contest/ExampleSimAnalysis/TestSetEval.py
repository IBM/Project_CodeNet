"""
Program for predicting similarity of testset samples.
- The DNN is loaded from a given TensorFlow check point.
- The testset is a csv file with the following format:
  <sample number>,<relative path to 1-st file>,<relative path to 2-nd file>
- The program converts source code into token sequences
  using the tokenizer from Project_CodeNet
- Tokens coding is defined with dictionary of tokens hard coded in the program.
- It is required that tokens coding is the same as the one used for DNN training.
- More examples of token dictionaries can be found in  Project_CodeNet Github
- Additionally to the testset the program can read a csv file with ground truth labels of the test set sample if it is given
- The file with labels has the following format:
  <sample number>,<label>
    * The label = 1 for similar source code files, otherwise label = 0
- The program computes the average accuracy of detecting similarity and dissimilarity of test set samples, if labels are defined
- The program also writes down file csv file with predicted probabilities that samples represent similar source code files

The program uses the following components:
- The tokenizer from Project_CodeNet 
- Keras API of TensorFlow ML framework

Program arguments are described at the end of the file
"""
import sys
import os
import argparse
import csv
import numpy as np
import tensorflow as tf

def makeTokenSet():
    """
    Make a token set 
    The set of tokens must be the same as it used for trainning the DNN
    Here we make a CPP56X token set of C++ tokens
    Returns a dictionary of tokens:
    - Key is a string representing the token
    - Value is integer value of token
    """
    #CPP56 OPERATORS
    operators = [
        "=", "+", "-", "*", "/",                  #Assignment and arithmetic operators
        "%", "&", "|", "^", "~", "<<", ">>",      #Bitwise Operators
        "+=", "-=", "*=", "/=", "%=", "++", "--", #Compound arithmetic assignment operators
        "&=", "|=", "^=", "<<=", ">>=",           #Compound bitwise assignment operators
        "==", "!=", "<", "<=", ">", ">=",         #Comparison operators
        "?", "&&", "||", "!",                     #Logical operators
        "(", ")", "{", "}", "[", "]", "->",
        ";", ","]                                 #Others    
    #CPP56 KEYWORDS
    keywords= ["if", "else", "for", "while",
               "switch", 
               "enum", "int", "char", "short", "long",
               "float", "double", "bool"]
    #CPP SYNONYMS
    synonyms = {"and": "&&", "or": "||", "not": "!"}

    token_dict = {}
    for _i, _op in enumerate(operators + keywords):
        token_dict[_op] = _i
    print(f"Token set of {len(token_dict)} tokens is constructed")    
    for _syn, _orig in synonyms.items():
        token_dict[_syn] = token_dict[_orig]
    print(f"Additionally it has {len(synonyms)} synonym tokens")    
    return token_dict

#Dictionary of tokens and their indicies
token_set = makeTokenSet()

def tokenizeFile(filename, tokenizer):
    """
    Tokenize a given file
    Parameters:
    - filename     -- name of source code file to tokenize
    - tokenizer -- path to tokenizer executable
    Returns:
    - a list of integer token values representing the source code file
    """
    #Name of temporary file for tokenized source code
    TMP_TOKENIZATION = "./t_o_k_e_n_s.o_u_t"
    #Tokenization command ignoring macros
    #tokenize_cmd = tokenizer + " -wcmcsv"
    #Tokenization command tokenising macros
    tokenize_cmd = tokenizer + " -wmcsv"
    if os.system(f"{tokenize_cmd}  -o {TMP_TOKENIZATION} {filename}"):
        sys.exit(f"Tokenization error in file {filename}")
    tokens = []
    with open(TMP_TOKENIZATION, newline='',
              encoding="ISO-8859-1") as csvfile:
        token_reader = csv.reader(csvfile)
        token_reader.__next__() #Skip csv header
        for _, _, _tok_class, _tok_value in token_reader:
            if _tok_class == "operator" or _tok_class == "keyword":
                try:
                    tokens.append(token_set[_tok_value] + 1)
                except KeyError:
                    #ignore tokens that are not in the tokens set
                    pass
    return tokens

def makeDataset(source, test, tokenizer):
    """
    Make tensorflow dataset 
    for predicting similarity of testset samples with Simaese DNN
    Parameters:
    - source    -- path to directory with source code files 
                   to analyze similarity
    - test      -- path to the testsetrfile specifying pairs 
                   of source code file to analyze similarity
    - tokenizer -- path to tokenizer executable
    Returns:
    - dataset as list of two numpy arrays.
      Each numpy array represets set of token sequences for one input of DNN
    """   
    tokenizations = {}
    samples = []
    max_code_len = 0
    with open(test, newline='') as csvfile:
        test_reader = csv.reader(csvfile)
        test_reader.__next__() #Skip csv header
        for _num, fn1, fn2 in test_reader:
            try:
                tok_seq1 = tokenizations[fn1]
            except KeyError:
                tok_seq1 = tokenizeFile(source + '/' + fn1, tokenizer)
                tokenizations[fn1] = tok_seq1
                max_code_len = max(max_code_len, len(tok_seq1))
            try:
                tok_seq2 = tokenizations[fn2]
            except KeyError:
                tok_seq2 = tokenizeFile(source + '/' + fn2, tokenizer)
                tokenizations[fn2] = tok_seq2                
                max_code_len = max(max_code_len, len(tok_seq2))
            samples.append((tok_seq1, tok_seq2))
    np_ds1 = np.zeros(shape=(len(samples), max_code_len), 
                      dtype=np.int32)
    np_ds2 = np.zeros(shape=(len(samples), max_code_len), 
                      dtype=np.int32)
    for _i, _s in enumerate(samples):
        tok_seq1, tok_seq2 = _s
        np_ds1[_i][0:len(tok_seq1)] = np.asarray(tok_seq1, dtype=np.int32)
        np_ds2[_i][0:len(tok_seq2)] = np.asarray(tok_seq2, dtype=np.int32)
    print(f"Dataset of {len(samples)} samples is constructed")
    return [np_ds1, np_ds2]

def loadLabels(filename):
    """
    Load ground truth lables if they exist
    Parameters:
    - filename  -- Path to labels file
    Returns:
    - numpy array with labels to compare with the predicted similarity
      or None if no ground truth lables are provided
    """
    if filename is None:
        print("Labels of test samples are not specified")
        print("Accuracy of DNN on this test cannot be evaluated")        
        return None
    if not os.path.exists(filename):
        print(f"File {filename} with labels of test samples is not found")
        print("Accuracy of DNN on this test cannot be evaluated")
        return None
    labels = []
    with open(filename, newline='') as csvfile:
        test_reader = csv.reader(csvfile)
        test_reader.__next__() #Skip csv header
        for _num, _lbl in test_reader:
            labels.append(int(_lbl))
    return np.asarray(labels)

def writePredictions(test, probabilities, filename):
    """
    Write down similarity predictions
    Parameters:
    - test           -- path to the testset file specifying pairs 
                        of source code file to analyze similarity
    - probabilities  -- numpy array with probabilities of similarities
    - filename       -- filename to write predictions
    """
    with open(test, newline='') as csvin,\
         open(filename, 'w', newline='') as csvout:
        test_reader = csv.reader(csvin)
        writer = csv.writer(csvout, lineterminator=os.linesep)
        test_reader.__next__() #Skip csv header
        writer.writerow(["pair-id", "file1", "file2",
                         "confidence", "prediction"])
        _i = 0
        for _num, _fn1, _fn2 in test_reader:
            writer.writerow([_num, _fn1, _fn2, probabilities[_i][0],
                             "Similar" if probabilities[_i][0] >= 0.5
                             else "Dissimilar"])
            _i += 1
    
def main(args):
    """
    Main function of program for predicting similarity testset samples

    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    if not os.path.exists(args.source_code):
        sys.exit(f"Directory {args.source_code} with source code is not found")
    if not os.path.exists(args.test):
        sys.exit(f"File {args.test} with test pairs is not found")
    if not os.path.exists(args.tokenizer):
        sys.exit(f"Tokenizer {args.tokenizer} is not found")
    if not os.path.exists(args.dnn):
        sys.exit(f"Check point with dnn model {args.dnn} is not found")
    ds = makeDataset(args.source_code, args.test, args.tokenizer)
    labels = loadLabels(args.labels)
    #Load trained DNN from TF checkpoint
    dnn = tf.keras.models.load_model(args.dnn)
    if labels is not None:
        if ds[0].shape[0] == labels.shape[0]:
            #Evaluate DNN accuracy on the testset
            loss, acc = dnn.evaluate(ds, labels, verbose = args.progress)
            print("\nEvaluation accuracy is {:5.2f}%".format(acc * 100))
            print("Evaluation loss is {:5.2f}".format(loss))
        else:
            print(f"Numers of labels {labels.shape[0]} " +
                f"and samples {ds[0].shape[0]} is different ")
            print("Accuracy of DNN on this test cannot be evaluated")
    #Compute probabilities of similarity predicted by DNN
    prob = dnn.predict(ds, verbose = args.progress)
    writePredictions(args.test, prob, args.predictions)
##############################################################################
# Program arguments are described below
##############################################################################
if __name__ == '__main__':
    print("\nPREDICTING SIMILARITY OF TESTSET SAMPLES")
    #Handle command-line arguments
    parser = argparse.ArgumentParser("TestSetEval")
    parser.add_argument("source_code", type=str,
                        help="directory with source code files to analyze similarity")
    parser.add_argument("test", type=str,
                        help="file with sample pairs to analyze similarity")
    parser.add_argument("--labels", type=str, default = None,
                        help="file with similarity labels of test samples")
    parser.add_argument("--dnn", default = "./dnn_ckpt",
                        type=str, help="checkpoint file with trained dnn")    
    parser.add_argument("--tokenizer", default = "tokenize",
                        type=str, help="path to tokenizer of source code files")
    parser.add_argument("--predictions", default = "./predictions.csv",
                        type=str, help="file to write similarity predictions")
    parser.add_argument("--batch", default=400, type=int,
                        help="batch size")
    parser.add_argument('--progress', default=1, type=int,
                        choices=[0, 1, 2],
                        help="mode of Keras training progress bar")
    args = parser.parse_args()

    print("Program arguments used:")
    for k,v in sorted(vars(args).items()):
        print("{}: {}".format(k,v))
        
    main(args)


