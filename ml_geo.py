# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 12:53:11 2016

@author: trexleraj
"""

#want to take institution list from pubframe and bin into GPS coords.  
#use geopy lib to take addresses and convert.
#bin into 1

#test git.

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
import collections


coord_array=pd.DataFrame(index=np.arange(0,32400,1),columns=['count','name'])

sql_file='mydb.sqlite'
db=sqlite3.connect(sql_file)
db.text_factory=str
instframe=pd.read_sql('SELECT * from instframe',db)
conn=db.cursor()

geo_list=[]
place_list=[]
j_list=[]
i_list=[]


for pmid in short['pmid']:
    try:
        inst=conn.execute('SELECT inst FROM instframe WHERE pmid LIKE "%{a}%"'.format(a=pmid)).fetchall()
        if inst:        
            for x in inst:
                px=x[0].split(',')
                    if len(px)>=2:
                        locate=px[-2]+px[-1]
                        location=geolocator.geocode(locate,exactly_one=True,timeout=10)
                        if location:
                            #write a row to db with lat/lon/pmid data/'place_id'/journalname
                            #def a function to write this stuff, so can call below as well.
                            #how to deal with missing data?
                            geo_list.append([location.latitude,location.longitude])
                            place_list.append(location.raw['place_id'])
                            j_list.append(j)
                            i_list.append(idx)
                        else:
                            if len(px)>=3:
                                locate=px[-3]+px[-2]
                                location=geolocator.geocode(locate,exactly_one=True,timeout=10)
                                if location:
                                    geo_list.append([location.latitude,location.longitude])
                                    place_list.append(location.raw['place_id'])
                                    j_list.append(j)
                                    i_list.append(idx)
                                else:
                                    #write row with a placeholder value or make a flag for missing data.  
                                    #would be useful to know how many missing data from each pmid
                                    geo_list.append(-500)
                                    place_list.append(-500)
                                    j_list.append(-500)
                                    i_list.append(idx)
                            else:
                                geo_list.append(-500)
                                place_list.append(-500)
                                j_list.append(-500)
                                i_list.append(idx)
                    else:
                        geo_list.append(-500)
                        place_list.append(-500)
                        j_list.append(-500)
                        i_list.append(idx)
        else:
            #if no inst, just mark place with -500 for dropping later.
            geo_list.append(-500)
            place_list.append(-500)
            j_list.append(-500)
            i_list.append(idx)            
    
    except:
        #keep record of how many failed accesses to db.  would mean no insts on record for that pmid.
        fails=fails+1
        continue 

    

for (idx,other) in pubframe.iterrows():
    time.sleep(1.5)
    institutions=pubframe.loc[idx,'inst']
    j=pubframe.loc[idx,'jif']
    if institutions!='[None]':

        in_list=institutions.split(';')
        for x in in_list:
            px=x.split(',')
            
            if len(px)>=2:
                locate=px[-2]+px[-1]
                location=geolocator.geocode(locate,exactly_one=True,timeout=10)
                if location:
                    geo_list.append([location.latitude,location.longitude])
                    place_list.append(location.raw['place_id'])
                    j_list.append(j)
                    i_list.append(idx)
                else:
                    if len(px)>=3:
                        locate=px[-3]+px[-2]
                        location=geolocator.geocode(locate,exactly_one=True,timeout=10)
                        if location:
                            geo_list.append([location.latitude,location.longitude])
                            place_list.append(location.raw['place_id'])
                            j_list.append(j)
                            i_list.append(idx)
                        else:
                            geo_list.append(-500)
                            place_list.append(-500)
                            j_list.append(-500)
                            i_list.append(idx)
                    else:
                        geo_list.append(-500)
                        place_list.append(-500)
                        j_list.append(-500)
                        i_list.append(idx)
            else:
                geo_list.append(-500)
                place_list.append(-500)
                j_list.append(-500)
                i_list.append(idx)
    else:
        geo_list.append(-500)
        place_list.append(-500)
        j_list.append(-500)
        i_list.append(idx)
        

savegeo=pd.DataFrame(columns=['geo','place','jif','idx'])
savegeo['geo']=geo_list
savegeo['place']=place_list
savegeo['jif']=j_list
savegeo['idx']=i_list
savegeo.to_csv('savegeo.csv')

journals={}
for x in jifs:
    journals[jifs[x]]=x

def jif_to_j(jlist):
    convert=[]
    for x in jlist:
        n=round(x,3)
        convert.append(journals[n])
    return convert
        

savegeo=pd.read_csv('savegeo.csv',converters={"geo": ast.literal_eval})
savegeo.drop('Unnamed: 0',1,inplace=True)

#issue is reading this as csv makes the datatypes weird.  strings instead of tuples...
geo=savegeo[savegeo['place']!=-500]
geo['journal']=jif_to_j(geo['jif'])

lat=[x[0] for x in geo['geo']]
lon=[x[1] for x in geo['geo']]

geo['lat']=lat
geo['lon']=lon
geo.drop('geo',1,inplace=True)

geofit=pd.DataFrame(columns=['lat','lon'])
geofit['lat']=lat
geofit['lon']=lon


#cluster the institutions geographically.
clusts=KMeans(n_clusters=20).fit(geofit)

clust_idx=clusts.predict(geofit)
centers=clusts.cluster_centers_

for c in np.unique(clust_idx):
    locale=geo[clust_idx==c]
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







    
