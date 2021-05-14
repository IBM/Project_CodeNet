"""
Module for constracting TF dataset 
from two lists of sequences of tokens and array of labels
"""
import sys
import os
import math

import numpy as np
import tensorflow as tf

from TokensSimilDS import SimilarityDSMaker
from DsUtilities  import makeShardOptions

class genConstructor():
    """
    Class for constructing generators to make TF datasets
    To be used for further experiments
    """
    def __init__(self, samples, problem_solutions):
        """
        Parameters:

        """
        self._samples = samples
        self._problem_solutions  = problem_solutions

        def getGenerators():
            """
            """
            def gen4DS_1st():
                """
                Generator for TF dataset
                """
                for _p, _s, _, _ in self.samples:
                    yield self.problems_solutions[_p][_s]
            def gen4DS_2nd():
                """
                Generator for TF dataset
                """
                for _, _, _p, _s in self.samples:
                    yield self.problems_solutions[_p][_s]
            return gen4DS_1st, gen4DS_2nd
#---------------- End of class genConstructor -------------------------

class DoubleSeqTfDataset():
    """
    Class for constracting TF dataset 
    from two lists of sequences of tokens and array of labels
    """
    def __init__(self):
        """
        Initialize object DoubleSeqTfDataset
        Parameters:
        """
        pass

    @classmethod
    def makeDoubleSeqDataset(cls, seq1, seq2, labels, batch_size,
                             shard = "OFF"):
        """
        Make TF dataset from two lists of sequences of tokens 
        and array of labels
        The constructed dtaset of TensorFlow Dataset of from_generator type
        Parameters:
        - seq1         -- 1-st sequence of tokens
        - seq2         -- 2-nd sequence of tokens
        - labels       -- labels as numpy array
                          If labels is None, the dataset is test dataset
        - batch_size   -- batch size
        - shard      -- option to shard dataset:
                        * "OFF"  -- AutoShardPolicy.OFF
                        " "DATA" -- AutoShardPolicy.DATA
        Returns:
        - Tensorflow dataset combined from 
          * two tensorflow datasets representing each sequence of tokens; and
          * tensorflow dataset rezenting labels 
        """
        _ds1 = cls.dsFromGenerator(seq1, batch_size)
        _ds2 = cls.dsFromGenerator(seq2, batch_size)
        _ds = tf.data.Dataset.zip((_ds1, _ds2))
        _t_labels  = tf.convert_to_tensor(labels)
        _l = tf.data.Dataset.from_tensor_slices(_t_labels)
        _ds = tf.data.Dataset.zip((_ds, _l))
        _ds_options = makeShardOptions(policy = shard)
        _ds = _ds.batch(batch_size).with_options(_ds_options)
        return _ds

    @classmethod
    def dsFromGenerator(cls, samples, batch_size):
        """
        Make TF dataset from samples generator,
        defined with list of sequences
        Parameters:
        - samples    -- list of samples (sequences of tokens)
        - batch_size -- batch size
        Returns: TF dataset
        """
        _s = tf.data.Dataset.from_generator(
            lambda: samples, output_signature=(
                tf.TensorSpec(shape=([None]), dtype=tf.int32)))
        _s = _s.padded_batch(batch_size, padding_values = 0,
                             drop_remainder=True)
        _s = _s.unbatch()
        return _s

    @classmethod
    def makeDatasetOptions(cls):
        """
        Make Dataset options: 
        currently they are chard options for multi GPU mode
        Returns: dataset options
        """
        #Setting TF sharding policy for multi GPU mode. 
        #It should be either OFF or DATA
        _options = tf.data.Options()
        _options.experimental_distribute.auto_shard_policy = \
            tf.data.experimental.AutoShardPolicy.OFF
        return _options
#---------------- End of class makeDoubleSeqDataset -------------------------

