'''
Created on Apr 22, 2016

@author: eli
'''

import math
import re
import threading
import itertools
import sys
import time

from Tkinter import Tk
from tkFileDialog import askopenfilename

def select_input_file():
    Tk().withdraw() 
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    return filename


def is_jiberish(inputstr):    
    '''
    return 1 if pattern matches
    return 0 otherwise'''  
    pattern1 = '[zrtypqsdfghjklmwxcvbnZRTYPQSDFGHJKLMWXCVBN]{4,}'
    pattern2 = '[qsdfghjklmQSDFGHJKLM]{3,}'
   
    flag = 0
    
    '''vowels = re.findall('[aAeEiIoOuU]', inputstr)
    vc = len(vowels)'''            
   
    if re.search(pattern1, inputstr) <>  None:
        flag = 1
    elif re.search(pattern2, inputstr) <> None:
        flag = 1
    
    return flag



def dist(v1,v2):
    keyboard = {'q':(0,1),'w':(0,2),'e':(0,3), 'r':(0,4),'t':(0,5),'y':(0,6),'u':(0,7),'i':(0,8),'o':(0,9),'p':(0,10), 
                'a':(1,1), 's':(1,2), 'd':(1,3),'f':(1,4),'g':(1,5),'h':(1,6), 'j':(1,7), 'k':(1,8), 'l':(1,9),
                'z':(2,1), 'x':(2,2), 'c':(2,3), 'v':(2,4), 'b':(2,5), 'n':(2,6),'m':(2,7),'m':(2,8)}
    x1, y1 = keyboard[v1.lower()]
    x2, y2 = keyboard[v2.lower()]
    pd = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return pd
    
    

class StrDist:
    
    def __init__(self, src=None):
        if src <> None: 
            self.points = 0 
            self.target = list(src)
        else:
            self.points = 0
            self.target = []    
        
    def getDist(self):
        
        if self.target <> None:
            prev = self.target[0]
            for curr in self.target:
                self.points += dist(curr, prev)
                prev = curr
            return self.points / len(self.target)
        else:
            return 0
''' Signal used to communicate to the thread and stop the thread'''
       
class Signal: 
    go = True
    

def spin(msg, signal):
    write, flush = sys.stdout.write, sys.stdout.flush 
    for char in itertools.cycle('|/-\\'):
        status = char + ' ' + msg
        write(status)
        flush()
        ''' flush() to refresh the screen
        '''
        write('\x00' * len(status))
        time.sleep(.1)
        if not signal.go:
            break
    write(' ' * len(status) + '\x00' * len(status))