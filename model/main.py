#!flask/bin/python
# testcommit version 2
# creating a branch
# 

import os
from flask import Flask
from flask import request
import pandas as pd
from sklearn import linear_model
from sklearn import datasets
import pickle
import numpy as np

diabetes = datasets.load_diabetes()

# Pick just one feature 
X = diabetes.data[:, np.newaxis, 2]

# creating and saving some model
regr = linear_model.LinearRegression()
regr.fit(X, diabetes.target)
pickle.dump(regr, open('diabetes.pkl', 'wb'))

app = Flask(__name__)

@app.route('/isAlive')
def index():
    return "true"

@app.route('/prediction/', methods=['GET'])
def get_prediction():
    feature = float(request.args.get('f'))
    model = pickle.load(open('diabetes.pkl', 'rb'))
    pred = model.predict([[feature]])
    return str(pred)

# note that with FROM tiangolo/uwsgi-nginx-flask:python3.6 the default port is 80, which I changed in the Docker file to 8080.
if __name__ == '__main__':
        app.run(host='0.0.0.0')


