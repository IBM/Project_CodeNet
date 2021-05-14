"""
Program for predicting similarity of two source code files by 
Sequence or Tokens technique

History of traing is pickled to be plotted with other application

The programm processes all files in the given directory
Each file there contains all samples of one class of samples,
i.e. tokenised source code

Number of classes (lables) is defined automatically
"""
import sys
import os
import argparse
import pickle

main_dir = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([f"{main_dir}/Dataset",
                 f"{main_dir}/ModelMaker",
                 f"{main_dir}/PostProcessor",
                 f"{main_dir}/CommonFunctions"])

from Utilities        import resetSeeds
from DsUtilities      import DataRand
from ProgramArguments import *
from SimilConfusion   import SimilConfusAnalysis

def predict(dnn, ds, batch = 32):
    """
    Predict if dataset samples represent similar or dissimilar 
    source code solutions of problems
    Parameters:
    - dnn   -- neural network classifier
    - ds    -- dataset as numpy array of samples
    - batch -- batch size for running dnn
    Returns: numpy array of prdiction probabilities
    """
    return dnn.predict(ds, batch_size = batch)


def train(dnn, train_ds, val_ds, epochs,
          batch_size, history_fn, verbose):
    """
    Train given DNN on given dataset

    - dnn            -- DNN compiled and optimized
    - train_ds       -- Training dataset as a pair 
                        of sample and lables arrays
    - val_ds         -- Validation dataset as a pair 
                        of sample and lables arrays
    - epochs         -- Number of training epochs
    - batch_size     -- Training batch size
    - verbose        -- Keras mode of verbosity: 0, 1, 2
    """
    history = dnn.fit(train_ds[0], train_ds[1],
                      epochs = epochs, batch_size = batch_size,
                      validation_data = (val_ds[0], val_ds[1]),
                      verbose = verbose)

    with open(history_fn, 'wb') as _jar:
        pickle.dump(history.history, _jar)

def main(args):
    """
    Main function of program for predicting similarity of 
    two source code samples

    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    resetSeeds()
    DataRand.setDsSeeds(args.seed_ds)
    
    _convolutions = list(zip(args.filters, args.kernels, args.strides) 
                         if args.strides
                         else zip(args.filters, args.kernels))
    
    if args.model == 'basic':
        from SeqTokSimDataset import SeqTokSimilarityDS
        from SeqModelMaker    import SeqModelFactory
        _ds = SeqTokSimilarityDS(args.dataset,
                                 min_n_solutions = args.min_solutions,
                                 max_n_problems = args.problems,
                                 short_code_th = args.short_code,
                                 long_code_th = args.long_code,
                                 max_seq_length = args.seq_len)

        _model_factory = SeqModelFactory(_ds.n_token_types * 2, 1)
        _dnn = _model_factory.cnnDNN(_convolutions, args.dense,
                                     input_type = args.coding,
                                     pool = args.pool,
                                     conv_act = args.conv_act,
                                     regular = (args.l1, args.l2),
                                     optimizer = args.optimizer)
        print("Basic model for sequence similarity is constructed")
    else:
        from SeqTok2WaySimDataset import SeqTok2WaySimDS
        from FuncModelMaker       import FuncModelFactory
        _ds = SeqTok2WaySimDS(args.dataset,
                              min_n_solutions = args.min_solutions,
                              max_n_problems = args.problems,
                              short_code_th = args.short_code,
                              long_code_th = args.long_code,
                              max_seq_length = args.seq_len)

        _model_factory = FuncModelFactory(1, regularizer = (args.l1, args.l2))
        _dnn = _model_factory.twoWaySimilarityCNN(_ds.n_token_types,
                                                  _convolutions,
                                                  args.dense,
                                                  pool = args.pool,
                                                  side_dense = [],
                                                  conv_act = args.conv_act,
                                                  shared = (args.model == 'symmetric'),
                                                  input_type = args.coding,
                                                  embedding_dim = args.embed,
                                                  optimizer = args.optimizer)
        print("Two way model for sequence similarity is constructed")
        
    _val_ds, _train_ds = \
        _ds.trainValidDsSameProblems(
            args.valpart, args.valsize, args.trainsize,
            args.similpart) \
        if args.validation == "same" else \
           _ds.trainValidDsDifferentProblems(
               args.valpart, args.valsize, args.trainsize,
               args.similpart)
    train(_dnn, _train_ds, _val_ds, args.epochs,
          args.batch, args.history, args.progress)

    del _train_ds
    _val_samples, _labels, _annotations = _val_ds
    _prob = predict(_dnn, _val_samples, batch = args.batch)
    _confusion = SimilConfusAnalysis(_prob, _labels, _ds.solution_names,
                                     _ds.problems, _annotations)
    _confusion.writeReport()

################################################################################
# Args are described below
################################################################################
if __name__ == '__main__':
    print("\nCODE SIMILARITY WITH SEQUENCE OF TOKENS TECHNIQUE")
    #Handle command-line arguments
    parser = makeArgParserCodeML(
        "Sequence of tokens source code similarity analysis",
        task = "similarity")
    parser = addSeqTokensArgs(parser)
    parser.add_argument("--model", type=str, 
                        default= "basic",
                        choices=["basic", "two_way", "symmetric"],
                        help="classifier model: " +
                        "either basic or two_way or symmetric two_way")
    parser = addRegularizationArgs(parser)
    args = parseArguments(parser)
    checkConvolution(args)

    main(args)


