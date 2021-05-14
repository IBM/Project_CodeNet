"""
Program for analysis of distribution of problems solutions dataset
"""
import sys
import os
import argparse
from VectorKMeans import SetOfClusters

sys.path.extend(["../BagOfTokens"])
from DatasetLoader import BagOfTokensLoader

def main(args):
    """
    Main function of program for analysing bags of tokens distribution of 
    of sorce code solutions of several problems

    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    ds_loader = BagOfTokensLoader(args.samples, args.tokens)
    all_samples, problem_samples = ds_loader.getPartitionedSampes()
    dist_analyzer = SetOfClusters(problem_samples)
    dist_analyzer.printClustCentersDistr()
    dist_analyzer.printClustToCentersDistr()
    dist_analyzer.printClustersDistr()
    dist_analyzer.printClustersStat()

#######################################################################
# Command line arguments of are described below
#######################################################################
if __name__ == '__main__':
    print("\nANALYSIS OF SOURCE CODE DATASET DISTRIBUTION BY BAG OF TOKENS")

    #Command-line arguments
    parser = argparse.ArgumentParser(
        description = "Analysis of distribution of bags of tokens of source code dataset")
    parser.add_argument('samples',
                        type=str, help='path to data directory')
    parser.add_argument('--tokens', default=17, type=int,
                        help='number of tokens')
    args = parser.parse_args()

    print("Parameter settings used:")
    for k,v in sorted(vars(args).items()):
        print("{}: {}".format(k,v))

    main(args)
