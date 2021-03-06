import math
import os
import time
from math import ceil

import cv2
import sys
import matplotlib

from scipy import signal
from scipy import ndimage

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.python.framework import ops
from tensorflow.python.ops import gen_nn_ops
from tensorflow.python.framework.graph_util import convert_variables_to_constants
from PIL import Image

from conv2d import Conv2d
from max_pool_2d import MaxPool2d
import ssim
import msssim
import datetime
import io
import utils
import gc
import freeze_graph as fg
import tensorflow.contrib.slim as slim
from recog_model import inception_resnet_v1 as model
import load_recog as recog

np.set_printoptions(threshold=np.nan)

class Network:
    IMAGE_HEIGHT = 128
    IMAGE_WIDTH = 128
    IMAGE_CHANNELS = 1

    def __init__(self, layers=None, skip_connections=False):
        with tf.variable_scope('encoder-decoder'):
            if layers == None:
                    layers = []
                    layers.append(Conv2d(kernel_size=7, strides=[1, 2, 2, 1], output_channels=64, name='conv_1_1'))
                    layers.append(Conv2d(kernel_size=7, strides=[1, 1, 1, 1], output_channels=64, name='conv_1_2'))
                    layers.append(MaxPool2d(kernel_size=2, name='max_1', skip_connection=skip_connections))

                    layers.append(Conv2d(kernel_size=7, strides=[1, 2, 2, 1], output_channels=64, name='conv_2_1'))
                    layers.append(Conv2d(kernel_size=7, strides=[1, 1, 1, 1], output_channels=64, name='conv_2_2'))
                    layers.append(MaxPool2d(kernel_size=2, name='max_2', skip_connection=skip_connections))

                    layers.append(Conv2d(kernel_size=7, strides=[1, 2, 2, 1], output_channels=64, name='conv_3_1'))
                    layers.append(Conv2d(kernel_size=7, strides=[1, 1, 1, 1], output_channels=64, name='conv_3_2'))            
                    layers.append(Conv2d(kernel_size=7, strides=[1, 1, 1, 1], output_channels=64, name='conv_3_3'))

            self.inputs = tf.placeholder(tf.float32, [None, self.IMAGE_HEIGHT, self.IMAGE_WIDTH, self.IMAGE_CHANNELS], name='inputs')
            self.targets = tf.placeholder(tf.float32, [None, self.IMAGE_HEIGHT, self.IMAGE_WIDTH, 1], name='targets')
            self.is_training = tf.placeholder_with_default(False, [], name='is_training')
            self.description = ""

            self.layers = {}

            net = self.inputs

            # ENCODER
            for layer in layers:
                    self.layers[layer.name] = net = layer.create_layer(net)
                    self.description += "{}".format(layer.get_description())

            layers.reverse()
            Conv2d.reverse_global_variables()    

            #midfield
            '''old_shape = net.get_shape()
            o_s = old_shape.as_list()
            feature_len = o_s[1]*o_s[2]*o_s[3]
            net = tf.reshape(net, [-1, feature_len])
            for i in range(3):
                    net = slim.fully_connected(net, feature_len, scope="fc_{}".format(i+1))
                    self.fc_vars = tf.contrib.framework.get_variables("fc_{}".format(i+1))
            net = tf.reshape(net, [-1, o_s[1], o_s[2], o_s[3]])'''

            # DECODER
            layers_len = len(layers)
            for i, layer in enumerate(layers):
                    if i == (layers_len-1):
                            self.segmentation_result = layer.create_layer_reversed(net, prev_layer=self.layers[layer.name], last_layer=True)
                    else:
                            net = layer.create_layer_reversed(net, prev_layer=self.layers[layer.name])
    
        self.variables = tf.contrib.framework.get_variables(scope='encoder-decoder')
       
        self.final_result = self.segmentation_result

        self.rec1 = Recognizer(self.final_result, reuse=tf.AUTO_REUSE)
        self.rec2 = Recognizer(self.inputs, reuse=tf.AUTO_REUSE)
        self.rec3 = Recognizer(self.targets, reuse=tf.AUTO_REUSE)

        # MSE loss
        # Expression Removal with MSE loss function
        output = self.segmentation_result
        inputv = self.targets
        mean = tf.reduce_mean(tf.square(output - inputv))
        # Recognition feature sets
        rec1_loss = self.rec1.modelo
        rec2_loss = self.rec2.modelo
        rec3_loss = self.rec3.modelo
        output_weight = tf.constant(3, shape=[], dtype=tf.float32)
        cost_rec1 = tf.multiply(output_weight, tf.reduce_sum(tf.reduce_mean(tf.abs(rec1_loss - rec3_loss), 0)))
        cost_rec2 = tf.reduce_sum(tf.reduce_mean(tf.abs(rec1_loss - rec2_loss), 0))
        # Cost based on recognition
        final_weight = tf.constant(10, shape=[], dtype=tf.float32)
        self.cost_rec = tf.multiply(final_weight, mean) + cost_rec1 + cost_rec2
        #self.cost_rec = tf.constant(0, dtype=tf.float32)
        self.cost_mse = mean
        self.train_op_rec = tf.train.AdamOptimizer(learning_rate=tf.train.polynomial_decay(0.00001, 1, 10000, 0.0000001)).minimize(self.cost_rec)
        self.train_op_mse = tf.train.AdamOptimizer(learning_rate=tf.train.polynomial_decay(0.0001, 1, 10000, 0.00001)).minimize(self.cost_mse)
        with tf.name_scope('accuracy'):
            correct_pred = tf.py_func(msssim.MultiScaleSSIM, [self.final_result, self.targets], tf.float32)
            self.accuracy = correct_pred
            self.mse = tf.reduce_mean(tf.square(self.final_result - self.targets))

            tf.summary.scalar('accuracy', self.accuracy)

        self.summaries = tf.summary.merge_all()

    def loadRecog(self, sess):
        self.rec1.load(sess)
        self.rec2.load(sess)
        self.rec3.load(sess)

class Recognizer:
    '''
    Classe do Reconhecedor
    Input: Duas imagens de face
    Output: Métrica de similaridade entre elas
    Arquitetura: InceptionNet do FaceNet
    '''
    def __init__(self, inputs, reuse=None):		
        self.modelo, *_ = model(inputs, False, reuse=reuse)

    def load(self, sess):
        recog.load_model(sess, "recog")

    def computeRecog(self):
        return self.modelo

class Dataset:
    def __init__(self, batch_size, folder='data128x128', include_hair=False):
        self.batch_size = batch_size
        self.include_hair = include_hair
        
        train_files = os.listdir(os.path.join(folder, 'inputs/train'))
        validation_files = os.listdir(os.path.join(folder, 'inputs/valid'))
        test_files = os.listdir(os.path.join(folder, 'inputs/test'))

        self.train_inputs, self.train_paths, self.train_targets = self.file_paths_to_images(folder, train_files)
        self.test_inputs, self.test_paths, self.test_targets = self.file_paths_to_images(folder, test_files, mode="test")
        self.valid_inputs, self.valid_paths, self.valid_targets = self.file_paths_to_images(folder, validation_files, mode="valid")

        self.pointer = 0
        self.permutation = np.random.permutation(len(self.train_inputs))
        
    def progress(self, count, total, status=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
        sys.stdout.flush()

    def file_paths_to_images(self, folder, files_list, mode="train"):
        inputs = []
        targets = []
        in_path = []
        test_path = []

        for count,file in enumerate(files_list):
            #self.progress(count, len(files_list), status="Carregando imagens de {}".format(mode))
            input_image = os.path.join(folder, 'inputs/{}'.format(mode), file)
            output_image = os.path.join(folder, 'targets/{}'.format(mode), file)
            in_path.append(os.path.join('inputs/{}'.format(mode), file))

            test_image = cv2.imread(input_image, 0)
            test_image = cv2.resize(test_image, (128, 128))
            inputs.append(test_image)

            target_image = cv2.imread(output_image, 0)
            target_image = cv2.resize(target_image, (128, 128))
            targets.append(target_image)

        return inputs, in_path, targets

    def train_valid_test_split(self, X, ratio=None):
        if ratio is None:
            ratio = (0.7, .15, .15)

        N = len(X)
        return (
            X[:int(ceil(N * ratio[0]))],
            X[int(ceil(N * ratio[0])): int(ceil(N * ratio[0] + N * ratio[1]))],
            X[int(ceil(N * ratio[0] + N * ratio[1])):]
        )

    def num_batches_in_epoch(self):
        return int(math.floor(len(self.train_inputs) / self.batch_size))

    def reset_batch_pointer(self):
        self.permutation = np.random.permutation(len(self.train_inputs))
        self.pointer = 0

    def next_batch(self,pretrain=False):
        inputs = []
        targets = []
        
        for i in range(self.batch_size):
            if pretrain:
                inputs.append(np.array(self.train_targets[self.permutation[self.pointer + i]]))
                targets.append(np.array(self.train_targets[self.permutation[self.pointer + i]]))
            else:
                inputs.append(np.array(self.train_inputs[self.permutation[self.pointer + i]]))
                targets.append(np.array(self.train_targets[self.permutation[self.pointer + i]]))

        self.pointer += self.batch_size

        return np.array(inputs, dtype=np.uint8), np.array(targets, dtype=np.uint8)
        
    def all_test_batches(self, mode = "input"):
        if(mode == "input"):
        	return np.array(self.test_inputs, dtype=np.uint8), self.test_paths, len(self.test_inputs)//self.batch_size
        else:
        	return np.array(self.test_targets, dtype=np.uint8), self.test_paths, len(self.test_inputs)//self.batch_size

    @property
    def valid_set(self):
        return np.array(self.valid_inputs, dtype=np.uint8), np.array(self.valid_targets, dtype=np.uint8)


def draw_results(test_inputs, test_targets, test_segmentation, test_final, test_accuracy, network, batch_num):
    n_examples_to_plot = 12
    fig, axs = plt.subplots(4, n_examples_to_plot, figsize=(n_examples_to_plot * 3, 10))
    fig.suptitle("Accuracy: {}, {}".format(test_accuracy, network.description), fontsize=20)
    for example_i in range(n_examples_to_plot):
        axs[0][example_i].imshow(test_inputs[example_i], cmap='gray')
        axs[1][example_i].imshow(test_targets[example_i].astype(np.float32), cmap='gray')
        axs[2][example_i].imshow(np.reshape(test_segmentation[example_i], [network.IMAGE_HEIGHT, network.IMAGE_WIDTH]),cmap='gray')
        final = np.reshape(test_final[example_i], [network.IMAGE_HEIGHT, network.IMAGE_WIDTH])
        axs[3][example_i].imshow(final,cmap='gray')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    IMAGE_PLOT_DIR = 'image_plots/'
    if not os.path.exists(IMAGE_PLOT_DIR):
        os.makedirs(IMAGE_PLOT_DIR)

    plt.savefig('{}/figure{}.jpg'.format(IMAGE_PLOT_DIR, batch_num))
    plt.close('all')
    return buf


def train():
    BATCH_SIZE = 256

    network = Network()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # create directory for saving models
    # os.makedirs(os.path.join('save', network.description, timestamp))

    dataset = Dataset(folder='data{}_{}'.format(network.IMAGE_HEIGHT, network.IMAGE_WIDTH), include_hair=False, batch_size=BATCH_SIZE)

    inputs, targets = dataset.next_batch()

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        network.loadRecog(sess)

        summary_writer = tf.summary.FileWriter('{}/{}-{}'.format('logs', network.description, timestamp), graph=tf.get_default_graph())
        saver = tf.train.Saver(var_list=network.variables, max_to_keep=10)

        #Pre treino
        n_epochs = 50
        print("Iniciando Pretreino")
        for epoch_i in range(n_epochs):
            dataset.reset_batch_pointer()

            for batch_i in range(dataset.num_batches_in_epoch()):
                batch_num = epoch_i * dataset.num_batches_in_epoch() + batch_i + 1

                start = time.time()
                batch_inputs, batch_targets = dataset.next_batch(pretrain=True)
                batch_inputs = np.reshape(batch_inputs,(dataset.batch_size, network.IMAGE_HEIGHT, network.IMAGE_WIDTH, 1))
                batch_targets = np.reshape(batch_targets,(dataset.batch_size, network.IMAGE_HEIGHT, network.IMAGE_WIDTH, 1))

                batch_inputs = np.multiply(batch_inputs, 1.0 / 255)
                batch_targets = np.multiply(batch_targets, 1.0 / 255)

                cost1, rec,_ = sess.run([network.cost_mse, network.cost_rec, network.train_op_mse],feed_dict={network.inputs: batch_inputs, network.targets: batch_targets, network.is_training: True})
                end = time.time()
                print('{}/{}, epoch: {}, mse/rec: {}/{}, batch time: {}'.format(batch_num, n_epochs * dataset.num_batches_in_epoch(), epoch_i, cost1, rec, round(end - start,5)))        

        test_accuracies = []
        test_mse = []
        n_epochs = 3000
        global_start = time.time()
        print("Iniciando treino real")
        for epoch_i in range(n_epochs):
            dataset.reset_batch_pointer()

            for batch_i in range(dataset.num_batches_in_epoch()):
                batch_num = epoch_i * dataset.num_batches_in_epoch() + batch_i + 1

                start = time.time()
                batch_inputs, batch_targets = dataset.next_batch()
                batch_inputs = np.reshape(batch_inputs,(dataset.batch_size, network.IMAGE_HEIGHT, network.IMAGE_WIDTH, 1))
                batch_targets = np.reshape(batch_targets,(dataset.batch_size, network.IMAGE_HEIGHT, network.IMAGE_WIDTH, 1))

                batch_inputs = np.multiply(batch_inputs, 1.0 / 255)
                batch_targets = np.multiply(batch_targets, 1.0 / 255)

                if batch_num % 5 == 0:
                	cost1, rec, _ = sess.run([network.cost_mse, network.cost_rec, network.train_op_rec],feed_dict={network.inputs: batch_inputs, network.targets: batch_targets, network.is_training: True})
                else:
                	cost1, rec, _ = sess.run([network.cost_mse, network.cost_rec, network.train_op_mse],feed_dict={network.inputs: batch_inputs, network.targets: batch_targets, network.is_training: True})

                end = time.time()
                print('{}/{}, epoch: {}, mse/recog: {}/{}, batch time: {}'.format(batch_num, n_epochs * dataset.num_batches_in_epoch(), epoch_i, cost1, rec, round(end - start,5)))

                if batch_num % 2000 == 0 or batch_num == n_epochs * dataset.num_batches_in_epoch():
                    test_inputs, test_targets = dataset.valid_set
                    test_inputs, test_targets = test_inputs[:100], test_targets[:100]

                    test_inputs = np.reshape(test_inputs, (-1, network.IMAGE_HEIGHT, network.IMAGE_WIDTH, 1))
                    test_targets = np.reshape(test_targets, (-1, network.IMAGE_HEIGHT, network.IMAGE_WIDTH, 1))
                    test_inputs = np.multiply(test_inputs, 1.0 / 255)
                    test_targets = np.multiply(test_targets, 1.0 / 255)

                    test_accuracy, mse = sess.run([network.accuracy, network.mse],
                                                      feed_dict={network.inputs: test_inputs,network.targets: test_targets,network.is_training: False})

                    #summary_writer.add_summary(summary, batch_num)

                    print('Step {}, test accuracy: {}'.format(batch_num, test_accuracy))
                    min_mse = (0,0)
                    test_accuracies.append((test_accuracy, batch_num))
                    test_mse.append((mse, batch_num))
                    print("Accuracies in time: ", [test_accuracies[x][0] for x in range(len(test_accuracies))])
                    print("MSE in time: ", [test_mse[x][0] for x in range(len(test_mse))])
                    max_acc = max(test_accuracies)
                    min_mse = min(test_mse)
                    print("Best accuracy: {} in batch {}".format(max_acc[0], max_acc[1]))
                    print("Total time: {}".format(time.time() - global_start))

                    # Plot example reconstructions
                    n_examples = 12
                    permutation = np.random.permutation(n_examples)
                    inputs = []
                    targets = []
                    for i in range(n_examples):
                        inputs.append(np.array(dataset.valid_inputs[permutation[i]]))
                        targets.append(np.array(dataset.valid_targets[permutation[i]]))

                    test_inputs, test_targets = np.array(inputs, dtype=np.uint8), np.array(targets, dtype=np.uint8)
                    test_inputs = np.multiply(test_inputs, 1.0 / 255)

                    test_segmentation, test_final = sess.run([network.segmentation_result, network.final_result], feed_dict={
                        network.inputs: np.reshape(test_inputs,[n_examples, network.IMAGE_HEIGHT, network.IMAGE_WIDTH, 1]), network.is_training: False})

                    # Prepare the plot
                    test_plot_buf = draw_results(test_inputs, test_targets, test_segmentation, test_final, test_accuracy, network,
                                                 batch_num)

                    # Convert PNG buffer to TF image
                    image = tf.image.decode_png(test_plot_buf.getvalue(), channels=4)

                    # Add the batch dimension
                    image = tf.expand_dims(image, 0)

                    # Add image summary
                    image_summary_op = tf.summary.image("plot", image)

                    image_summary = sess.run(image_summary_op)
                    summary_writer.add_summary(image_summary)

                    if (batch_num > 50000):
                        print("saving model...")
                        # minimal_graph = convert_variables_to_constants(sess, sess.graph_def, ["output"])

                        # tf.train.write_graph(minimal_graph, '.', "save/minimal_graph.txt", as_text=True)
                        saver.save(sess,"save/checkpoint.data")

                        variables = sess.run(network.variables)

                        with open("variables.txt", "w") as f:
                            for v in variables:
                                print("Variable: ", v, file=f)
                        print("All variables saved")


                        '''checkpoint_state_name = "checkpoint_state"
                        input_graph_name = "input_graph.pb"
                        output_graph_name = "output_graph.pb"

                        input_graph_path = "save/minimal_graph.txt"
                        input_saver_def_path = ""
                        input_binary = False
                        input_checkpoint_path = 'save/checkpoint.data' + "-0"

                        # Note that we this normally should be only "output_node"!!!
                        output_node_names = "output" 
                        restore_op_name = "save/restore_all"
                        filename_tensor_name = "save/Const:0"
                        output_graph_path = os.path.join("save", output_graph_name)
                        clear_devices = False

                        fg.freeze_graph(input_graph_path, input_saver_def_path,input_binary, input_checkpoint_path,
				output_node_names, restore_op_name,filename_tensor_name, output_graph_path,clear_devices, False)'''

if __name__ == '__main__':
    train()
