#!/usr/bin/env python
import _init_paths
import caffe
import argparse
import pprint
import numpy as np
import sys
import os
from train import train_net


def parse_args():
    parser = argparse.ArgumentParser(description='Train a vgg face network')
    parser.add_argument('--gpu', dest='gpu_id',
                        help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--solver', dest='solver',
                        help='solver prototxt',
                        default=None, type=str)
    parser.add_argument('--iters', dest='max_iters',
                        help='number of iterations to train',
                        default=40000, type=int)
    parser.add_argument('--snap', dest='snapshot_iters',
                        help='number of iterations to save',
                        default=10000, type=int)
    parser.add_argument('--weights', dest='pretrained_model',
                        help='initialize with pretrained model weights',
                        default=None, type=str)
    parser.add_argument('--rand', dest='randomize',
                        help='randomize (do not use a fixed seed)',
                        action='store_true')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    print('Called with args:')
    print(args)

    # set up caffe
    caffe.set_mode_cpu()

    output_dir = os.path.join(".", "outputs")

    train_net(args.solver, args.snapshot_iters, output_dir,
              pretrained_model=args.pretrained_model,
              max_iters=args.max_iters)

