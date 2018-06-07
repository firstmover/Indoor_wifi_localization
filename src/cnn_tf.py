import os
import sys
import numpy as np
import tensorflow as tf
from datetime import datetime


class CNN():
    """
    simple CNN class
    """

    def __init__(self, x_shape, y_shape, ckpt_dir, tsbd_dir, learning_rate=0.00001):
        """
        x_shape: tensor(placeholder) shape (N, H, W, C)
        y_shape: tensor(placeholder) shape (N, 2)
        ckpt_dir: path to dir for saving checkpoint
        tsbd_dir: path to dir for saving tensorboard records
        """
        self.graph = tf.Graph()
        with self.graph.as_default():
            self.X = tf.placeholder(tf.float32, x_shape)  # (~, 6, 10, 1)
            self.dropout_rate = tf.placeholder(tf.float32, [])

            self.conv1_1 = conv(self.X, 1, 3, 1, 16, 1, 1, name="conv1_1", padding="VALID")  # (~, 6, 8, 16)
            self.conv1_2 = conv(self.conv1_1, 1, 3, 16, 16, 1, 1, name="conv1_2", padding="VALID")  # (~, 6, 6, 16)
            self.pool1 = max_pool(self.conv1_2, 1, 2, 1, 2, name="pool1", padding="VALID")  # (~, 6, 3, 16)
            print("conv1_1 shape: {}".format(self.conv1_1.shape))
            print("conv1_2 shape: {}".format(self.conv1_2.shape))
            print("pool1 shape: {}".format(self.pool1.shape))

            self.flattened = tf.reshape(self.pool1, [-1, 6 * 3 * 16])
            self.fc1 = fc(self.flattened, 6 * 3 * 16, 256, name="fc1")
            self.dropout1 = dropout(self.fc1, self.dropout_rate)
            self.pred = fc(self.dropout1, 256, 2, name="fc2")
            print("flattened shape: {}".format(self.flattened.shape))
            print("fc1 shape: {}".format(self.fc1.shape))
            print("fc2 shape: {}".format(self.pred.shape))

            self.Y = tf.placeholder(tf.float32, y_shape)
            self.loss = tf.reduce_mean(tf.abs(self.pred - self.Y))

            self.layers = ["conv1_1", "conv1_2", "pool1", "fc1", "fc2"]
            self.var_list = [v for v in tf.trainable_variables() if v.name.split('/')[0] in self.layers]
            print("variables:")
            for v in self.var_list:
                print(v.name)
            self.gradients = tf.gradients(self.loss, self.var_list)
            self.optimizer = tf.train.AdamOptimizer(learning_rate)
            self.train_op = self.optimizer.apply_gradients(grads_and_vars=list(zip(self.gradients, self.var_list)))
            self.saver = tf.train.Saver()

        self.sess = tf.Session(graph=self.graph)

        self.writer = tf.summary.FileWriter(tsbd_dir)
        self.ckpt_dir = ckpt_dir
        self.train_summary = tf.summary.scalar("train/loss", self.loss)
        self.val_summary = tf.summary.scalar("val/loss", self.loss)

    def initialize(self, weights_path=None):
        """
        initialize weights
        """
        with self.graph.as_default():
            self.sess.run(tf.global_variables_initializer())
            if weights_path is None:
                self.writer.add_graph(self.graph)
                pass
            else:
                print("resuming from {}".format(weights_path))
                self.saver.restore(self.sess, weights_path)

    def train(self, train_ds, val_ds, st_epoch=0, ed_epoch=5000, display_epochs=100, save_epochs=5000):
        with self.graph.as_default():
            epoch = st_epoch
            while epoch < ed_epoch:
                loss, top, s = self.sess.run([self.loss, self.train_op, self.train_summary], \
                                             feed_dict={self.X: np.expand_dims(train_ds.ndary, -1),
                                                        self.Y: train_ds.pos,
                                                        self.dropout_rate: 0.5
                                                        })
                epoch += 1
                if epoch % display_epochs == 0:
                    print("[{}]:epoch {} loss {}".format(datetime.now(), epoch, loss))
                    self.writer.add_summary(s, epoch)

                if epoch % save_epochs == 0:
                    loss, s = self.sess.run([self.loss, self.val_summary], \
                                            feed_dict={self.X: np.expand_dims(val_ds.ndary, -1),
                                                       self.Y: val_ds.pos,
                                                       self.dropout_rate: 1.0
                                                       })
                    print("\t\t[{}]:validation loss {}".format(datetime.now(), loss))
                    self.writer.add_summary(s, epoch)
                    ckpt_path = os.path.join(self.ckpt_dir, "model_epoch{}.ckpt".format(epoch))
                    self.saver.save(self.sess, ckpt_path)

    def test(self, test_ds):
        with self.graph.as_default():
            pred, loss = self.sess.run([self.pred, self.loss], feed_dict={self.X: np.expand_dims(test_ds.ndary, -1),
                                                                          self.Y: test_ds.pos,
                                                                          self.dropout_rate: 1.0
                                                                          })
            return pred

    def save(self, ckpt_path):
        self.saver.save(self.sess, ckpt_path)


"""
Predefine all necessary layer for the CNN
"""


def conv(x, filter_height, filter_width, input_channels, num_filters, stride_y, stride_x, name,
         padding='SAME', non_linear="RELU", groups=1):
    """
    Adapted from: https://github.com/ethereon/caffe-tensorflow
    """

    # Create lambda function for the convolution
    convolve = lambda i, k: tf.nn.conv2d(i, k,
                                         strides=[1, stride_y, stride_x, 1],
                                         padding=padding)

    with tf.variable_scope(name, reuse=tf.AUTO_REUSE) as scope:
        # Create tf variables for the weights and biases of the conv layer
        weights = tf.get_variable('weights', shape=[filter_height, filter_width, input_channels / groups, num_filters])
        biases = tf.get_variable('biases', shape=[num_filters])

        if groups == 1:
            conv = convolve(x, weights)

        # In the cases of multiple groups, split inputs & weights and
        else:
            # Split input and weights and convolve them separately
            input_groups = tf.split(axis=3, num_or_size_splits=groups, value=x)
            weight_groups = tf.split(axis=3, num_or_size_splits=groups, value=weights)
            output_groups = [convolve(i, k) for i, k in zip(input_groups, weight_groups)]

            # Concat the convolved output together again
            conv = tf.concat(axis=3, values=output_groups)

        # Add biases
        bias = tf.reshape(tf.nn.bias_add(conv, biases), tf.shape(conv))

        # Apply non_linear function
        if non_linear == "RELU":
            non_lin = tf.nn.relu(bias, name=scope.name)
        elif non_linear == "NONE":
            non_lin = tf.identity(bias, name=scope.name)

        return non_lin


def fc(x, num_in, num_out, name, relu=True):
    with tf.variable_scope(name) as scope:

        # Create tf variables for the weights and biases
        weights = tf.get_variable('weights', shape=[num_in, num_out], trainable=True)
        biases = tf.get_variable('biases', [num_out], trainable=True)

        # Matrix multiply weights and inputs and add bias
        act = tf.nn.xw_plus_b(x, weights, biases, name=scope.name)

        if relu == True:
            # Apply ReLu non linearity
            relu = tf.nn.relu(act)
            return relu
        else:
            return act


def max_pool(x, filter_height, filter_width, stride_y, stride_x, name, padding='SAME'):
    return tf.nn.max_pool(x, ksize=[1, filter_height, filter_width, 1],
                          strides=[1, stride_y, stride_x, 1],
                          padding=padding, name=name)


def lrn(x, radius, alpha, beta, name, bias=1.0):
    return tf.nn.local_response_normalization(x, depth_radius=radius, alpha=alpha,
                                              beta=beta, bias=bias, name=name)


def dropout(x, keep_prob):
    return tf.nn.dropout(x, keep_prob)


# train the cnn
if __name__ == "__main__":
    from dataset import Dataset

    with open("../data/train.txt", "r") as f:
        tlines = [l.strip() for l in f.readlines()]
    with open("../data/val.txt", "r") as f:
        vlines = [l.strip() for l in f.readlines()]
    train_ds = Dataset(tlines)
    val_ds = Dataset(vlines)
    cnn = CNN([None, 6, 10, 1], [None, 2], "../cnn_data/ckpt/abs_loss", "../cnn_data/tsbd/abs_loss", 0.00001)
    cnn.initialize()
    cnn.train(train_ds, val_ds, 0, 20000)
