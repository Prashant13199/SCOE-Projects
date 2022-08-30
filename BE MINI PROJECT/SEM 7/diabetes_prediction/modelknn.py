import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split

import warnings
warnings.filterwarnings('ignore')

import pickle
dataset = pd.read_csv('diabetes.csv')

dataset_X = dataset.iloc[:,[1, 4, 5, 7]].values
dataset_Y = dataset.iloc[:,8].values

from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range = (0,1))
dataset_scaled = sc.fit_transform(dataset_X)

dataset_scaled = pd.DataFrame(dataset_scaled)

X = dataset_scaled
Y = dataset_Y

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.20, random_state = 0)

classifier = KNeighborsClassifier(n_neighbors=11,p=2,metric='euclidean')
classifier.fit(X_train,Y_train)
y_pred = classifier.predict(X_test)

pickle.dump(classifier, open('modelknn.pkl','wb'))
model = pickle.load(open('modelknn.pkl','rb'))



