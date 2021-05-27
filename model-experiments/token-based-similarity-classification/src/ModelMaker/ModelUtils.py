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

class UniqueSeed():
    """
    Class for generating unique seed for 
    model initializing DNN models
    """
    #Initial value of seed
    seed = 1234
    #Step at which seed is incrtemented after its each query
    step = 17

    @classmethod
    def getSeed(cls):
        """
        Get unique seed
        """
        cls.seed += cls.step
        return cls.seed
    
    @classmethod
    def setSeed(cls, seed, step = 17):
        """
        Initialize seed externally 
        Parameters:
        - seed  -- Initial value of seed
        - step  -- Step at which seed is incretemented 
                   after its each query
        """
        cls.seed = seed
        cls.step = step

    def __init__(self):
        pass

class BaseModelFactory():
    """
    Base class for factories of DNN models
    Supplies utility methods of other DNN factories
    """
    @classmethod
    def computeInitializer(cls, seed = None):
        """
        Compute layer initializer
        Parameters:
        - seed  -- seed for random generator used by analyzer
                   If it is None a unique repeatable seed is generated
        """
        _seed = seed if seed else UniqueSeed.getSeed()
        #_initializer=initializers.GlorotNormal(seed=seed)
        _initializer=initializers.GlorotUniform(seed=seed)
        return _initializer

    @classmethod
    def computeRegularizer(cls, regular):
        """
        Compute l1 and l2 regulizer
        Parameters:
        - regular  -- regularizer as a pair (l1, l2) 
                      or None if no regularization is applied.
        """
        return None if regular is None \
            else tensorflow.keras.regularizers.l1_l2(l1=regular[0],
                                                     l2=regular[1])

    @classmethod
    def compClassification(cls, labels):
        """
        Compute classification function
        Parameters:
        - labels  -- number of labels (classes)
        """
        return "sigmoid" if labels == 1 \
            else "softmax"

    @classmethod
    def compLoss(cls, labels):
        """
        Compute loss function
        Parameters:
        - labels  -- number of labels (classes)
        """
        return "binary_crossentropy" if labels == 1 \
            else "sparse_categorical_crossentropy"

    @classmethod
    def compileDNN(cls, dnn, loss, optimizer = "rmsprop"):
        """
        Compile sequential DNN
        Parameters:
        - dnn         -- DNN to compile
        - loss        -- loss to use for training
        - optimizer   -- training optimizer
        Returns compiled DNN
        """
        dnn.compile(optimizer = optimizer, loss = loss,
                    metrics = ['accuracy'])
        print("Summary of DNN constructed")
        dnn.summary()
        return dnn

    def __init__(self):
        pass
#---------------- End of class BaseModelFactory ---------------------------

class SeqBlockFactory(BaseModelFactory):
    """
    Factory of sequential DNN blocks for processing sequences of tokens
    for code classification and similarity analysis 

    Provides functions for creating sequential DNN building blocks
    """
    def __init__(self, tokens):
        """
        Initialize factory of DNN sequential building blocks
        Parameters:
        - tokens -- number of types of tokens
                    It is the size (dimensionality) of sequence vectors
                    or number of values for cathegorical input coding
        """
        super(SeqBlockFactory, self).__init__()
        self.n_tokens = tokens
                    
    def addConv1Layer(self, dnn, convolution, activation = None,
                      bias = True, regularizer = None):
        """
        Add to the dnn a convolutional layer
        Parameters:
        - dnn           -- dnn to buld
        - convolution   -- specification of the convolutional layer
                           as list of tuples:
                           either (n filters, kernel width, stride)
                           or (n filters, kernel width) if stride = 1
        - activation    -- activation on convolutional layer
        - bias          -- use or do not use bias on convolutional layer
        - regularizer   -- regularizer of convolution kernels
        Returns exit code:
        - 0 if the layer is successfully added
        - 1 if the layer is specified incorrectly
        """
        if len(convolution) == 3:
            dnn.add(layers.Conv1D(convolution[0], convolution[1],
                strides=convolution[2],
                activation = activation, 
                use_bias = bias,
                kernel_regularizer = regularizer,
                kernel_initializer = BaseModelFactory.computeInitializer()))
            return 0
        elif len(convolution) == 2:
            dnn.add(layers.Conv1D(convolution[0], convolution[1],
                activation = activation, 
                use_bias = bias,
                kernel_regularizer = regularizer,
                kernel_initializer = BaseModelFactory.computeInitializer()))
            return 0
        else:
            return 1

    def addConv1(self, dnn, convolutions, activation = None,
                 bias = True, out_no_act = True,
                 regularizer = None):
        """
        Add to the dnn a stack of convolutional layers
        Parameters:
        - dnn           -- dnn to buld
        - convolutions  -- specification of convolutional layers
                           as list of tuples:
                           either (n filters, kernel width, stride)
                           or (n filters, kernel width) if stride = 1
        - activation    -- activation on all convolutional layers
                           but the last one
        - bias          -- use or do not use bias on convolutional layers
        - out_no_act    -- flag of no activation on last layer
        - regularizer   -- regularizer of convolution kernels
        """            
        for _i in range(len(convolutions)):
            _act = None if _i == len(convolutions) - 1  and out_no_act \
                else activation
            if self.addConv1Layer(dnn, convolutions[_i], activation = _act,
                                  bias = bias, regularizer = regularizer):
                print(f"Wrong specification of convolutional layer {-i}")
                _n_conv_parms = len(convolutions[_i])
                print(f"It has incorrect number {_n_conv_parm} of parameters")
                sys.exit(0)

    def addDense(self, dnn, dense, bias = True, regularizer = None):
        """
        Add a stack of dense layers to the dnn 
        Parameters:
        - dnn         -- dnn to buld
        - dense       -- specification of dense layers as list of
                         their width
        - bias        -- use or do not use bias on dense layers
        - regularizer -- regularizer of dense weight matrix
        """
        if not dense: return
        for _w in dense:
            dnn.add(layers.Dense(_w, activation = 'relu',
                use_bias = bias,
                kernel_regularizer=regularizer,
                kernel_initializer = BaseModelFactory.computeInitializer()))

    def addPooling(self, dnn, pool):
        """
        Add pooling layer to the dnn
        Parameters:
        - dnn     -- dnn to buld
        - pool    -- pooling operation; either
                     'max' for maximum or 'aver' for average
        """
        if pool == 'max':
            dnn.add(layers.GlobalMaxPooling1D())
        elif pool == 'aver':
            dnn.add(layers.GlobalAveragePooling1D())
        else:
            print(f"Error: Wrong pooling operation {pool}\n" +
                  "It should be either max or aver")
            sys.exit(0)

    def addDropout(self, dnn, rate):
        """
        Add droput layer to dnn
        Parameters:
        - dnn     -- dnn to buld
        - rate    -- dropout rate
                     If it is 0 or None no droput layer is inserted
        """
        if rate:
            dnn.add(layers.Dropout(rate, seed = UniqueSeed.getSeed())) 

    def addEmbedding(self, dnn, trainable = False, width = None,
                     regularizer = None):
        """
        Add embedding layer to the DNN
        
        Parameters:
        - dnn         -- dnn to buld
        - trainable   -- flag defining that embedding should be trainable
                         If it is False embedding layer transforms
                         categorical coding into one hot coding
        - width       -- dimension of embedding vectors
                         It effects trainable embedding only.
                         If it is None self.n_tokens is used.
        - regularizer -- regularizer of convolution and dense kernels
                         effects on trainable embedding
        """
        if trainable:
            _output_dim = width if width else self.n_tokens
            _initializer = \
                tensorflow.keras.initializers.RandomUniform(seed = \
                                            UniqueSeed.getSeed())
            dnn.add(layers.Embedding(
                input_dim = self.n_tokens + 1, 
                output_dim = _output_dim,
                embeddings_initializer = _initializer,
                mask_zero = True,
                embeddings_regularizer = regularizer))
        else:
            #Transformation of categorical coding into one-hot
            _initializer = tensorflow.keras.initializers.Identity()
            dnn.add(layers.Embedding(
                input_dim = self.n_tokens + 1, 
                output_dim = self.n_tokens,
                embeddings_initializer = _initializer,
                mask_zero = True))


    def convTower(self, convolutions,
                  conv_act = None, out_no_act = True,
                  conv_bias = True,
                  input_type = "one_hot",
                  regularizer = None, embedding_dim = None,
                  regul_dense_only = True):
        """
        Make sequential DNN building block of stack 
        of convolutional layers
        Parameters:
        - convolutions  -- specification of convolutional layers
                           as list of tuples:
                           either (kernel width, n filters, stride)
                           or (kernel width, n filters) if stride = 1
        - conv_act      -- activation of convolutional layers
        - out_no_act    -- flag of no activation on last convolutional layer
        - conv_bias     -- use bias for convolutional layers
        - input_type    -- type of input layer:
                           - one_hot     -  one hot coding of input samples
                           - categorical - categorical coding 
                                           decoded by preprocessing layer
                           - trainable   - categorical coding processed
                                           by trainable embedding layer
        - regularizer   -- regularizer applied to weights of dense layer
                           and to convolutionand embedding layers if 
                           parameters regul_dense_only = False
        - embedding_dim -- size of embedding vectors
                           It effects trainable embedding only,
                           i.e. input_type == "trainable"
                           If it is None self.n_tokens is used.
                           If it is None self.n_tokens is used
        - regul_dense_only -- flag to regulirize only dense layers
        Returns:
        - dnn  -- constructed DNN building block
        """
        _conv_regul  = None if regul_dense_only else regularizer
        _embed_regul = None if regul_dense_only else regularizer
        _dnn = models.Sequential()
        if input_type == "one_hot":
            _dnn.add(layers.Input(shape=(None, self.n_tokens,)))
        elif input_type == "categorical" or input_type == "trainable":
            _trainable = (input_type == "trainable")
            _dnn.add(layers.Input(shape=(None,)))
            self.addEmbedding(_dnn, trainable = _trainable,
                              width = embedding_dim,
                              regularizer = _embed_regul)
        else:
            sys.exit(f"Wrong type {input_type} of input_type parameter of sequentinal convolution block")
        self.addConv1(_dnn, convolutions, activation = conv_act,
                      bias = conv_bias,
                      out_no_act = out_no_act, 
                      regularizer = _conv_regul)
        return _dnn

    def convBlock(self, convolutions, dense = [], pool = 'max',
                  conv_act = None, conv_bias = True,
                  dense_bias = True, input_type = "one_hot",
                  regularizer = None, embedding_dim = None,
                  dropout_rate = 0,
                  regul_dense_only = True):
        """
        Make sequential convolutional DNN building block
        Parameters:
        - convolutions  -- specification of convolutional layers
                           as list of tuples:
                           either (kernel width, n filters, stride)
                           or (kernel width, n filters) if stride = 1
        - dense         -- specification of dense layers as list of
                           their width except the last one
        - pool          -- pooling operation either:
                           'max' for maximum or 
                           'aver' for average
        - conv_act      -- activation of convolutional layers
        - conv_bias     -- use bias for convolutional layers
        - dense_bias    -- use bias for dense layers
        - input_type    -- type of input layer:
                           - one_hot     -  one hot coding of input samples
                           - categorical - categorical coding 
                                           decoded by preprocessing layer
                           - trainable   - categorical coding processed
                                           by trainable embedding layer
        - regularizer   -- regularizer applied to weights of dense layer
                           and to convolutionand embedding layers if 
                           parameters regul_dense_only = False
        - embedding_dim -- size of embedding vectors
                           It effects trainable embedding only,
                           i.e. input_type == "trainable"
                           If it is None self.n_tokens is used.
                           If it is None self.n_tokens is used
        - dropout_rate  -- dropout rate for inserted dropout layer
                           If it is 0 or None no droput layer is inserted
        - regul_dense_only -- flag to regulirize only dense layers
        Returns:
        - dnn  -- constructed DNN building block
        """
        _conv_regul  = None if regul_dense_only else regularizer
        _embed_regul = None if regul_dense_only else regularizer
        _dnn = models.Sequential()
        if input_type == "one_hot":
            _dnn.add(layers.Input(shape=(None, self.n_tokens,)))
        elif input_type == "categorical" or input_type == "trainable":
            _trainable = (input_type == "trainable")
            _dnn.add(layers.Input(shape=(None,)))
            self.addEmbedding(_dnn, trainable = _trainable,
                              width = embedding_dim,
                              regularizer = _embed_regul)
        else:
            sys.exit(f"Wrong type {input_type} of input_type parameter of functional convolution block")
        self.addConv1(_dnn, convolutions, activation = conv_act,
                      bias = conv_bias,
                      out_no_act = (pool == 'max'), 
                      regularizer = _conv_regul)
        self.addPooling(_dnn, pool)
        self.addDense(_dnn, dense, bias = dense_bias,
                      regularizer = regularizer)
        self.addDropout(_dnn, dropout_rate)
        return _dnn

    def addClassifier(self, dnn, labels, bias = True, 
                      regularizer = None):
        """
        Add to the dnn a dense layer with classifier
        Classifier is either softmax for more than 2 classes
        or sigmoid for 2 classes
        It is expected that input shape is known
        Parameters:
        - dnn         -- dnn to complete
        - labels  -- number of labels (classes)
        - bias    -- use or do not use bias on dense layers
        - regularizer   -- regularizer applied to weights of 
                           convolution, dense, and embedding layers
        """
        dnn.add(layers.Dense(labels, 
                activation = self.compClassification(labels),
                use_bias = bias,
                kernel_regularizer=regularizer,
                kernel_initializer = BaseModelFactory.computeInitializer()))
#---------------- End of class SeqBlockFactory ----------------------
