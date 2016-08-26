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

coord_array=pd.DataFrame(index=np.arange(0,32400,1),columns=['count','name'])


for (idx,other) in pubframe.iterrows():
    institutions=pubframe.loc[idx,'inst']
    for ii in institutions:
        q=ii.encode('ascii','replace')
        location=geolocator.geocode(q,exactly_one=True)
        
        
    
for loop over pubframe to get insts:
    inside for loop over insts:
        location=geolocator.geocode(ii)
        round GPS coords and += coord_array.ix[GPS,'count']