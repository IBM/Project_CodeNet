#!/usr/bin/env python

# Copyright (c) 2020 IBM Corp. - Geert Janssen <geert@us.ibm.com>

import os
#0 = all messages are logged (default behavior)
#1 = INFO messages are not printed
#2 = INFO and WARNING messages are not printed
#3 = INFO, WARNING, and ERROR messages are not printed
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
import tensorflow as tf
from tensorflow import keras
import numpy as np
from pprint import pprint
from dataclasses import dataclass
import re

@dataclass
class Config:
    MAX_LEN = 256               # length of each input sample
    BATCH_SIZE = 32             # batch size
    LR = 0.001                  # learning rate
    VOCAB_SIZE = 512            # max number of words in vocabulary
    EMBED_DIM = 128             # word embedding vector size
    NUM_HEAD = 8                # used in bert model
    FF_DIM = 128                # feedforward; used in bert model
    NUM_LAYERS = 1              # number of BERT module layers

config = Config()

class MaskedLanguageModel(tf.keras.Model):
    pass

# Load pretrained bert model
mlm_model = keras.models.load_model(
    "bert_mlm_codenet.h5", custom_objects={"MaskedLanguageModel": MaskedLanguageModel}
)
mlm_model.trainable = False
#mlm_model.summary()

# Get the vocabulary:
import pickle
with open("vocabulary.pkl", "rb") as f:
    vocabulary = pickle.load(f)

# token<->id mappings as dicts:
id2token = dict(enumerate(vocabulary))
token2id = {y: x for x, y in id2token.items()}
mask_token_id = len(vocabulary)-1
print("mask_token_id:", mask_token_id)

# Mimick the TextVectorization tokenization.
def tokenize(text):
    # split at ' '
    return text.split()

# Turns text into list of vocabulary indices.
def encode(text):
    R = [0] * config.MAX_LEN # all padding
    text = tokenize(text)
    for i in range(len(text)):
        w = text[i]
        if w in token2id:
            R[i] = token2id[w]
        else:
            R[i] = 1 # OOV: [UNK]
    return np.array(R)

# Opposite of encode: restores text string from token ids.
def decode(tokens):
    return " ".join([id2token[t] for t in tokens if t != 0])

# Do predictions:
def predict(text):
    sample = np.reshape(encode(text), (1, config.MAX_LEN))
    print("sample.shape:", sample.shape) #(1, 256)
    prediction = mlm_model.predict(sample)
    print("prediction.shape:", prediction.shape) #(1, 256, 512)

    # position of token2id['[mask]'] in list:
    masked_index = np.where(sample == mask_token_id)[1][0]
    print("masked_index:", masked_index)
    # all substitute word probabilities:
    mask_prediction = prediction[0][masked_index]
    #mask_prediction.shape = (512,)
    top_k = 1
    # word indices with top-k highest probabilities:
    # Trick: negate array so order is reversed:
    #top_indices = (-mask_prediction).argsort()[0:top_k]
    top_indices = mask_prediction.argsort()[-top_k:][::-1]
    # probabilities of the top_k
    values = mask_prediction[top_indices]

    for i in range(len(top_indices)):
        w = id2token[top_indices[i]]
        v = values[i]
        # fill in the blank:
        #tokens = np.copy(sample[0])
        #tokens[masked_index] = p
        result = {
            "input_text": text,
            # better use original text:
            "prediction": text.replace('[mask]', w),
            "probability": v,
            #"predicted mask token": w,
        }
        pprint(result)

# Read a sentence from stdin, 1 per line:
import sys

if sys.stdin.isatty():
    print("Enter a line of C tokens with [mask] replacing some token:")
for line in sys.stdin:
    line = line.rstrip()
    predict(line)
