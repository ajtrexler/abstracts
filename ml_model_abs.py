# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 16:47:46 2016

@author: adam
"""

from sklearn import linear_model
from sklearn.decomposition import PCA
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from sklearn.feature_selection import SelectFromModel
import seaborn as sea

#assign jifs per row
absframe['jif']=pubframe['jif']
titleframe['jif']=pubframe['jif']

def lasso_predictions(trainer,alpha):
    #take trainer data, assign jif vars and then remove jifs from training data.  separate out the cv dataset but use
    #full dataset to make predictions.
    #set cross-validation data taking every 10th row and then dropping that from training data.
    cv_data=trainer[0::10]
    trainer_data=trainer.drop(cv_data.index)
    
    cv_jif=cv_data['jif']
    cv_data=cv_data.drop('jif',1)
    trainer_jif=trainer_data['jif']
    trainer_data=trainer_data.drop('jif',1)
    
    full_data=trainer.drop('jif',1)

    lasso=linear_model.Lasso(alpha=alpha)

    model=lasso.fit(trainer_data,trainer_jif)
    trainer_pred=model.predict(trainer_data)
    cv_pred=model.predict(cv_data)

    cv_score=r2_score(cv_jif,cv_pred)
    full_pred=model.predict(full_data)
    
    return full_pred,cv_score
    
#   use lassocv or whatever to get best CV for each model set. 
#def get_alpha(trainer):
#    jifs=trainer['jif']
#    data=trainer.drop('jif',1)
#    
#    lassocv=linear_model.LassoCV()
#    cvmodel=lassocv.fit(data,jifs)
    
    
#sweep for best number of components for pca dim reduction.
#pca_test=[]
#trainer=titleframe.drop('jif',1)
#
#for n in np.arange(0,3500,100):
#    pca=PCA(n_components=n)
#    pca.fit(trainer)
#    pca_test.append(np.sum(pca.explained_variance_ratio_))
#seems to suggest >1000 components accounts for variability

#pca2=PCA(n_components=1500)
#
#pca2.fit(train_data_frame)
#transform_frame=pca2.transform(train_data_frame)
#cv_transform=pca2.transform(cv_data_frame)

abs_predictions,w_abs=lasso_predictions(absframe,0.1)
title_predictions,w_title=lasso_predictions(titleframe,0.25)

avg_predictions=[]
for x,y in zip(abs_predictions,title_predictions):
    avg_predictions.append(np.mean([x,y]))
    

est=linear_model.LassoCV()
sfm=SelectFromModel(est,threshold=0.1)
sfm.fit(trainer_data,trainer_jif)
n_feats=sfm.transform(trainer_data).shape[1]

abs_sfm_predictions,w_abs_trans=lasso_predictions(transform,0.1)
    
    