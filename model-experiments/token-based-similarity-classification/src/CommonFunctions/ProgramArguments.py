"""
Module of functions defining program parameters
"""
import sys
import argparse

def makeArgParserCodeML(description, task = "classification"):
    """
    Make program arguments parser for machine learning
    for analysis of source code problems
    Parameters:
    - description  -- string describing the parser
    - task         -- task for which dataset is used:
                      either 'classification' or 'similarity'
    Returns: constructed argument parser
    """
    parser = argparse.ArgumentParser(description = description)
    parser.add_argument("dataset",
                        type=str, help="dataset directory")
    parser.add_argument("--min_solutions", type=int, default=8,
                        help = "min number of problem solutions")
    parser.add_argument("--problems", default=None, type=int,
                        help = "max number of problems to load")
    parser.add_argument("--short_code", default = 4, type=int,
                        help = "shortest code to load")
    parser.add_argument("--long_code", default = None, type=int,
                        help = "longest code to load")
    parser.add_argument("--testpart", default=0, type=float,
                        help="part of whole dataset for testing")    
    parser.add_argument("--valpart", default=0.2, type=float,
                        help="fraction of training dataset for validation")
    parser.add_argument("--batch", default=32, type=int,
                        help="batch size")
    parser.add_argument("--seed_ds", type=int, default=101,
                        help = "seed for making randomized dataset")
    parser.add_argument("--seed_model", type=int, default=101,
                        help = "seed for making randomized model")    
    parser.add_argument("--dnn", default="basic",
                        type=str, help="dnn model")    
    parser.add_argument('--progress', default=1, type=int,
                        choices=[0, 1, 2],
                        help="mode of keras training progress bar")
    parser.add_argument("--epochs", default=32, type=int,
                        help="number of train epochs")
    parser.add_argument("--patience", default=32, type=int,
                        help="number of epoch to train without improvements")
    parser.add_argument("--dense", type=int, nargs='*',
                        help="sizes of dense layers")
    parser.add_argument("--regul_dense_only", action="store_true", 
                        default=False,
                        help="regulirize only dense layers")
    parser.add_argument("--history", type=str, 
                        default="./train_history.pcl",
                        help="filename to write history of training")
    parser.add_argument("--optimizer", type=str, default="rmsprop", 
                        choices=["sgd", "rmsprop", "adam", "adadelta",
                                 "adagrad", "adamax", "nadam", "ftrl"],
                        help="training optimizer")
    parser.add_argument("--ckpt_dir", default = None,
                        type=str, help="checkpoint directory")
    if task == "similarity":
        parser.add_argument("--validation", type=str, 
                            default="same", choices=["same", "different"],
                            help="validation with same or different " + 
                            "as training problems")
        parser.add_argument("--valsize", default=5000, type=int,
                            help="size of validation dataset")
        parser.add_argument("--trainsize", default=20000, type=int,
                            help="size of training dataset")
        parser.add_argument("--similpart", default=0.5, type=float,
                            help="fraction of all samples, " + 
                            "representing pairs of similar source code")
    elif task == "classification":
        parser.add_argument("--balanced_split", action="store_true", 
                            default=False,
                            help="balanced split of problem solutions " + 
                            "for training, validation and testing")        
    else:
        sys.exit(f"Wrong machine learning task {task}. " +
                "It should be either 'classification' or 'similarity'")
    return parser

def addSeqTokensArgs(parser):
    """
    Add arguments defining DNN processing sequences of tokens
    Parameters:
    - parser  -- argument parser as an object of ArgumentParser
                 to add arguments
    Returns: constructed argument parser
    """
    parser.add_argument('--seq_len', default=None, type=int,
                        help='maximum lengths of token sequence')
    parser.add_argument("--coding", type=str, default="categorical", 
                        choices=["categorical", "trainable", "one_hot"],
                        help="dnn input data coding: " + 
                        "either one-hot or categorical or trainable")
    parser.add_argument("--embed", default=None, type=int,
                        help="size of embedding vectors; " + 
                        "number of tokens if it is not defined" )
    parser.add_argument("--kernels", required=True,
                        type=int, nargs='+',
                        help="width of convolution kernels")
    parser.add_argument("--filters", required=True,
                        type=int, nargs='+',
                        help="number of convolution filters")
    parser.add_argument("--strides", default = None,
                        type=int, nargs='+',
                        help="strides of convolutions")
    parser.add_argument("--conv_act", type=str, 
                        default= None, choices=["relu", "sigmoid", "tanh"],
                        help="activation of convolutional layers")
    parser.add_argument("--pool", type=str, 
                        default="max", choices=["max", "aver"],
                        help="operation of pooling layer")
    parser.add_argument("--dropout", default=0, type=float,
                        help="rate of dropout")
    return parser

def addRegularizationArgs(parser):
    """
    Add arguments defining regularization
    Parameters:
    - parser  -- argument parser as an object of ArgumentParser
                 to add arguments
    Returns: constructed argument parser
    """
    parser.add_argument("--l1", default=0, type=float,
                        help="l1 regularization")
    parser.add_argument("--l2", default=0, type=float,
                        help="l2 regularization")
    return parser

def parseArguments(parser):
    """
    Parse program arguments
    Parameters:
    - parser  -- argument parser as an object of ArgumentParser
                 to add arguments
    Returns: object with program arguments
    """
    args = parser.parse_args()

    print("Parameter settings used:")
    for k,v in sorted(vars(args).items()):
        print("{}: {}".format(k,v))

    return args

def checkConvolution(args):
    """
    Check definition of convolution by program arguments
    Parameters:
    - args object with program arguments
    """
    if len(args.kernels) != len(args.filters):
        print("Error: Numbers of convolution kernels and filters are different")
        sys.exit(1)
    if args.strides and len(args.strides) != len(args.filters):
        print("Error: Numbers of convolution kernels and strides are different")
        sys.exit(1)   
