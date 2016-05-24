'''
Created on Apr 4, 2016

@author: eli
'''
import csv
import re
from nltk.corpus import names
from myUtil import StrDist, is_jiberish, select_input_file

EMAIL = 'ACCOUNT_KEY'
LASTNAME = 'LAST_NAME'
FIRSTNAME = 'FIRST_NAME'
SPAMSCORE = 'SpamScore'
NAMECHECK = 'NameCheck'
NAMEMATCHEMAIL ='NameEmailMatch'
FAKEEMAIL = 'JiberishEmial'
FAKENAMES = 'JiberishNames'
RANDOMEMAIL = 'RandomEmailID'

def name_in_email(mailid,name):    
    return ( mailid.lower().find(name.lower()))

Rules = [ NAMECHECK, NAMEMATCHEMAIL, FAKENAMES, FAKEEMAIL, RANDOMEMAIL]
Scores = {NAMECHECK:40, NAMEMATCHEMAIL:30, FAKENAMES:30, FAKEEMAIL:20, RANDOMEMAIL:10}

def get_score(kv):
    ScoreSum = 0
    for rule in Rules:
        ScoreSum += kv[rule] * Scores[rule]
    kv['SpamScore'] = ScoreSum
    return kv

def check_name(s):
    '''return 0 for valid names, otherwise return the possibility of jiberish'''
    if s.capitalize().decode('windows-1252') in names.words():
        return 0
    else:
        return 1         
                                       
def main():
    rowNo = 0

    
    SourceCSV = select_input_file()()
    csvfile = open(SourceCSV, "rb")
    PathFilePrefix = re.match('(.+)\.(\w+)$',SourceCSV)
    fname = PathFilePrefix.group(1) + '-out.csv'
    outfile = open(fname, "wb")
    
    reader = csv.reader(csvfile)
    writer = csv.writer(outfile)


    ''' NameCheck 0: Neither FirstName nor Last Name not found in Names database, 1: FirstName or LastName found, 2: both found
    eMailCheckByName 0: No Name or Name Variations found in email id, 1: emailId contains either first name or last name.  
    eMailIdDist:  the pythagras distance of characters in EmailID
    '''
                      
    
    for line in reader:
        
    
        row =[]
        
        if rowNo == 0:
            ''' read the header line from csv, assemble the new header line by adding additional ant-spam fields'''
            headline = [col for col in line]
            for col in Rules: headline.append(col)
            headline.append('SpamScore')
            writer.writerow(headline)
        else:
            ''' read csv body lines'''
            '''kv pairs contains the original fields, additional fields need to be appeneded.  zip only takes the shorter list when the two lists have different lengths'''
            kv_pairs = dict(zip(headline, line))
            
            try: 
                emailid = kv_pairs[EMAIL].split('@')[0]
                cleanemailid = re.sub('[^a-zA-Z]+', "", emailid)
                lname = kv_pairs['LAST_NAME']
                fname = kv_pairs['FIRST_NAME']
            except KeyError:
                print "error at %d" (rowNo)
                continue
            kv_pairs[NAMECHECK] = 0
            kv_pairs[FAKENAMES] = 0
            kv_pairs[FAKEEMAIL] = 0
            kv_pairs[NAMEMATCHEMAIL] = 0 
            kv_pairs[RANDOMEMAIL] =0
            
            result = map(check_name, [lname,fname])
            kv_pairs[NAMECHECK] = result[0] & result[1]
            
            
            if kv_pairs[NAMECHECK] <> 0: 
                kv_pairs[FAKENAMES] = is_jiberish(fname) | is_jiberish(lname) 
           
            if cleanemailid.lower().find(fname.lower()) == -1  and  cleanemailid.lower().find(lname.lower()) == -1:
                kv_pairs[NAMEMATCHEMAIL] = 1
            
            if kv_pairs[NAMEMATCHEMAIL] <> 0:
                kv_pairs[FAKEEMAIL] =  is_jiberish(cleanemailid)
                AvgDist = 0
                if  cleanemailid <> '':
                    AvgDist = StrDist(cleanemailid).getDist()/ len(cleanemailid)
                    kv_pairs[RANDOMEMAIL] = 2 - AvgDist 
                    
            kv_pairs = get_score(kv_pairs)   
            
            try:
                for key in headline: row.append(kv_pairs[key])
            except KeyError:
                print row
                print headline 
                print kv_pairs   
            writer.writerow(row)
        rowNo += 1
             
        
    csvfile.close()
    outfile.close()
    print ('completed')
if __name__ == '__main__':
    main()