"""
Module for making experimental Siamese DNNs for similarity 
analysis
"""
import sys
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import models
from tensorflow.keras import layers

from ModelUtils      import *
from FuncModelMaker  import FuncModelFactory

#LOSS FUNCTIONS
register = keras.utils.register_keras_serializable('loss_function', name='loss_function')

@register
def cappedCrossEntropy(y_true, y_pred):
    """
    Capped binary cross entropy loss function 
    """
    return -(keras.backend.cast(y_true, tf.float32) * 
             tf.math.minimum((keras.backend.log(y_pred) + 0.1), 0) + 
             5 * (1.0 - keras.backend.cast(y_true, tf.float32)) * 
             tf.math.minimum((keras.backend.log(1 - y_pred) + 0.01), 0) )

#@register
def relaxedCrossEntropy(y_true, y_pred):
    """
    Relaxed binary cross entropy loss function 
    """
    return -(keras.backend.cast(y_true, tf.float32) * 
             keras.backend.log(y_pred) + 
             (1.0 - keras.backend.cast(y_true, tf.float32)) * 
             keras.backend.log((1 - y_pred + 0.1) / (1 + 0.1)))

#@register
def sinCrossEntropy(y_true, y_pred):
    """
    Binary cross entropy loss function 
    with sin transformation of predicted probability
    """
    return -(keras.backend.cast(y_true, tf.float32) * 
             keras.backend.log(keras.backend.sin(3.1415926 * (y_pred - 0.5)) / 2.0 + 0.5000001) + 
             (1.0 - keras.backend.cast(y_true, tf.float32)) * 
             keras.backend.log(keras.backend.sin(3.1415926 * (0.5 - y_pred)) / 2.0 + 0.5000001))

def getLossFunction(loss = None):
    """
    Compute loss function as function of the argument
    Parameters:
    - loss   -- loss function as a string
    """
    if loss is None:
        return "binary_crossentropy"
    elif loss == "relaxedCrossEntropy":
        return relaxedCrossEntropy
    elif loss == "sinCrossEntropy":
        return sinCrossEntropy
    elif loss == "cappedCrossEntropy":
        return cappedCrossEntropy
    else:
        sys.exit(f"Unknown loss function {loss}")
    
#---------------- End of lOSS FUNCTIONS ---------------------------

class ExpSiameseModelFactory(FuncModelFactory):
    """
    Class for making experimental DNNs
    Provides functions for creating experimental DNNs
    both for classification and similarity analysis of
    source code represented with sequence of tokens
    Set all external parameters of DNNs,
    which can be amended or even modified in each    
    """
    def __init__(self, n_labels, regularizer = None, loss = None):
        """
        Initialize factory for DNNs
        Parameters:
        - n_labels     -- number of labels (classes)
        - regularizer  -- regularizer as a pair (l1, l2) 
                          or None if no regularization is applied
                          Same regularization is applied to all layers
        """
        super(ExpSiameseModelFactory, self).__init__(n_labels, 
                                    regularizer = regularizer)
        self.loss = getLossFunction(loss)

    def makeCNN(self, dnn,
                n_tokens,
                convolutions, w_dense,
                pool = 'max', side_dense = [],
                conv_act = None, conv_bias = True,
                dense_bias = True,
                input_type = "trainable",
                embedding_dim = None,
                regul_dense_only = True,
                dropout_rate = 0,
                merge = "concatenate",
                optimizer = "adam"):
        """
        Make experimental two way convolutional Siamese dnn 
        for sequence similarity analysis
        Parameters to each DNN are passed as self object member 
        Parameters:
        - dnn   -- string specifying type of DNN to make
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
        self.n_tokens =n_tokens 
        self.convolutions = convolutions
        self.w_dense = w_dense
        self.pool = pool
        self.side_dense = side_dense
        self.conv_act = conv_act
        self.conv_bias = conv_bias
        self.dense_bias = dense_bias
        self.input_type = input_type
        self.embedding_dim = embedding_dim
        self.regul_dense_only = regul_dense_only
        self.dropout_rate = dropout_rate
        self.merge = merge
        self.optimizer = optimizer
        if dnn == "concatenate":
            return self.concatCNN()
        elif dnn == "subtract":
            return self.subtractCNN()
        elif dnn == "dot_prod_sigmoid":
            return self.dot_prodCNN()
        elif dnn == "cosine":
            return self.cosineCNN()
        elif dnn == "multiply":
            return self.multiplyCNN()
        elif dnn == "plain":
            return self.plainCNN()
        else:
            sys.exit(f"Requested dnn {dnn} is not known")

    def expCompile(self, inputs, output, 
                   optimizer = "rmsprop", 
                   loss = "binary_crossentropy",
                   metrics = ["accuracy"]):
        """
        Experomental version of function for 
        making functional dnn model and compiling it
        Parameters:
        - inputs     -- list of dnn inputs
        - output     -- dnn output
        - optimizer  -- training optimizer
        - loss       -- loss function used by optimizer
                        * If loss = None the lost is binary_crossentropy
        - metrics    -- list of metric functions used by optimizer
        Returns compiled DNN
        """
        _dnn = models.Model(inputs, output)
        _loss = loss if loss else "binary_crossentropy"
        _dnn.compile(optimizer = optimizer, loss = loss,
                     metrics = metrics)
        print("Summary of DNN constructed")
        _dnn.summary()
        return _dnn 

    def siameseBlock(self):
        """
        Make Siamese block of CNN
        Outputs are Max pooled tensors of convolved input sequence

        Parameters are taken from members of object self
        Returns 4 tensors:
        - input tensor 1
        - input tensor 2
        - output tensor 1
        - output tensor 2      
        """
        _input1 = layers.Input(shape=(None,))
        _input2 = layers.Input(shape=(None,))
        _maker = SeqBlockFactory(self.n_tokens)
        _conv = _maker.convBlock(
            self.convolutions, 
            dense = self.side_dense, 
            pool = self.pool,
            conv_act = self.conv_act, 
            conv_bias = self.conv_bias,
            dense_bias = self.dense_bias, 
            input_type = self.input_type,
            regularizer = self._regularizer,
            embedding_dim = self.embedding_dim,
            dropout_rate = self.dropout_rate,
            regul_dense_only = self.regul_dense_only)
        _pool1 = _conv(_input1)
        _pool2 = _conv(_input2)  
        return _input1, _input2, _pool1, _pool2

    def denseTower(self, input_tensor, dense, 
                   bias = True, activation = "relu"):
        """
        Make a stack of dense layers
        Stack may have no layers
        It is expected that input shape is known
        Parameters:
         - input_tensor  -- input tensor
         - dense  -- specification of dense layers as list of
                     their width except the last one
         - bias    -- use or do not use bias on dense layers
         - activation of all layers except the last one
        Returns: output tensor
        """
        _output = input_tensor
        _output = input_tensor
        if dense:
            for _w in dense:
                _output = layers.Dense(_w, activation = activation,
                        use_bias = bias,
                        kernel_regularizer=self._regularizer,
                        kernel_initializer = BaseModelFactory.computeInitializer()
                )(_output)
        return _output

    def expDenseClassifier(self, input_tensor, dense, 
                           bias = True, activation = "relu"):
        """
        Make a stack of dense layers with classifier
        Classifier is either softmax for more than 2 classes
        or sigmoid for 2 classes
        It is expected that input shape is known
        Parameters:
         - input_tensor  -- input tensor
         - dense  -- specification of dense layers as list of
                     their width except the last one
         - bias    -- use or do not use bias on dense layers
         - activation of all layers except the last one
        Returns: output tensor
        """
        _output = self.denseTower(input_tensor, dense, 
                                  bias =bias, activation = activation)
        _output = layers.Dense(self.n_labels, 
                activation = self.class_layer,
                use_bias = bias,
                kernel_regularizer=self._regularizer,
                kernel_initializer = BaseModelFactory.computeInitializer())(_output)
        return _output

    def concatCNN(self):
        """
        Siamese CNN with merging by concatenation
        """
        _input1, _input2,  _pool1, _pool2 = self.self.siameseBlock()
        _merged = layers.concatenate([_pool1, _pool2])
        _output = self._denseClassifier(_merged, self.w_dense)
        return self.expCompile([_input1, _input2,], _output,
                               optimizer = self.optimizer)

    def biasedDenseLayer(self, input_tensor, width, 
                         min_bias, rate_bias = 0.5, activation = "tanh"):
        """
        Experimental dense layer with fixed value of bias
        Parameters:
        - input_tensor  -- input tensor
        - width         -- width 
        - min_bias      -- minimum bias value to shift 0 value of 
                           previous layer output
        - rate_bias     -- rate of enforcing bias constraint
        - activation    -- activation function
        Returns output tensor
        """
        _l = layers.Dense(width, activation = activation,
                          use_bias = True,
                          kernel_regularizer=self._regularizer,
                          kernel_initializer = initializers.RandomUniform(
                              minval=0, maxval=0.1, seed=UniqueSeed.getSeed()),
                          #kernel_constraint = keras.constraints.NonNeg(),
                          bias_initializer = keras.initializers.Constant(min_bias), 
                          bias_constraint = keras.constraints.MinMaxNorm(
                              min_value=min_bias, rate=rate_bias, axis=0))
        return _l(input_tensor)

    def subtractCNN(self):
        """
        Siamese CNN with merging by computing 
        absolute value of difference
        """
        _bias_shift = 3.0    #minimum bias shift
        _rate_bias  = 0.5    #rate of enforcing bias constraint
        _diff_activation = "tanh"  # activation of layer processing 
                                   #difference of feature vectors
                                   #either tanh or None

        _input1, _input2,  _pool1, _pool2 = self.siameseBlock()
        _merged = self._absDifference(_pool1, _pool2)
        _x = self.biasedDenseLayer(_merged,  self.w_dense[0], 
                                    _bias_shift, rate_bias = _rate_bias,
                                    activation = "relu")
        _output = self.expDenseClassifier(_x, self.w_dense[1:])
        return self.expCompile([_input1, _input2,], _output,
                               optimizer = self.optimizer)

    def dot_prodCNN(self):
        """
        Siamese CNN with merging by dot product
        """
        _input1, _input2,  _pool1, _pool2 = self.siameseBlock()
        _output = layers.Dot(axes = 1, normalize = False)([_pool1, _pool2])
        _output = layers.Activation("sigmoid")(_output)
        return self.expCompile([_input1, _input2,], _output,
                               optimizer = self.optimizer)

    def cosineCNN(self):
        """
        Siamese CNN with merging by cosine
        """
        _input1, _input2,  _pool1, _pool2 = self.siameseBlock()
        _output = layers.Dot(axes = 1, 
                             normalize = True)([_pool1, _pool2])
        return self.expCompile([_input1, _input2,], _output,
                               optimizer = self.optimizer,
                               loss = keras.losses.SquaredHinge(),
                               metrics = [keras.metrics.SquaredHinge()])
                               #loss = keras.losses.Hinge(reduction="auto"),
                               #metrics = [keras.metrics.Hinge()])

    def multiplyCNN(self):
        """
        Siamese CNN with merging by multiplication
        """
        _input1, _input2,  _pool1, _pool2 = self.siameseBlock()
        #_pool1 = layers.Activation("tanh")(_pool1)
        #_pool2 = layers.Activation("tanh")(_pool2)
        _multiplied = keras.layers.Multiply()([_pool1, _pool2])
        _output = self.expDenseClassifier(_multiplied, self.w_dense)
        return self.expCompile([_input1, _input2,], _output,
                               optimizer = self.optimizer)

    def plainCNN(self, loss_function = "binary_crossentropy"):
        """
        Old plain siamese CNN
        Parameters:
        - loss_function  -- loss function
        """
        _input1, _input2,  _pool1, _pool2 = self.siameseBlock()
        _merged = self._absDifference(_pool1, _pool2)
        _output = self._denseClassifier(_merged, self.w_dense)
        return self.expCompile([_input1, _input2,], _output,
                               optimizer = self.optimizer, 
                               loss = self.loss)
#---------------- End of class ExpSiameseModelFactory ---------------------------
