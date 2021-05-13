#!/usr/bin/env python

# Copyright (c) 2020 IBM Corp. - Geert Janssen <geert@us.ibm.com>

# Based on: masked_language_modeling.py
# https://keras.io/examples/nlp/masked_language_modeling/
# Fixed spelling errors in messages and comments.

# Preparation on dyce2:
# virtualenv --system-site-packages tf-nightly
# source tf-nightly/bin/activate
# pip install tf-nightly
# pip install dataclasses
# pip install pandas
# pip install pydot
# Results in TF 2.5.0 using the available CUDA 11

import os
#0 = all messages are logged (default behavior)
#1 = INFO messages are not printed
#2 = INFO and WARNING messages are not printed
#3 = INFO, WARNING, and ERROR messages are not printed
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization
from dataclasses import dataclass
import pandas as pd
import numpy as np
import glob
import re
from pprint import pprint

@dataclass
class Config:
    MAX_LEN = 256               # length of each input sample in tokens
    BATCH_SIZE = 32             # batch size
    LR = 0.001                  # learning rate
    VOCAB_SIZE = 512            # max number of words in vocabulary
    EMBED_DIM = 128             # word embedding vector size
    NUM_HEAD = 8                # used in bert model
    FF_DIM = 128                # feedforward; used in bert model
    NUM_LAYERS = 1              # number of BERT module layers

config = Config()

# Every sample file contains a single line of text.
# Returns these lines as a list of strings.
def get_text_list_from_files(files):
    text_list = []
    for name in files:
        with open(name) as f:
            for line in f:
                text_list.append(line)
    return text_list

# Compose the full path names to the token files.
# Creates and returns a dataframe.
# Frame has single key "tokens".
def get_data_from_text_files(folder_name):
    files = glob.glob(folder_name + "/*.toks")
    texts = get_text_list_from_files(files)
    df = pd.DataFrame({"tokens": texts})
    df = df.sample(len(df)).reset_index(drop=True)
    return df

all_data = get_data_from_text_files("train")
#print("all_data:", all_data)

# Part of TF dataflow graph.
def custom_standardization(input_data):
    # No special prep.
    return input_data

def get_vectorize_layer(texts, vocab_size, max_seq):
    """Build Text vectorization layer

    Args:
      texts (list): List of string, i.e., input texts
      vocab_size (int): vocab size
      max_seq (int): Maximum sequence length.

    Returns:
        layers.Layer: Return TextVectorization Keras Layer
    """
    vectorize_layer = TextVectorization(
        max_tokens=vocab_size,
        output_mode="int",
        standardize=custom_standardization,
        output_sequence_length=max_seq,
    )
    vectorize_layer.adapt(texts)

    # Insert mask token in vocabulary
    vocab = vectorize_layer.get_vocabulary()
    #print("len(vocab):", len(vocab)) #177
    #vocab: ['', '[UNK]', 'the', 'and', 'a', 'of', ...] all lower-case
    #GJ20: where do the empty string and [UNK] come from?
    # they are created by adapt() as words 0 and 1
    # '' is padding token; [UNK] is OOV token
    vocab = vocab[2:len(vocab)-1] + ["[mask]"]
    #print("len(vocab):", len(vocab)) #175
    #GJ20: anyway first 2 words removed and '[mask]' added at the end
    vectorize_layer.set_vocabulary(vocab)
    # '' and [UNK] are back in
    #vocab = vectorize_layer.get_vocabulary()
    #print("len(vocab):", len(vocab)) #177
    # '[mask]' has been added as last (least frequent) word in the vocab
    return vectorize_layer

vectorize_layer = get_vectorize_layer(
    all_data.tokens.values.tolist(),
    config.VOCAB_SIZE,
    config.MAX_LEN,
)

# Serialize vocabulary and dump to file:
import pickle
with open("vocabulary.pkl", "wb") as out:
    pickle.dump(vectorize_layer.get_vocabulary(), out)

# Get mask token id for masked language model
mask_token_id = vectorize_layer(["[mask]"]).numpy()[0][0]
#print("mask_token_id:", mask_token_id) #176 (always last index in vocab)

# Encodes the token strings by int vocab indices.
def encode(texts):
    encoded_texts = vectorize_layer(texts)
    return encoded_texts.numpy()

# Randomly replace tokens by the [mask] and keep replaced token as label.
def get_masked_input_and_labels(encoded_texts):
    # These numbers come from something called "BERT recipe":
    # 15% used for prediction. 80% of that is masked. 10% is random token,
    # 10% is just left as is.
    
    # 15% BERT masking
    #print("encoded_texts.shape:", encoded_texts.shape) #(50000, 256)
    inp_mask = np.random.rand(*encoded_texts.shape) < 0.15
    #print("inp_mask:", inp_mask) #[[False False True ...] ...]
    # Do not mask special tokens
    # GJ20: what are these special tokens? 0 and 1! But why <= 2? Mistake?
    inp_mask[encoded_texts < 2] = False
    # Set targets to -1 by default, it means ignore
    labels = -1 * np.ones(encoded_texts.shape, dtype=int)
    # Set labels for masked tokens
    labels[inp_mask] = encoded_texts[inp_mask]
    # False positions -> -1, True -> encoded word (vocab index)
    #print("labels:", labels) #[[10 -1 -1 ...] [-1 -1 -1 994 ...] ... ]

    # Prepare input
    encoded_texts_masked = np.copy(encoded_texts)
    # Set input to [MASK] which is the last token for the 90% of tokens
    # This means leaving 10% unchanged
    inp_mask_2mask = inp_mask & (np.random.rand(*encoded_texts.shape) < 0.90)
    # mask token is the last in the dict
    encoded_texts_masked[inp_mask_2mask] = mask_token_id

    # Set 10% to a random token
    inp_mask_2random = inp_mask_2mask & (np.random.rand(*encoded_texts.shape) < 1 / 9)
    #GJ20: why 3 and not 2?
    encoded_texts_masked[inp_mask_2random] = np.random.randint(
        2, mask_token_id, inp_mask_2random.sum()
    )

    # Prepare sample_weights to pass to .fit() method
    sample_weights = np.ones(labels.shape)
    sample_weights[labels == -1] = 0

    # y_labels would be same as encoded_texts, i.e., input tokens
    y_labels = np.copy(encoded_texts)

    return encoded_texts_masked, y_labels, sample_weights

# Prepare data for masked language model
x_all_tokens = encode(all_data.tokens.values)
#print("x_all_tokens.shape:", x_all_tokens.shape) #(50000, 256)

# Encoding and masking step:
x_masked_train, y_masked_labels, sample_weights = get_masked_input_and_labels(
    x_all_tokens
)

mlm_ds = (
    tf.data.Dataset.from_tensor_slices(
        (x_masked_train, y_masked_labels, sample_weights))
    .shuffle(1000)
    .batch(config.BATCH_SIZE)
)

# i is layer number 0,1,2...
def bert_module(query, key, value, i):
    # Multi headed self-attention
    attention_output = layers.MultiHeadAttention(
        num_heads=config.NUM_HEAD,
        key_dim=config.EMBED_DIM // config.NUM_HEAD,
        name="encoder_{}/multiheadattention".format(i),
    )(query, key, value)
    attention_output = layers.Dropout(0.1, name="encoder_{}/att_dropout".format(i))(attention_output)
    attention_output = layers.LayerNormalization(
        epsilon=1e-6, name="encoder_{}/att_layernormalization".format(i)
    )(query + attention_output)

    # Feed-forward layer
    ffn = keras.Sequential(
        [
            layers.Dense(config.FF_DIM, activation="relu"),
            layers.Dense(config.EMBED_DIM),
        ],
        name="encoder_{}/ffn".format(i),
    )
    ffn_output = ffn(attention_output)
    ffn_output = layers.Dropout(0.1, name="encoder_{}/ffn_dropout".format(i))(
        ffn_output
    )
    sequence_output = layers.LayerNormalization(
        epsilon=1e-6, name="encoder_{}/ffn_layernormalization".format(i)
    )(attention_output + ffn_output)
    return sequence_output

def get_pos_encoding_matrix(max_len, d_emb):
    pos_enc = np.array(
        [
            [pos / np.power(10000, 2 * (j // 2) / d_emb) for j in range(d_emb)]
            if pos != 0
            else np.zeros(d_emb)
            for pos in range(max_len)
        ]
    )
    #pos_enc.shape = (512, 128)
    # 0::2 means start at 0 and step 2 (all even)
    pos_enc[1:, 0::2] = np.sin(pos_enc[1:, 0::2])  # dim 2i
    pos_enc[1:, 1::2] = np.cos(pos_enc[1:, 1::2])  # dim 2i+1
    return pos_enc

loss_fn = keras.losses.SparseCategoricalCrossentropy(
    reduction=tf.keras.losses.Reduction.NONE
)
loss_tracker = tf.keras.metrics.Mean(name="loss")

class MaskedLanguageModel(tf.keras.Model):
    def train_step(self, inputs):
        if len(inputs) == 3:
            features, labels, sample_weight = inputs
        else:
            features, labels = inputs
            sample_weight = None

        with tf.GradientTape() as tape:
            predictions = self(features, training=True)
            loss = loss_fn(labels, predictions, sample_weight=sample_weight)

        # Compute gradients
        trainable_vars = self.trainable_variables
        gradients = tape.gradient(loss, trainable_vars)

        # Update weights
        self.optimizer.apply_gradients(zip(gradients, trainable_vars))

        # Compute our own metrics
        loss_tracker.update_state(loss, sample_weight=sample_weight)

        # Return a dict mapping metric names to current value
        return {"loss": loss_tracker.result()}

    @property
    def metrics(self):
        # We list our `Metric` objects here so that `reset_states()` can be
        # called automatically at the start of each epoch
        # or at the start of `evaluate()`.
        # If you don't implement this property, you have to call
        # `reset_states()` yourself at the time of your choosing.
        return [loss_tracker]

def create_masked_language_bert_model():
    inputs = layers.Input((config.MAX_LEN,), dtype=tf.int64)

    word_embeddings = layers.Embedding(
        input_dim=config.VOCAB_SIZE,
        output_dim=config.EMBED_DIM,
        name="word_embedding"
    )(inputs)
    # GJ20: what does this do? Positional embedding part of transformer.
    position_embeddings = layers.Embedding(
        input_dim=config.MAX_LEN,
        output_dim=config.EMBED_DIM,
        weights=[get_pos_encoding_matrix(config.MAX_LEN, config.EMBED_DIM)],
        name="position_embedding",
    )(tf.range(start=0, limit=config.MAX_LEN, delta=1))
    embeddings = word_embeddings + position_embeddings

    encoder_output = embeddings
    for i in range(config.NUM_LAYERS):
        encoder_output = bert_module(encoder_output, encoder_output, encoder_output, i)

    mlm_output = layers.Dense(config.VOCAB_SIZE, name="mlm_cls", activation="softmax")(encoder_output)
    mlm_model = MaskedLanguageModel(inputs, mlm_output, name="masked_bert_model")

    optimizer = keras.optimizers.Adam(learning_rate=config.LR)
    mlm_model.compile(optimizer=optimizer)
    return mlm_model

# token<->id mappings as dicts:
id2token = dict(enumerate(vectorize_layer.get_vocabulary()))
token2id = {y: x for x, y in id2token.items()}

class MaskedTextGenerator(keras.callbacks.Callback):
    def __init__(self, sample_tokens, top_k=5):
        # encoded review
        self.sample_tokens = sample_tokens
        self.k = top_k

    def decode(self, tokens):
        return " ".join([id2token[t] for t in tokens if t != 0])

    def convert_ids_to_tokens(self, id):
        return id2token[id]

    def on_epoch_end(self, epoch, logs=None):
        prediction = self.model.predict(self.sample_tokens)
        # index of token2id['[mask]'] in list:
        masked_index = np.where(self.sample_tokens == mask_token_id)
        masked_index = masked_index[1]
        mask_prediction = prediction[0][masked_index]

        top_indices = mask_prediction[0].argsort()[-self.k :][::-1]
        values = mask_prediction[0][top_indices]

        for i in range(len(top_indices)):
            p = top_indices[i]
            v = values[i]
            tokens = np.copy(sample_tokens[0])
            # fill in the blank:
            tokens[masked_index[0]] = p
            result = {
                "input_text": self.decode(sample_tokens[0].numpy()),
                "prediction": self.decode(tokens),
                "probability": v,
                #"predicted mask token": self.convert_ids_to_tokens(p),
            }
            pprint(result)

sample_tokens = vectorize_layer(["# include < identifier . identifier > # include < identifier . [mask] > int identifier ( int identifier operator int operator identifier operator int identifier ) { }"])

generator_callback = MaskedTextGenerator(sample_tokens.numpy())

bert_masked_model = create_masked_language_bert_model()
bert_masked_model.summary()

from tensorflow.keras.utils import plot_model
# File extension determines output format!
#plot_model(bert_masked_model, to_file='bert_mlm_codenet.pdf', show_shapes=True)
plot_model(bert_masked_model, to_file='bert_mlm_codenet.dot', show_shapes=True, expand_nested=True)
quit()
#GJ20: 5 epochs of 50000 samples with 32 per badge gives 1562.5 iterations.
print("Train BERT MLM model on CodeNet:")
bert_masked_model.fit(mlm_ds, epochs=5, callbacks=[generator_callback])
bert_masked_model.save("bert_mlm_codenet.h5")
