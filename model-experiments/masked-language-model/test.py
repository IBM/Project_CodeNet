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
from dataclasses import dataclass
import glob
import re
import random

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
#print("mask_token_id:", mask_token_id)

# Every sample contains a single line of text.
# Returns list of strings.
def get_text_list_from_files(files):
    text_list = []
    for name in files:
        with open(name) as f:
            for line in f:
                text_list.append(line)
    return text_list

# Compose the full path names to the token files.
def get_data_from_text_files(folder_name):
    files = glob.glob(folder_name + "/*.toks")
    texts = get_text_list_from_files(files)
    return texts

tests = get_data_from_text_files("test")

# Mimick the TextVectorization tokenization.
def tokenize(text):
    # split at ' '
    return text.split()

# Turns text into list of vocabulary indices.
def encode(text):
    R = [0] * config.MAX_LEN # all padding
    text = tokenize(text)
    ntoks = len(text)
    if ntoks > config.MAX_LEN:
        ntoks = config.MAX_LEN
        text = text[:ntoks]
    # pick random position (never a padding):
    k = random.randint(0, ntoks-1)
    golden = 0
    for i in range(len(text)):
        w = text[i]
        if w in token2id:
            R[i] = token2id[w]
        else:
            R[i] = 1 # OOV: [UNK]
        if i == k:
            #golden = w
            golden = R[i]
            #print("k:", k, "golden:", golden)
            R[i] = mask_token_id
    return k, golden, np.array(R)

def predict(text):
    k, golden, R = encode(text)
    sample = np.reshape(R, (1, config.MAX_LEN))
    #print("sample.shape:", sample.shape) #(1, 256)
    prediction = mlm_model.predict(sample)
    #print("prediction.shape:", prediction.shape) #(1, 256, 512)

    # position of token2id['[mask]'] in list:
    masked_index = k
    #print("masked_index:", masked_index)
    # all substitute word probabilities:
    mask_prediction = prediction[0][masked_index]
    # word indices with top-k highest probabilities:
    top_k = 5
    # Trick: negate array so order is reversed:
    #top_indices = (-mask_prediction).argsort()[0:top_k]
    top_indices = mask_prediction.argsort()[-top_k:][::-1]
    # probabilities of the top_k
    values = mask_prediction[top_indices]
    correct_top1 = top_indices[0] == golden
    correct_top5 = False
    for i in range(len(top_indices)):
        if top_indices[i] == golden:
            correct_top5 = True
            break
    return correct_top1, correct_top5

# enumerate all tests
correct_top1 = 0
correct_top5 = 0
num_tests = 0
for test in tests:
    for i in range(10):
        # predict and check
        top1, top5 = predict(test)
        if top1:
            correct_top1+=1
        if top5:
            correct_top5+=1
        num_tests+=1

print("top-1 accuracy:", correct_top1/num_tests);
print("top-5 accuracy:", correct_top5/num_tests);
