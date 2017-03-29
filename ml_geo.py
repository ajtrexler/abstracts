# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 12:53:11 2016

@author: trexleraj
"""

#want to take institution list from pubframe and bin into GPS coords.  
#use geopy lib to take addresses and convert.
#bin into 1

#reason for entry as primary id is that pmid will not be unique and primary KEY must be unique.

import geopy
import numpy as np
from geopy.geocoders import Nominatim
geolocator = Nominatim()
import time
from sklearn.neighbors import NearestNeighbors as knn
from sklearn import manifold
from sklearn.cluster import KMeans
import ast
import scipy as sci
import sqlite3
import collections
from sklearn import preprocessing as ppp
import seaborn as sea


coord_array=pd.DataFrame(index=np.arange(0,32400,1),columns=['count','name'])

sql_file='mydb.sqlite'
db=sqlite3.connect(sql_file)
db.text_factory=str
instframe=pd.read_sql('SELECT * from instframe',db)
all_ids=list(np.unique(instframe['pmid']))
conn=db.cursor()

#check where we're at in the geoframe
if os.path.isfile(sql_file):
    #get idx of latest entry
    tn4='geoframe'
    conn.execute('CREATE TABLE IF NOT EXISTS {tn}(pmid INT, lat DEC, lon DEC, place DEC, entry INT, PRIMARY KEY (entry))'.format(tn=tn4))
    db.commit()
    try:
        bottom=all_ids.index(conn.execute('SELECT pmid FROM geoframe ORDER BY rowid DESC LIMIT 1').fetchall()[0][0])+1
    except:
        bottom=0 

def inst_entry(loc_entry,pmid):
    loc_df=pd.DataFrame(index=[0])
    loc_df['lat']=loc_entry.latitude
    loc_df['lon']=loc_entry.longitude
    loc_df['place']=loc_entry.raw['place_id']
    loc_df['pmid']=pmid
    if conn.execute('SELECT COUNT (*) FROM geoframe').fetchall()[0][0] != 0:
        loc_df['entry']=conn.execute('SELECT COUNT (*) FROM geoframe').fetchall()[0][0]+1

    else:
        loc_df['entry']=1
    
    loc_df.to_sql('geoframe',db,if_exists='append',index=False)
    db.commit()

def blank_entry(pmid,code):
    loc_df=pd.DataFrame(index=[0])
    loc_df['pmid']=pmid
    loc_df['place']=code
    if conn.execute('SELECT COUNT (*) FROM geoframe').fetchall()[0][0] != 0:
        loc_df['entry']=conn.execute('SELECT COUNT (*) FROM geoframe').fetchall()[0][0]+1

    else:
        loc_df['entry']=1
    loc_df.to_sql('geoframe',db,if_exists='append',index=False)
    db.commit()

def fetch_location(locate):
    e=0
    while e<10:     
        try:
            return geolocator.geocode(locate,exactly_one=True,timeout=10)
        except:
            e=e+1
            continue
    print 'geolocator api failure possible'
            

    
fails=0
for x in range(bottom,len(all_ids),1):
    time.sleep(2)
    pmid=all_ids[x]
    if x % 25 == 0:
        print x
    try:
        inst=conn.execute('SELECT inst FROM instframe WHERE pmid LIKE "%{a}%"'.format(a=pmid)).fetchall()
        if inst:        
            for x in inst:
                px=x[0].split(',')
                if len(px)>=2:
                    locate=px[-2]+px[-1]
                    location=fetch_location(locate)
                    
                    if location:
                        inst_entry(location,pmid)
                        #write a row to db with lat/lon/pmid data/'place_id'/journalname
                        #def a function to write this stuff, so can call below as well.
                        #how to deal with missing data?

                    else:
                        if len(px)>=3:
                            locate=px[-3]+px[-2]
                            location=fetch_location(locate)
                            if location:
                                inst_entry(location,pmid)

                            else:
                                #write row with a placeholder value or make a flag for missing data.  
                                #would be useful to know how many missing data from each pmid
                                blank_entry(-500)
                        else:
                            blank_entry(-500)
                else:
                    blank_entry(pmid,-500)
        else:
            #if no inst, just mark place with -999 for dropping later.
            #-999 will mean no institutional data
            blank_entry(pmid,-999)          
    
    except:
        #keep record of how many failed accesses to db.  would mean no insts on record for that pmid.
        fails=fails+1
        print fails
        continue 




sql_file='mydb.sqlite'
db=sqlite3.connect(sql_file)
db.text_factory=str
geo=pd.read_sql('SELECT * from geoframe',db)
geo.drop(geo.loc[geo['place']==-500].index,0,inplace=True)
geo.reset_index(inplace=True)

geofit=geo[['lat','lon']]
geo['journal']=geo['pmid'].apply(lambda x: pubframe.loc[pubframe['pmid']==x,'journal'].values[0])
labeler=ppp.LabelEncoder().fit(geo['journal'])
labels=labeler.transform(geo['journal'])
geo['journal']=labels
#cluster the institutions geographically.
clusts=KMeans(n_clusters=50).fit(geofit)

clust_idx=clusts.predict(geofit)
centers=clusts.cluster_centers_

#here need to exclude neighbors with same pmid value.  probably easiest to do this post knn so dont need to implement a fresh knn.
nbrs=knn(n_neighbors=25).fit(geofit)
distances, n_idx = nbrs.kneighbors(geofit)

#drop same pmid from knn n_idx lists to prevent leakage.
fix_n_idx=[]
for i,x in enumerate(n_idx):
    blah=geo.iloc[x]['pmid'].drop_duplicates(keep='first')
    blah=blah[blah!=int(geo.iloc[i]['pmid'])]
    fix_n_idx.append(blah.values)
    
    
local_js={}
for x,pmid in zip(n_idx,geo['pmid']):
    if pmid in local_js:
        entry=np.bincount(geo.loc[x]['journal'].values,minlength=16)
        local_js[pmid]=entry+local_js[pmid]
    else:    
        local_js[pmid]=np.bincount(geo.loc[x]['journal'].values,minlength=16)
l=[]
for x in local_js.keys():
    l.append(geo.loc[geo['pmid']==x]['journal'].values[0])
    
nbr_vals=pd.DataFrame(index=local_js.keys(),data=local_js.values())
nbr_vals['journal']=l
nbr_vals.reset_index(inplace='True')

'''
y=np.argmax(local_js.values(),1)
q=pd.DataFrame(columns=['y','l'])
q['y']=y
q['l']=l  
sea.jointplot(x='l',y='y',data=q,kind='hex')


fnorms=np.bincount(labels)/float(len(labels))

place_encoder=ppp.LabelEncoder().fit(geo['place'])
geo['place_enc']=place_encoder.transform(geo['place'])

oh_geo=ppp.OneHotEncoder().fit_transform(geo['place'].reshape(-1,1))
test=pd.DataFrame(index=geo['pmid'],data=oh_geo.toarray())
def sum_inst(x):
    local=test.loc[x]
    if len(np.shape(local))>1:
        return pd.DataFrame(data=local.sum()).T
    else:
        return pd.DataFrame(data=local).T



newframe=geo['pmid'].apply(sum_inst)  
out=newframe.to_frame()    
new=pd.DataFrame(index=geo['pmid'],data=out.values)



howpop=[]
for i in np.unique(geo['place_enc']):
    geo.loc[(geo['place_enc']==i)]
    howpop.append(len(geo.loc[(geo['place_enc']==i)]))
    
    
for c in np.unique(clust_idx):
    locale=geo[clust_idx==c]
    counts=(np.bincount(locale['journal'],minlength=16))/(fnorms*len(locale))
    plt.figure()
    plt.suptitle('cluster'+str(c))
    plt.plot(counts)
    centroid=centers[c]
    vote=[]
    dist=[]
    #want each point to vote for cluster journal, with an associated weight.
    for l in locale.iterrows():
        point=[l[1]['lat'],l[1]['lon']]
        dist.append(sci.spatial.distance.euclidean(centroid,point))
        vote.append(l[1]['journal'])
    vote_count=collections.Counter(vote)
    locale_pred=vote_count.most_common()[0]
    geo.loc[locale.index,'pred']=locale_pred[0]
#not working super well, obvs from distribution of the

#so possibly use distribution of journals within each cluster to
        







csp=plt.cm.jet(np.linspace(0,1,len(np.unique(val))))
plt.scatter(x=lat,y=lon,c=csp)
plt.scatter(x=geofit['lat'],y=geofit['lon'],c='black')
plt.scatter(x=cluster1['lat'],y=cluster1['lon'],c='red')
'''






    
