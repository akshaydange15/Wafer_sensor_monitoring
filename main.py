from wsgiref import simple_server
from flask import Flask, request, render_template
from flask import Response
import os
from flask_cors import CORS, cross_origin
from prediction_Validation_Insertion import pred_validation
from trainingModel import trainModel
from training_Validation_Insertion import train_validation
import flask_monitoringdashboard as dashboard
from predictFromModel import prediction
import json

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

#name of API is app
app = Flask(__name__)
dashboard.bind(app)
CORS(app)       #allow cross origin communication

#Home page of API
"""in prediction use same method as training only change in schema file here we have to change structure of file
we take one column(Target) less than training

when new point arrive it's distance get calculate from centroid of clusters already present 
new point closer to a cluster that model trigger and respective prediction DONE !!!"""
@app.route("/", methods=['GET'])
@cross_origin()
#render home page
def home():
    return render_template('index.html')

#prediction route
@app.route("/predict", methods=['POST'])
@cross_origin()
def predictRouteClient():
    try:
        """in Schema training we consider all column while in schema_prediction we have to drop and output column from .JSON file"""
        # request receive from Postman method
        if request.json is not None:
            path = request.json['filepath']

            #validate file with customer input
            pred_val = pred_validation(path) #object initialization
            pred_val.prediction_validation() #calling the prediction_validation function

            #start prediction
            pred = prediction(path) #object initialization
            # predicting for dataset present in database
            path,json_predictions = pred.predictionFromModel()
            return Response("Prediction File created at !!!"  +str(path) +'and few of the predictions are '+str(json.loads(json_predictions) ))

        #request receive from HTML (API)
        elif request.form is not None:
            path = request.form['filepath']

            pred_val = pred_validation(path) #object initialization

            pred_val.prediction_validation() #calling the prediction_validation function

            pred = prediction(path) #object initialization

            # predicting for dataset present in database
            path,json_predictions = pred.predictionFromModel()
            return Response("Prediction File created at !!!"  +str(path) +'and few of the predictions are '+str(json.loads(json_predictions) ))
        else:
            print('Nothing Matched')
    except ValueError:
        return Response("Error Occurred! %s" %ValueError)
    except KeyError:
        return Response("Error Occurred! %s" %KeyError)
    except Exception as e:
        return Response("Error Occurred! %s" %e)


#training of data perform here
@app.route("/train", methods=['POST'])
@cross_origin()
def trainRouteClient():

    try:
        #folderPath where client provide training data
        #here we use local system folder to hold traning data
        if request.json['folderPath'] is not None:
            path = request.json['folderPath']   #user will provide training data folder path, here ./Training_Batch_Files


            train_valObj = train_validation(path) #object initialization

            train_valObj.train_validation()#calling the training_validation function


            trainModelObj = trainModel() #object initialization
            trainModelObj.trainingModel() #training the model for the files in the table


    except ValueError:

        return Response("Error Occurred! %s" % ValueError)

    except KeyError:

        return Response("Error Occurred! %s" % KeyError)

    except Exception as e:

        return Response("Error Occurred! %s" % e)
    return Response("Training successfull!!")

#Flak API configuration
port = int(os.getenv("PORT",5000))
#calling main method

#starting of Application
if __name__ == "__main__":
    host = '0.0.0.0'
    port = 5000
    httpd = simple_server.make_server(host, port, app)
    # print("Serving on %s %d" % (host, port))
    httpd.serve_forever()
