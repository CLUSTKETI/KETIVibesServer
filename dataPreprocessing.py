from wsgiref.simple_server import WSGIRequestHandler
from flask import request, session
from flask_restx import Resource, Api, Namespace, reqparse

from flask import render_template, make_response, redirect
##
import sys
sys.path.append("../")
sys.path.append("../..")

from flask_restx import Api, fields
api = Api()
DataPreprocessing = Namespace(name = 'DataPreprocessing',  description='Data Preprocessing package test')
html_headers = {'Context-Type':'text/html'}

from db_model import dbModel
db_client = dbModel.db_client

import json
"""
TO DO : Data Num parameter setting
"""
@DataPreprocessing.route('/testPreproessing')
class nanDataPackageTest(Resource):
    def get(self):
        return make_response(render_template('dataPreprocessing/testPreproessing.html'), 200, html_headers)  


@DataPreprocessing.route('/nanDataPackageTest')
class nanDataPackageTest(Resource):
    def get(self):
        return make_response(render_template('dataPreprocessing/preprocessingSimulation.html'), 200, html_headers)  

from KETIAppDataServer.data_manager import echart
from KETIPrePartialDataPreprocessing import data_preprocessing

DBMSPreprocessingParser = reqparse.RequestParser()
DBMSPreprocessingParser.add_argument('db_name',  type=str, help='database name of influxdb', location='json',required=True)
DBMSPreprocessingParser.add_argument('ms_name',  type=str, help='ms names of DB', location='json',required=True)
DBMSPreprocessingParser.add_argument('feature_name',  type=str, help='ms names of DB', location='json',required=True)
DBMSPreprocessingParser.add_argument('data_num',  type=int, help='number of ingested data', location='json',required=True)
#DBMSPreprocessingParser.add_argument('process_param',  type=dict, help='parameter for preprocessing', location='json',required=True)
@DataPreprocessing.route('/getAllResultData')
class getProcessedDataSet(Resource):
    @DataPreprocessing.doc("Get All preprocessing Result")
    @DataPreprocessing.expect(DBMSPreprocessingParser) 
    def post(self):
    
        ## 홑따옴표 => 쌍따옴표, True => true, None => "none", '2000' => 200, 줄바꿈문자
        """
        This API gets all processed result
        # Input
        ``` json
        {
            "db_name": "air_indoor_중학교", 
            "ms_name": "ICW0W2000012", 
            "feature_name": "in_cici_co2", 
            "data_num": 200, 
            "process_param": { "refine_param": {"removeDuplication": {"flag": true}, \
               "staticFrequency": {"flag": true, "frequency": "None"}},\
               "outlier_param": {"certainErrorToNaN": {"flag": true}, \
               "unCertainErrorToNaN": {"flag": true, "param": {"neighbor": 0.5}}, "data_type": "air"}, \
               "imputation_param": {"serialImputation": {"flag": true, "imputation_method": [{"min": 0, "max": 1000, "method": "linear", "parameter": {}}], \
               "totalNonNanRatio": 80}}\
            }

        }
        ```
        # Output 
        ``` json
        {
            "result" : 
            {
                'column_name1':{'min':min_value, 'max':max_value},
                'column_name2':{'min':min_value, 'max':max_value},
                'column_name3':{'min':min_value, 'max':max_value}
            }
        }
        ```

        """
        
        preprocessing_param = request.get_json(force=True)
        db_name = preprocessing_param['db_name']
        ms_name = preprocessing_param['ms_name']
        feature_name = preprocessing_param['feature_name']
        data_num = preprocessing_param['data_num']
        #tag_key = checkNoneBoolean(preprocessing_param['tag_key'])
        #tag_value = checkNoneBoolean(preprocessing_param['tag_value'])

        data = db_client.get_datafront_by_num(data_num, db_name, ms_name)[[feature_name]]
        #data = db_client.get_datafront_by_num(data_num, db_name, ms_name, tag_key, tag_value)[[feature_name]]
        partialP = data_preprocessing.packagedPartialProcessing(preprocessing_param['process_param'])
        multiple_dataset = partialP.allPartialProcessing(data)
        result={}
        for key in multiple_dataset.keys():
            result[key] = echart.getEChartFormatResult(multiple_dataset[key])
        
        return json.dumps(result)


global OriginalData # OriginalData
global RefinedData
global DataWithoutCertainOutlier
global DataWithoutUncertainOutlier
global ImputedData
global currentDataStepFlag
# Original->Refine-> RangeCheck (DataWithoutCertainOutlier)->OutlierDetectoin ->imputation
DBMSFeatureNumParser = reqparse.RequestParser()
DBMSFeatureNumParser.add_argument('db_name',  type=str, help='database name of influxdb', location='json',required=True)
DBMSFeatureNumParser.add_argument('ms_name',  type=str, help='ms names of DB', location='json',required=True)
DBMSFeatureNumParser.add_argument('feature_name',  type=str, help='ms names of DB', location='json',required=True)
#DBMSFeatureNumParser.add_argument('data_num',  type=int, help='number of ingested data', location='json',required=True)
@DataPreprocessing.route('/getOriginalData')
class getOriginalData(Resource):
    @DataPreprocessing.doc("Get data by DB, MS, Num, Feature")
    @DataPreprocessing.expect(DBMSFeatureNumParser) 
    def post(self):
        """
        Get Dataframe by DB, MS, Num, Feature Data
        Store Original DataFrame
        Return data in json format
        
        # Input
        ``` json
        {
            "db_name" : "air_indoor_초등학교",
            "ms_name" : "ICW0W2000021",
            'feature_name': 'in_cici_co2', 
            'data_num': '2000'
        }
        ```
        """
        preprocessing_param = request.get_json(force=True)
        db_name = preprocessing_param['db_name']
        ms_name = preprocessing_param['ms_name']
        feature_name = preprocessing_param['feature_name']
        # TODO 
        #data_num = preprocessing_param['data_num']
        data_num = 10000
       
        global OriginalData
        OriginalData = db_client.get_dataend_by_num(data_num, db_name, ms_name)
        OriginalData = OriginalData[[feature_name]]
      
        global currentDataStepFlag
        currentDataStepFlag = 'Original'

        result = {"result": echart.getEChartFormatResult(OriginalData)}
        return json.dumps(result)



def checkNoneBoolean(input):
      if input.lower() =='none':
            return None
      elif input.lower()  == 'true':
            return True
      elif input.lower()  == 'false':
            return False
      else:
            return input

ParameterParser = reqparse.RequestParser()
ParameterParser.add_argument('parameter',  type=str, help='processing parameter', location='json',required=True)
@DataPreprocessing.route('/refinementData')
class refinementParameter(Resource):
    @DataPreprocessing.doc("Get Refined Data and Store It")
    @DataPreprocessing.expect(ParameterParser) 
    def post(self):
        """
        Get Refined Data and Store It
        
        # Input
        ``` json
        {
            "parameter" : {'removeDuplication': {'flag': True}, 'staticFrequency': {'flag': True, 'frequency': None}}
        }
        ```

        """
        # ex parameter = {'removeDuplication': {'flag': True}, 'staticFrequency': {'flag': True, 'frequency': "3M"}}
        preprocessing_param = request.get_json(force=True)
        refine_param = preprocessing_param['parameter']
        print(refine_param)
        refine_param["removeDuplication"]["flag"] = checkNoneBoolean(refine_param["removeDuplication"]["flag"])
        refine_param["staticFrequency"]["flag"] = checkNoneBoolean(refine_param["staticFrequency"]["flag"])
        refine_param["staticFrequency"]["frequency"] = checkNoneBoolean(refine_param["staticFrequency"]["frequency"])
        global RefinedData
        global OriginalData

        global currentDataStepFlag
        currentDataStepFlag = 'Refinement'

        from KETIPrePartialDataPreprocessing.data_preprocessing import DataPreprocessing
        RefinedData = DataPreprocessing().get_refinedData(OriginalData, refine_param)
        result = {"result": echart.getEChartFormatResult(RefinedData)}

        return json.dumps(result)

@DataPreprocessing.route('/getDataWithoutCertainOutlier')
class getDataWithoutCertainOutlier(Resource):
    @DataPreprocessing.doc("Get Data Without CertainOutlier and Store it ")
    @DataPreprocessing.expect(ParameterParser) 
    def post(self):
        """
        Get Refined Data and Store It
        
        # Input
        ``` json
        {
            "parameter" : {'flag': True}
        }
        ```
        """
        
        preprocessing_param = request.get_json(force=True)
        CertainParam = preprocessing_param['parameter']
        CertainParam["flag"] = checkNoneBoolean(CertainParam["flag"])

        global RefinedData
        global DataWithoutCertainOutlier
        
        global currentDataStepFlag
        currentDataStepFlag = 'RangeCheck'
        
        from KETIPrePartialDataPreprocessing.error_detection.errorToNaN import errorToNaN 
        DataWithoutCertainOutlier = errorToNaN().getDataWithCertainNaN(RefinedData, CertainParam)

        result = {"result": echart.getEChartFormatResult(DataWithoutCertainOutlier)}

        return json.dumps(result)



@DataPreprocessing.route('/getDataWithoutUnCertainOutlier')
class getDataWithoutUnCertainOutlier(Resource):
    @DataPreprocessing.doc("Get Data Without UnCertainOutlier and Store it ")
    @DataPreprocessing.expect(ParameterParser) 
    def post(self):
        """
        Get Data without Uncertain Outlier data
        
        # Input
        ``` json
        {
            "parameter" : {
                'flag': True,
                'param': {'outlierDetectorConfig': [
                    { 'algorithm': 'SD',
                      'percentile': 99,
                      'alg_parameter': {'period': 1440, 'limit': 15}},
                    { 'algorithm': 'MoG', 
                      'percentile': 99.9, 
                      'alg_parameter': {'MoG_components': 2,'MoG_covariance': 'full','MoG_max_iter': 100}}
                ]}
            }
        }
        ```
        """
        
        preprocessing_param = request.get_json(force=True)
        UnCertainParam = preprocessing_param['parameter']
        UnCertainParam["flag"] = checkNoneBoolean(UnCertainParam["flag"])
        

        global DataWithoutCertainOutlier
        global DataWithoutUncertainOutlier

        global currentDataStepFlag
        currentDataStepFlag = 'OutlierDetection'

        from KETIPrePartialDataPreprocessing.error_detection.errorToNaN import errorToNaN 
        DataWithoutUncertainOutlier = errorToNaN().getDataWithUncertainNaN(DataWithoutCertainOutlier, UnCertainParam)
        result = {"result": echart.getEChartFormatResult(DataWithoutUncertainOutlier)}

        return json.dumps(result)


@DataPreprocessing.route('/getImputedData')
class getImputedData(Resource):
    @DataPreprocessing.doc("Get Imputed Data and Store it ")
    @DataPreprocessing.expect(ParameterParser) 
    def post(self):
        """
        Get Data without Uncertain Outlier data
        
        # Input
        ``` json
        {
            "parameter" : {
                'serialImputation': {
                    'flag': True,
                    'imputation_method': [
                        {'min': 0,'max': 30,'method': 'linear','parameter': {}},
                        {'min': 31,'max': 100, 'method': 'KNN', 'parameter': {'n_neighbors': 10, 'weights': 'uniform', 'metric': 'nan_euclidean'}}],
                'totalNonNanRatio': 100}}
        }
        ```
        """
        preprocessing_param = request.get_json(force=True)
        imputationParam = preprocessing_param['parameter']
        imputationParam["serialImputation"]["flag"] = checkNoneBoolean(imputationParam["serialImputation"]["flag"])

        print("===imputationParam===")
        print(imputationParam)

        global DataWithoutUncertainOutlier
        global ImputedData

        global currentDataStepFlag
        currentDataStepFlag = 'Imputation'

        from KETIPrePartialDataPreprocessing.data_preprocessing import DataPreprocessing
        ImputedData= DataPreprocessing().get_imputedData(DataWithoutUncertainOutlier, imputationParam)
       
        result = {"result": echart.getEChartFormatResult(ImputedData)}

        return json.dumps(result)


@DataPreprocessing.route('/getCurrentStep')
class getCurrentStep(Resource):       
    def get(self):
       
        global currentDataStepFlag

        result = {"result" : currentDataStepFlag}

        return  json.dumps(result)


@DataPreprocessing.route('/getNoProcessedData')
class getNoProcessedData(Resource):
    @DataPreprocessing.doc("No Data Preprocessing")
    @DataPreprocessing.expect(ParameterParser) 
    def post(self):
        """
        No Data Preprocessing
        
        """
        preprocessing_param = request.get_json(force=True)
        db_name = preprocessing_param['db_name']
        ms_name = preprocessing_param['ms_name']
        feature_name = preprocessing_param['feature_name']
        #data_num = preprocessing_param['data_num']
        data_num = 10000
        
       
        global ImputedData
        ImputedData = db_client.get_dataend_by_num(data_num, db_name, ms_name)
        ImputedData = ImputedData[[feature_name]]

        global currentDataStepFlag
        currentDataStepFlag = 'Imputation'

        result = {"result": echart.getEChartFormatResult(ImputedData)}
        return json.dumps(result)



@DataPreprocessing.route('/saveData')
class saveData(Resource):
    @DataPreprocessing.doc("saveData")
    @DataPreprocessing.expect(ParameterParser) 
    def post(self):
        
        """
        Save final preprocessed data
        
        # Input
        
        ```
        # Output
          file address: 

        """
        

        """
        global OriginalData # OriginalData
        global RefinedData
        global DataWithoutCertainOutlier
        global DataWithoutUncertainOutlier
        global ImputedData
        global currentDataStepFlag

        #post 로 block number를 받는다.
        #CSV 이름을 생성한다.
        number = 1
        # 이때  그냥 file_name으로 하면 안되고 폴더 등을 지정해줘야 돌아갈 것입니다.
        # dataLearning.py
        # root_path = os.path.dirname(os.path.abspath(__file__)) 
        # model_path = root_path + "/model"

        file_name = "data"+str(number)+".csv" # "data1.csv"
        # file_path = os.join.path(rootpath, file_name)
        # ImputedData CSV로 저장
        
        ImputedData.to_csv(file_path)

        """

        import csv, os
        from datetime import datetime

        now = datetime.now()

        """
        header = ['name', 'area', 'country_code2', 'country_code3']
        data = [
            ['Albania', 28748, 'AL', 'ALB'],
            ['Algeria', 2381741, 'DZ', 'DZA'],
            ['American Samoa', 199, 'AS', 'ASM'],
            ['Andorra', 468, 'AD', 'AND'],
            ['Angola', 1246700, 'AO', 'AGO']
        ]
       """
        param = request.get_json(force=True)      
        global ImputedData

        curTime = now.strftime('%Y-%m-%d %H:%M:%S')

        no = param['parameter']
        file_name = 'testCsv/test_block'+no+'_'+curTime+'.csv'
        root_path = os.path.dirname(os.path.abspath(__file__)) 
        file_path = os.path.join(root_path, file_name)

        #path = os.getcwd()    
      
        ImputedData.to_csv(file_path)

        result = {"result": file_name}

        return json.dumps(result)
       

