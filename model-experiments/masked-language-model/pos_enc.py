#!/usr/bin/env python

# Copyright (c) 2020 IBM Corp. - Geert Janssen <geert@us.ibm.com>

import numpy as np
import matplotlib.pyplot as plt

tokens = 256
dimensions = 128

def get_pos_encoding_matrix(max_len, d_emb):
    pos_enc = np.array(
        [
            [pos / np.power(10000, 2 * (j // 2) / d_emb) for j in range(d_emb)]
            if pos != 0
            else np.zeros(d_emb)
            for pos in range(max_len)
        ]
    )
    #print("pos_enc.shape:", pos_enc.shape) # (256,128)
    # 0::2 means start at 0 and step 2 (all even)
    pos_enc[1:, 0::2] = np.sin(pos_enc[1:, 0::2])  # dim 2i
    pos_enc[1:, 1::2] = np.cos(pos_enc[1:, 1::2])  # dim 2i+1
    return pos_enc

pos_encoding = get_pos_encoding_matrix(tokens, dimensions)

plt.figure(figsize=(12,8))
plt.pcolormesh(pos_encoding, cmap='viridis')
plt.xlabel('Embedding Dimensions')
plt.xlim((0, dimensions))
plt.ylim((tokens,0))
plt.ylabel('Token Position')
plt.colorbar()
plt.show()
