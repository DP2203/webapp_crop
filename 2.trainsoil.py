import pandas as pd
data=pd.read_csv("Crop_recommendation.csv")
data=data.dropna(how='any')
colums=data.columns
X=data.loc[:,["N","P","K"]]
y=data.loc[:,colums[7]]

#array Conver
X=X.to_numpy()

#spilit data
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

import warnings
warnings.filterwarnings("ignore")
names = ["K-Nearest Neighbors", "SVM",
         "Decision Tree", "Random Forest",
         "Naive Bayes","ExtraTreesClassifier","VotingClassifier"]

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import VotingClassifier
classifiers = [
    make_pipeline(Normalizer(),KNeighborsClassifier()),
    make_pipeline(Normalizer(),LinearSVC()),
    make_pipeline(Normalizer(),DecisionTreeClassifier()),
    make_pipeline(Normalizer(),RandomForestClassifier()),
    make_pipeline(Normalizer(),GaussianNB()),
    make_pipeline(Normalizer(),ExtraTreesClassifier()),
    make_pipeline(Normalizer(),VotingClassifier(estimators=[('DT', DecisionTreeClassifier()), ('rf', RandomForestClassifier()), ('et', ExtraTreesClassifier())], voting='hard'))]
clfF=[]
for name, clf in zip(names, classifiers):
    clf.fit(X_train, y_train)
    y_pred=clf.predict(X_test)
    print(name)
    print(confusion_matrix(y_test, y_pred))
    print(classification_report(y_test, y_pred))
    print('--------------------------------------------------------------')
    clfF.append(clf)
import pickle
import bz2
sfile = bz2.BZ2File("modelS.pkl", 'w')
pickle.dump(clfF, sfile)   
    
    
    
    
    
    
    
    
    
    
    