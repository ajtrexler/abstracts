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
tn2='authframe'
tn3='instframe'

db=sqlite3.connect(sql_file)
db.text_factory=str
conn=db.cursor()

conn.execute('CREATE TABLE {tn}(pmid INT, date BLOB, journal TEXT, jif INT, abstract TEXT, title TEXT, num_auth INT, senior TEXT, first TEXT, PRIMARY KEY (pmid))'.format(tn=table_name1))
conn.execute('CREATE TABLE {tn}(pmid INT, name TEXT, entry INT, PRIMARY KEY (entry))'.format(tn=tn2))
conn.execute('CREATE TABLE {tn}(pmid INT, inst TEST, entry INT, PRIMARY KEY (entry))'.format(tn=tn3))

db.commit()
db.close()

pubframe.to_sql(sql_file,db,if_exists='append')

