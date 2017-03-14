# -*- coding: utf-8 -*-
"""
Created on Sat Sep 17 16:22:14 2016

@author: adam
"""

#re-config problem as classification instead of regression.

from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
from sklearn import naive_bayes
from sklearn import ensemble

#assign journal name per row
hash_df['journal']=pubframe['journal']
title_df['journal']=pubframe['journal']

def make_bayes(trainer):
    cv_data=trainer[0::10]
    trainer_data=trainer.drop(cv_data.index)
    
    cv_targets=cv_data['journal']
    cv_data=cv_data.drop('journal',1)
    trainer_targets=trainer_data['journal']
    trainer_data=trainer_data.drop('journal',1)
    
    full_data=trainer.drop('journal',1)
    gnb=naive_bayes.MultinomialNB()
    model=gnb.fit(trainer_data,trainer_targets)
    pred_trainer=model.predict(trainer_data)
    pred_cv=model.predict(cv_data)
    
    q=metrics.accuracy_score(cv_targets,pred_cv)
    return q
    

def make_bags(trainer):
    cv_data=trainer[0::10]
    trainer_data=trainer.drop(cv_data.index)
    
    cv_targets=cv_data['journal']
    cv_data=cv_data.drop('journal',1)
    trainer_targets=trainer_data['journal']
    trainer_data=trainer_data.drop('journal',1)
    
    full_data=trainer.drop('journal',1)
    bag=sklearn.ensemble.BaggingClassifier(n_estimators=20)
    model=bag.fit(trainer_data,trainer_targets)
    pred_trainer=model.predict(trainer_data)
    prob_trainer=model.predict_proba(cv_data)
    pred_cv=model.predict(cv_data)
    
    q=metrics.accuracy_score(cv_targets,pred_cv)
    return q,prob_trainer
    
    
q_abstract=make_bayes(hash_df)
q_titles=make_bayes(title_df)

metaframe['journal']=pubframe['journal']
q_meta,probs=make_bags(metaframe)