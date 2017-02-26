# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 20:55:53 2016

@author: adam
want to manually build database for pubs
first efetch a list of all the IDs based on search term.  will want to
iterate over all the journals in journal list.

then use efetch to iteratively collect data on each article.

parse the data from efetch using soup.

"""

from Bio import Entrez
from datetime import datetime
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from decimal import *
import time
import csv
import requests
import sqlite3
import os

'''
setup SQL database.
'''
sql_file='mydb.sqlite'
db=sqlite3.connect(sql_file)
db.text_factory=str


Entrez.email='adam.trexler@posteo.net'
jifs=dict([('"Science (New York, N.Y.)"[Journal]',34.661),
              ('"Nature"[Journal]',38.138),
              ('"Biophysical journal"[Journal]',3.632),
              ('"Biochemistry"[Journal]',2.876),
              ('"Cell"[Journal]',28.710),
              ('"Proceedings of the National Academy of Sciences of the United States of America"[Journal]',9.423),
              ('"PLoS biology"[Journal]',8.668),
              ('"Molecular biology of the cell"[Journal]',4.037),
              ('"Neuron"[Journal]',13.974),
              ('"Molecular cell"[Journal]',13.958),
              ('"The Journal of general physiology"[Journal]',4.788),
              ('"Blood"[Journal]',11.841),
              ('"The Journal of cell biology"[Journal]',9.786),
              ('"The Journal of biological chemistry"[Journal]',4.573),
              ('"elife"[Journal]',8.303),
              ('"Journal of cell science"[Journal]',4.706)])
              
              
pubs=[]

#iterate over jifs dict to get all the pmids saved into pubs variable.  so maybe make the pubframe here and save into it journal and jif
#for j in jifs:
#    time.sleep(3)   
#    #esearch for list of IDS.  get full set here.
#    id_list_handle=Entrez.esearch(db='pubmed',term=j,retmax=10000,datetype='pdat',mindate='2015/01/01',maxdate='2016/01/01')
#    id_list=Entrez.read(id_list_handle)
#    rec_per_j[j]=len(id_list['IdList'])
#    pubs=pubs+id_list['IdList']
#
#idfile=open('pub_list.csv','wb')
#wr=csv.writer(idfile)
#wr.writerow(pubs)
#idfile.close()

fromfile=open('pub_list.csv','r')
rr=csv.reader(fromfile)
for line in rr:
    pubs=line

#want t odefine functions to fetch most of this stuff so can pass error when theres no abstract or whatever.
def fetch_abs(article):
    
    if 'Abstract' in article.keys():
        return str(article['Abstract']['AbstractText'])
    else:
        return 'None'

def make_authlist(auths,pmid):
    names=[]
    for x in auths:
        if ('ForeName' in x) & ('LastName' in x):
            names.append(x['ForeName'] + ' ' + x['LastName'])
    apd=pd.DataFrame(columns=['pmid','name'])
    apd['name']=names
    apd['pmid']=pmid
    return apd


#problem here is people with more than one affiliation.  parse on periods?
def make_instlist(auths,pmid):
    inst=[]
    for x in auths:
        if x['AffiliationInfo']:
            xinst=x['AffiliationInfo'][0]['Affiliation']
            xinst.encode('ascii','replace')
        else:
            xinst='None'

        #first parse xinst for email addresses.
        res=re.search('\S+@\S+',xinst)
        if res:
            xinst=xinst.replace(res.group(),'')
            print res.group()
        
        #find how many periods.
        perres=re.search('\w{1}(\.)',xinst)        
        if perres:
            xinst=xinst.replace(perres.group(1),'')
        linst=xinst.split('.')
        for l in linst:
            l=l.strip()
            secres=re.search('address',l)
            if (l!='') & (l not in inst) & (not secres):
                inst.append(l)
    ipd=pd.DataFrame(columns=['pmid','inst'])
    ipd['inst']=inst
    ipd['pmid']=pmid
    return ipd        
    
def get_date(mcite):
    if mcite.has_key('DateCompleted'):
        q=mcite['DateCompleted'].values()
        return datetime(int(q[2]),int(q[0]),int(q[1]))
    else:
        return 0

def fetch_authors(article):
    if article.has_key('AuthorList'):
        return article['AuthorList']
    else:
        return 'None'
        
        
chunk=100
#just chunk at 100, seems like either way need to iterate over pub list and feed in limited number to efetch or epost.
#check in db what latest UID is, get argnum for that.  if db: check, else: make db
if os.path.isfile(sql_file):
    #get idx of latest entry
    conn=db.cursor()
    conn.execute('SELECT * FROM Table ORDER BY ID DESC LIMIT 1')
else:
    bottom=0
#set up iteration starting from argnum
for i in range(bottom,len(pubs),chunk):
    l=pubs[i:i+chunk]
    handle=Entrez.efetch(db='pubmed',id=l,retstart=i,retmode='xml',retmax=100)
    record=Entrez.read(handle)
    #init dataframe to save stuff into.  indices will be PMIDs.
    pubframe=pd.DataFrame(columns=['date','journal','jif','abstract','title','num_auth','senior','first'])
    authframe=pd.DataFrame(columns=['pmid','name'])
    instframe=pd.DataFrame(columns=['pmid','inst'])

    #loop over every entry in record to extract and save the details.
    for x in record['PubmedArticle']:
        mcite=x['MedlineCitation']
        pdata=x['PubmedData']
        pmid=int(mcite['PMID'])
        article=mcite['Article']
        
        pubframe.loc[pmid,'abstract']=fetch_abs(article)
                
        journal=article['Journal']['Title']
       
        pubframe.loc[pmid,'journal']=journal
        pubframe.loc[pmid,'jif']=jifs['"'+journal+'"[Journal]']
        
        art_title=article['ArticleTitle']
        art_title.encode('ascii','replace')
        pubframe.loc[pmid,'title']=art_title
        
        pubframe.loc[pmid,'date']=get_date(mcite)
        
       
           
        #parse sep first and last authors and affiliations.  might as well go all auths.  for all auths, could then compute diversity of institution or whatever as a metric.
        auth_list=fetch_authors(article)
        #remove all articles without authors, presumably not research articles.        
        if auth_list!='None':
            pubframe.loc[pmid,'num_auth']=len(auth_list) 
            if 'CollectiveName' in auth_list[0]: 
                pubframe.loc[pmid,'first']='collective'
            else:
                pubframe.loc[pmid,'first']=auth_list[0]['ForeName']+' ' + auth_list[0]['LastName']         
            authframe=pd.concat([authframe,make_authlist(auth_list,pmid)],ignore_index=True)
            
            if 'CollectiveName' in auth_list[-1]: 
                pubframe.loc[pmid,'senior']='collective'
            else:
                pubframe.loc[pmid,'senior']=auth_list[-1]['ForeName']+' ' + auth_list[-1]['LastName']
                
            instframe=pd.concat([instframe,make_instlist(auth_list,pmid)],ignore_index=True)
        else:
            pubframe.ix[pmid]=0

        #next remove things without abstracts
        if pubframe.loc[pmid,'abstract']=='None':
            pubframe.ix[pmid]=0

    #remove zero rows
    instframe=instframe[]
    q=pubframe[pubframe['abstract']==0].index.values #get pmid from 0 abstract rows
    pubframe=pubframe[pubframe['abstract']!=0]

    #check this pmid over instframe and authframe and remove those values to clean up the dbs.
    instframe=instframe[instframe['pmid'].isin(q)==False]
    authframe=authframe[authframe['pmid'].isin(q)==False]
    
    
    pubframe.to_sql(sql_file,db,if_exists='append')

db.commit()
db.close()