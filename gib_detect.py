#!/usr/bin/python

import pickle
import gib_detect_train
import os
from gib_detect_train import DATA_DIR

model_filename = os.path.join(DATA_DIR,'model.data')

model_data = pickle.load(open(model_filename, 'rb'))
model_mat = model_data['mat']
threshold = model_data['thresh']
'''
while True:
    l = raw_input()
    model_mat = model_data['mat']
    threshold = model_data['thresh']
    print gib_detect_train.avg_transition_prob(l, model_mat) > threshold
'''
cur = os.path.abspath('.')
src= os.path.join(cur,'test.csv')
dst = os.path.join(cur,'out.txt')
with open(src, 'rb') as fh:
    with open(dst,'wt') as wh:
        for lno,line in enumerate(fh):
            try: 
                f,l  = line.strip('\r\n').split(',')
            except ValueError:
                print ' file read error at line{}, {}\n'.format(lno, line)
                continue 
            if len(f) > 2: 
                fp = gib_detect_train.avg_prob_over_trigram(f, model_mat)
            else:
                fp = 0
            
            if len(l) > 2:
                lp = gib_detect_train.avg_prob_over_trigram(l, model_mat)
            else: 
                lp = 0
            wl = '{}, {}, {}, {}, {}\n'.format(f,fp,l,lp, (fp+lp)/2 )
            print wl
            wh.write(wl)
