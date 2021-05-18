"""
Module for analysing confusion matrix and accuracy 
of similarity analysis of source code
"""
import sys
import os
from abc import ABC, abstractmethod
import pickle
import numpy as np
import sklearn.metrics as metrics

from ConfusionAnalysis import ConfusionAnalysis

class SimilConfusAnalysis(ConfusionAnalysis):
    """
    Class for constructing and analysing confusion matrix
    """
    @classmethod
    def similarityToProb(cls, sim_metric, labels01):
        """
        Convert similarity metric to probabilities
        Parameters:
        - sim_metric  -- similarity metric
       - labels01        -- label types flag:
                             True:   0/1 labels
                             Flase:  -1/+1 labels
        """
        if labels01: 
            return sim_metric
        return (sim_metric + 1.0) / 2.0

    def __init__(self, probabilities, labels, solutions, 
                 problems, annotations, extreme = 0.1,
                 labels01 = True):
        """
        Construct confusion matrix
        Parameters:
        - probabilities - classification probabilities as numpy array
        - labels       - labels of samples as numpy array
        - solutions    - list of sub-lists of file names of problem solutions
                         Each sub-list contains sample names of one problem
                         All sublists are part of the whole list of sample names
        - problems     - list of names of problems
        - annotations  - list of sample annotations
                         Each sample is represented as 4-tuple
                         <problem 1, solution 1, problem 2, solution 2>,
                         where problems and solutions are their indices
        - extreme      - fraction of cases to be reported 
                         as extreme ones
        - labels01        -- label types flag:
                             True:   0/1 labels
                             Flase:  -1/+1 labels
        """
        super(SimilConfusAnalysis, self).__init__(
            self.similarityToProb(probabilities, labels01), 
            self.similarityToProb(labels, labels01), 
            solutions, problems, extreme)
        self.annotations = annotations
        self.simil_stat_fn = "similarity_stat.lst"
        self.dissimil_stat_fn = "dissimilarity_stat.lst"
        self.max_n_cases_report = 32
        self._n_cases_report = min(self.max_n_cases_report, self._n_extreme_cases)
        self.tn, self.fp, self.fn, self.tp = self.conf_mat.ravel()
        self.precision_score = \
            metrics.precision_score(self.labels, self.predictions)
        self.recall_score = \
            metrics.recall_score(self.labels, self.predictions)
        self.f1_score = \
            metrics.f1_score(self.labels, self.predictions)
        self.fbeta_score_05 = \
            metrics.fbeta_score(self.labels, self.predictions, beta=0.5)
        self.fbeta_score_1 = \
            metrics.fbeta_score(self.labels, self.predictions, beta=1)
        self.fbeta_score_2 = \
            metrics.fbeta_score(self.labels, self.predictions, beta=2)
        self.precision, self.recall, self.threshold = \
            metrics.precision_recall_curve(self.labels, self.probabilities)
        self.average_precision_score = \
            metrics.average_precision_score(self.labels, self.probabilities)

    def getPredictions(self):
        """
        Get classification predictions
        Returns: - classification predictions  
        """
        return self.probabilities.round()[:,0].astype(int)

    def printConfusionReport(self):
        """"
        Print confusion report
        """
        print("\nClassification report")
        print("-----------------------")
        print(metrics.classification_report(
            self.labels, self.predictions,
            target_names = ["dissimilar", "similar"]))
        print("\nConfusion matrix")
        print("----------------")
        print("            Dissimilar  Similar")
        print("Dissimilar     {:7d}  {:7d}".
              format(self.conf_mat[0, 0], self.conf_mat[0,1]))
        print("Similar        {:7d}  {:7d}".
              format(self.conf_mat[1, 0], self.conf_mat[1, 1]))
        print("\n")
        print(f"tn = {self.tn}, fp = {self.fp}," + 
              f"fn = {self.fn}, tp = {self.tp}")
        print(f"precision_score = {self.precision_score:.4f}")
        print(f"recall_score = {self.recall_score:.4f}")
        print(f"f1_score = {self.f1_score:.4f}")
        print(f"fbeta_score(0.5) = {self.fbeta_score_05:.4f}")
        print(f"fbeta_score(1) = {self.fbeta_score_1:.4f}")
        print(f"fbeta_score(2) = {self.fbeta_score_2:.4f}")
        print(f"average_precision_score = {self.average_precision_score:.4f}")
        with open("roc.pcl", 'wb') as _jar:
            _roc = {"precision" : self.precision, 
                    "recall"    : self.recall, 
                    "threshold" : self.threshold}
            pickle.dump(_roc, _jar)

    def similarityConfusion(self):
        """
        Compute and print following matricies:
        - matrix of numbers of similarity/dissimilarity tests 
          for solutions of pairs of problems
        - matrix of correct detections of similarity/dissimilarity
          of solutions of pairs of problems
        """
        #Matrix of numbers of cases when similarity or dissimilarity 
        #of two solutions is detected correctly
        self.sim_num_correct = \
            np.zeros((self._n_problems, self._n_problems), dtype=int)
        #Matrix of total numbers of similarity/dissimilarity tests 
        self.sim_num_samples = \
            np.zeros((self._n_problems, self._n_problems), dtype=int)
        for _s, _p, _l in zip(self.annotations, self.predictions, 
                              self.labels):
            _problem1, _, _problem2, _ = _s
            self.sim_num_samples[_problem1, _problem2] += 1
            self.sim_num_correct[_problem1, _problem2] += int(_p == _l)

    def compSimTestAccuracy(self):
        """
        Compute lists of accuracy of similarity and dissimilarity detection
        Returns:
        - list of tested problems
          i-th element of list is either True or False 
          indicating if solutions of i-th problem were tested
        - list of accuracy of similarity detection
          An element of the list is a pair: <problem, accuracy>
        - list of accuracy of dissimilarity tests
          Elements of this list are tuples
          <problem1, problem2, acc1, acc2, acc1+acc2, abs(acc1-acc2)>
          If any accuracy acc1(acc2) is not defined: 
             acc1(acc2) = None
             acc1+acc2  = 2*acc2(2*acc1)
             abs(acc1-acc2) = 0
        """
        _sim = []
        _dissim = []
        _tested_problems = [False] * len(self.problems)
        for _i in range(self._n_problems):
            for _j in range(self._n_problems):
                if _j > _i: break
                _ntests_ij = self.sim_num_samples[_i, _j]
                _ntests_ji = self.sim_num_samples[_j, _i]
                if _ntests_ij + _ntests_ji == 0: continue
                _tested_problems[_i] = True
                _tested_problems[_j] = True
                if _j == _i:
                    _acc = self.sim_num_correct[_i, _j] / _ntests_ij
                    _sim.append((_i, _acc))
                    continue
                if _ntests_ij == 0:
                    _acc_ji = self.sim_num_correct[_j, _i] / _ntests_ji
                    _dissim.append((_j, _i, None, _acc_ji, _acc_ji, 0))
                    continue
                if _ntests_ji == 0:
                    _acc_ij = self.sim_num_correct[_i, _j] / _ntests_ij
                    _dissim.append((_i, _j,  _acc_ij, None, _acc_ij, 0))
                    continue
                _acc_ij = self.sim_num_correct[_i, _j] / _ntests_ij
                _acc_ji = self.sim_num_correct[_j, _i] / _ntests_ji
                _acc = ((self.sim_num_correct[_i, _j] + 
                         self.sim_num_correct[_j, _i]) /
                        (_ntests_ij + _ntests_ji))
                _dissim.append((_i, _j,  _acc_ij, _acc_ji, _acc, 
                                abs(_acc_ij - _acc_ji)))
        return _tested_problems, _sim, _dissim

    def writeSimDissimAccuracy(self, tested_problems, f):
        """
        Write matrix of accuracy of similarity/dissimilarity detection
        Parameters:
        - tested_problems  -- list of tested problems
                              i-th element of list is either True or False 
                              indicating if solutions of i-th problem 
                              were tested
        - f                -- file to write to
        """
        f.write("Matrix of similarity/dissimilarity detection accuracy\n")
        f.write("-----------------------------------------------------\n")
        _s = "    "
        for _i, _tested in enumerate(tested_problems):
            if not _tested: continue
            _s += "{:5d} ".format(_i)
        f.write(_s + "\n")
        for _i, _tested_row in enumerate(tested_problems): 
            if not _tested_row: continue
            _s = "{:3d} ".format(_i)
            for _j, _tested_col in enumerate(tested_problems):
                if not _tested_col: continue
                if self.sim_num_samples[_i, _j]:
                    _acc = self.sim_num_correct[_i, _j] / self.sim_num_samples[_i, _j]
                    _s += "{:5.1f} ".format(100.0 * _acc)
                else:
                    _s += " -   "
            f.write(_s + "\n")

    def reportSimilarityProblems(self, sim_accuracy, f):
        """
        Write down accuracy of similarity detection 
        of two solutions of same problem
        Parameters:
        - sim_accuracy  -- list of accuracy of similarity detection
                            An element of the list is a pair: 
                            <problem, accuracy>
        - f             -- file to write the report to
        """
        f.write("#    Probl   Accu-      N      N     Problem name\n")
        f.write("     numb    racy     tests  errors              \n")
        for _i, _p_acc in enumerate(sim_accuracy):
            _p = _p_acc[0]
            f.write("{:4d}  {:4d}  {:6.2f}%   {:5d}  {:5d}   {:s}\n".
                  format(_i, _p, _p_acc[1] * 100.0, 
                         self.sim_num_samples[_p, _p], 
                         self.sim_num_samples[_p, _p] - self.sim_num_correct[_p, _p],
                         self.problems[_p]))

    def getSimilarityMistakes(self, problems):
        """
        Get list of errors in similarity detection 
        of problem solutions
        Parameters:
        -  problems -- indices of problems to report
        Returns: list of lists of indices of samples for which
        it was incorrectly decided that they give dissimilar solutions
        """
        #Number of mistakes to detect that two solutions 
        #of same problem are similar
        _mistakes = [[] for i in range(len(problems))]
        for _i in range(self._n_samples):
            _problem1, _solution1, _problem2, _solution2 = self.annotations[_i]
            if _problem1 != _problem2: continue
            if (self.predictions[_i] != self.labels[_i] and 
                _problem1 in problems):
                _bad_idx = problems.index(_problem1)
                _mistakes[_bad_idx].append(_i)
        return _mistakes

    def reportSimilarityMisclass(self, sim_accuracy, mistakes, f):
        """
        Report errors in similarity detection of problem solutions
        Parameters:
        - sim_accuracy  -- list of accuracy of similarity detection
                           An element of the list is a pair: 
                           <problem, accuracy>
        - problems  --  problems to report
        - mistakes  --  list of lists of indices of samples for which
                        it was incorrectly decided that they give 
                        disssimilar solutions
        - f         -- to write report to
        """
        for _i, _c in enumerate(sim_accuracy):
            _p, _a = _c
            if not mistakes[_i]: continue
            f.write(f"#{_i}  For problem {self.problems[_p]} number {_p} " + 
                    f"having {100.0 * _a : .2f}% accuracy of similarity detection\n")
            f.write(f"there are {len(mistakes[_i])} " + 
                    "incorrectly detected missimilarities:\n")
            self.writeMistakes(mistakes[_i], f)

    def writeMistakes(self, mistakes, f):
        """
        Report problem solutions whose similarity was 
        incorrectly classified
        Parameters:
        - mistakes     -- list of indices of incorrectly 
                          classified samples
        - f            -- to write report to
        """
        def _getConf(s):
            """
            Get confedence of predicting sample s
            Convert sigmoid output to probability
            """
            _p = self.probabilities[s][0]
            return _p if self.predictions[s] else 1 - _p
        _n_errs_report = min(len(mistakes), self.max_n_cases_report)
        _line = ""
        _punct = ", "
        for _i, _err_sample in enumerate(sorted(mistakes,
                key =_getConf, reverse = True)[: _n_errs_report]):
            _p1, _solution1, _p2, _solution2 = \
                self.annotations[_err_sample]
            #Convert sigmoid output to probability
            #_p = self.probabilities[_err_sample][0]
            #_conf = _p if self.predictions[_err_sample] else 1 - _p
            _conf = "{:6.2f}".format(100.0 * _getConf(_err_sample))
            if len(_line) > 80:
                f.write(_line + "\n")
                _line = ""
            if _i + 1 == len(mistakes):
                _punct = ""
            _line += (self.solutions[_p1][_solution1] + 
                      "/" + self.solutions[_p2][_solution2] + '(' + 
                      _conf + '%)' + _punct)
        if _line: f.write(_line + "\n\n")
                
    def reportSimilarity(self, sim_accuracy):
        """
        Analyze and report information on detection of similarity 
        of problem solutions
        Parameters:
        - sim_accuracy  -- list of accuracy of similarity detection
                            An element of the list is a pair: <problem, accuracy>
        """
        with open(f"{self.report_dir}/{self.simil_stat_fn}", 'w') as _f:        
            _f.write("Statistics on similarity detection\n")
            _f.write("----------------------------------\n")
            self.reportSimilarityProblems(sim_accuracy, _f)
            _sim_acc =\
                    sorted(sim_accuracy, key = lambda _s : _s[1])
            _worst_problems = _sim_acc[: self._n_cases_report]
            _best_problems = _sim_acc[-self._n_cases_report :]
            _problems = list(zip(*(_worst_problems + _best_problems)))[0]
            _mistakes  = self.getSimilarityMistakes(_problems)
            _f.write("\nProblems with worst similarity detection\n")
            _f.write("------------------------------------------\n")
            self.reportSimilarityProblems(_worst_problems, _f)
            _f.write("\nSimilarity detection errors for worst problems:\n")
            _f.write("-------------------------------------------------\n")
            self.reportSimilarityMisclass(_worst_problems,
                                    _mistakes[: len(_worst_problems)], _f)
            _f.write("\nProblems with best similarity detection\n")
            _f.write("------------------------------------------\n")
            self.reportSimilarityProblems(_best_problems, _f)
            _f.write("\nSimilarity detection errors for best problems:\n")
            _f.write("-----------------------------------------------\n")
            self.reportSimilarityMisclass(_best_problems,
                                _mistakes[len(_worst_problems) :], _f)

    def reportDissimilarityProblems(self, tests, f):
        """
        Print report on accuracy of dissimilarity detection
        of solutions of pairs of problems
        Parameters:
        - tests -- list of accuracy of dissimilarity tests
                   Elements of this list are tuples
                   <problem1, problem2, acc1, acc2, acc1+acc2, abs(acc1-acc2)>
                   If any accuracy acc1(acc2) is not defined: 
                   acc1(acc2) = None
                   acc1+acc2  = 2*acc2(2*acc1)
                   abs(acc1-acc2) = 0
                   * acc1 is for similarity of problem1 to problem2 solutions
                   * acc2 is for similarity of problem2 to problem1 solutions
        - f     -- File to write to
        """
        f.write("#               1-st problem                                   2-nd problem        \n")
        f.write("    Indx    Name         tsts  errs  Acc-cy Indx   Name          Tsts  Errs  Acc-cy\n")
        f.write("-----------------------------------------------------------------------------------\n")
        for _i, _t in enumerate(tests):
            _p1, _p2, _a1, _a2, _a12, _diff = _t
            _acc1 = "{:6.2f}%".format(100.0 * _a1) if _a1 is not None else "   -   "
            _acc2 = "{:6.2f}%".format(100.0 * _a2) if _a2 is not None else "   -   "
            f.write("{:3d} {:4d} {:16s} {:4d} {:4d} {:5s} {:4d} {:16s} {:4d} {:4d} {:5s}\n".
                format(_i, _p1, self.problems[_p1], 
                       self.sim_num_samples[_p1, _p2], 
                       self.sim_num_samples[_p1, _p2] - self.sim_num_correct[_p1, _p2],
                       _acc1,
                       _p2, self.problems[_p2], 
                       self.sim_num_samples[_p2, _p1], 
                       self.sim_num_samples[_p2, _p1] - self.sim_num_correct[_p2, _p1],
                       _acc2))

    def getDissimilarityMistakes(self, tests):
        """
        Get list of errors in dissimilarity detection 
        of problem solutions
        Parameters:
        -  tests -- list of accuracy of dissimilarity tests
                    Elements of this list are tuples
                    <problem1, problem2, acc1, acc2, acc1+acc2, abs(acc1-acc2)>
                    If any accuracy acc1(acc2) is not defined: 
                    acc1(acc2) = None
                    acc1+acc2  = 2*acc2(2*acc1)
                    abs(acc1-acc2) = 0
        Returns: list of lists of indices of samples for which
        it was incorrectly decided that they represent similar solutions
        """
        #Number of mistakes to detect that two solutions 
        #of same problem are similar
        _test_ids_1 = [(_x[0], _x[1]) for _x in tests]
        _test_ids_2 = [(_x[1], _x[0]) for _x in tests]
        _mistakes = [[] for i in range(len(tests))]
        for _i in range(self._n_samples):
            _problem1, _solution1, _problem2, _solution2 = self.annotations[_i]
            if _problem1 == _problem2: continue
            if self.predictions[_i] == self.labels[_i]: continue
            _t = (_problem1, _problem2)
            if _t in _test_ids_1:
                _bad_idx = _test_ids_1.index(_t)
                _mistakes[_bad_idx].append(_i)
            if _t in _test_ids_2:
                _bad_idx = _test_ids_2.index(_t)
                _mistakes[_bad_idx].append(_i)
        return _mistakes

    def reportDissimilarityMisclass(self, tests, mistakes, f):
        """
        Report errors in dissimilarity detection of problem solutions
        Parameters:
        - tests     --   tests to report
                         list of accuracy of dissimilarity tests
                         Elements of this list are tuples
                         <problem1, problem2, acc1, acc2, acc1+acc2, abs(acc1-acc2)>
                         If any accuracy acc1(acc2) is not defined: 
                         acc1(acc2) = None
                         acc1+acc2  = 2*acc2(2*acc1)
                         abs(acc1-acc2) = 0
        - mistakes  --  list of lists of indices of samples for which
        - f         -- file to write to
        it was incorrectly decided that they give similar solutions
        """
        for _i, _t in enumerate(tests):
            if not mistakes[_i]: continue
            _p1, _p2, _a1, _a2, _a12, _diff = _t
            _acc1 = "{:6.2f}%".format(100.0 * _a1) if _a1 is not None else "-"
            _acc2 = "{:6.2f}%".format(100.0 * _a2) if _a2 is not None else "-"
            f.write(f"#{_i}  For problem {self.problems[_p1]} number {_p1} " + 
                    f"and problem {self.problems[_p2]} number {_p2} " + 
                    f"having {_acc1} and {_acc2} " + 
                    "accuracies of dissimilarity detection\n")
            f.write(f"There are {len(mistakes[_i])} " + 
                    "incorrectly detected similarities:\n")
            self.writeMistakes(mistakes[_i], f)

    def reportDissimilarity(self, dissim_acc):
        """
        Analyze and report information on detection of dissimilarity 
        of problem solutions
        Parameters:
        - dissim_acc  -- list of accuracy of dissimilarity tests
                         Elements of this list are tuples
                         <problem1, problem2, acc1, acc2, acc1+acc2, abs(acc1-acc2)>
                         If any accuracy acc1(acc2) is not defined: 
                         acc1(acc2) = None
                         acc1+acc2  = 2*acc2(2*acc1)
                         abs(acc1-acc2) = 0
        """
        #Sort according to accuracy minimum
        dissim_acc.sort(key = lambda _s : _s[4])
        _worst_tests = dissim_acc[: self._n_cases_report]
        _best_tests = dissim_acc[-self._n_cases_report :]
        _mistakes = self.getDissimilarityMistakes(_worst_tests + _best_tests)
        with open(f"{self.report_dir}/{self.dissimil_stat_fn}", 'w') as _f:        
            _f.write("\nWorst dissimilarity tests:\n")
            _f.write("----------------------------\n")
            self.reportDissimilarityProblems(_worst_tests, _f)
            self.reportDissimilarityMisclass(_worst_tests, 
                                _mistakes[: len(_worst_tests)], _f)
            _f.write("\nBest dissimilarity tests:\n")
            _f.write("-------------------------\n")
            self.reportDissimilarityProblems(_best_tests, _f)
            self.reportDissimilarityMisclass(_best_tests, 
                            _mistakes[len(_worst_tests) :], _f)
            _f.write("\nTests with high asymmetry of similarity detection:\n")
            _f.write("---------------------------------------------------\n")
            #Sort according to accuracy discrepancy
            dissim_acc.sort(key = lambda _s : _s[5])
            _asymm_tests = dissim_acc[-self._n_cases_report :]
            _mistakes = self.getDissimilarityMistakes(_asymm_tests)
            self.reportDissimilarityProblems(_asymm_tests, _f)
            self.reportDissimilarityMisclass(_asymm_tests, _mistakes, _f)

    def writeReport(self):
        """
        Write report on similarity analysis
        """
        self.printConfusionReport()
        self.similarityConfusion()
        _tested_problems, _sim_acc, _dissim_acc = \
                                self.compSimTestAccuracy()
        with open(f"{self.report_dir}/{self._conf_mat_fn}", 'w') as _f:
            self.writeSimDissimAccuracy(_tested_problems, _f)
        self.reportSimilarity(_sim_acc)
        self.reportDissimilarity(_dissim_acc)
#---------------- End of class  ConfusionAnalysis ----------------------




    
