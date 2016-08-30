# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 16:47:46 2016

@author: adam
"""

from sklearn import linear_model
from sklearn.decomposition import PCA
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt


#assign jifs per row
absframe['jif']=jifs

#set a cross-validation frame, cv_frame, for testing the model as every 10th row.  drop that from the trainer frame.
cv_data_frame=absframe[0::10]
train_data_frame=absframe.drop(cv_frame.index)

#set jif values for each dataset and then drop those from the trainer and cv_frames.
trainer_jif=train_data_frame['jif']
cv_jif=cv_data_frame['jif']

cv_data_frame=cv_data_frame.drop('jif',1)
train_data_frame=train_data_frame.drop('jif',1)

#sweep for best number of components for pca dim reduction.
#pca_test=[]
#for n in np.arange(0,5000,250):
#    pca=PCA(n_components=n)
#    pca.fit(train_data_frame)
#    pca_test.append(np.sum(pca.explained_variance_ratio_))
##seems to suggest >1000 components accounts for variability

pca2=PCA(n_components=1500)

pca2.fit(train_data_frame)
transform_frame=pca2.transform(train_data_frame)
cv_transform=pca2.transform(cv_data_frame)

#mats for fitting below
training_set=train_data_frame
cv_set=cv_data_frame

alpha=0.2
lasso=linear_model.Lasso(alpha=alpha)

mod=lasso.fit(training_set,trainer_jif)
pred=mod.predict(training_set)
cv_pred=mod.predict(cv_set)

score_lasso=r2_score(trainer_jif,pred)
cv_score_lasso=r2_score(cv_jif,cv_pred)

plt.scatter(cv_jif,cv_pred)