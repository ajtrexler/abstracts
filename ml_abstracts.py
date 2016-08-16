# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 18:03:07 2016

@author: adam
"""


#probably a nparray is the way to go.  need to make an array with column for every word in every dict.
#

#crude way to get list of common words.
words=open(r'C:\Users\trexleraj\Desktop\python dev\scripts\words')
words_txt=words.read()
common=words_txt.split('\n')
common.pop()
common.pop()
words.close()

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
    
#all_abs_dict is a dict of dicts, with the key being the pmid from pubframe and value being dict of all words from the abstract
#this block ofcode just makes the dict by calling make_abs_dict    
all_abs_dict={}
for (index,other) in pubframe.iterrows():
    all_abs_dict[index]=(make_abs_dict(pubframe.loc[index,'abstract']))            

#after the all_abs_dict is made, know what all the words in the abstracts are so then just combine them all into one big word list
#this list is just all the words in all the abstracts
big_word_list=[]
for d in all_abs_dict:
    for dd in all_abs_dict[d]:
        if dd not in big_word_list:
            big_word_list.append(dd)

#absframe will be what algo is used on.  it will encode whether a word is located in an abstract and zero if not over all the words in all the abstracts
absframe=pd.DataFrame(columns=big_word_list)

for e in all_abs_dict:
    local=all_abs_dict[e]
    dict_absframe={}
    for k in big_word_list:
        if k in local.keys():
            dict_absframe[k]=local[k]
        else:
            dict_absframe[k]=0
    
    absframe.loc[e]=dict_absframe

            
#next need to add encoding to absframe with JIF or whatever other metric to predict.
#will neef to eventually loadinto this pubs from variety of journals, so entire corpus should be 
#multi journal abstract list so have variation along JIF axis
            


