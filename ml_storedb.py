# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 14:06:59 2017
idea is to run ml_getpubs.py many times and then store that data in sql database that 
is setup in this script.
@author: trexleraj
"""

import sqlite3

sql_file='mydb.sqlite'
table_name1='absframe'
table_name2='geoframe'

abs_columns=['date','journal','jif','abstract','title','num_auth','senior','first','full_auth','inst']
abs_col_types=['TEXT','TEXT','REAL','TEXT','TEXT','INTEGER','TEXT','TEXT','TEXT','TEXT','TEXT']

q=[]
for row in zip(abs_columns,abs_col_types):
    q.append(" ".join(map(str,row)))

db=sqlite3.connect(sql_file)
conn=db.cursor()

conn.execute('CREATE TABLE absframe(pmid INT, jif INT,journal TEXT, abstract TEXT, PRIMARY KEY (pmid))')

conn.execute('CREATE TABLE {tn}({nant})'.format(tn=table_name1,nant=q))

db.commit()
db.close()