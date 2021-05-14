"""
Module for making Keras functional Neural Network models 
for similarity analysis of source code.
The module provides factory class for making
Neural Network models 
"""
import sys
import tensorflow
from tensorflow.keras import models
from tensorflow.keras import layers

from ModelUtils import SeqBlockFactory, BaseModelFactory

class FuncModelFactory(object):
    """
    Factory of DNNs for code classification and similarity analysis 

    Provides functions for creating DNNs for similarity 
    analysis of source code represented with sequence of tokens
    If the number of lables > 1 the constructed DNN uses;
    - softmax for classification 
    - categorical_crossentropy for loss function
    othervise constructed DNN uses:
    - sigmoid for classification
    - binary_crossentropy for loss function
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
        self.n_labels = n_labels
        self.class_layer = \
                BaseModelFactory.compClassification(n_labels)
        self._regularizer = \
                BaseModelFactory.computeRegularizer(regularizer)

    def _convLayer(self, input_tensor, convolution,
                   activation = None, bias = True):
        """
        Construct a convolutional layer
        Regularization is applied with self._regularizer
        Parameters:
        - input_tensor  -- input tensor
        - convolution   -- specification of the convolutional layer
                           as list of tuples:
                           either (n filters, kernel width, stride)
                           or (n filters, kernel width) if stride = 1
        - activation    -- activation on convolutional layer
        - bias          -- use or do not use bias on convolutional layer
        Returns: 
        - output tensor if the layer is successfully created
        - None if the layer is specified incorrectly
        """
        if len(convolution) == 3:
            return layers.Conv1D(convolution[0], convolution[1],
                    strides=convolution[2],
                    activation = activation,
                    use_bias = bias,
                    kernel_regularizer=self._regularizer,
                    kernel_initializer = BaseModelFactory.computeInitializer()
            )(input_tensor)
        elif len(convolution) == 2:
            return layers.Conv1D(convolution[0], convolution[1],
                    activation = activation,
                    use_bias = bias,
                    kernel_regularizer=self._regularizer,
                    kernel_initializer = BaseModelFactory.computeInitializer()
            )(input_tensor)
        else:
            return None

    def _convolution1(self, input_tensor, convolutions,
                      activation = None, bias = True,
                      out_no_act = True):
        """
        Make a stack of convolutional layers
        Parameters:
        - input_tensor  -- input tensor
        - convolutions  -- specification of convolutional layers
                           as list of tuples:
                           either (n filters, kernel width, stride)
                           or (n filters, kernel width) if stride = 1
        - activation    -- activation on all convolutional layers
                           but the last one
        - bias          -- use or do not use bias on convolutional layers
        - out_no_act    -- flag of no activation on last layer
        Returns: 
        - output tensor
        """
        _output = input_tensor
        for _i in range(len(convolutions)):
            _act = None if _i == len(convolutions) - 1 and out_no_act \
                else activation
            _output = self._convLayer(_output, convolutions[_i],
                                      activation = _act, bias = bias)
            if _output is None:
                print(f"Wrong specification of convolutional layer {-i}")
                _n_conv_parms = len(convolutions[_i])
                print(f"It has incorrect number {_n_conv_parm} of parameters")
                sys.exit(0)
        return _output

    def _absDifference(self, input1, input2):
        """
        Compute absolute value of difference of two tensor
        Parameters:
        - input1  -- 1-st operand
        - input2  -- 2-nd operand
        """
        _diff1 = layers.Subtract()([input1, input2])
        _diff2 = layers.Subtract()([input2, input1])
        #return layers.Maximum()([_diff1, _diff2])
        return layers.Minimum()([_diff1, _diff2])


    def _denseClassifier(self, input_tensor, dense, bias = True):
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
        Returns: output tensor
        """
        _output = input_tensor
        if dense:
            for _w in dense:
                _output = layers.Dense(_w, activation = 'relu',
                        use_bias = bias,
                        kernel_regularizer=self._regularizer,
                        kernel_initializer = BaseModelFactory.computeInitializer()
                )(_output)
        _output = layers.Dense(self.n_labels, 
                activation = self.class_layer,
                use_bias = bias,
                kernel_regularizer=self._regularizer,
                kernel_initializer = BaseModelFactory.computeInitializer())(_output)
        return _output

    def _dotProdClassifier(self, input1, input2):
        """
        Add dot product classifier
        Dot product is not normalized but is transformed by sigmoid 
        to probabilities as it helps convergence which is still inferior 
        to conventional methods of merging two embeddings
        !!!The function is for experiments only
        Parameters:
        - input1  -- 1-st operand of dot product 
        - input2  -- 2-nd operand of dot product 
        """
        _output = layers.Dot(axes = 1, normalize = False)([input1, input2])
        return tensorflow.keras.layers.Activation("sigmoid")(_output)


    def twoWaySimilarityCNN(self, n_tokens,
                            convolutions, w_dense,
                            pool = 'max', side_dense = [],
                            conv_act = None, conv_bias = True,
                            dense_bias = True, shared = False,
                            input_type = "one_hot",
                            embedding_dim = None,
                            regul_dense_only = True,
                            dropout_rate = 0,
                            optimizer = "rmsprop"):
        """
        Make symmetric two way convolutional dnn 
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
                           - one_hot     -  one hot coding of input samples
                           - categorical - categorical coding 
                                           decoded by preprocessing layer
                           - trainable   - categorical coding processed
                                           by trainable embedding layer
        - embedding_dim -- size of embedding vectors
        - dropout_rate  -- dropout rate for inserted dropout layer
                           If it is 0 or None no droput layer is inserted
        - regul_dense_only -- flag to regulirize only dense layers
        - optimizer   -- training optimizer
        Returns compiled dnn
        """
        if input_type == "one_hot":
            _input1 = layers.Input(shape=(None, n_tokens,))
            _input2 = layers.Input(shape=(None, n_tokens,))
        elif input_type == "categorical" or input_type == "trainable":
            _input1 = layers.Input(shape=(None,))
            _input2 = layers.Input(shape=(None,))
        else:
            sys.exit(f"Wrong type {input_type} of input_type parameter of twoWaySimilarityCNN")
        _maker = SeqBlockFactory(n_tokens)
        if shared:
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
        else:
            _conv1 = _maker.convBlock(
                convolutions, dense = side_dense, pool = pool,
                conv_act = conv_act, conv_bias = conv_bias,
                dense_bias = dense_bias, input_type = input_type,
                regularizer = self._regularizer,
                embedding_dim = embedding_dim,
                dropout_rate = dropout_rate,
                regul_dense_only = regul_dense_only)
            _conv2 = _maker.convBlock(
                convolutions, dense = side_dense, pool = pool,
                conv_act = conv_act, conv_bias = conv_bias,
                dense_bias = dense_bias, input_type = input_type,
                regularizer = self._regularizer,
                embedding_dim = embedding_dim,
                dropout_rate = dropout_rate,
                regul_dense_only = regul_dense_only)
            _pool1 = _conv1(_input1)
            _pool2 = _conv2(_input2)
        _merged = layers.concatenate([_pool1, _pool2], axis=-1)
        _output = self._denseClassifier(_merged, w_dense)
        return self._compile([_input1, _input2,], _output,
                             optimizer = optimizer)

    def _compile(self, inputs, output, optimizer = "rmsprop"):
        """
        Make functional dnn model and compile it
        Parameters:
        - inputs  -- list of dnn inputs
        - output  -- dnn output
        - optimizer   -- training optimizer
        Returns compiled DNN
        """
        _dnn = models.Model(inputs, output)
        _loss = BaseModelFactory.compLoss(self.n_labels)
        _dnn = SeqBlockFactory.compileDNN(
            _dnn, _loss, optimizer = optimizer)
        return _dnn

    def siameseSimilarityCNN(self, n_tokens,
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
            _output = self._denseClassifier(_merged, w_dense)
        elif merge == "dot_prod_sigmoid":
            _output = self._dotProdClassifier(_pool1, _pool2)
        elif merge == "cosine":
            _output = layers.Dot(axes = 1, 
                        normalize = True)([_pool1, _pool2])
        else:
            sys.exit(f"Wrong method {merge} of merging outputs of Siamese blocks")
        return self._compile([_input1, _input2,], _output,
                             optimizer = optimizer)

    def twoWayAsymSimilarityCNN(self, n_tokens1, n_tokens2,
                                convolutions, w_dense,
                                pool = 'max', side_dense = [],
                                conv_act = None, conv_bias = True,
                                dense_bias = True,
                                input_type = "trainable",
                                embedding_dim1 = None,
                                embedding_dim2 = None,
                                regul_dense_only = True,
                                dropout_rate = 0,
                                merge = "subtract",
                                optimizer = "adam"):
        """
        Make asymmetric two way convolutional dnn 
        for similarity analysis of token sequences
        of code written in two different languages
        
        Parameters:
        - n_tokens1     -- number of types of tokens for 1-st language
        - n_tokens2     -- number of types of tokens for 2-nd language
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
        - embedding_dim1 -- size of embedding vectors for 1-st language
        - embedding_dim2 -- size of embedding vectors for 2-nd language
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
        _maker1 = SeqBlockFactory(n_tokens1)
        _conv1 = _maker1.convBlock(
            convolutions, dense = side_dense, pool = pool,
            conv_act = conv_act, conv_bias = conv_bias,
            dense_bias = dense_bias, input_type = input_type,
            regularizer = self._regularizer,
            embedding_dim = embedding_dim1,
            dropout_rate = dropout_rate,
            regul_dense_only = regul_dense_only)
        _maker2 = SeqBlockFactory(n_tokens2)
        _conv2 = _maker2.convBlock(
            convolutions, dense = side_dense, pool = pool,
            conv_act = conv_act, conv_bias = conv_bias,
            dense_bias = dense_bias, input_type = input_type,
            regularizer = self._regularizer,
            embedding_dim = embedding_dim2,
            dropout_rate = dropout_rate,
            regul_dense_only = regul_dense_only)
        _pool1 = _conv1(_input1)
        _pool2 = _conv2(_input2)
        if merge == "concatenate":
            _merged = layers.concatenate([_pool1, _pool2], axis=-1)
            _output = self._denseClassifier(_merged, w_dense)
        elif merge == "subtract":
            _merged = self._absDifference(_pool1, _pool2)
            _output = self._denseClassifier(_merged, w_dense)
        elif merge == "dot_prod_sigmoid":
            _output = self._dotProdClassifier(_pool1, _pool2)
        elif merge == "cosine":
            _output = layers.Dot(axes = 1, 
                        normalize = True)([_pool1, _pool2])
        else:
            sys.exit(f"Wrong method {merge} of merging outputs of Siamese blocks")
        return self._compile([_input1, _input2,], _output,
                             optimizer = optimizer)
#---------------- End of class FuncModelFactory ---------------------------
