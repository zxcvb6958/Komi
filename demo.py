#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tools._init_paths
from timer import Timer
import os.path as osp
import os
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
import json


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
    caffe.set_mode_gpu()
    caffe.set_device(1)
    net = caffe.Net(deployPrototxt, modelFile, caffe.TEST)

    return net

def read_imagelist(labelfile):
    file = open(labelfile)
    lines = file.readlines()
    test_num=len(lines)
    file.close()

    x = np.empty((test_num, 3, 224, 224))
    i = 0
    timer = Timer()
    timer.tic()
    db = []


    for line in lines:
        path = line.strip('\n').split(' ')
        #read left image
        filename = path[0]
        img = skimage.io.imread(filename, as_grey=False)
        image = skimage.transform.resize(img, (224,224))*255
        x[i, 0, :, :] = image[:, :, 0]
        x[i, 1, :, :] = image[:, :, 1]
        x[i, 2, :, :] = image[:, :, 2]
        # if image.ndim < 3:
        #     print 'gray:' + filename
        #     x[i, 0, :, :] = image[:, :]
        #     x[i, 1, :, :] = image[:, :]
        #     x[i, 2, :, :] = image[:, :]
        # else:
        #     x[i, 0, :, :] = image[:, :, 0]
        #     x[i, 1, :, :] = image[:, :, 1]
        #     x[i, 2, :, :] = image[:, :, 2]

        db.append({
            'filename' : filename,
            'label' : int(path[1]),
            'w' : img.shape[0],
            'h' : img.shape[1]
        })

        i = i + 1
        if i % 100 == 0 or i == 13233:
            timer.toc()
            print "{0}/13233 images, average time {1:.3f} s".format(i, timer.average_time)
            timer.tic()
    
    timer.toc()

    return x, db

def extractFeature(face_data, net):
    test_num=np.shape(face_data)[0]
    print 'extract feature'

    out = net.forward_all(data = face_data)                                                                  
    feature = np.float64(out['fc7'])
    feature = np.reshape(feature, (test_num, 4096))

    return feature


def evaluate_search(db, feature, dump_json=None):
    test_num = len(db)
    ret = {'image_root': '/home/wangcheng/Komi', 'results': []}
    # for i in range(test_num):
    #     now_data = feature[i]
    #     now_label = labels[i]

    #     for j in range(test_num):
    #         test_data = feature[j]
    #         test_label = labels[j]
    #         now_data = now_data.reshape((1, -1))
    #         test_data = test_data.reshape((1, -1))
    #         dis = pw.pairwise_distances(now_data, test_data, metric='cosine')

    mt = []
    print 'get pairwise distances'
    mt_temp = pw.pairwise_distances(feature, metric='cosine')
    mt = mt_temp.tolist()

    for i in range(test_num):
        mt[i][i] = 1
    
    count = 0
    vaild_count = 0
    last_label = 0
    rank1_acc = 0
    rank5_acc = 0
    timer = Timer()
    timer.tic()

    for i in range(test_num):
        if db[i]['label'] != last_label and i+1 < test_num and db[i]['label'] == db[i+1]['label']:
            vaild_count += 1
            last_label = db[i]['label']
            w = db[i]['w']
            h = db[i]['h']
            probe_gt = []

            for j in range(test_num):
                test_w = db[j]['w']
                test_h = db[j]['h']

                if db[j]['label'] > db[i]['label']:
                    break

                if db[j]['label'] == db[i]['label'] and j != i:
                    probe_gt.append({
                        'img': db[j]['filename'],
                        'roi': [10, 10, test_w-10, test_h-10]
                    })

            new_entry = {'probe_img': db[i]['filename'],
                        'probe_roi': [10, 10, w-10, h-10],
                        'probe_gt': probe_gt,
                        'gallery': []}
            
            rank5_label = False

            for j in range(20):
                min_index = mt[i].index(min(mt[i]))
                mt[i][min_index] = 1

                if j == 0 and db[min_index]['label'] == db[i]['label']:
                    rank1_acc += 1

                if j < 5 and not rank5_label and db[min_index]['label'] == db[i]['label']:
                    rank5_acc += 1
                    rank5_label = True

                rank_target = db[min_index]

                new_entry['gallery'].append({
                    "roi" : [10, 10, rank_target['w']-10, rank_target['h']-10],
                    "score" : 1,
                    "correct" : 1 if rank_target['label'] == db[i]['label'] else 0,
                    "img" : rank_target['filename']
                })

            ret['results'].append(new_entry)

        count += 1
        if count % 100 == 0 or count == 13233:
            timer.toc()
            print "{0}/13233 images, average time {1:.3f} s".format(count, timer.average_time)
            timer.tic()


    timer.toc()

    rank1 = (rank1_acc - 0.0) / vaild_count
    print 'rank-1 acc: {0}'.format(rank1)

    rank5 = (rank5_acc - 0.0) / vaild_count
    print 'rank-5 acc: {0}'.format(rank5)

    if dump_json is not None:
            if not osp.isdir(osp.dirname(dump_json)):
                os.makedirs(osp.dirname(dump_json))
            with open(dump_json, 'w') as f:
                json.dump(ret, f)


if __name__ == '__main__':
    face_data, db = read_imagelist('data/test/images.txt')

    net = initilize()
    feature = extractFeature(face_data, net)
    del face_data
    del net

    evaluate_search(db, feature, osp.join('vis', 'results.json'))
