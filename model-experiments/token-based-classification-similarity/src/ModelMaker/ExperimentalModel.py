"""
Module for making experimental DNNs
"""
import sys
import tensorflow
from tensorflow import keras
from tensorflow.keras import models
from tensorflow.keras import layers

from ModelUtils      import *
from FuncModelMaker  import FuncModelFactory

class ExperimentModelFactory(FuncModelFactory):
    """
    Class for making experimental DNNs
    Provides functions for creating experimental DNNs
    both for classification and similarity analysis of
    source code represented with sequence of tokens
    """
    def __init__(self, n_labels, regularizer = None):
        """
        Initialize factory for DNNs
        Parameters:
        - n_labels     -- number of labels (classes)
        - regularizer  -- regularizer as a pair (l1, l2) 
                          or None if no regularization is applied
                          Same regularization is applied to all layers
        """
        super(ExperimentModelFactory, self).__init__(n_labels, 
                                    regularizer = regularizer)

    def doublePoolClassCNN(self, n_tokens, 
                           convolutions, dense,
                           conv_act = None, conv_bias = True,
                           dense_bias = True,
                           input_type = "trainable",
                           embedding_dim = None,
                           regul_dense_only = True,
                           dropout_rate = 0,
                           optimizer = "rmsprop"):
        """
        Classificating CNN with both max and average 
        global pooling operations
        Parameters:
        - convolutions  -- specification of convolutional layers
                           as list of tuples:
                           either (kernel width, n filters, stride)
                           or (kernel width, n filters) if stride = 1
        - dense         -- specification of dense layers as list of
                           their width except the last one
        - conv_act      -- activation of convolutional layers
        - conv_bias     -- use bias for convolutional layers
        - dense_bias    -- use bias for dense layers
        - input_type    -- type of input layer:
                           - categorical - categorical coding 
                                           decoded by preprocessing layer
                           - trainable   - categorical coding processed
                                           by trainable embedding layer
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
        _input = layers.Input(shape=(None,))
        _maker = SeqBlockFactory(n_tokens)
        _conv_tower1 = _maker.convTower(convolutions,
            conv_act = conv_act, out_no_act = True,
            conv_bias = conv_bias,
            input_type = input_type,
            regularizer = self._regularizer,
            embedding_dim = embedding_dim,
            regul_dense_only = regul_dense_only)
        _conv_tower2 = _maker.convTower(convolutions,
            conv_act = conv_act, out_no_act = True,
            conv_bias = conv_bias,
            input_type = input_type,
            regularizer = self._regularizer,
            embedding_dim = embedding_dim,
            regul_dense_only = regul_dense_only)        
        _conv1 = _conv_tower1(_input)
        _conv2 = _conv_tower2(_input)
        _max_pool  = layers.GlobalMaxPooling1D()(_conv1)
        _aver_pool = \
            layers.GlobalAveragePooling1D()(_conv2)
        #keras.layers.Lambda(lambda x: keras.backend.stop_gradient(x))(_conv))
        _merged = layers.concatenate([_max_pool, _aver_pool],
                                     axis=-1)
        if dropout_rate:
            _merged = layers.Dropout(dropout_rate, 
                        seed = UniqueSeed.getSeed())(_merged)
        _output = self._denseClassifier(_merged, dense)
        return self._compile(_input, _output,
                             optimizer = optimizer)

    def _expCompile(self, inputs, output, 
                    optimizer = "rmsprop", 
                    loss = None):
        """
        Experomental version of function for 
        making functional dnn model and compiling it
        Parameters:
        - inputs     -- list of dnn inputs
        - output     -- dnn output
        - optimizer  -- training optimizer
        - loss       -- loss function used by optimizer
                        * If loss = None the lost is computed 
                          from the number of labels
        Returns compiled DNN
        """
        _dnn = models.Model(inputs, output)
        _loss = loss if loss else \
                BaseModelFactory.compLoss(self.n_labels)
        _dnn = SeqBlockFactory.compileDNN(
            _dnn, _loss, optimizer = optimizer)
        return _dnn

    def _expBiasedDenseLayer(self, input_tensor, width, bias):
        """
        Experimental dense layer with fixed value of bias
        Parameters:
        - input_tensor  -- input tensor
        - width         -- width 
        - bias          -- bias values
        """
        _l = layers.Dense(width, activation = 'tanh',
            use_bias = bias,
            kernel_regularizer=self._regularizer,
            kernel_initializer = BaseModelFactory.computeInitializer(),
            bias_initializer = keras.initializers.Constant(bias), 
            bias_constraint = keras.constraints.MinMaxNorm(
                min_value=bias, rate=0.5, axis=0))  #max_value=bias, 
        return _l(input_tensor)
        

    def siameseExperimentalCNN(self, n_tokens,
                               convolutions, w_dense,
                               pool = 'max', side_dense = [],
                               conv_act = None, conv_bias = True,
                               dense_bias = True,
                               input_type = "trainable",
                               embedding_dim = None,
                               regul_dense_only = True,
                               dropout_rate = 0,
                               merge = "concatenate",
                               optimizer = "rmsprop"):
        """
        Make two way convolutional Siamese dnn 
        for sequence similarity analysis
        
        Parameters:
        - n_tokens  -- number of types of tokens
        - convolutions  -- specification of convolutional layers
                           as list of tuples:
                           either (kernel width, n filters, stride)
                           or (kernel width, n filters) if stride = 1
        - w_dense       -- specification of dense layers as list of
                           their width except the last one
        - pool          -- pooling operation either:
                           'max' for maximum or 
                           'aver' for average
        - side_dense    -- specification of each branch dense layers 
                           as list of their width
        - conv_act      -- activation of convolutional layers
        - conv_bias     -- use bias for convolutional layers
        - dense_bias    -- use bias for dense layers
        - input_type    -- type of input layer:
                           - categorical - categorical coding 
                                           decoded by preprocessing layer
                           - trainable   - categorical coding processed
                                           by trainable embedding layer
        - embedding_dim -- size of embedding vectors
        - dropout_rate  -- dropout rate for inserted dropout layer
                           If it is 0 or None no droput layer is inserted
        - merge         -- method of merging outputs of Siamese blocks
                           * if concatenate, the outputs are concatenated
                             and processed with dense layers
                           * if subract, absolute value of difference 
                             of the outputs is computed
                           * if "dot_prod_sigmoid" it is computed 
                             sigmoid of dot product of outputs
                           * if "cosine" it is computed 
                             normalized dot product of normalized outputs
        - regul_dense_only -- flag to regulirize only dense layers
        - optimizer   -- training optimizer
        Returns compiled dnn
        """
        _input1 = layers.Input(shape=(None,))
        _input2 = layers.Input(shape=(None,))
        _maker = SeqBlockFactory(n_tokens)
        _conv = _maker.convBlock(
            convolutions, dense = side_dense, pool = pool,
            conv_act = conv_act, conv_bias = conv_bias,
            dense_bias = dense_bias, input_type = input_type,
            regularizer = self._regularizer,
            embedding_dim = embedding_dim,
            dropout_rate = dropout_rate,
            regul_dense_only = regul_dense_only)
        _pool1 = _conv(_input1)
        _pool2 = _conv(_input2)
        if merge == "concatenate":
            _merged = layers.concatenate([_pool1, _pool2])
            _output = self._denseClassifier(_merged, w_dense)
        elif merge == "subtract":
            _merged = self._absDifference(_pool1, _pool2)
            _x = self._expBiasedDenseLayer(_merged,  w_dense[0], 4)
            _output = self._denseClassifier(_x, w_dense[1:])
        elif merge == "dot_prod_sigmoid":
            _output = self._dotProdClassifier(_pool1, _pool2)
        elif merge == "cosine":
            _output = layers.Dot(axes = 1, 
                        normalize = True)([_pool1, _pool2])
        else:
            sys.exit(f"Wrong method {merge} of merging outputs of Siamese blocks")
        return self._expCompile([_input1, _input2,], _output,
                                optimizer = optimizer)
#---------------- End of class ExperimentModelFactory ---------------------------
