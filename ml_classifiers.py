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
from sklearn import linear_model as lin_mod

#assign journal name per row
labeler=ppp.LabelEncoder().fit(pubframe['journal'])
labels=labeler.transform(pubframe['journal'])

hash_df['journal']=labels
title_df['journal']=labels
metaframe['journal']=labels


random.seed(a=1224)
#cix=random.sample(xrange(len(hash_df)),int(np.asarray(len(hash_df))*frac))
#cix_geo=random.sample(xrange(len(nbr_vals)),int(np.asarray(len(nbr_vals))*frac))
cix=random.sample(xrange(len(hash_df)),1000)
cix_geo=random.sample(xrange(len(nbr_vals)),1000)

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
    return q,probs,model
    

def make_bags(trainer):
    cv_data,cv_targets,trainer_data,trainer_targets=sep_data(trainer,cix,0.2)
    #basemod=sklearn.svm.SVC()
    bag=sklearn.ensemble.BaggingClassifier(n_estimators=50)
    model=bag.fit(trainer_data,trainer_targets)
    pred_trainer=model.predict(trainer_data)
    prob_trainer=model.predict_proba(cv_data)
    pred_cv=model.predict(cv_data)
    
    q=metrics.accuracy_score(cv_targets,pred_cv)
    print metrics.classification_report(cv_targets,pred_cv)

    return q,prob_trainer,model

def make_geo_bags(trainer):
    cv_data,cv_targets,trainer_data,trainer_targets=sep_data(trainer,cix_geo,0.2)
    #basemod=sklearn.svm.SVC()
    bag=sklearn.ensemble.BaggingClassifier(n_estimators=50)
    model=bag.fit(trainer_data,trainer_targets)
    pred_trainer=model.predict(trainer_data)
    prob_trainer=model.predict_proba(cv_data)
    pred_cv=model.predict(cv_data)
    
    q=metrics.accuracy_score(cv_targets,pred_cv)
    print metrics.classification_report(cv_targets,pred_cv)

    return q,prob_trainer,model


    
q_abstract,abs_prob,mod_abs=make_bayes(hash_df)
q_titles,title_probs,mod_title=make_bayes(title_df)

q_meta,probs,mod_meta=make_bags(metaframe)

q,p,mod_geo=make_geo_bags(nbr_vals)


#need to now stack!
#straight average probabilities approach
test_targets=hash_df.loc[cix,'journal']
out=[]
for x,y,z,q in zip(abs_prob,title_probs,probs,p):
    out.append(np.mean([x,y,z,q],0))
labs_avg=[]    
for x in out:
    labs_avg.append(np.argmax(x))
print metrics.classification_report(test_targets,labs_avg)

#use majority vote or failing that take highest prob.
majvote=[]
for x,y,z,q in zip(abs_prob,title_probs,probs,p):
    s=pd.Series(np.argmax([x,y,z,q],1))
    if s[s.duplicated()].any():
        majvote.append(s[s.duplicated()].values[0])
    else:
        majvote.append(sorted(zip(np.max([x,y,z,q],1),np.argmax([x,y,z,q],1)),reverse=True)[0][1])

print metrics.classification_report(test_targets,majvote)        

#straight highest prob
highvote=[]
for x,y,z,q in zip(abs_prob,title_probs,probs,p):
    s=pd.Series(np.argmax([x,y,z,q],1))
    highvote.append(sorted(zip(np.max([x,y,z,q],1),np.argmax([x,y,z,q],1)),reverse=True)[0][1])

print metrics.classification_report(test_targets,highvote)    
        
