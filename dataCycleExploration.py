from flask import request
from flask_restx import Resource, Namespace, reqparse
from flask import render_template, make_response
import math
import pandas as pd
from datetime import timedelta
from KETIPreDataSelection.dataRemovebyNaN import clean_feature_data
from KETIPreDataIngestion.dataByCondition import cycle_Module


DataCycleExploration = Namespace(name = 'DataCycleExploration',  description='DataCycleExploration')
html_headers = {'Context-Type':'text/html'}

from db_model import dbModel
db_client = dbModel.db_client

@DataCycleExploration.route('/')
@DataCycleExploration.doc("Get dataCycleExploration Index page")
class DataCycleExploration_index(Resource):
    @DataCycleExploration.doc("Get dataCycleExploration Index page")
    def get(self):
        """
        Return data cycle exploration(clustering) page
        """
        return make_response(render_template('dataExploration/dataCycleExploration.html'), 200, html_headers) 


prepro_parser = reqparse.RequestParser()
prepro_parser.add_argument('db_name',  type=str, help='database name of influxdb', location='json',required=True)
prepro_parser.add_argument('ms_name',  type=str, help='measurement name of influxdb', location='json',required=True)
prepro_parser.add_argument('start_time',  type=str,help='start time of data', location='json',required=True)
prepro_parser.add_argument('end_time',  type=str,help='end time of data', location='json',required=True)
prepro_parser.add_argument('nanLimitInfo',  type=str,help='column names of influxdb', location='json',required=True)
prepro_parser.add_argument('cycle',  type=str,help='data cycle of measurement', location='json',required=True)
prepro_parser.add_argument('cycle_times',  type=int,help='column names of influxdb', location='json',required=True)
prepro_parser.add_argument('column_names',  required=True, help='column names of influxdb', type=str, location='json')
prepro_parser.add_argument('resampling_rate',  type=str,help='column names of influxdb', location='json',required=True)

@DataCycleExploration.route('/preprocessing')
@DataCycleExploration.doc("Preprocessing a table for clustering")
class CycleDataSet(Resource):
    @DataCycleExploration.doc("Preprocessing a table for clustering")
    @DataCycleExploration.expect(prepro_parser)
    def post(get):
        """
        Preprocessing a slicing dataframe  for clustering

        # ex. Input
        ### /clustering과 동일한 param 구조지만, 'ms_name'가 추가되어야 한다(payload 동일)
        ``` json
        {
            'db_name' : 'air_indoor_경로당',
            'ms_name' : 'ICL1L2000235',
            'start_time' : "2021-02-04 00:00:00",
            'end_time' : "2021-03-30 00:00:00",
            'nanLimitInfo' : {'type': 'num', 'ConsecutiveNanLimit': 1, 'totalNaNLimit': 10},
            'cycle' : 'Day',
            'cycle_times' : '1',
            'column_names' : ['in_ciai'],
            'resampling_rate' : '60'
        }
        ```

        # ex. Output
        ``` json
        cycle_info = 
        { 1 : {
                'time_index': '2021-02-05 00:00:00',
                'data': [94.0, 94.0, 94.0, 94.0, 94.0, 94.0, 92.0, 91.0, 91.0, 91.0, 88.0, 89.0, 79.0, 89.0, 93.0, 95.0, 96.0, 96.0, 97.0, 97.0, 96.0, 96.0, 97.0, 96.0],
                'flag': 1
                },
          2 : {
                'time_index': '2021-02-06 00:00:00',
                'data': [94.0, 94.0, 94.0, 94.0, 94.0, 94.0, 92.0, 91.0, 91.0, 91.0, 88.0, 89.0, 79.0, 89.0, 93.0, 95.0, 96.0, 96.0, 97.0, 97.0, 96.0, 96.0, 97.0, 96.0],
                'flag': 1
                },
            ... 
        }
        ```
        """
        params = request.get_json()
       
        #db_name, ms_name, feature_name, NanInfoForCleanData, feature_list, freq_min, start_time, end_time, feature_cycle, feature_cycle_times = getDatawithParam(db_client,params)
        NanInfoForCleanData, feature_list, freq_min, feature_cycle, feature_cycle_times, start_time, end_time, db_name, ms_name, tag_key, tag_value = getDatawithParam(db_client,params)
        query_data = db_client.get_data_by_time(start_time, end_time, db_name, ms_name, tag_key, tag_value)
        cycle_info = getCycleDataQualityCheckTable(query_data,feature_cycle,feature_cycle_times, feature_list, freq_min, NanInfoForCleanData)
        return cycle_info



@DataCycleExploration.doc("Execute Clustering")
@DataCycleExploration.route('/clustering')
class CycleClustering(Resource):
    @DataCycleExploration.doc("Execute Clustering")
    @DataCycleExploration.expect(prepro_parser) 
    def post(self):
        """
        Clustering all tables

        ## param으로 들어가는 'Input'과 return되는 'ouput' data 예시
        
        # ex. Input
        ``` json
        {
            'db_name' : 'air_indoor_경로당',
            'ms_name' : 'ICL1L2000235',
            'start_time' : "2021-02-04 00:00:00",
            'end_time' : "2021-03-30 00:00:00",
            'nanLimitInfo' : {'type': 'num', 'ConsecutiveNanLimit': 1, 'totalNaNLimit': 10},
            'cycle' : 'Day',
            'cycle_times' : '1',
            'column_names' : ['in_ciai'],
            'resampling_rate' : '60'
        }
        ```
        
        # ex. Output 
        ``` json
        {
            'data':{'2021-02-05 00:00:00': '3', '2021-02-06 00:00:00': '5', '2021-02-07 00:00:00': '5', ...(etc)... '2021-03-28 00:00:00': '6', '2021-03-29 00:00:00': '1', '2021-03-30 00:00:00': '3'} 
            'img': figdata(Clustering image)
        }
        ```
        """
        params = request.get_json()

        NanInfoForCleanData, feature_list, freq_min, feature_cycle, feature_cycle_times, start_time, end_time, db_name, ms_name, tag_key, tag_value = getDatawithParam(db_client,params)
        query_data = db_client.get_data_by_time(start_time, end_time, db_name, ms_name, tag_key, tag_value)
        result, figdata, figdata2=  clusteringByCycle(query_data, feature_cycle, feature_cycle_times, feature_list, freq_min, NanInfoForCleanData , model="som")

        return {'data':result, 'img':figdata}


## Cycle Function
def clusteringByCycle(query_data, feature_cycle, feature_cycle_times, feature_list, freq_min, NanInfoForCleanData , model="som"):
    # 아래 함수들과 짜놓은 함수들을 이용하여 Cycle 단위의 클러스터링이 되도록 모듈화
    
    feature_name = feature_list[0]
    from KETIPreDataIngestion.dataByCondition import cycle_Module
    dataSet = cycle_Module.getCycleSelectDataSet(query_data, feature_cycle, feature_cycle_times, str(freq_min)+'min' )
    CMS = clean_feature_data.CleanFeatureData(feature_list, freq_min)
    dataSet, dataSetName, NaNRemovedDataSet, imputedDatasetName, ImputedDataSet  = CMS.getMultipleCleanDataSetsByFeature(dataSet, NanInfoForCleanData)
    feature_dataset= ImputedDataSet[feature_name]
    feature_datasetName = imputedDatasetName[feature_name]

    model ="som"
    from KETIAppMachineLearning.Clustering import interface
    result, figdata, figdata2 = interface.clusteringByMethod(feature_dataset, feature_datasetName, model)

    return result, figdata, figdata2


# 실행 확인 완료
def getCycleDataQualityCheckTable(query_data,feature_cycle,feature_cycle_times, feature_list, freq_min, NanInfoForCleanData):
    """
    """
    feature_name = feature_list[0]
    data = cycle_Module.getCycleselectDataFrame(query_data, feature_cycle, feature_cycle_times, str(freq_min)+'min' )
    CMS = clean_feature_data.CleanFeatureData(feature_list, freq_min)

    cycle_info = {}
    for i in range(len(data)): # feature_name 뭔지 정확히 확인 후, 수정 필요

        refinedData, NaNRemovedData, ImputedData, finalFlag = CMS.getOneCleanDataSetByFeature(data[i], NanInfoForCleanData)
        index_name = str(data[i].index[0].strftime('%Y-%m-%d %H:%M:%S'))

        feature_data=[]
        flag = finalFlag[feature_name] # 0:useless data, 1:useful data
        if(flag==0):
            feature_data = list(refinedData[feature_name].replace({math.nan:None}))
        elif(flag==1):
            feature_data = list(ImputedData[feature_name].replace({math.nan:None}))
        
        cycle_info[i] = {'time_index':index_name,'data':feature_data,'flag':flag}

    return cycle_info
    

def getDatawithParam(db_client, params):
    """
    Parameter Parsing

    dic 형식으로 들어온 데이터를 원하는 형식에 맞게 변환

    :param params: A handle to the class `KETIPreDataIngestion.data_influx.influx_Client.influxClient`
    :type params: dictionary

    :returns: db_name, ms_name, feature_name, NanInfoForCleanData, feature_list, freq_min, start_time, end_time, feature_cycle, feature_cycle_times
    :rtype: string, string, string, dictionary, string, integer, datatine, datetime, string, integer
    """

    db_name = params["db_name"]
    ms_name = params["ms_name"]
    tag_key = params["tag_key"]
    tag_value = params["tag_value"]
    
    if tag_key =="None":
        tag_key=None
        tag_value=None
    
    feature_list = params["column_names"]
    start_time = pd.to_datetime(params["start_time"])
    end_time = pd.to_datetime(params["end_time"])
    NanInfoForCleanData = params['nanLimitInfo'] # ex) {'type':'num', 'ConsecutiveNanLimit':2, 'totalNaNLimit':5}
    freq_min =  int(params["resampling_rate"])
    feature_cycle = params["cycle"]
    feature_cycle_times = params["cycle_times"]

    #### Parameter Parsing End
    return NanInfoForCleanData, feature_list, freq_min, feature_cycle, feature_cycle_times, start_time, end_time, db_name, ms_name, tag_key, tag_value

## Cycle Function End