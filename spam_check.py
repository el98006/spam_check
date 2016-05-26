'''
Created on Apr 4, 2016
v1.1
- use context for file operation
- use generator to pipeline the processing of input csv file
- code style
 
@author: eli
'''
import csv
import re
import time
from nltk.corpus import names
from util import StrDist, is_jiberish, select_input_file
from numpy.core.multiarray import ITEM_HASOBJECT


EMAIL = 'ACCOUNT_KEY'
LAST_NAME = 'LAST_NAME'
FIRS_TNAME = 'FIRST_NAME'
FAKE_NAMES = 'JiberishNames'
NAME_CHECK = 'NameCheck'

NAME_MATCH_EMAIL ='NameEmailMatch'
FAKE_EMAIL = 'JiberishEmail'
EMAIL_SCORE = 'EmailScore'

SPAM_SCORE = 'SpamScore'

def name_in_email(mailid,name):    
    return ( mailid.lower().find(name.lower()))

Rules = [ NAME_CHECK, NAME_MATCH_EMAIL, FAKE_NAMES, FAKE_EMAIL, EMAIL_SCORE]
Scores = {NAME_CHECK:40, NAME_MATCH_EMAIL:30, FAKE_NAMES:30, FAKE_EMAIL:20, EMAIL_SCORE:10}

def get_score(kv):
    score = 0
    for rule in Rules:
        try:
            score += kv[rule] * Scores[rule]
        except KeyError:
            print "error record:"
            print kv
    kv[SPAM_SCORE] = score
    return kv

def check_name(s):
    '''return 0 for valid names, otherwise return the possibility of Jiberish'''
    if s.capitalize().decode('windows-1252') in names.words():
        return 0
    else:
        return 1    
    
# read_csv opens a csv file and return all lines in a generator
def read_csv(csv_file):
    '''first row contains header info'''
    
    with open(csv_file, "rb") as csvfile:
        for row in csv.reader(csvfile):
            yield row

# generator converts rows into col_dictionarys
def to_col_dict(rows):
    
    ''' first line is the headline, contains the field names, rows.next() the header,  retain the order
    of columns'''
    
    col_names = rows.next()
    '''convert csv row into dictionary format'''
    for r in rows:     
        col_dict = dict(zip(col_names, r))
        yield col_dict      
        
# generate spam ratings
def spam_rating(col_dicts):
    
    for item in col_dicts:
        try:
            email = item[EMAIL].split('@')[0]        
            '''filter out non characters'''
            cleanemailid = re.sub('[^a-zA-Z]+', "", email)
            lname = item[LAST_NAME]
            fname = item[FIRS_TNAME]
        except KeyError:
            print "error at %s" (email)
            continue

        item[NAME_CHECK] = 0
        item[FAKE_NAMES] = 0
        item[NAME_MATCH_EMAIL] = 0
        item[FAKE_EMAIL] = 0
        item[EMAIL_SCORE] = 0
        item[SPAM_SCORE] = 0
        
        result = [check_name(x) for x in [lname,fname]]
        
        item[NAME_CHECK] = result[0] & result[1]
        if item[NAME_CHECK] <> 0: 
            item[FAKE_NAMES] = is_jiberish(fname) | is_jiberish(lname) 
       
        if cleanemailid.lower().find(fname.lower()) == -1  and  cleanemailid.lower().find(lname.lower()) == -1:
            item[NAME_MATCH_EMAIL] = 1
        
        if item[NAME_MATCH_EMAIL] == 1:
            item[FAKE_EMAIL] =  is_jiberish(cleanemailid)
            AvgDist = 0
            if  cleanemailid <> '' and item[FAKE_EMAIL]:
                AvgDist = StrDist(cleanemailid).getDist()/ len(cleanemailid)
                item[EMAIL_SCORE] = AvgDist 
        
        item = get_score(item)
        
        yield item

def save_to_csv(col_dicts, fname):
    counter = 0
    
    with open(fname, "wb") as outfile:
        csvwriter = csv.writer(outfile)
        '''write the header, get the 1st item, extract the keys'''
        row = col_dicts.next()
        col_names = row.keys()
    
        csvwriter.writerow(col_names)
    
        for item in col_dicts:
            line = []
            for col in col_names:
                try: 
                    line.append(item[col])
                except KeyError:
                    item[col]='?'
                    line.append(item[col])
                
            csvwriter.writerow(line)
            counter += 1
    return counter                      
def main():
    
    SourceCSV = select_input_file()  
    PathFilePrefix = re.match('(.+)\.(\w+)$',SourceCSV)
    fullpath_outfile = PathFilePrefix.group(1) + '-out.csv'
   

    rows = read_csv(SourceCSV) 
    
    t_start =time.time()
    
    col_dicts = to_col_dict(rows)
    
    rated_col_dicts = spam_rating(col_dicts)
    
    rec_no = save_to_csv(rated_col_dicts,fullpath_outfile)
    
    t_stop = time.time()
    
    print "{} records process in {:<3.5f} seconds".format(rec_no, t_stop - t_start)

if __name__ == '__main__':
    main()
