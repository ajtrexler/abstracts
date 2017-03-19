# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 18:03:07 2016

@author: adam
"""

import sqlite3
import time
import pandas as pd
import pickle
import re
import sklearn
from sklearn import feature_extraction
import numpy as np
import matplotlib.pyplot as plt
import os


start=time.time()
#crude way to get list of common words.
words=open('words')
words_txt=words.read()
common=words_txt.split('\n')
common.pop()
common.pop()
words.close()

sql_file='mydb.sqlite'
db=sqlite3.connect(sql_file)
db.text_factory=str
pubframe=pd.read_sql('SELECT * from absframe',db)
authframe=pd.read_sql('SELECT * from authframe',db)

if os.path.isfile('author_freq.pkl'):
    #if author_freq in pkl, then just load it
    with open('author_freq.pkl','rb') as f:
        freq=pickle.load(f)    
else:
    #generate the author freq dict from the database
    conn=db.cursor()
    freq={}
    z=0
    for auth in authframe.loc[authframe.duplicated('name')==True]['name'].values:
        try:
            freq[auth]=len(conn.execute('SELECT * FROM authframe WHERE name LIKE "%{a}%"'.format(a=auth)).fetchall())
        except:
            continue
        z=z+1
        if z % 100==0:
            print z

if os.path.isfile('author_sumfreq.pkl'):
    #if author_sumfreq in pkl, then just load it
    with open('author_sumfreq.pkl','rb') as f:
        sumauthfreq=pickle.load(f)    
else:
    #generate sumauthfreq
    start=time.time()    
    sumauthfreq={}
    fails=0
    conn=db.cursor()
    
    for pmid in pubframe['pmid']:
        try:
            authors=conn.execute('SELECT name FROM authframe WHERE pmid LIKE "%{a}%"'.format(a=pmid)).fetchall()
            sumauthfreq[pmid]=np.sum([authframe.loc[authframe['name']==a[0],'freq'].values[0] for a in authors])
        except:
            fails=fails+1
            continue    
    print (time.time()-start)/60,'minutes'
    with open('author_sumfreq.pkl', 'wb') as f:
        pickle.dump(sumauthfreq, f, pickle.HIGHEST_PROTOCOL)
    
    db.close()



def authfreq_ret(x):
    if x in freq:
        return freq[x]
    else:
        return 1
        
authframe['freq']=authframe['name'].apply(lambda x: authfreq_ret(x))
pubframe['sumfreq']=authframe['pmid'].apply(lambda x: sumauthfreq[x])
authframe.drop('entry',1,inplace=True)
#build out metadata frame from authframe
#sum freqs from all auths
metaframe=pubframe[['sumfreq','num_auth']]
metaframe['first']=pubframe['first'].apply(lambda x: authfreq_ret(x))
metaframe['senior']=pubframe['senior'].apply(lambda x: authfreq_ret(x))
#leakage from title length since this is often restricted by journal
#metaframe['titlelen']=pubframe['title'].apply(len)
first_encoder=ppp.LabelEncoder().fit(pubframe['first'])
metaframe['1auth']=first_encoder.transform(pubframe['first'])

last_encoder=ppp.LabelEncoder().fit(pubframe['senior'])
metaframe['lastauth']=last_encoder.transform(pubframe['senior'])


#make a dict of all rhe words in an abstract.  remove most common 100 english words.
def make_abs_dict(a):
    allwords={}
    #need to make a re.search for all non word stuff.
    a=re.sub(r'[^\w\s]', ' ', a)
    a=a.lower()
    for w in a.split(' '):
        if (w not in common) & (w!=''):
            if w not in allwords:
                allwords[w]=1
            else:
                allwords[w]+=1
    return allwords

def make_auth_list(a): 
    all_authors=[]
    for auth in a.split(','):
        auth=auth.replace('[','')
        auth=auth.replace(']','')
        all_authors.append(auth.lstrip())
    return all_authors
#all_abs_dict is a dict of dicts, with the key being the pmid from pubframe and value being dict of all words from the abstract
#this block ofcode just makes the dict by calling make_abs_dict    
#also do this to make separate titles dict.
all_abs_dict={}
all_titles_dict={}
all_auth_dict={}
for (index,other) in pubframe.iterrows():
    authors_list=[]
    all_abs_dict[index]=(make_abs_dict(pubframe.loc[index,'abstract']))       
    all_titles_dict[index]=(make_abs_dict(pubframe.loc[index,'title']))  
   # authors_list=make_auth_list(pubframe.loc[index,'full_auth'])
#    for a in authors_list:
#        if a not in all_auth_dict.keys():
#            all_auth_dict.setdefault(a,[])
#            all_auth_dict[a].append(pubframe.loc[index,'jif'])
#        else:
#            all_auth_dict[a].append(pubframe.loc[index,'jif'])

       
    
#after the all_abs_dict is made, know what all the words in the abstracts are so then just combine them all into one big word list
#this list is just all the words in all the abstracts
big_word_list=[]
big_title_list=[]
for d in all_abs_dict:
    for dd in all_abs_dict[d]:
        if dd not in big_word_list:
            big_word_list.append(dd)

for t in all_titles_dict:
    for tt in all_titles_dict[t]:
         if tt not in big_title_list:
            big_title_list.append(tt) 

            
hasher=sklearn.feature_extraction.FeatureHasher(n_features=2**11,non_negative=True)      
abshash=hasher.transform(all_abs_dict.values())
hash_df=pd.DataFrame(index=pubframe.index.values,data=abshash.toarray())
titlehash=hasher.transform(all_titles_dict.values())
title_df=pd.DataFrame(index=pubframe.index.values,data=titlehash.toarray())            


'''
below is code for manually creating hash tables for each abstract that explicitly wha tthe feature names (the words)
are.  they of course take way longer than the hasing trick above.
'''            
##absframe will be what algo is used on.  it will encode whether a word is located in an abstract and zero if not over all the words in all the abstracts
#absframe=pd.DataFrame(columns=big_word_list)
#titleframe=pd.DataFrame(columns=big_title_list)
#
#for e in all_abs_dict:
#    local=all_abs_dict[e]
#    dict_absframe={}
#    for k in big_word_list:
#        if k in local.keys():
#            dict_absframe[k]=local[k]
#        else:
#            dict_absframe[k]=0
#    
#    absframe.loc[e]=dict_absframe
#
#for f in all_titles_dict:
#    local=all_abs_dict[f]
#    dict_titleframe={}
#    for l in big_title_list:
#        if l in local.keys():
#            dict_titleframe[l]=local[l]
#        else:
#            dict_titleframe[l]=0
#    
#    titleframe.loc[f]=dict_titleframe        
##next need to add encoding to absframe with JIF or whatever other metric to predict.
##will neef to eventually loadinto this pubs from variety of journals, so entire corpus should be 
##multi journal abstract list so have variation along JIF axis
#            
#print 'time to parse {s} abstracts:'.format(s=len(pubframe)),(time.time()-start)/60,'minutes'

