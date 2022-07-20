from flask import request
from flask_restx import Resource, Api, Namespace
from flask import render_template, make_response
import os
import pandas as pd
##
import sys
import numpy as np
import pandas as pd
sys.path.append("../")
sys.path.append("../..")

##
DataInference = Namespace(name = 'DataInference',  description='Code For Data Inference')
html_headers = {'Context-Type':'text/html'}

test_duration={'start':'2020-10-10 00:00:00', 'end':'2020-10-18 00:00:00'}

dir_root = os.getcwd()
app_root = os.path.join(dir_root,'..','KETIAppMachineLearning')


import json
@DataInference.route('/prediction/<string:target_feature>/<int:past_min>/<int:future_min>/<int:re_frequency_min>')

class prediction(Resource):
    def get(self, target_feature, past_min, future_min, re_frequency_min):
        target_feature ='CO2ppm'
        features_list=['CO2ppm']
        features ={'target_feature':target_feature, "feature_list": features_list}
        time_min={'past_min' :past_min, "future_min": future_min, "re_frequency_min":re_frequency_min }
        learning_method_num = 4

        from KETIAppMachineLearning.VIBES.settings import vibe_setting as vls
        VI= vls.vibe_learning(features, time_min, learning_method_num)
        model_info=VI.learning_information
        self.model = self.model_load(VI.model_file_name)

        ##### Modify! ####
        input_data = self.file_input_load('test_data.csv', VI)
        ##### Modify! ####

        if len(input_data)> 0:
                from KETIAppMachineLearning.VIBES import VIBE_inference
                inv_yhat= VIBE_inference.inference(input_data, VI) 
                from KETIAppDataServer.visual_manager import DF_manager
                input_data_json, data_index = DF_manager.get_jsonDF(input_data)
        else:
            input_data_json={}
            data_index={}

        return make_response(render_template('dataPrediction/LSTMInference.html', model_info = model_info, 
        data = input_data_json, data_index = data_index, yhat =round(inv_yhat,2)), 200, html_headers)
        

    def file_input_load(self, data_file_name, VI):  
        import pandas as pd
        test_data_fileName = os.path.join(app_root, 'VIBES','data',data_file_name)
        data_set = pd.read_csv(test_data_fileName, index_col=['datetime'], parse_dates=['datetime'])
        data_set = data_set[VI.feature_list]
        data_set = data_set[-VI.X_row_num:]
        return data_set

    def model_load(self, model_file_name):
        import requests
        import json
        
        #json_file_name = os.path.join(app_root, app_id, 'model', model_id+'.json')
        #h5_file_name = os.path.join(app_root, app_id, 'model', model_id+'.h5')
        json_file_name = os.path.join(model_file_name+'.json')
        h5_file_name = os.path.join(model_file_name+'.h5')


        from keras.models import model_from_json
        json_file = open(json_file_name, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights(h5_file_name)
        return loaded_model

