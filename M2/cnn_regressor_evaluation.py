""" Evaluation on the convolutional neural network.
This version uses data converted to a TFRecords file containing tf.train.Example 
protocol buffers.
See tensorflow/g3doc/how_tos/reading_data.md#reading-from-files for context.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import time
import datetime
import math

import numpy as np
import tensorflow as tf

import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt


# Basic model parameters as external flags.
flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_float('learning_rate', 0.01, 'Initial learning rate.')
flags.DEFINE_integer('num_epochs', 1, 'Number of epochs to run trainer.')
flags.DEFINE_integer('num_epochs_eval', 1, 'Number of epochs to run evaluation.')
flags.DEFINE_integer('batch_size', 100, 'Batch size.')
flags.DEFINE_integer('image_pixels', 4800, 'Number of pixels in image')

flags.DEFINE_integer('hidden1', 32, 'Number of units in hidden layer 1.')
flags.DEFINE_integer('hidden2', 2, 'Number of units in hidden layer 2.')
flags.DEFINE_integer('num_classes', 1, 'Number of classes')

flags.DEFINE_string('train_dir', 'output', 'Directory with the training data.')
flags.DEFINE_string('training_data_file', 'train-00000-of-00001', 'Training data file')
flags.DEFINE_string('evaluation_data_file', 'validation-00000-of-00001', 'Training data file')


def read_and_decode(filename_queue):
  reader = tf.TFRecordReader()
  _, serialized_example = reader.read(filename_queue)
  features = tf.parse_single_example(
  	serialized_example,
  	features={
      'image/height':tf.FixedLenFeature([], tf.int64),
      'image/width': tf.FixedLenFeature([], tf.int64),
      'image/colorspace': tf.FixedLenFeature([], tf.string),
      'image/channels': tf.FixedLenFeature([], tf.int64),
      'image/class/label': tf.FixedLenFeature([], tf.int64),
      'image/class/text': tf.FixedLenFeature([], tf.string),
      'image/format': tf.FixedLenFeature([], tf.string),
      'image/filename': tf.FixedLenFeature([],tf.string),
      'image/encoded': tf.FixedLenFeature([], tf.string),
      'image/avg_intensity': tf.FixedLenFeature([], tf.float32),
      'image/intensity_label': tf.FixedLenFeature([], tf.float32)
  })

  # Convert from a scalar string tensor to a uint8 tensor with shape
  # [FLAGS.image_pixels].
  image = tf.decode_raw(features['image/encoded'], tf.uint8)
  image.set_shape([FLAGS.image_pixels])

  # Convert from [0, 255] -> [-0.5, 0.5] floats.
  image = tf.cast(image, tf.float32) * (1. / 255) - 0.5
  
  # Convert ground truth
  ground_truth = tf.cast(features['image/avg_intensity'], tf.float32) * (1. / 255) - 0.5
  
  # Introduce noise
  label = tf.cast(features['image/intensity_label'], tf.float32) * (1. / 255) - 0.5

  return image, label, ground_truth

  """Reads input data num_epochs times.
  Args:
    train: Selects between the training (True) and validation (False) data.
    batch_size: Number of examples per returned batch.
    num_epochs: Number of times to read the input data, or 0/None to
       train forever.
  Returns:
    A tuple (images, labels), where:
    * images is a float tensor with shape [batch_size, FLAGS.image_height, FLAGS.image_width, FLAGS.num_channels]
      in the range [-0.5, 0.5].
    * labels is an int32 tensor with shape [batch_size] with the true label,
      a number in the range [0, FLAGS.num_classes).
    Note that an tf.train.QueueRunner is added to the graph, which
    must be run using e.g. tf.train.start_queue_runners().
  """
def inputs(train, batch_size, num_epochs):

  if not num_epochs: num_epochs = None
  filename = os.path.join(FLAGS.train_dir,
                          FLAGS.training_data_file if train else FLAGS.evaluation_data_file)

  with tf.name_scope('input'):
    filename_queue = tf.train.string_input_producer(
        [filename], num_epochs=num_epochs)

    # Even when reading in multiple threads, share the filename queue
    image, label, ground_truth = read_and_decode(filename_queue)

    # Shuffle the examples and collect them into FLAGS.batch_size batches.
    # (Internally uses a RandomShuffleQueue.)We run this in two threads to avoid being a bottleneck.
    images, sparse_labels, ground_truths = tf.train.shuffle_batch(
        [image, label, ground_truth], batch_size=batch_size, num_threads=2,
        capacity=1000 + 3 * batch_size,
        # Ensures a minimum amount of shuffling of examples.
        min_after_dequeue=1000)
    
    return images, sparse_labels, ground_truths

def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')



def inference_graph(images, train):

	### Dimension info: images shape: unknown at this point since images is a placeholder
	### Dimension info: images shape: expected to be [100, 4800] for a batch size of 100 and image size 60*80*1
	print("images dim:")
	print(images.get_shape())
	
	### Dimension info: images_reshaped shape: expected to be [100, 60, 80, 1]
	images_reshaped = tf.reshape(images, [-1,60,80,1])
	#images_resized = tf.image.resize_images(images_reshaped, [60,80])
	print("images_reshaped size:")
	print(images_reshaped.get_shape())
	
	#To compute 32 features for each 5*5 patch - dimensions: [patch size, patch size, input channels, output channels]
	W_conv1 = weight_variable([5, 5, 1, 4])
	b_conv1 = bias_variable([4])
	
	### Dimension info: h_conv1 shape: expected to be [100, 60, 80, 4]
	h_conv1 = tf.nn.relu(conv2d(images_reshaped, W_conv1) + b_conv1)
	print("conv1 shape:")
	print(h_conv1.get_shape())
	
	#To compute 64 features for each 5*5 patch - dimensions: [patch size, patch size, input channels, output channels]
	W_conv2 = weight_variable([5, 5, 4, 4])
	b_conv2 = bias_variable([4])
	
	### Dimension info: h_conv2 shape: expected to be [100, 60, 80, 4]
	h_conv2 = tf.nn.relu(conv2d(h_conv1, W_conv2) + b_conv2)
	print("conv2 shape:")
	print(h_conv2.get_shape())
	
	W_fc1 = weight_variable([60 * 80 * 4, FLAGS.hidden1])
	print(W_fc1.get_shape())
	b_fc1 = bias_variable([FLAGS.hidden1])
	
	### Dimension info: h_pool2_flat shape: expected to be [100, 19200]
	h_conv2_flat = tf.reshape(h_conv2, [-1, 60 * 80 * 4])
	print("conv2_flat shape:")
	print(h_conv2_flat.get_shape())
	
	### Dimension info: h_fc1 shape: expected to be [100, 128]
	h_fc1 = tf.nn.relu(tf.matmul(h_conv2_flat, W_fc1) + b_fc1)
	print("fully connected shape:")
	print(h_fc1.get_shape())
		
	W_fc2 = weight_variable([FLAGS.hidden1, FLAGS.num_classes])
	b_fc2 = bias_variable([FLAGS.num_classes])
	
	### Dimension info: logits shape: expected to be [100, 1]
	logits = tf.matmul(h_fc1, W_fc2) + b_fc2
	print("logits shape:")
	print(logits.get_shape())
	
	logits = tf.cast(logits, tf.float32)
	
	return logits
	

"""Build the training graph.
   Args:
       logits: Logits tensor, float - [BATCH_SIZE, NUM_CLASSES].
       labels: Labels tensor, int32 - [BATCH_SIZE], with values in the
         range [0, NUM_CLASSES).
       learning_rate: The learning rate to use for gradient descent.
   Returns:
       train_op: The Op for training.
       loss: The Op for calculating loss.
"""
    
def training_graph(logits, labels, learning_rate):

    print("logits shape")
    print(logits.get_shape())
    
    # Reshape logits into a 1D array
    flattened_logits = tf.reshape(logits, [-1])
    
    print("flattened logits shape")
    print(flattened_logits.get_shape())
    
    # Define the cost function
    loss = tf.reduce_sum(tf.square(flattened_logits-labels)) / FLAGS.batch_size
    
    # Create the gradient descent optimizer with the given learning rate.
    optimizer = tf.train.GradientDescentOptimizer(learning_rate)
    
    # Create a variable to track the global step (iteration).
    global_step = tf.Variable(0, name='global_step', trainable=False)
    
    # Use the optimizer to apply the gradients that minimize the loss
    # (and also increment the global step counter) as a single training step.
    train_op = optimizer.minimize(loss, global_step=global_step)
    
    return train_op, loss

"""    #labels = tf.reshape(labels, [-1])
    # Create an operation that calculates loss.
    print("logits shape in graph:")
    print(logits.get_shape())
    print("labels shape is graph:")
    print(labels.get_shape())
    
    
    loss = tf.reduce_mean(tf.square(logits-labels))
    #loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=labels))
    print("loss shape")
    print(loss.get_shape())
    
    # Create the gradient descent optimizer with the given learning rate.
    optimizer = tf.train.GradientDescentOptimizer(learning_rate)
    
    # Create a variable to track the global step (iteration).
    global_step = tf.Variable(0, name='global_step', trainable=False)
    
    # Use the optimizer to apply the gradients that minimize the loss
    # (and also increment the global step counter) as a single training step.
    train_op = optimizer.minimize(loss, global_step=global_step)
    """
    
    
def run_evaluation():
	# Tell TensorFlow that the model will be built into the default Graph.
	treedom_graph=tf.Graph()
	with treedom_graph.as_default():
	
		#Generate placeholders for images and labels
	    images_placeholder=tf.placeholder(tf.float32)
	    labels_placeholder=tf.placeholder(tf.float32)
	    #Remember these operands
	    tf.add_to_collection("images", images_placeholder)
	    tf.add_to_collection("labels", labels_placeholder)
	    
	    # Build a Graph that computes predictions from the inference model.
	    logits = inference_graph(images_placeholder, True)
	    tf.add_to_collection("logits", logits)
	    
	    #create images and labels
	    images_eval, labels_eval, gts_eval = inputs(train=False, batch_size=FLAGS.batch_size, num_epochs=FLAGS.num_epochs_eval)
	    
	    #create eval op
	    eval_op_values, eval_op_indices = tf.nn.top_k(logits)
	    	    
	    #ititalize global and local variables
	    init = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
	    
	    #Create a saver for writing training checkpoints
	    #saver=tf.train.Saver()
	    
	with tf.Session(graph=treedom_graph) as sess:		
		
		sess.run(init)
		
		checkpoint = 'output/cnn-e%d-p10000/check' % (FLAGS.num_epochs)
		
		saver=tf.train.Saver()
		saver.restore(sess, checkpoint)
		
		logits = tf.get_collection("logits")[0]
		print("logits:")
		print(logits)
		
		images_placeholder = tf.get_collection("images")[0]
		print("images")
		print(images_placeholder)
		
		labels_placeholder = tf.get_collection("labels")[0]
		print("labels")
		print(labels_placeholder)
		
		#variable for tracking losses - to be displayed in losses.png
		predictions = []
		labels = []
		ground_truths = []
		
		step = 0
		total_error = 0
		
		# Start input enqueue threads.
		coord = tf.train.Coordinator()
		threads = tf.train.start_queue_runners(sess=sess, coord=coord)
	
		try:
			while not coord.should_stop():
				start_time = time.time()
				
				print("Threading")

				image, label, ground_truth = sess.run([images_eval, labels_eval, gts_eval])

				prediction, _ = sess.run([eval_op_values, eval_op_indices], feed_dict={images_placeholder: image, labels_placeholder: label})
				
				prediction = prediction.flatten()
				
				labels.append(label)
				ground_truths.append(ground_truth)
				predictions.append(prediction)
				
				duration = time.time() - start_time
				
				abs = np.square(label - prediction)

				error = np.sum(abs)
				
				print("Error: %.6f Step: %d" % (error, step))
					
				step += 1
				total_error += error
				
		except tf.errors.OutOfRangeError:
			print('Done training for %d epochs, %d iterations.' % (FLAGS.num_epochs_eval, step))
			f.write('Done training for %d epochs, %d iterations.\n' % (FLAGS.num_epochs_eval, step))
		finally:
			coord.request_stop()
		
		total_error = total_error / (step * FLAGS.batch_size)
		
		print("Error rate during evaluation of %d steps: %.3f" % (step, total_error))
		f.write("Error rate during evaluation of %d steps: %.3f\n" % (step, total_error))

		# Wait for threads to finish.
		coord.join(threads)
		
		fig=plt.figure()
		a=fig.add_subplot(111)
		a.plot(ground_truths, ground_truths, 'ro', label="ground truth")
		a.plot(ground_truths, labels, 'bo', label="labels")
		a.plot(ground_truths, predictions, 'go', label="predictions")
		#plt.legend()
		fig.savefig('output/cnn-e%d-p10000/cnn_regresssion_evaluation.png' % (FLAGS.num_epochs))
		
		sess.close()
		
directory = 'output/cnn-e' + str(FLAGS.num_epochs) + '-p10000'
print(directory)
if not os.path.exists(directory):
	os.makedirs(directory)

f = open('output/cnn-e%d-p10000/log' % (FLAGS.num_epochs), 'a+')
f.write('\n\n----CNN REGRESSOR EVALUATION----\n\n')
f.write('Batch size: %d\n' % (FLAGS.batch_size))
f.write('Number of epochs: %d\n' % (FLAGS.num_epochs))
f.write('Image size: %d\n\n' % (FLAGS.image_pixels))
f.write('--Model information--\n')
f.write('Layer 1 hidden units: %d\n' % (FLAGS.hidden1))
f.write('Layer 2 hidden units: %d\n\n' % (FLAGS.hidden2))
f.write('--Results--\n')

run_evaluation()

start_time=datetime.datetime.now()
f.write('\nStarted training: ')
f.write(str(start_time))
f.write('\n')
end_time=datetime.datetime.now()
f.write('Finished training: ')
f.write(str(end_time))
f.write('\nTraining took: ')
f.write(str(end_time - start_time))
f.write('\n\nTraining ended successfully\n')
f.close()