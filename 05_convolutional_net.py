import tensorflow as tf
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data

batch_size = 128
test_size = 256

mnist = input_data.read_data_sets("/home/liuchong/PycharmProjects/tensorflow/Fun-Try/MNIST_data/", one_hot=True)
trX, trY, teX, teY = mnist.train.images, mnist.train.labels, mnist.test.images, mnist.test.labels

trX = trX.reshape([-1, 28, 28, 1])
teX = teX.reshape([-1, 28, 28, 1])

X = tf.placeholder(tf.float32, [None, 28, 28, 1])
Y = tf.placeholder(tf.float32, [None, 10])

def init_weight(shape):
    return tf.Variable(tf.random_normal(shape, stddev=0.01))

def model(X, w, w2, w3, w4, w_o, p_keep_conv, p_keep_hidden):
    l1a = tf.nn.relu(tf.nn.conv2d(X, w, strides=[1,1,1,1], padding='SAME')) #[?, 28, 28, 32]
    l1 = tf.nn.max_pool(l1a, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME') #[?, 14, 14, 32]
    l1 = tf.nn.dropout(l1, p_keep_conv)

    l2a = tf.nn.relu(tf.nn.conv2d(l1, w2, strides=[1,1,1,1], padding='SAME')) #[?, 14, 14, 64]
    l2 = tf.nn.max_pool(l2a, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME') #[?, 7, 7, 64]
    l2 = tf.nn.dropout(l2, p_keep_conv)

    l3a = tf.nn.relu(tf.nn.conv2d(l2, w3, strides=[1,1,1,1], padding='SAME')) #[?, 7, 7, 128]
    l3 = tf.nn.max_pool(l3a, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME') #[?, 4, 4, 128]
    l3 = tf.reshape(l3, [-1, w4.get_shape().as_list()[0]]) #[?, 2048]
    l3 = tf.nn.dropout(l3, p_keep_conv)

    l4 = tf.nn.relu(tf.matmul(l3, w4))
    l4 = tf.nn.dropout(l4, p_keep_hidden)

    return tf.matmul(l4, w_o)

w = init_weight([3,3,1,32])
w2 = init_weight([3,3,32,64])
w3 = init_weight([3,3,64,128])
w4 = init_weight([2048, 625])
w_o = init_weight([625, 10])

p_keep_conv = tf.placeholder(tf.float32)
p_keep_hidden = tf.placeholder(tf.float32)

py_x = model(X, w, w2, w3, w4, w_o, p_keep_conv, p_keep_hidden)

cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=py_x, labels=Y))

train_op = tf.train.RMSPropOptimizer(0.001, 0.9).minimize(cost)

predict = tf.argmax(py_x, 1)

with tf.Session() as sess:
    tf.global_variables_initializer().run()

    for i in range(100):
        training_batch = zip(range(0, len(trX), batch_size), range(batch_size, len(trX)+1, batch_size))
        for start, end in training_batch:
            sess.run(train_op, feed_dict={X:trX[start:end], Y:trY[start:end], p_keep_conv:0.8, p_keep_hidden:0.5})
        test_indices = np.arange(len(teX))
        np.random.shuffle(test_indices)
        test_indices = test_indices[0:test_size]

        print (i, np.mean(np.argmax(teY[test_indices], axis=1) == sess.run(predict, feed_dict={X:teX[test_indices],
                                                                                               p_keep_conv:1.0,
                                                                                               p_keep_hidden:1.0})))