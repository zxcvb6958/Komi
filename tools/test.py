#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _init_paths
from timer import Timer
import os.path as osp
import math
import sklearn
import numpy as np
import matplotlib.pyplot as plt
import skimage
caffe_root = './caffe/'
import sys
sys.path.insert(0, caffe_root + 'python')
import caffe
import sklearn.metrics.pairwise as pw
import cPickle


def pickle(data, file_path):
    with open(file_path, 'wb') as f:
        cPickle.dump(data, f)

def unpickle(file_path):
    with open(file_path, 'rb') as f:
        data = cPickle.load(f)
    return data

def initilize():
    print 'initilizing...'
    deployPrototxt = "models/VGG_FACE_deploy.prototxt"
    # modelFile = "data/pretrained_model/VGG_FACE.caffemodel"
    modelFile = "outputs/face_iter_50000.caffemodel"
    # caffe.set_mode_gpu()
    # caffe.set_device(3)
    caffe.set_mode_cpu()
    net = caffe.Net(deployPrototxt, modelFile, caffe.TEST)

    return net

def read_imagelist(labelfile):
    file = open(labelfile)
    lines = file.readlines()
    test_num=len(lines)
    file.close()

    x = np.empty((test_num, 3, 224, 224))
    y = np.empty((test_num, 3, 224, 224))
    labels = []
    i = 0
    timer = Timer()
    timer.tic()

    for line in lines:
        path = line.strip('\n').split('\t')
        #read left image
        filename = path[0]
        filename = osp.join('data', 'lfw', filename)
        img = skimage.io.imread(filename, as_grey=False)
        image = skimage.transform.resize(img, (224,224))*255
        if image.ndim < 3:
            print 'gray:' + filename
            x[i, 0, :, :] = image[:, :]
            x[i, 1, :, :] = image[:, :]
            x[i, 2, :, :] = image[:, :]
        else:
            x[i, 0, :, :] = image[:, :, 0]
            x[i, 1, :, :] = image[:, :, 1]
            x[i, 2, :, :] = image[:, :, 2]
        
        #read right image
        filename = path[1]
        filename = osp.join('data', 'lfw', filename)
        img = skimage.io.imread(filename, as_grey=False)
        image = skimage.transform.resize(img, (224,224))*255
        if image.ndim < 3:
            print 'gray:' + filename
            y[i, 0, :, :] = image[:, :]
            y[i, 1, :, :] = image[:, :]
            y[i, 2, :, :] = image[:, :]
        else:
            y[i, 0, :, :] = image[:, :, 0]
            y[i, 1, :, :] = image[:, :, 1]
            y[i, 2, :, :] = image[:, :, 2]
        #read label
        labels.append(int(path[2]))

        i = i + 1
        if i % 100 == 0:
            timer.toc()
            print "{0}/6000 images, average time {1:.3f} s".format(i, timer.average_time)
            timer.tic()
    
    timer.toc()

    return x, y, labels

def extractFeature(leftdata, rightdata):
    test_num=np.shape(leftdata)[0]

    out = net.forward_all(data = leftdata)                                                                  
    feature1 = np.float64(out['fc7'])
    featureleft=np.reshape(feature1, (test_num, 4096))

    out = net.forward_all(data = rightdata)                                                                                   
    feature2 = np.float64(out['fc7'])
    featureright=np.reshape(feature2, (test_num, 4096))

    return featureleft, featureright

def calculate_accuracy(distance, labels, num):    
    accuracy = {}
    predict = np.empty((num,))
    threshold = 0.1
    while threshold <= 0.9 :
        for i in range(num):
            if distance[i] >= threshold:
                 predict[i] = 0
            else:
                 predict[i] = 1
        predict_right = 0.0
        for i in range(num):
            if predict[i] == labels[i]:
               predict_right += 1.0
        current_accuracy = (predict_right / num)
        accuracy[str(threshold)] = current_accuracy
        threshold = threshold + 0.001
    temp = sorted(accuracy.items(), key = lambda d:d[1], reverse = True)
    highestAccuracy = temp[0][1]
    thres = temp[0][0]
    return highestAccuracy, thres


if __name__=='__main__':
    net = initilize()

    leftdata, rightdata, labels = read_imagelist('data/test/label.txt')
    featureleft, featureright = extractFeature(leftdata, rightdata)

    test_num = len(labels)
    mt = pw.pairwise_distances(featureleft, featureright, metric='cosine')
    distance = np.empty((test_num,))
    for i in range(test_num):
        distance[i] = mt[i][i]
    distance_norm = np.empty((test_num,))

    for i in range(test_num):
        distance_norm[i] = (distance[i]-np.min(distance))/(np.max(distance)-np.min(distance))

    highestAccuracy, threshold = calculate_accuracy(distance_norm,labels,len(labels))
    print ("the highest accuracy is : %.4f, and the corresponding threshold is %s \n"%(highestAccuracy, threshold))
