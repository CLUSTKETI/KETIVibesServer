from flask import request
from flask_restx import Resource, Namespace, reqparse
from flask import render_template, make_response

DataDomainExploration = Namespace(name = 'DataDomainExploration',  description='DataDomainExploration')
html_headers = {'Context-Type':'text/html'}

from db_model import dbModel
db_client = dbModel.db_client

# 기본 dataExploration 메인 페이지
@DataDomainExploration.route('/')
@DataDomainExploration.doc("Get dataExploration Index page")
class DataDomainExploration_index(Resource):
    @DataDomainExploration.doc("Get dataExploration Index page")
    def get(self):
        """
        Return data domain exploration(clustering) page
        """
        return make_response(render_template('dataExploration/dataDomainExploration.html'), 200, html_headers)  

# post로 입력을 받았을 때, add_argument를 통해 입력 파라미터 설정 가능
prepro_parser = reqparse.RequestParser()
prepro_parser.add_argument('db_name',  type=str, help='database name of influxdb', location='json',required=True)
prepro_parser.add_argument('start_time',  type=str,help='column names of influxdb', location='json',required=True)
prepro_parser.add_argument('nanLimitInfo',  type=str,help='column names of influxdb', location='json',required=True)
prepro_parser.add_argument('duration_day',  type=int,help='column names of influxdb', location='json',required=True)
prepro_parser.add_argument('column_names',  required=True, type=str, location='json')
prepro_parser.add_argument('resampling_rate',  type=str,help='column names of influxdb', location='json',required=True)

@DataDomainExploration.route('/preprocessing')
@DataDomainExploration.doc("Preprocessing a table for clustering")
class DataSet(Resource):
    @DataDomainExploration.doc("Preprocessing a table for clustering")
    @DataDomainExploration.expect(prepro_parser) # 특정 스키마가 들어 올 것을 기대 -> 즉 미리 정의한 객체를 넣는 것?
    def post(self):
        """
        Preprocessing a table for clustering
        
        ## param으로 들어가는 'Input'과 return되는 'ouput' data 예시


        # ex. Input
        ### /clustering과 동일한 param 구조지만, 'ms_name'가 추가되어야 한다(payload 동일)
        ``` json
        {
            'db_name' : 'air_indoor_경로당',
            'start_time' : "2021-02-04 00:00:00",
            'nanLimitInfo' : {'type': 'num', 'ConsecutiveNanLimit': 1, 'totalNaNLimit': 10},
            'duration_day' : 1,
            'column_names' : ['in_ciai'],
            'resampling_rate' : '60',
            'ms_name' : 'ICL1L2000270'
        }
        ```
        
        # ex. Output
        ``` json
        {
            'table': 'ICL1L2000270',
            'data': [94.0, 94.0, 94.0, 94.0, 94.0, 94.0, 92.0, 91.0, 91.0, 91.0, 88.0, 89.0, 79.0, 89.0, 93.0, 95.0, 96.0, 96.0, 97.0, 97.0, 96.0, 96.0, 97.0, 96.0],
            'flag': 1
        }
        ```
        """
        params = request.get_json()
        print("========params===========")
        print(params)
        ms_name, feature_data, flag  = getMSDataQualityCheckTable(db_client,params)
        
      
        return {'table':ms_name,'data':feature_data,'flag':flag} 
        

@DataDomainExploration.doc("Execute Clustering")
@DataDomainExploration.route('/clustering')
class Clustering(Resource):
    @DataDomainExploration.doc("Execute Clustering")
    @DataDomainExploration.expect(prepro_parser) 
    def post(self):
       
        """
        Clustering all tables

        ## param으로 들어가는 'Input'과 return되는 'ouput' data 예시
        
        # ex. Input
        ``` json
        {
            'db_name' : 'air_indoor_경로당',
            'start_time' : "2021-02-04 00:00:00",
            'nanLimitInfo' : {'type': 'num', 'ConsecutiveNanLimit': 1, 'totalNaNLimit': 10},
            'duration_day' : 1,
            'column_names' : ['in_ciai'],
            'resampling_rate' : '60'
        }
        ```
        
        # ex. Output 
        ``` json
        {
            'data':{'ICL1L2000236': '3', 'ICL1L2000237': '5', 'ICL1L2000238': '5', ...(etc)... 'ICL1L2000280': '6', 'ICL1L2000281': '1', 'ICL1L2000283': '3'} 
            'img': figdata(Clustering image)
        }
        ```
        """
        # 현재 som을 강제로 밀어넣지만, User Interface에서 입력 받아 Params로 넘겨줄 수 있도록
        params = request.get_json()
        result, figdata, figdata2 =  clusteringByDomain(dbModel.db_client, params, "som")
        
        print('===clustering===')
        print('result', result)
        return {'data':result, 'img':figdata}


import math
import pandas as pd
from datetime import timedelta
from KETIPreDataSelection.dataRemovebyNaN import clean_feature_data

## Domain Function
def clusteringByDomain(db_client, params, model="som"):
    """
    This is the function to run clustering.
    

    :param db_client: A handle to the class `KETIPreDataIngestion.data_influx.influx_Client.influxClient`
    :type db_client: class:`KETIAppDataServer.db_model.dbModel.db_client`
    :param params: all of parameters which are needed for clustering 
    :type params: dictionary

    :returns: clustering result
    :rtype: dictionary
    
    
    prameter ``param`` example
    docstring::
        {
            'db_name' : 'air_indoor_경로당',
            'start_time' : "2021-02-04 00:00:00",
            'nanLimitInfo' : {'type': 'num', 'ConsecutiveNanLimit': 1, 'totalNaNLimit': 10},
            'duration_day' : 1,
            'column_names' : ['in_ciai'],
            'resampling_rate' : '60'
        }

    return example
    docstring::
        {
            'data':{'ICL1L2000236': '3', 'ICL1L2000237': '5', 'ICL1L2000238': '5', ...(etc)... 'ICL1L2000280': '6', 'ICL1L2000281': '1', 'ICL1L2000283': '3'} 
            'img': figdata(Clustering image)
        }
    
    """
    
    db_name, feature_name, NanInfoForCleanData, feature_list, freq_min, start_time, end_time = getDomainExplorationParameter(params)
    CMS = clean_feature_data.CleanFeatureData(feature_list, freq_min)

    model ="som"
    from KETIPreDataIngestion.data_influx import influx_Module
    dataSet = influx_Module.getAllMSDataSetFromInfluxDB(start_time, end_time, db_client, db_name)
    duration = {"start_time": start_time, "end_time":end_time}
    dataSet, dataSetName, NaNRemovedDataSet, imputedDatasetName, ImputedDataSet  = CMS.getMultipleCleanDataSetsByFeature(dataSet, NanInfoForCleanData, duration)
    feature_dataset= ImputedDataSet[feature_name]
    feature_datasetName = imputedDatasetName[feature_name]
    from KETIAppMachineLearning.Clustering import interface
    result, figdata, figdata2 = interface.clusteringByMethod(feature_dataset, feature_datasetName, model)
    return result, figdata, figdata2

def getMSDataQualityCheckTable(db_client,params):
    """
    This is the function to preprocess each table once.


    :param db_client: A handle to the class `KETIPreDataIngestion.data_influx.influx_Client.influxClient`
    :type db_client: class:`KETIAppDataServer.db_model.dbModel.db_client`
    :param params: preprocessing parameter
    :type params: dictionary

    :returns: preprocessing result
    :rtype: dictionary
    
    
    prameter ``param`` example
    docstring::
        {
            'db_name' : 'air_indoor_경로당',
            'start_time' : "2021-02-04 00:00:00",
            'nanLimitInfo' : {'type': 'num', 'ConsecutiveNanLimit': 1, 'totalNaNLimit': 10},
            'duration_day' : 1,
            'column_names' : ['in_ciai'],
            'resampling_rate' : '60',
            'ms_name' : 'ICL1L2000270'
        }

    return example
    docstring::
        {
            'table': 'ICL1L2000270',
            'data': [94.0, 94.0, 94.0, 94.0, 94.0, 94.0, 92.0, 91.0, 91.0, 91.0, 88.0, 89.0, 79.0, 89.0, 93.0, 95.0, 96.0, 96.0, 97.0, 97.0, 96.0, 96.0, 97.0, 96.0],
            'flag': 1
        }
    
    """
    db_name, feature_name, NanInfoForCleanData, feature_list, freq_min, start_time, end_time = getDomainExplorationParameter(params)
    CMS = clean_feature_data.CleanFeatureData(feature_list, freq_min)
    ms_name = params["ms_name"]

    data = db_client.get_data_by_time(start_time, end_time, db_name, ms_name)
    duration = {"start_time": start_time, "end_time":end_time}
    refinedData, NaNRemovedData, ImputedData, finalFlag = CMS.getOneCleanDataSetByFeature(data, NanInfoForCleanData, duration)
    
    feature_data=[]
    flag = finalFlag[feature_name] # 0:useless data, 1:useful data
    if(flag==0):
        feature_data = list(refinedData[feature_name].replace({math.nan:None}))
    elif(flag==1):
        feature_data = list(ImputedData[feature_name].replace({math.nan:None})) 

    return ms_name, feature_data, flag 

def getDomainExplorationParameter(params):
    #### Parameter Parsing
    """
    Parameter Parsing

    dic 형식으로 들어온 데이터를 원하는 형식에 맞게 변환

    :param params: A handle to the class `KETIPreDataIngestion.data_influx.influx_Client.influxClient`
    :type params: dictionary

    :returns: db_name, feature_name, NanInfoForCleanData, feature_list, freq_min, query_start_time, query_end_time
    :rtype: string, string, dictionary, string, integer, datatine, datetime

    
    Example
        -------
        >>> query_start_time = pd.to_datetime(params["start_time"])
        >>> query_end_time = query_start_time + timedelta(days = duration_day)
        >>> freq_min =  int(params["resampling_rate"])
        >>> etc...

    """
    db_name = params["db_name"]
    feature_list = params["column_names"]
    feature_name = feature_list[0]
    duration_day = params["duration_day"] # 1 or 7
    query_start_time = pd.to_datetime(params["start_time"])
    query_end_time = query_start_time + timedelta(days = duration_day)
    NanInfoForCleanData = params['nanLimitInfo'] # ex) {'type':'num', 'ConsecutiveNanLimit':2, 'totalNaNLimit':5}
    freq_min =  int(params["resampling_rate"])

    #### Parameter Parsing End
    return db_name, feature_name, NanInfoForCleanData, feature_list, freq_min, query_start_time, query_end_time

## Domain Function End