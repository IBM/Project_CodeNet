"""
Model for making Neural Network models 
for classification of source code.
The module provides factory class for making
Neural Network models 
"""
import sys
import tensorflow
from tensorflow.keras import models
from tensorflow.keras import layers
from tensorflow.keras import initializers

from ModelUtils import *

class SeqModelFactory(SeqBlockFactory):
    """
    Factory of DNNs for code classification and similarity analysis 

    Provides functions for creating DNNs  of different types
    If the number of lables > 1 the constructed DNN uses;
    - softmax for classification 
    - sparse_categorical_crossentropy for loss function
    othervise constructed DNN uses:
    - sigmoid for classification
    - binary_crossentropy for loss function
    """
    def __init__(self, tokens, labels):
        """
        Initialize factory for DNNs
        Parameters:
        - tokens  -- number of types of tokens
                       Actually it is the size (dimensionality) 
                       of sequence vectors.
                       For similarity analysis it is twice
                       the number of tokens
        - labels  -- number of labels (classes)
        """
        self.n_labels = labels
        super(SeqModelFactory, self).__init__(tokens)

    def denseDNN(self, dense, bias = True,
                 regular = None, optimizer = "adam"):
        """
        Make DNN with dense (fully connected) layers
        Parameters:
        - dense    -- list of hidden layers widths
                      for all layers except the last one
                      If w_hidden is none or empty list,
                      Linear classifier is constructed
        - bias     -- use or do not use bias on dense layers
        - regular  -- regularizer as a pair (l1, l2) 
                      or None if no regularization is applied.
                      Regularization is applied dense layers
        - optimizer -- training optimizer
        """
        _regularizer = self.computeRegularizer(regular)
        _dnn = models.Sequential()
        _dnn.add(layers.Input(shape=(self.n_tokens)))
        self.addDense(_dnn, dense, bias = bias, 
            regularizer = _regularizer)
        self.addClassifier(_dnn, self.n_labels, bias = bias, 
                           regularizer = _regularizer)
        return self.compileDNN(_dnn, self.compLoss(self.n_labels),
                               optimizer = optimizer)

    def cnnDNN(self, convolutions, dense, pool = 'max',
               conv_act = None, conv_bias = True,
               dense_bias = True, input_type = "categorical",
               regular = None, optimizer = "rmsprop",
               embedding_dim = None,
               dropout_rate = 0,
               regul_dense_only = True):
        """
        Make convolutional model
        Parameters:
        - convolutions  -- specification of convolutional layers
                           as list of tuples:
                           either (kernel width, n filters, stride)
                           or (kernel width, n filters) if stride = 1
        - dense       -- specification of dense layers as list of
                           their width except the last one
        - pool          -- pooling operation either:
                           'max' for maximum or 
                           'aver' for average
        - conv_act      -- activation of convolutional layers
        - conv_bias     -- use bias for convolutional layers
        - dense_bias    -- use bias for dense layers
        - input_type    -- type of input layer:
                           - one_hot     - one hot coding of input samples
                                 It also used for predefined input vectors,
                                 even if they are not one-hot.
                           - categorical - categorical coding 
                                           decoded by preprocessing layer
                           - trainable   - categorical coding processed
                                           by trainable embedding layer
        - regular       -- regularizer as a pair (l1, l2) 
                           or None if no regularization is applied.
                           Regularization is applied to both convolution 
                           and dense layers
        - embedding_dim -- size of embedding vectors
                           It effects trainable embedding only,
                           i.e. input_type == "trainable"
        - dropout_rate  -- dropout rate for inserted dropout layer
                           If it is 0 or None no droput layer is inserted
        - optimizer   -- training optimizer
        - regul_dense_only -- flag to regulirize only dense layers
        Returns:
        - compiled dnn
        """
        _regularizer = self.computeRegularizer(regular)
        _dnn = self.convBlock(
            convolutions, dense = dense, pool = pool,
            conv_act =conv_act, conv_bias = conv_bias,
            dense_bias = dense_bias, input_type = input_type,
            regularizer = _regularizer,
            embedding_dim = embedding_dim,
            dropout_rate = dropout_rate,
            regul_dense_only = regul_dense_only)
        self.addClassifier(_dnn, self.n_labels, bias = dense_bias, 
                           regularizer = _regularizer)
        return self.compileDNN(_dnn, self.compLoss(self.n_labels),
                               optimizer = optimizer)
#---------------- End of class SeqModelFactory ----------------------------
