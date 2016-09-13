# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 12:53:11 2016

@author: trexleraj
"""

#want to take institution list from pubframe and bin into GPS coords.  
#use geopy lib to take addresses and convert.
#bin into 1

import geopy
import numpy as np
from geopy.geocoders import Nominatim
geolocator = Nominatim()
import time
from sklearn.neighbors import NearestNeighbors as knn
from sklearn import manifold

#coord_array=pd.DataFrame(index=np.arange(0,32400,1),columns=['count','name'])
#
#geo_list=[]
#place_list=[]
#j_list=[]
#i_list=[]
#
#for (idx,other) in pubframe.iterrows():
#    time.sleep(1.5)
#    institutions=pubframe.loc[idx,'inst']
#    j=pubframe.loc[idx,'jif']
#    if institutions!='[None]':
#
#        in_list=institutions.split(';')
#        for x in in_list:
#            px=x.split(',')
#            
#            if len(px)>=2:
#                locate=px[-2]+px[-1]
#                location=geolocator.geocode(locate,exactly_one=True,timeout=10)
#                if location:
#                    geo_list.append([location.latitude,location.longitude])
#                    place_list.append(location.raw['place_id'])
#                    j_list.append(j)
#                    i_list.append(idx)
#                else:
#                    if len(px)>=3:
#                        locate=px[-3]+px[-2]
#                        location=geolocator.geocode(locate,exactly_one=True,timeout=10)
#                        if location:
#                            geo_list.append([location.latitude,location.longitude])
#                            place_list.append(location.raw['place_id'])
#                            j_list.append(j)
#                            i_list.append(idx)
#                        else:
#                            geo_list.append(-500)
#                            place_list.append(-500)
#                            j_list.append(-500)
#                            i_list.append(idx)
#                    else:
#                        geo_list.append(-500)
#                        place_list.append(-500)
#                        j_list.append(-500)
#                        i_list.append(idx)
#            else:
#                geo_list.append(-500)
#                place_list.append(-500)
#                j_list.append(-500)
#                i_list.append(idx)
#    else:
#        geo_list.append(-500)
#        place_list.append(-500)
#        j_list.append(-500)
#        i_list.append(idx)
#        
#
#savegeo=pd.DataFrame(columns=['geo','place','jif','idx'])
#savegeo['geo']=geo_list
#savegeo['place']=place_list
#savegeo['jif']=j_list
#savegeo['idx']=i_list
#savegeo.to_csv('savegeo.csv')


savegeo=pd.from_csv('savegeo.csv')
geo=savegeo[savegeo['geo']!=-500]
lat=[x[0] for x in geo['geo']]
lon=[x[1] for x in geo['geo']]

geofit=pd.DataFrame(columns=['lat','lon'])
geofit['lat']=lat
geofit['lon']=lon

#want to now isomap and assign average jif per cluster.  knn doesnt seem to be proper
#way to cluster here, because will just find the X nearest neighbors of all points
#instead of actually clustering.
nbrs=knn(n_neighbors=50,algorithm='auto').fit(geofit)
dist,g_idx=nbrs.kneighbors(geofit)

isomap=manifold.Isomap(25,25).fit(geofit)
geo_iso=isomap.transform(geofit)
plt.scatter(x=yes,y=xes)





    