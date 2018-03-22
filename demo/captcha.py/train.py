#!/usr/bin/env python
#-*- coding: utf8 -*-

import numpy as np
import tensorflow as tf

import gen

labels_units = len(gen.rand_seqs) + 2
# print labels_units # 38

def text_to_seqs(text):
    return [gen.rand_seqs.index(c) + 1 for c in text]

def seqs_to_text(seqs):
    return ''.join([gen.rand_seqs[i-1] for i in seqs])

def conv(inputs, filters, kernel_size, strides):
    return tf.layers.conv2d(inputs,
        filters     = filters,
        kernel_size = kernel_size,
        strides     = strides,
        padding     = "same",
        activation  = tf.nn.leaky_relu,
        use_bias    = True,
        kernel_initializer = tf.contrib.layers.xavier_initializer_conv2d(),
        bias_initializer = tf.constant_initializer(0.0001),
    )

def build_net():
    net = {}
    net['x'] = tf.placeholder(tf.float32, shape=[None, 40, 120, 4], name="X")
    net['y'] = tf.sparse_placeholder(tf.int32, name="Y")
    net['len'] = tf.placeholder(tf.int32, shape=[None])

    layer = net['x']
    layer = conv(layer, 32, 5, 2)
    layer = conv(layer, 64, 3, 1)
    layer = conv(layer, 128, 3, 1)
    layer = conv(layer, 128, 3, 2)
    layer = conv(layer, 256, 3, 1)
    layer = conv(layer, 256, 3, 2)
    layer = conv(layer, 512, 3, 1)
    layer = conv(layer, 512, 1, 1)
    logits = layer
    # print logits.get_shape()
    # (?, 5, 15, 512) -> (15, ?, 5, 512)
    logits = tf.transpose(logits, (2, 0, 1, 3))
    # (15, ?, 5, 512) -> (15 * ?, 5 * 512)
    logits = tf.reshape(logits, (-1, 2560))
    # (15 * ?, 5 * 512) -> (15 * ?, 512)
    logits = tf.layers.dense(logits,
        units       = 512,
        activation  = tf.nn.leaky_relu,
        use_bias    = True,
        kernel_initializer = tf.truncated_normal_initializer(stddev=0.1),
        bias_initializer = tf.constant_initializer(0.01),
    )
    # (15 * ?, 512) -> (15 * ?, n_class)
    logits = tf.layers.dense(logits,
        units       = labels_units,
        activation  = None,
        use_bias    = True,
        kernel_initializer = tf.truncated_normal_initializer(stddev=0.1),
        bias_initializer = tf.constant_initializer(0.01),
    )
    # (15 * ?, n_class) -> (15, ?, n_class)
    logits = tf.reshape(logits, (15, -1, labels_units))
    loss = tf.nn.ctc_loss(labels=net['y'], inputs=logits, sequence_length=net['len'])
    net['loss'] = tf.reduce_mean(loss)
    net['train_op'] = tf.train.AdamOptimizer(learning_rate=0.000005).minimize(net['loss'])
    decoded, log_prob = tf.nn.ctc_beam_search_decoder(logits, net['len'], merge_repeated=False)
    net['decoded'] = decoded[0]
    net['acc'] = tf.reduce_mean(tf.edit_distance(tf.cast(net['decoded'], tf.int32), net['y']))
    return net

def sparse_tuple_from(sequences, dtype=np.int32):
    indices = []
    values = []
    for n, seq in enumerate(sequences):
        indices.extend(zip([n] * len(seq), xrange(len(seq))))
        values.extend(seq)
    indices = np.asarray(indices, dtype=np.int64)
    values = np.asarray(values, dtype=dtype)
    shape = np.asarray([len(sequences), np.asarray(indices).max(0)[1] + 1], dtype=np.int64)
    return indices, values, shape

def decode_a_seq(indexes, sparse_tensor):
    decoded = []
    for m in indexes:
        char = gen.rand_seqs[sparse_tensor[1][m]-1]
        decoded.append(char)
    return ''.join(decoded)

def decode_sparse_tensor(sparse_tensor):
    decoded_indexes = list()
    current_i = 0
    current_seq = []
    for offset, i_and_index in enumerate(sparse_tensor[0]):
        i = i_and_index[0]
        if i != current_i:
            decoded_indexes.append(current_seq)
            current_i = i
            current_seq = list()
        current_seq.append(offset)
    decoded_indexes.append(current_seq)
    result = []
    for index in decoded_indexes:
        result.append(decode_a_seq(index, sparse_tensor))
    return result

def train(net):
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    for i in xrange(10000000):
        xs, ys = [], []
        lens = []
        for j in xrange(16):
            text, image = gen.gene_code()
            seqs = text_to_seqs(text)
            vec = np.asarray(image).astype('float32') / 255.0
            xs.append(vec)
            ys.append(seqs)
            lens.append(4)
        ys = sparse_tuple_from(ys)
        _, loss, decoded, acc = sess.run(
            (net['train_op'], net['loss'], net['decoded'], net['acc']),
            feed_dict={net['x']: xs, net['y']: ys, net['len']: lens})
        if i % 100 == 0:
            print i, loss, acc
            # print ys[0].shape, ys[1].shape, ys[2].shape
            # print decoded[0].shape, decoded[1].shape, decoded[2].shape
            print '', decode_sparse_tensor(ys)
            print '', decode_sparse_tensor(decoded)

if __name__ == '__main__':
    # print text_to_seqs('SYW5')
    # print seqs_to_text(text_to_seqs('SYW5'))
    net = build_net()
    train(net)
