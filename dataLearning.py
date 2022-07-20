from flask import request, session
from flask_restx import Resource, Namespace
from flask import render_template, make_response
import os, json
import KETIAppDataServer.data_manager.lstm as lstm
from KETIAppMachineLearning.ML.settings.learning_setting import make_hash_for_db_ms, list_files

DataLearning = Namespace(name = 'DataLearning',  description='Code For Machine Learning')
html_headers = {'Context-Type':'text/html'}
root_path = os.path.dirname(os.path.abspath(__file__)) 
model_path = root_path + "/model"

default_db_info  = {"db_info":
                [{'db_name': 'farm_inner_air',
                'measurement': 'HS1',
                'start': '2020-09-11 00:00:00',
                'end': '2020-10-13 00:00:00'},

                {'db_name': 'farm_outdoor_air_clean',
                'measurement': 'sangju',
                'start': '2020-09-11 00:00:00',
                'end': '2020-10-13 00:00:00'},

                {'db_name': 'farm_outdoor_weather_clean',
                'measurement': 'sangju',
                'start': '2020-09-11 00:00:00',
                'end': '2020-10-13 00:00:00'}]}
global integratedDataSet

@DataLearning.route('/dataset')
class DataSet(Resource):
    def post(self):
        """
        Return measurement list having a certain column in a database 
        
        # Input
        ``` json
        {
            "db_info":{
                [
                    {
                        'db_name': 'farm_inner_air',
                        measurement': 'HS1',
                        'start': '2020-09-11 00:00:00',
                        'end': '2020-10-13 00:00:00'
                    },
                ]
            },
            "re_freq_min":4
        }
        ```
        
        # Output 
        ``` json
        {
            "features":[column1, column2]
        }
        ```
        """
        global integratedDataSet
        intDataInfo = request.get_json()["db_info"]
        #session['intDataInfo']=intDataInfo
        if(request.get_json()['re_freq_min']=='') : freq_min = 4
        else : freq_min = int(request.get_json()['re_freq_min'])
        integratedDataSet = lstm.integrate(intDataInfo, freq_min)

        res = {"features":list(integratedDataSet.columns)}
        return res

@DataLearning.route('/params')
class Params(Resource):
    def post(self):
        # 
        """
        Return file contents for model parameter
        
        # Input
        ``` json
        {
            "file_name":file_name
        }
        ```
        
        # Output 
        ``` json
        {
            "model parameter info"
        }
        ```
        """
        file_name = request.get_json()['file_name']
        with open(model_path+file_name) as json_file:
            json_data = json.load(json_file)
        return json_data

@DataLearning.route('/integration/hash')
class Params(Resource):
    def post(self):
        """
        Return integration info id
        
        # Input
        ``` json
        {
            "intDataInfo":{
                [
                    {
                        'db_name': 'farm_inner_air',
                        measurement': 'HS1',
                        'start': '2020-09-11 00:00:00',
                        'end': '2020-10-13 00:00:00'
                    },
                ]
            }
        }
        ```
        
        # Output 
        ``` json
        {
            "integration_info_id": "123-455-543"
        }
        ```
        """
        db_info = request.get_json()['intDataInfo']
        integration_info_id = make_hash_for_db_ms(db_info)
        return {"integration_info_id":integration_info_id}


@DataLearning.route('/LSTMInference')
class InferLSTM(Resource):
    def get(self):
        """
        Return LSTM Inference page
        """
        hierarchy_dir = list_files(model_path)
        return make_response(render_template('dataPrediction/LSTMInference.html', hierarchy_dir = hierarchy_dir), 200, html_headers)
    
    def post(self):
        """
        Run inference
        
        # Input
        ``` json
        {
            "model_param":{model parameter information},
            "test_duration":{"start":"2021-02-03 00:00:00", "end":"2021-03-04 00:00:00"}
        }
        ```
        
        # Output 
        ``` json
        {
            "ori_img":original_img,
            "mini_img":minimal_img, 
            "result_date":"2021-03-04 00:08:00",
            "result_value":36.234
        }
        ```
        """
        model_param = request.get_json()['model_param']
        test_duration = request.get_json()['test_duration']
        return lstm.run_inference(model_param,test_duration,root_path)

@DataLearning.route('/LSTMLearning')
class TrainLSTM(Resource):
    def get(self):
        """
        Return LSTM Learning page
        """
        if 'integration_param' in session :
            db_info = session.get('integration_param')['intDataInfo']
        else:
            db_info = default_db_info
        return make_response(render_template('dataPrediction/LSTMLearning.html',db_info = db_info), 200, html_headers)
    
    def post(self):
        """
        Run learning
        
        # Input
        ``` json
        {
            "model_param":{model parameter information},
            "test_duration":{"start":"2021-02-03 00:00:00", "end":"2021-03-04 00:00:00"}
        }
        ```
        
        # Output 
        ``` json
        {
            "img": plotting_res(lines), 
            "rmse" : lines, 
            "mid_data":{
                "partial_dataset_type":string,
                "file_path":string
            }
        }
        ```
        """
        if 'integration_param' in session :
            intDataInfo = session.get('integration_param')['intDataInfo']
        else : 
            intDataInfo = default_db_info
        global integratedDataSet
        params = request.get_json()
        return lstm.run(intDataInfo, params,root_path, integratedDataSet)
