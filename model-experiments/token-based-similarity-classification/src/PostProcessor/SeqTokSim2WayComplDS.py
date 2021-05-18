"""
Module for constracting COMPLETE test dataset 
of sequence of tokens for similarity analysis
The dataset has all pairs of all problem solutions
It is TF from-genrator dataset
"""
import sys
import numpy as np
import tensorflow as tf

from DataLoader import SeqOfTokensLoader
from DoubleSeqTfDS import DoubleSeqTfDataset
from DsUtilities  import makeShardOptions

class SeqTokSim2WayComplDS(SeqOfTokensLoader):
    """
    Class for constracting COMPLETE test dataset 
    of sequence of tokens for similarity analysis
    The dataset has all pairs of all problem solutions
    It is TF from-generator based dataset
    Specializes parent class with functions 
    computing sequence of tokens
    """
    def __init__(self, dir_name, short_code_th = 1,
                 max_seq_length = None, seq_len_to_pad = None,
                 labels01 = True, ):
        """
        Initialize object SeqTok2WaySimDS
        
        Parameters:
        - dir_name  -- directory with files of tokenized source code files
        - short_code_th   -- minimum length of code to load
        - max_seq_length  -- maximum length of token sequencen to truncate.
        - seq_len_to_pad  -- sequence lengths to pad to
        - labels01        -- label types flag:
                             True:   0/1 labels
                             Flase:  -1/+1 labels
        """
        super(SeqTokSim2WayComplDS, self).__init__(
            dir_name, min_n_solutions = 1,
            problem_list = None, max_n_problems = None,
            short_code_th = short_code_th, long_code_th = None)
        #Minimum lengths of sequence of tokens
        #All shorter ones are padded with 0
        self.min_seq_length = seq_len_to_pad
        self.labels01 = labels01
        self.samples, self.probl_sol_ranges, \
            self.sample_names = self.loadAllSamples()
        self.seq_length =  \
            self.code_max_length if max_seq_length is None \
            else max_seq_length
        self.n_samples = self.probl_sol_ranges[-1]
        self.annotateSamples()

    def annotateSamples(self):
        """
        Annotate samples with their problem indices and names
        """
        self.sample_probl_indices = np.zeros(self.n_samples, 
                                             dtype = np.int32)
        for _i in range(len(self.probl_sol_ranges) - 1):
            self.sample_probl_indices[self.probl_sol_ranges[_i] : 
                            self.probl_sol_ranges[_i + 1]].fill(_i)

    def makeSample(self, tokens):
        """
        Compute sequence of tokens from list of tokens
        No actual computation requires as the parent class 
        did everything correctly
        Parameters:
        - tokens list of tokens as int values
        Returns:
        - sequence of tokens as numpy array
        """
        _s = list(map(lambda _tok: _tok + 1, tokens))
        _l = len(_s)
        if _l < self.min_seq_length:
            _s.extend([0] * (self.min_seq_length - _l))
        return np.asarray(_s, dtype = np.int32)

    def goodOLDtestDataset(self, batch = 500, shard = "OFF"):
        """
        Make similarity dataset in the form of 
        TensorFlow  Dataset of from_generator type
        Parameters:
        - batch           -- batch size for TF dataset
        - shard      -- option to shard dataset:
                        * "OFF"  -- AutoShardPolicy.OFF
                        " "DATA" -- AutoShardPolicy.DATA
        Returns:
        - Tensorflow dataset combined fromhaving 3 components 
          * two sequences of tokens; and
          * labels 
        """
        def _sample_generator():
            """
            Function-generator of similarity samples
            Returns pair:
            - sequence of tokens of 1-st source code file
            - sequence of tokens of 2-st source code file
            - label: 1 if the files solve the same problem
                     0 otherwise
            """
            _sample_count = 0
            for _i in range(self.n_samples):
                for _j in range(self.n_samples):
                    #_sample_count += 1
                    #if _sample_count > 100000: return
                    yield self.samples[_i], self.samples[_j]

        def _label_generator():
            """
            Function-generator of similarity sample labels
            Returns pair:
            - label: 1 if the files solve the same problem
                     0 otherwise
            """
            _sample_count = 0
            for _i in range(self.n_samples):
                for _j in range(self.n_samples):
                    #_sample_count += 1
                    #if _sample_count > 100000: return
                    yield int(self.sample_probl_indices[_i] == 
                               self.sample_probl_indices[_j])    
                    
        _ds = tf.data.Dataset.from_generator(_sample_generator,
                output_signature=(
                    (tf.TensorSpec(shape=([None]), dtype=tf.int32),
                     tf.TensorSpec(shape=([None]), dtype=tf.int32))))
        _ds = _ds.padded_batch(batch, padding_values = (0, 0),
                               padded_shapes = ([None], [None]))
        _ds = _ds.unbatch()
        _dl = tf.data.Dataset.from_generator(_label_generator,
                output_signature=tf.TensorSpec(shape=(), dtype=tf.int32))
        _ds = tf.data.Dataset.zip((_ds, _dl)).batch(batch, drop_remainder=True)
        _ds_options = makeShardOptions(policy = shard)
        _ds = _ds.with_options(_ds_options)
        return _ds

    #!!!Another version of tf datset constructor
    #=================================
    def testDataset(self, batch = 500, shard = "OFF"):
        """
        Make similarity dataset in the form of 
        TensorFlow  Dataset of from_generator type
        The dataset has samples of all pairs of problem solutions
        The dataset is generated as sequence of subsequences
        corresponding to problems solutions
        All subsequences have the same length equals 
        to the number of all problem solutions
        i-th subsequence consists of similarity samples of the form:
        <i-th solution, other solution> for all others solutions
        
        Parameters:
        - batch           -- batch size for TF dataset
        - shard      -- option to shard dataset:
                        * "OFF"  -- AutoShardPolicy.OFF
                        " "DATA" -- AutoShardPolicy.DATA
        Returns:
        - Tensorflow dataset combined fromhaving 3 components 
          * two sequences of tokens; and
          * labels
        """
        def _sample_generator01():
            """
            Function-generator of similarity samples
            with 0 and 1 similarity labels
            Returns 3 tuple:
            - sequence of tokens of 1-st source code file
            - sequence of tokens of 2-st source code file
            - label: 1 if the files solve the same problem
                     0 otherwise
            """
            for _i in range(self.n_samples):
                for _j in range(self.n_samples):
                    yield (self.samples[_i], self.samples[_j]), \
                        int(self.sample_probl_indices[_i] == 
                            self.sample_probl_indices[_j])

        def _sample_generator_symmetric():
            """
            Function-generator of similarity samples
            with symmetric -1 and +1 similarity labels
            Returns 3 tuple:
            - sequence of tokens of 1-st source code file
            - sequence of tokens of 2-st source code file
            - label: 1 if the files solve the same problem
                     0 otherwise
            """
            for _i in range(self.n_samples):
                for _j in range(self.n_samples):
                    yield (self.samples[_i], self.samples[_j]), \
                        2 * int(self.sample_probl_indices[_i] == 
                            self.sample_probl_indices[_j]) - 1

        _sample_generator = _sample_generator01 if self.labels01 \
                            else _sample_generator_symmetric
            
        _ds = tf.data.Dataset.from_generator(_sample_generator,
                output_signature=(
                    (tf.TensorSpec(shape=([None]), dtype=tf.int32),
                     tf.TensorSpec(shape=([None]), dtype=tf.int32)),
                    tf.TensorSpec(shape=(), dtype=tf.int32)))

        _ds = _ds.padded_batch(batch,         #padding_values = (0, 0),
                    padded_shapes = (([None], [None]), ()), 
                               drop_remainder=True)
        _ds_options = makeShardOptions(policy = shard)
        _ds = _ds.with_options(_ds_options)
        return _ds
#---------------- End of class SeqTok2WaySimDsTF -------------------------

