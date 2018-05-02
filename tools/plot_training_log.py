#!/usr/bin/env python

import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def print_help():
    print "python plot_training_log.py path/to/log"

def isfloat(x):
    return x.isdigit or x == '.'

def parse_log(filepath):
    print "locate in %s"%filepath
    log = open(filepath)

    x = []
    y = []
    lines = log.readlines()

    for line in lines:
        words = line.split(' ')
        if "Iteration" in words and "loss" in words:
            x.append(int(filter(str.isdigit, words[words.index("Iteration") + 1])))
            y.append(float(filter(isfloat, words[words.index("loss") + 2])))
        

    return x, y

def plot_log(x, y, output_dir):
    plt.plot(x, y)
    plt.title('loss curve')
    plt.xlabel('Iteration')
    plt.ylabel('loss')

    # plt.show()
    save_path = os.path.join(output_dir, "loss_curve.jpg")
    plt.savefig(save_path)
    print "save as %s"%save_path

def plot_other_loss(x, id_loss, output_dir):
    stack = []
    for i, loss in enumerate(id_loss):
        if len(stack) == 100:
            stack.pop(0)
        
        stack.append(loss)
        id_loss[i] = sum(stack) / len(stack)


    plt.plot(x, id_loss)
    plt.title('id loss curve')
    plt.xlabel('Iteration')
    plt.ylabel('id_loss')

    save_path = os.path.join(output_dir, "other_loss.jpg")
    plt.savefig(save_path)
    print "save as %s"%save_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_help()
    else:    
        path_to_logs = sys.argv[1]
        output_dir = sys.argv[2]
        x, y = parse_log(path_to_logs)
        plot_log(x, y, output_dir)
