"""
"""
import sys
import os
import math
import argparse
import pickle
from VectorKMeans import VectorsClustered

sys.path.extend(["../BagOfTokens"])
from DatasetLoader import BagOfTokensLoader

def main(args):
    """
    Main function of program for bag of tokens cluster analysis of 
    of one problem source code solutions

    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    ds = BagOfTokensLoader(args.samples, args.tokens)
    samples, _, _, _, _, = ds.loadProblem(args.problem)
    sol_clustered = VectorsClustered(samples)
    sol_clustered.kmeansCluster(args.clusters)
    sol_clustered.printClustersStat()
#######################################################################
# Command line arguments of are described below
#######################################################################
if __name__ == '__main__':
    print("\nCLUSTER ANALAYSIS OF BAG OF TOKENS OF SOURCE CODE SOLUTIONS")

    #Command-line arguments
    parser = argparse.ArgumentParser(
        description = "Cluster analysis of bags of tokens of source code solution")
    parser.add_argument('samples',
                        type=str, help='path to data directory')
    parser.add_argument('problem',
                        type=str, help='filename of problem')
    parser.add_argument('--tokens', default=17, type=int,
                        help='number of tokens')
    parser.add_argument('--clusters', default=8, type=int,
                        help='number of clusters')
    args = parser.parse_args()

    print("Parameter settings used:")
    for k,v in sorted(vars(args).items()):
        print("{}: {}".format(k,v))

    main(args)


"""
#!!! OLD Experimental code
#-------------------------------------------
ds = BagOfTokensLoader("../../DataSet/ds5c/", 17)
samples = []
ds.loadSolutions("../../DataSet/ds5c/ALDS1_11_B.tkn", samples)
samples, _ = zip(*samples)
samples = np.stack(samples)
n_clusters=32
kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(samples)
#print(kmeans.labels_)
centers = kmeans.cluster_centers_
print(kmeans.inertia_)

for i in range(n_clusters):
    line = ""
    for j in range(n_clusters):
        line += "{:4.2f} ".format(np.linalg.norm(centers[i] - centers[j]))
    print(i, line + "\n")
#-----End of OLD Experimental code  -------------
"""
