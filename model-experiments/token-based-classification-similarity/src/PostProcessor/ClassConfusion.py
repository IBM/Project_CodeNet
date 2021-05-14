"""
Module for constructing and analysing confusion matrix
of source code classification
Prints confusion report and writes down 
statistics of classification accuracy
"""
import sys
import os
from abc import ABC, abstractmethod
import numpy as np
import csv
import sklearn.metrics as metrics

from ConfusionAnalysis import ConfusionAnalysis

class ClassConfusAnalysis(ConfusionAnalysis):
    """
    Class for constructing and analysing confusion matrix
    """
    def __init__(self, probabilities, labels, solutions, 
                 problems, extreme = 0.1):
        """
        Construct confusion matrix
        Parameters:
        - probabilities - classification probabilities as numpy array
        - labels        - list of samples labels
        - solutions     - list of file names of problem solutions,
                          i.e sample names for this case
        - problems      - list of problems 
                          i.e names of classes for this case
        - extreme       - fraction of cases to be reported 
                          as extreme ones
        """
        super(ClassConfusAnalysis, self).__init__(probabilities, 
            np.asarray(labels, dtype = np.int32), 
            solutions, problems, extreme)
        self.class_stat_fn = "class_statistics.lst"
        self.class_stat_csv = "class_statistics.csv"
        self.confused_classes_fn = "confused_classes.lst"
        self.confused_classes_csv = "confused_classes.csv"
        #Number of best and worst correct predictions of
        #worst classified classes to report
        self.n_right_pred_report = 32
        #Max number of confusions to report
        self.max_n_confus_report = 64
        #Max number of worst and best classes to report mistakes
        self.max_n_class_report = 16
        #Max number of misclassifications to report
        self.max_n_misclass_report = 32
        #Confidence in classification
        self.confidence = np.max(probabilities, axis=1)
        #Number of samples in each class as numpy array
        self._n_class_samples = self.conf_mat.sum(axis=1)
        #Number of predictions of each class as numpy array
        self._n_class_predict = self.conf_mat.sum(axis=0)
        #Number of correct predictions of each class
        self.n_corr_class_samples = np.diag(self.conf_mat)
        #Confusion matrix normalized with number of class samples
        self.norm_conf_mat = \
            self.conf_mat / (self._n_class_samples[:, np.newaxis])
        #Accuracy of class predictions as python list
        self.class_accuracy = \
            np.diag(self.norm_conf_mat).tolist()

    def getPredictions(self):
        """
        Get classification predictions
        Returns:  classification predictions  
        """
        return np.argmax(self.probabilities, axis=1)

    def reportClasses(self, classes, f):
        """
        Report classification of set of classes
        Parameters:
        - classes  -- classes to report
        - f        -- file to write report to
        """
        self.reportClassProblems(self._n_class_samples,
                                 self.n_corr_class_samples,
                                 classes, f)
        self.csvClassProblems(self._n_class_samples,
                                 self.n_corr_class_samples,
                                 classes)

    def csvClassProblems(self, tot_samples, corr_samples, 
                         problems):
        """
        Writes absolute and relative numbers of 
        correct and incorrect classifications of problems 
        to csv file
        Parameters:
        - tot_samples  -- vector of total numbers of samples 
                          corresponding to each problem
        - corr_samples -- vector of numbers of correctly classified samples
        - problems     -- list of indices of problems to report
        """
        with open(f"{self.report_dir}/{self.class_stat_csv}",
                  'w', newline='') as _csv_f:
            _w = csv.writer(_csv_f)
            _w.writerow(("Label",  "Accuracy", "N files", 
                       "N errors", "Problem"))
            for _c in problems:
                _w.writerow((_c, 
                            100.0 * float(corr_samples[_c]) / float(tot_samples[_c]),
                            tot_samples[_c], tot_samples[_c] - corr_samples[_c],
                             self.problems[_c]))

    def reportClassProblems(self, tot_samples, corr_samples, 
                            problems, f):
        """
        Writes absolute and relative numbers of 
        correct and incorrect classifications of problems

        Parameters:
        - tot_samples  -- vector of total numbers of samples 
                          corresponding to each problem
        - corr_samples -- vector of numbers of correctly classified samples
        - problems     -- list of indices of problems to report
        - f            -- file to write to
        """
        f.write("Label  Accur    Size  N errs   Problem name\n")
        for _c in sorted(problems,
            key = lambda _p: float(corr_samples[_p]) / float(tot_samples[_p])):
            f.write("{:4d}  {:5.1f}%   {:5d}   {:5d}   {:s}\n".
                    format(_c, 
                           100.0 * float(corr_samples[_c]) / float(tot_samples[_c]),
                           tot_samples[_c], tot_samples[_c] - corr_samples[_c],
                           self.problems[_c]))

    def getRightClassifications(self, classes):
        """
        Get list of correct classifications of given classes
        Parameters:
        - classes  -- indices of classes to report
        Returns list of lists of pairs, each of which is 
                <index of classified sample, confidence>
                Sublists correspond to given classes
                Each sublist is sorted according to confidence
        """
        _classifications = [[] for i in range(len(classes))]
        for _i in range(self._n_samples):
            if (self.predictions[_i] == self.labels[_i] and
                self.labels[_i] in classes):
                _idx = classes.index(self.labels[_i])
                _classifications[_idx].append((self.solutions[_i],
                                               self.confidence[_i]))
        for _cls in _classifications:
            if len(_cls) < 2: continue
            _cls.sort(key = lambda _c: _c[1], reverse = True)
        return _classifications

    def reportRightClassifications(self, classes, f):
        """
        Report correct classifications  of given classes
        Parameters:
        - classes          -- indices of classes to report
        - f                -- file to write to
        """
        _classifications = self.getRightClassifications(classes)
        for _i, _c in enumerate(sorted(classes, 
                        key = lambda _cl: self.class_accuracy[_cl])):
            if not _classifications[_i]: continue        
            f.write(f"#{_i}  Problem {self.problems[_c]} number {_c} " + 
                    f"is classified with {100.0 *self.class_accuracy[_c]:.2f}% " + 
                    "accuracy\n")
            f.write(f"There are {len(_classifications[_i])} correct classifications\n")
            if len(_classifications[_i]) < 2 * self.n_right_pred_report + 3:
                self.writeClassifications(_classifications[_i],
                                         "Solution predictions", f)
            else:
                self.writeClassifications(
                    _classifications[_i][: self.n_right_pred_report],
                    "Strongest predictions", f)                
                self.writeClassifications(
                    _classifications[_i][-self.n_right_pred_report :],
                    "Weakest predictions", f)
                
    def writeClassifications(self, predictions, title, f):
        """
        Write down information on classification predictions
        Parameters:
        - predictions - list of predictions each of which is
                        a pair <index of classified sample, confidence>
        - title       - text to put in the first line
        - f           - file to write to
        """
        _line = title
        _punct = ': '
        for _pred in predictions:
            _line += _punct
            _punct = ', '
            if len(_line) > 80:
                f.write(_line + "\n")
                _line = ""
            _line += f"{_pred[0]}/{100 * _pred[1]:.2f}%"
        if _line: f.write(_line + "\n")        
             
    def getClassMistakes(self, classes):
        """
        Get list of misclassifications for given classes
        Parameters:
        - classes  -- indices of classes to report
        Returns list of lists of miscalssifications:
                pairs <index of classified sample, prediction>
                Sublists gives misclassifications of classes
        """
        #Number of classification mistakes
        _mistakes = [[] for i in range(len(classes))]
        for _i in range(self._n_samples):
            if (self.predictions[_i] != self.labels[_i] and
                self.labels[_i] in classes):
                _bad_idx = classes.index(self.labels[_i])
                _mistakes[_bad_idx].append((_i, self.predictions[_i]))
        return _mistakes

    def reportMisclassifications(self, classes, mistakes, f):
        """
        Report misclassifications of given classes
        Parameters:
        - classes  -- indices of classes to report
        - mistakes -- list of lists of miscalssifications:
                      pairs <classified class index, prediction>
                      Sublists gives misclassifications of classes
        - f        -- file to write to
        """
        for _i, _c in enumerate(sorted(classes, 
                            key = lambda _cl: self.class_accuracy[_cl])):
            if not mistakes[_i]: continue
            f.write(f"#{_i}  Problem {self.problems[_c]} number {_c} " + 
                    f"is classified with {100.0 *self.class_accuracy[_c]:.2f}% " + 
                    "accuracy\n")
            _line = f"There are {len(mistakes[_i])} misclassified solutions"
            _punct = ': '
            for _err in sorted(mistakes[_i][: self.max_n_misclass_report], 
                    key = lambda _e: self.confidence[_e[0]], 
                               reverse = True):
                _conf = "{:5.2f}".format(100.0 * self.confidence[_err[0]])
                _line += _punct
                _punct = ', '
                if len(_line) > 80:
                    f.write(_line + "\n")
                    _line = ""
                _line += (self.solutions[_err[0]] + " => " + 
                          self.problems[_err[1]] + ' (' + _conf + '%)')
            if _line: f.write(_line + "\n")

    def reportConfusedClasses(self):
        """
        Report worst classification confusions,
        i.e. confused pairs of confused problems
        """
        _confusions = self.worstConfusions()
        _confusions = [_c for _c in _confusions if _c[0] != _c[1]]
        with open(f"{self.report_dir}/{self.confused_classes_fn}", 'w') as _lst, \
             open(f"{self.report_dir}/{self.confused_classes_csv}",
                  'w', newline='') as _csv:
            _lst.write("Most confused pairs of problems\n")
            _lst.write("-------------------------------\n")
            _lst.write(
                " Orig   Pred    N        N      %%    Original      Predicted\n")
            _lst.write(
                "Label  Label Samples  Errors  Errors  Problem       Problem  \n")
            _w = csv.writer(_csv)
            _w.writerow(("Original_Label", "Predicted_Label",
                         "N_samples", 
                        "%%_of_errors", "Original_Problem", 
                        "Predicted Problem"))
            for _c in sorted(_confusions,
                             key = lambda _conf:
                             self.norm_conf_mat[_conf[0], _conf[1]],
                             reverse = True):
                _lorig, _lpred = _c
                _lst.write("{:5d}  {:5d}  {:6d}  {:6d}  {:6.2f}  {:12s}  {:12s}\n".
                    format(_lorig, _lpred,
                           self._n_class_samples[_lorig],
                           self.conf_mat[_lorig, _lpred],
                           self.norm_conf_mat[_lorig, _lpred] * 100,
                           self.problems[_lorig], self.problems[_lpred]))
                _w.writerow((_lorig, _lpred, self._n_class_samples[_lorig],
                             self.norm_conf_mat[_lorig, _lpred] * 100,
                             self.problems[_lorig], self.problems[_lpred]))

    def worstConfusions(self):
        """
        Compute worst confusions of classification
        Returns list of pairs , each of which is
        a classified problem and the problem predicted
        """
        _n_confusions_report = \
            max(min(int(self._n_problems * self._n_problems * 
                self._n_extreme_cases), self.max_n_confus_report),
                self._n_problems)
        _flat_conf = self.norm_conf_mat.flatten()
        _part_index = \
            self._n_problems * self._n_problems
        _part_index -= (_n_confusions_report + self._n_problems)
        _worst_idx =  \
            np.argpartition(_flat_conf, _part_index)[_part_index :]
        _worst_idx =  \
            np.unravel_index(_worst_idx, 
                             self.norm_conf_mat.shape)
        _worst_idx = zip(_worst_idx[0].tolist(), _worst_idx[1].tolist())
        return _worst_idx
                
    def printClassAccuracy(self, f):
        """
        Report accuracy of classifications
        and their misclassified samples
        Parameters:
        -f   -- file to write report to
        """
        f.write("\nClassification statistics\n")
        f.write("-------------------------\n")
        self.reportClasses(range(self._n_problems), f)
        _class_acc = \
            sorted(zip(range(self._n_problems), self.class_accuracy), 
                   key = lambda _s : _s[1])
        _n_class_report = min(self._n_problems // 2,
                             self.max_n_class_report)
        _classes = _class_acc[: _n_class_report]
        _worst_classes = list(zip(*_classes))[0]
        _classes = _class_acc[-_n_class_report :]
        _best_classes = list(zip(*_classes))[0]
        _mistakes  = self.getClassMistakes(_worst_classes + _best_classes)
        f.write("\nWorst classified classes\n")
        f.write("--------------------------\n")
        self.reportClasses(_worst_classes, f)
        f.write("\nMisclassifications of the worst classified classes:\n")
        f.write("-----------------------------------------------------\n")
        self.reportMisclassifications(_worst_classes,
                    _mistakes[: len(_worst_classes)], f)
        f.write("\nCorrect classifications of the worst classified classes:\n")
        f.write("-----------------------------------------------------\n")
        self.reportRightClassifications(_worst_classes, f)
        f.write("\nBest classified classes\n")
        f.write("-------------------------\n")
        self.reportClasses(_best_classes, f)
        f.write("\nMisclassifications of the best classified classes:\n")
        f.write("---------------------------------------------------\n")
        self.reportMisclassifications(_best_classes, 
                                      _mistakes[len(_worst_classes) :], f)
                                      
    def writeReport(self):
        """
        Write report on classification and misclassification
        """
        with open(f"{self.report_dir}/{self._conf_mat_fn}", 'w') as _f:
            _f.write("Unnormalized confusion matrix\n")
            _f.write("row and column indices are labels\n")
            _f.write("---------------------------------\n")
            self.writeLargeMatrixInt(self.conf_mat, _f)
            _f.write("Normalized confusion matrix\n")
            _f.write("row and column indices are labels\n")
            _f.write("---------------------------------\n")
            self.writeLargeMatrixPct(self.norm_conf_mat, _f, 100.0)
        with open(f"{self.report_dir}/{self.class_stat_fn}", 'w') as _f:
            self.printClassAccuracy(_f)
        self.reportConfusedClasses()
        print("\nClassification report")
        print("-----------------------")
        print(metrics.classification_report(self.labels, 
                                    self.predictions,
                                    target_names = self.problems))
#---------------- End of class ClassConfusAnalysis ----------------------    

