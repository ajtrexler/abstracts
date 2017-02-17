# -*- coding: utf-8 -*-
"""
Created on Sat Sep 17 16:22:14 2016

@author: adam
"""

#re-config problem as classification instead of regression.

from sklearn.naive_bayes import GaussianNB
from sklearn import metrics

#assign journal name per row
absframe['journal']=pubframe['journal']
titleframe['journal']=pubframe['journal']

def make_bayes(trainer):
    cv_data=trainer[0::10]
    trainer_data=trainer.drop(cv_data.index)
    
    cv_targets=cv_data['journal']
    cv_data=cv_data.drop('journal',1)
    trainer_targets=trainer_data['journal']
    trainer_data=trainer_data.drop('journal',1)
    
    full_data=trainer.drop('journal',1)
    gnb=GaussianNB()
    model=gnb.fit(trainer_data,trainer_targets)
    pred_trainer=model.predict(trainer_data)
    pred_cv=model.predict(cv_data)
    
    q=metrics.accuracy_score(cv_targets,pred_cv)
    return q
    

q_abstract=make_bayes(absframe)
q_titles=make_bayes(titleframe)