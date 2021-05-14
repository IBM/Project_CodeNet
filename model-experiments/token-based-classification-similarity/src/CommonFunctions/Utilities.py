"""
Module defining some utility functions used with ML applications
"""
import os
import sys
import numpy as np
import tensorflow as tf
import random as python_random

def resetSeeds():
    """
    Reset system seeds for random generators
    """
    np.random.seed(123) 
    python_random.seed(123)
    tf.random.set_seed(1234)

def setupCheckpoint(checkpoint_dir):
    """
    Set up writing down checkpoints:
    - Make checkpoint directory is it does not exist
    - Find latest checkpoint
    Parameter:
    - checkpoint_dir  -- Directory for writing down checkpoints
    Returns:
    """
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
        latest_checkpoint = None
    else:
        checkpoints = [checkpoint_dir + "/" + name for 
                       name in os.listdir(checkpoint_dir)]  
        latest_checkpoint = max(checkpoints, key=os.path.getctime) \
            if checkpoints else None
    return latest_checkpoint

def getCheckpoint(checkpoint_dir, checkpoint = None):
    """
    Get either the specified checkpoint or the latest one
    Parameters:
    - checkpoint_dir  -- Directory with checkpoints
    - checkpoint      -- Checkpoint file name
    Returns: full path to checkpoint file
    """
    if not checkpoint_dir:
        sys.exit("Directory with DNN models is not defined")
    if not os.path.exists(checkpoint_dir):
        sys.exit(f"Directory {checkpoint_dir} with DNN models does not exist")
    if checkpoint:
        if os.path.exists(f"{checkpoint_dir}/checkpoint"):
            return ckpt_file
        else:
            sys.exit(f"Directory {checkpoint_dir} does not have checkpoint {checkpoint}")
    checkpoints = [checkpoint_dir + "/" + name for 
                       name in os.listdir(checkpoint_dir)]
    if checkpoints:
        return max(checkpoints, key=os.path.getctime)
    else:
        sys.exit(f"Directory {checkpoint_dir} with DNN models is empty")
    
def makeCkptCallback(checkpoint_dir, monitor = "val_accuracy"):
    """
    - Create callback function for writing down checkpoints
    Parameter:
    - checkpoint_dir  -- Directory for writing down checkpoints
    - monitor         -- value to monitor
    Returns:
    - Callback function created
    """
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath = checkpoint_dir + "/ckpt-{epoch}",
        monitor = monitor,
        verbose = 0, save_best_only = True,
        save_weights_only = False,
        mode = "auto", save_freq= "epoch")
    return checkpoint_callback

def memoryUsage(point):
    """
    Print memory usage
    Parameter:
    - point --  identifier of print: string or number
    """
    from resource import getrusage, RUSAGE_SELF
    _resource_usage = getrusage(RUSAGE_SELF)
    print(f"{point}:  MEMORY = {_resource_usage.ru_maxrss}")

def makeFilePath(*parts, m = None):
    """
    Make path to file and check its existance
    Check if the path exists and exit if it is not found
    The existance of the path is checked only if 
    the description of file is defined
    Parameters:
    - m      -- description of the path to pringt in the message 
                if the path does not exist
    - parts  -- parts to concatenate to get file path
    """
    _p = "/".join(parts).replace("//", "/")
    if m and not os.path.exists(_p):
        sys.exit(f"{m} {_p} is not found")
    return _p

'''
def accessModules(*modules):
    """
    Update sys.path to access required modules
    Parameters:
    - modules  -- modules to access
    """
    main_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
'''
           
    
