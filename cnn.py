
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

mnist = input_data.read_data_sets("/tmp/data",one_hot=True)

# Training parameters
learning_rate = 0.001
num_steps = 1000
batch_size = 128

# Network parameters
num_input = 784
num_classes = 10
dropout = 0.75

# tf graph input
X = tf.placeholder(tf.float32,[None,num_input])
Y = tf.placeholder(tf.float32,[None,num_classes])
keep_prob = tf.placeholder(tf.float32) # dropout

# Wrappers
def conv2d(x,W,b,strides=1):
    # Conv2D wrapper, with bias and relu activation
    x = tf.nn.conv2d(x,W,strides=[1,strides,strides,1],padding='SAME')
    x = tf.nn.bias_add(x,b)
    return tf.nn.relu(x)

def maxpool2d(x,k=2):
    # Maxpool2D wrapper
    return tf.nn.max_pool(x,ksize=[1,k,k,1],strides=[1,k,k,1],padding='SAME')

# CREATE MODEL
def conv_net(x,weights,biases, dropout):
    # MNIST data input is 1-D vectorof 784 features (28*28 pixels)
    # Reshape to match picture format [Height x Width x Channel]
    # Tensor input become 4-D: [Batch size, Height, Width, Channel]
    x = tf.reshape(x, shape=[-1,28,28,1])
    
    #Convolution layer 1
    conv1 = conv2d(x,weights['wc1'],biases['bc1'])
    # Max pooling
    conv1 = maxpool2d(conv1,k=2)
    
    # Convolution layer 2
    conv2 = conv2d(conv1,weights['wc2'],biases['bc2'])
    # Max pooling
    conv2 = maxpool2d(conv2,k=2)
    
    # Fully connected layer
    # Reshape conv2 output to fit fully connected layer input
    fc1 = tf.reshape(conv2,[-1,weights['wd1'].get_shape().as_list()[0]])
    fc1 = tf.add(tf.matmul(fc1,weights['wd1']),biases['bd1'])
    fc1 = tf.nn.relu(fc1)
    
    # Apply dropout 
    fc1 = tf.nn.dropout(fc1,dropout)
    
    # output, class prediction
    out = tf.add(tf.matmul(fc1,weights['out']),biases['out'])
    
    return out

# Store layers weights and biases
weights = {
    # 5x5 conv, 1 input,32 outputs (filters)
    'wc1': tf.Variable(tf.random_normal([5,5,1,32])),
    # 5x5 conv,32 inputs, 64 outputs
    'wc2': tf.Variable(tf.random_normal([5,5,32,64])),
    # fully connected, 7*7*64 inputs, 1024 outputs
    'wd1': tf.Variable(tf.random_normal([7*7*64,1024])),
    # 1024 inputs, 10 outputs 
    'out': tf.Variable(tf.random_normal([1024,num_classes]))
}

biases = {
    'bc1': tf.Variable(tf.random_normal([32])),
    'bc2': tf.Variable(tf.random_normal([64])),
    'bd1': tf.Variable(tf.random_normal([1024])),
    'out': tf.Variable(tf.random_normal([num_classes]))
}

logits = conv_net(X,weights,biases,keep_prob)
prediction = tf.nn.softmax(logits)

# Define loss and optimizer
loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=logits,labels=Y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
train_op = optimizer.minimize(loss_op)

# Model evaluation
correct_pred = tf.equal(tf.argmax(prediction,1),tf.argmax(Y,1))
accuracy = tf.reduce_mean(tf.cast(correct_pred,tf.float32))

# Initializing the variables
init = tf.global_variables_initializer()

# Training
with tf.Session() as sess:
    
    sess.run(init)
    
    for step in range(1,num_steps):
        batch_x,batch_y = mnist.train.next_batch(batch_size)
        
        # run optimization op
        sess.run(train_op, feed_dict={X:batch_x,Y:batch_y,keep_prob:dropout})
        if step % 100 == 0 or step == 1:
            # calculate batch loss and accuracy
            loss, acc = sess.run([loss_op,accuracy],feed_dict={X:batch_x,Y:batch_y,keep_prob:1.0})
            print("Step "+str(step)+", Minibatch Loss= " + "{:.4f}".format(loss)+", Training Accuracy+ "+"{:.3f}".format(acc))
            print("Testing Accuracy:",sess.run(accuracy,feed_dict={X:mnist.test.images[:256],Y:mnist.test.labels[:256],keep_prob:1.0}))
    
