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
import random
from sklearn import preprocessing as ppp

#assign journal name per row
labeler=ppp.LabelEncoder().fit(pubframe['journal'])
labels=labeler.transform(pubframe['journal'])

hash_df['journal']=labels
title_df['journal']=labels

random.seed(a=1224)
cix=random.sample(xrange(len(hash_df)),int(np.asarray(len(hash_df))*frac))

def sep_data(data,cix,frac):
    targ=data['journal']
    d=data.drop('journal',1)
    #cix=random.sample(xrange(len(data)),int(np.asarray(len(data))*frac))
    cvdata=d.iloc[cix,:]
    cvt=targ.iloc[cix]
    tdata=d.drop(cvdata.index,0)
    tt=targ.drop(cix)
    return cvdata,cvt,tdata,tt
    
def make_bayes(trainer):
    cv_data,cv_targets,trainer_data,trainer_targets=sep_data(trainer,cix,0.2)

    gnb=naive_bayes.MultinomialNB()
    model=gnb.fit(trainer_data,trainer_targets)
    pred_trainer=model.predict(trainer_data)
    pred_cv=model.predict(cv_data)
    probs=model.predict_proba(cv_data)
    q=metrics.accuracy_score(cv_targets,pred_cv)
    print metrics.classification_report(cv_targets,pred_cv)
    return q,probs
    

def make_bags(trainer):
    cv_data,cv_targets,trainer_data,trainer_targets=sep_data(trainer,cix,0.2)

    bag=sklearn.ensemble.BaggingClassifier(n_estimators=20)
    model=bag.fit(trainer_data,trainer_targets)
    pred_trainer=model.predict(trainer_data)
    prob_trainer=model.predict_proba(cv_data)
    pred_cv=model.predict(cv_data)
    
    q=metrics.accuracy_score(cv_targets,pred_cv)
    print metrics.classification_report(cv_targets,pred_cv)

    return q,prob_trainer

    
q_abstract,abs_prob=make_bayes(hash_df)
q_titles,title_probs=make_bayes(title_df)

metaframe['journal']=labels
q_meta,probs=make_bags(metaframe)

test_targets=hash_df.loc[cix,'journal']
out=[]
test_labs=[]
for x,y,z in zip(abs_prob,title_probs,probs):
    out.append(np.mean([x,y,z],0))



labs=[]    
for x in out:
    labs.append(np.argmax(x))

metrics.accuracy_score(test_targets,labs)