import math
import pickle
import os
from nltk.corpus import names, brown

alphabet = 'abcdefghijklmnopqrstuvwxyz'
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
HAM_SAMPLE = os.path.join(DATA_DIR,'good.txt')
SPAM_SAMPLE = os.path.join(DATA_DIR,'bad.txt')



def normalize(line):
    return [c.lower() for c in line if c.lower() in alphabet]

def ngram(n, l):
    filtered = normalize(l)
    for start in range(0, len(filtered) - n + 1):
        yield ''.join(filtered[start:start + n])
        
'''stay a bit away from lowest probality of good samples to ensure no good items being identified as spam by mistake
2% above the highest probability of bad samples to ensure all spams are caught'''
        
def get_thresh(good_prob, bad_prob, strategy):
    if strategy == 'CONSERVATIVE':
        thresh =  min(good_prob) * 0.98  
    elif strategy == 'AGGRESSSIVE':
        thresh = max(bad_prob) * 1.02  
    elif strategy == 'BALANCED':
        thresh = (min(good_prob) + max(bad_prob)) / 2
    else: 
        raise('wrong strategy')
    return thresh

def iterate_cube(mat):
    s = 0
    for i in xrange(len(alphabet)): 
        for j in xrange(len(alphabet)):
            for k in xrange(len(alphabet)):
                s = s + mat[i][j][k]
    return s

def normalize_cube(cube):
    total_cnt = iterate_cube(cube)
    for i in xrange(len(alphabet)): 
        for j in xrange(len(alphabet)):
            for k in xrange(len(alphabet)):
                cube[i][j][k] = math.log(cube[i][j][k]  * 100 / float(total_cnt)) 

def avg_transition_prob(input, log_prob_mat):
    log_prob = 0.0
    transition_ct = 0
    for a, b in ngram(2, input):
        log_prob += log_prob_mat[alphabet[a]][alphabet[b]]
        transition_ct += 1
    return math.exp(log_prob / (transition_ct or 1))

    
def avg_prob_over_trigram( input_str, prob_matrix):
    prob = 0.0
    transition_ct = 0
    for i, j, k in ngram(3, input_str):
        prob += prob_matrix[alphabet.index(i)][alphabet.index(j)][alphabet.index(k)]
        transition_ct += 1
    return math.exp(prob / (transition_ct or 1))


def bigram_train():
    k = len(alphabet)
    '''freq_matrix is a 26x 26 matrix, the value is the frequency  of two char sequence (i,j) based on statistics, set the init value to 10''' 
    freq_matrix = [[10 for i in xrange(k)] for i in xrange(k)]

    ''' use the nltk.names corpus to get the n-gram frequency'''
    for line in names.words():
        for a, b in ngram(2, line):
            freq_matrix[alphabet.index(a)][alphabet.index(b)] += 1

    for i , row in enumerate(freq_matrix):
        s = float(sum(row))
        for j in xrange(len(row)):
            row[j] = math.log(row[j] / s)


    good_probs = [avg_transition_prob(l, freq_matrix) for l in open(HAM_SAMPLE)]
    bad_probs = [avg_transition_prob(l, freq_matrix) for l in open(SPAM_SAMPLE)]

    print good_probs
    print bad_probs
    print 'Minimal P of Good: {}'.format(min(good_probs))
    print 'maximal P of Spam: {}'.format(max(bad_probs))

    thresh = get_thresh(good_probs, bad_probs, 'CONSERVATIVE')
    
    print thresh
    model_filename = os.path.join(DATA_DIR,'model.data')
    with open(model_filename,'xb') as fh:
        pickle.dump({'mat': freq_matrix, 'thresh': thresh}, fh) 



        
        
def tri_gram_training(): 
    freq_mat = []           
    leng = len(alphabet)
  
    
    freq_mat = [[[100 for i in xrange(leng)] for j in xrange(leng)] for k in xrange(leng)]
    ''' we can train with different nltk corpus,  names, brown '''    
    for line in brown.words():
        for i, j, k in ngram(3, line):
            freq_mat[alphabet.index(i)][alphabet.index(j)][alphabet.index(k)] +=10
    
    normalize_cube(freq_mat)
    
    good_probs = [avg_prob_over_trigram(item, freq_mat) for item in open(HAM_SAMPLE)]
    bad_probs =  [avg_prob_over_trigram(item, freq_mat) for item in open(SPAM_SAMPLE)]

    print good_probs
    print bad_probs
    print 'Minimal P of Good: {}'.format(min(good_probs))
    print 'maximal P of Spam: {}'.format(max(bad_probs))

    thresh = get_thresh(good_probs, bad_probs, 'CONSERVATIVE')
    
    print thresh
    model_filename = os.path.join(DATA_DIR,'model.data')
    with open(model_filename,'wb') as fh:
        pickle.dump({'mat': freq_mat, 'thresh': thresh}, fh)         


if __name__ == '__main__':
     tri_gram_training()
