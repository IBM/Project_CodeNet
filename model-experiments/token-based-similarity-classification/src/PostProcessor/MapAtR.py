"""
Program for computing MAP at R metric
using matrix of predicted similarity strength for all sample pairs
Input data are expected to be in the form of two pickled files:
-  problem_indices.pcl          -- specifies indices of tested problem 
                                   for each similarity test experiment
-  similarity_probabilities.pcl -- specifies matrix of similarity test 
                                   experiment results
                                   Each matrix column describes results
                                   of comparing one problem solution with 
                                   solutions of all other problems
"""
import sys
import os
import argparse
import pickle
import numpy as np

def map_at_r(sim, pids):
    """
    Function for computing MAP at R metric
    Parameter:
    - sim   --  2D numpy array of predicted similarity measures 
                for all pairs of samples
    - pids  --  1D numpy array of problem ids corresponding 
                to columns of matrix  of predicted similarity measures
    Returns: computed MAP at R metric
    """
    #Count number of source code solutions of each problem
    r = np.bincount(pids) - 1
    max_r = r.max()
    #Mask for ignoring the similarity predictions lying 
    #beyond the number of solutions of checked problem
    mask = np.arange(max_r)[np.newaxis, :] < r[pids][:, np.newaxis]
    np.fill_diagonal(sim,-np.inf)
    #Select and sort top predictions
    result = np.argpartition(-sim,
                    range(max_r + 1), axis=1)[:, : max_r]
    #Get correct similarity predictions
    tp = pids[result] == pids[:, np.newaxis]
    #Remove all predictions beyond the number of
    #solutions of tested problem
    tp[~mask] = False
    #Get only tested problem
    valid = r[pids] > 0
    #Compute cumulative probability of correct predictions
    p = np.cumsum(tp, axis=1, 
        dtype = np.float32) / np.arange(1, max_r+1, 
                            dtype = np.float32)[np.newaxis, :]
    #average across similarity prediction for each tested problem
    ap = (p * tp).sum(axis=1)[valid] / r[pids][valid]
    val = np.mean(ap).item()
    return val

def main(args):
    """
    Main function of program for computing MAP at R metric
    Arguments are descibed below
    """
    if not os.path.exists(args.similarities):
        sys.exit(f"Directory {args.similarities} with similarity analysis does not exist")
    with open(f"{args.similarities}/problem_indices.pcl", "rb") as _f:
        pids = pickle.load(_f)

    with open(f"{args.similarities}/similarity_probabilities.pcl", "rb") as _f:
        sim = pickle.load(_f)
    
    n_problem_solutions = pids.shape[0]
    if sim.shape[0] != n_problem_solutions * n_problem_solutions:
        sys.exit(
            f"Number of similarity samples {n_problem_solutions.shape[0]} ",
            f" is not square of number of problem solutions {n_problem_solutions}")
    map_r = map_at_r(sim.reshape(n_problem_solutions, n_problem_solutions),
                     pids)

    print("Map@R is ", map_r)

#######################################################################
# Command line arguments of are described below
#######################################################################
if __name__ == '__main__':
    print("\nComputation of MAP at R metric of similarity analysis")

    #Command-line arguments
    parser = argparse.ArgumentParser(
        description = "Computation of MAP at R metric")
    parser.add_argument('similarities', type=str,
                        help='Directory with similarity results')
    args = parser.parse_args()

    print("Parameter settings used:")
    for k,v in sorted(vars(args).items()):
        print("{}: {}".format(k,v))

    main(args)
