"""
Program for code classification by Bag or Tokens technique
using cluster analysis



Implements nearest cluster simple classifier of sorce code:

The programm processes all files in the given directory
Each file there contains all samples of one class of samples,
i.e. tokenised source code

Number of classes (lables) is defined automatically
"""
import sys
import os
import argparse

sys.path.extend(["../BagOfTokens"])
from DatasetLoader import BagOfTokensLoader
from NearestCluster import NearestClusterClassifier

def main(args):
    """
    Main function of program for classifying source code

    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    ds_loader = BagOfTokensLoader(args.samples, args.tokens)
    all_samples, problem_samples = ds_loader.getPartitionedSampes()
    val_train_split = args.valpart
    val_samples = \
        [_solutions[: int(float(len(_solutions)) * val_train_split)] 
         for _solutions in problem_samples]

    train_samples = \
        [_solutions[int(float(len(_solutions)) * val_train_split) :] 
         for _solutions in problem_samples]
    classifier = NearestClusterClassifier(train_samples, val_samples)
    #classifier.nClustersTrain(args.clusters)
    classifier.scaledClustersTrain(args.clusters)
    accuracy = classifier.validate()
    print("Accuracy: ", accuracy)


#######################################################################
# Command line arguments of are described below
#######################################################################
if __name__ == '__main__':
    print("\nCODE CLASSIFICATION WITH BAG OF TOKENS CLUTERING CLASSIFIER")

    #Command-line arguments
    parser = argparse.ArgumentParser(
        description = "Bag of Tokens program source code classifier")
    parser.add_argument('samples',
                        type=str, help='path to data directory')
    parser.add_argument('--tokens', default=17, type=int,
                        help='number of tokens')
    parser.add_argument('--valpart', default=0.2, type=float,
                        help='fraction of samples for validation')
    parser.add_argument('--clusters', default=8, type=int,
                        help='number of clusters')
    args = parser.parse_args()

    print("Parameter settings used:")
    for k,v in sorted(vars(args).items()):
        print("{}: {}".format(k,v))

    main(args)


