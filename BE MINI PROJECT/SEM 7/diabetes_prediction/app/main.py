import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
import pickle

app = Flask(__name__)
model = pickle.load(open('modelknn.pkl', 'rb'))
modelnaive = pickle.load(open('modelnaive.pkl', 'rb'))

dataset = pd.read_csv('diabetes.csv')

dataset_X = dataset.iloc[:,[1, 2, 5, 7]].values

from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range = (0,1))
dataset_scaled = sc.fit_transform(dataset_X)


@app.route('/')
def home():
    if request.method == 'GET':
        return render_template('index.html')


@app.route('/predict',methods=['POST'])
def predict():
    try:
        float_features = [float(x) for x in request.form.values()]
        final_features = [np.array(float_features)]
        print(sc.transform(final_features))
        prediction = model.predict( sc.transform(final_features) )
        print(prediction)
        if prediction == 1:
            pred = "You have Diabetes, please consult a Doctor."
        elif prediction == 0:
            pred = "You don't have Diabetes."
        output = "KNN : "+pred

        return render_template('index.html', prediction_text=output,a="a")
    except:
        return render_template('error.html')

@app.route('/predictnaive',methods=['POST'])
def predictnaive():
    try:
        float_features = [float(x) for x in request.form.values()]
        final_features = [np.array(float_features)]
        prediction = modelnaive.predict( sc.transform(final_features) )

        if prediction == 1:
            pred = "You have Diabetes, please consult a Doctor."
        elif prediction == 0:
            pred = "You don't have Diabetes."
        output = "Naive Bayes : " + pred 

        return render_template('index.html', prediction_text=output,a="a")
    except:
        return render_template('error.html')

