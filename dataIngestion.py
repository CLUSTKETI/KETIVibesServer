from flask import request, session
from flask_restx import Resource, Api, Namespace, reqparse
from flask import render_template, make_response
##
import sys
sys.path.append("../")
sys.path.append("../..")
import json
import pandas as pd
from KETIPreDataTransformation.general_transformation import dataScaler
##
DataIngestion = Namespace(name = 'DataIngestion',  description='Code For Data Prediction')
html_headers = {'Context-Type':'text/html'}

from KETIPreDataTransformation.general_transformation import basicTransform
from KETIPrePartialDataPreprocessing.data_preprocessing import DataPreprocessing
from KETIPreDataIngestion.dataByCondition import cycle_Module
from KETIAppDataServer.data_manager import echart

from db_model import dbModel
db_client = dbModel.db_client


############ DB, MS, Feature List Start
# from influxdb import InfluxDBClient, DataFrameClient

@DataIngestion.route('/db_list')
class dbList(Resource):
    def get(self):
        """
        Get all database list
                
        # Output Example
        ``` json
        {
            "result": ["traffic_seoul_bus", "farm_swine_vibes1", "air_indoor_경로당"]
        }
        """
        
        db_list = dbModel.db_list
        db_list.sort()
        result = {"result":db_list}
        return json.dumps(result)


@DataIngestion.route('/measurement_list/<string:db_name>')
@DataIngestion.doc(params={'db_name': 'influx db_name'})
class measurementList(Resource):
    @DataIngestion.doc("return measurement list of a database")
    def get(self, db_name):
        """
        ### return measurement list of a database
        
        # Input Example
        ```json
        {
            "db_name" : "air_indoor_경로당"
        }
        ```
        
        # Output Example
        ``` json
        {
            "result": ["ICL1L2000236", "ICL1L2000237", "ICL1L2000238"]
        }
        """
        ms_list = db_client.measurement_list(db_name)
        ms_list.sort()
        return json.dumps({"result": ms_list})
        
@DataIngestion.route('/featureList/<string:db_name>/<string:ms_name>')
@DataIngestion.doc(params={'db_name': 'influx DB Name', 'ms_name': 'influx MS Name'})
class featureList(Resource):
    @DataIngestion.doc("return feature list based on input MS/DB Name ")
    def get(self, db_name, ms_name):
        """
        return feature list based on input MS/DB Name

        ## Get feature(field) list of specific measurement of database
        # Input Example
        ```json
        {
            "db_name" : "air_indoor_초등학교",
            "ms_name" : "ICW0W2000021"
        }
        ```
        
        # Output Example
        ``` json
        {
            "result":["in_ciai", "in_cici", "in_cici_co2"]
        }

        """
        feature_list = db_client.get_fieldList(db_name, ms_name)
        feature_list.sort()
        result = {'result': feature_list}
        return json.dumps(result)


DBMSParser = reqparse.RequestParser()
DBMSParser.add_argument('db_name',  type=str, help='database name of influxdb', location='json',required=True)
DBMSParser.add_argument('ms_name',  type=str,help='ms names of DB', location='json',required=True)
@DataIngestion.route('/tagList')
class tagList(Resource):
    @DataIngestion.doc("Get tagList")
    @DataIngestion.expect(DBMSParser) 
    def post(self):
        """
        # Input Example
        ``` json
        {
            "db_name" : "finance_korean_stock",
            "ms_name" : "stock"
        }
        ```

        # Output Example
        ``` json
        {
            "result" : ['company', 'country', 'exchange', 'industry', 'ticker']
        }
        ```
        """
        json_result = request.get_json(force=True)        
        db_name = json_result['db_name']
        ms_name = json_result['ms_name']
        tagList = db_client.get_tagList(db_name, ms_name)
        result = {'result': tagList}

        return json.dumps(result)

DBMSTagKeyParser = reqparse.RequestParser()
DBMSTagKeyParser.add_argument('db_name',  type=str, help='database name of influxdb', location='json',required=True)
DBMSTagKeyParser.add_argument('ms_name',  type=str,help='ms names of DB', location='json',required=True)
DBMSTagKeyParser.add_argument('tag_key',  type=str,help='tagkey Name', location='json',required=True)
@DataIngestion.route('/distinctTagValue')
class distinctTagValue(Resource):
    @DataIngestion.doc("Get distnctTagValue")
    @DataIngestion.expect(DBMSTagKeyParser) 
    def post(self):
        """
        # Input Example
        ``` json
        {
            "db_name" : "finance_korean_stock",
            "ms_name" : "stock",
            "tag_key" : "company"
        }
        ```

        # Output Example
        ``` json
        {
            "result" : ['AJ네트웍스','ASML 홀딩 NV ADR','AT&T 5.625% 글로벌 노트', 'AT&T Inc',......]
        }
        ```
        """
        json_result = request.get_json(force=True)    
        
        db_name = json_result['db_name']
        ms_name = json_result['ms_name']
        tag_key = json_result['tag_key']
        distinctTagValue = db_client.get_TagValue(db_name, ms_name, tag_key)
        result = {'result': distinctTagValue}

        return json.dumps(result)
        #return json.dumps(result)#, ensure_ascii=False)

############ DB, MS, Feature List End

############ Dataset API Start
@DataIngestion.route('/dataIngestionByNum/<string:db_name>/<string:ms_name>/<string:number>')
@DataIngestion.doc(params={'db_name': 'influx DB Name', 'ms_name':'Measurement Name', 'number':'Number of Data'})
class dataIngestionByNumber(Resource):
    @DataIngestion.doc("returns dataframes as many as the specified number of data from the latest time")
    def get(self, db_name, ms_name, number):
        """
        returns dataframes as many as the specified number of data from the latest time

        Get Dataframe extracted from the latest time as many as input number from specific data
        At this time, data is specified as input db/ms
        
        # Input Example
        ```json
        db_name : air_indoor_초등학교
        ms_name : ICW0W2000021
        number : 100
        ```
        
        # Output Example
        ``` json
        {
            "value" : { "column_name1":[value1, value2, value3],
                        "column_name2":[value4, value5, value6] }
            "index" : : [index1, index2, index3]
        }
        ```
        """
        result={}
        # data read
        dataframe_by_num = db_client.get_dataend_by_num(number, db_name, ms_name)
        dataframe_by_num = dataframe_by_num[dataScaler.get_scalable_columns(dataframe_by_num)]

        # data preprocessing
        outlier_param = {'certainErrorToNaN': {'flag': True}, 'unCertainErrorToNaN': {'flag': False}} # data_type을 계속 air로 해도 될까요..?
        datawithMoreCertainNaN, datawithMoreUnCertainNaN = DataPreprocessing().get_errorToNaNData(dataframe_by_num, outlier_param)
        
        # transform json data
        result = echart.getEChartFormatResult(datawithMoreCertainNaN)
        
        return json.dumps(result)


@DataIngestion.route('/dataIngestionBystartEndtime/<string:db_name>/<string:ms_name>/<string:start_time>/<string:end_time>')
@DataIngestion.doc(params={'db_name': 'influx DB Name', 'ms_name':'Measurement Name', 'start_time':'Start time', 'end_time':'End time'}) 
class dataIngestionByDuration(Resource):
    @DataIngestion.doc("Get data of the specific measurement based on `start-end duration`")
    def get(self, db_name, ms_name, start_time, end_time):
        """
        Get data of the specific measurement based on `start-end duration`
        At this time, data is specified as input db/ms
        
        # Input Example
        ```json
        {
            "db_name" : "air_indoor_경로당",
            "ms_name" : "ICL1L2000236",
            "start_time": "2021-02-03 17:18:00",
            "end_time":"2021-02-04 17:18:00", 
        }
        ```
        
        # Output Example
        ``` json
        {
            "value" : { "column_name1":[value1, value2, value3],
                        "column_name2":[value4, value5, value6] }
            "index" : : [index1, index2, index3]
        }
        ```
        """
        result = {}
        start_time = pd.to_datetime(start_time)
        end_time = pd.to_datetime(end_time)

        dataframe_by_duration = db_client.get_data_by_time(start_time, end_time, db_name, ms_name)
        dataframe_by_duration = dataframe_by_duration[dataScaler.get_scalable_columns(dataframe_by_duration)]

        outlier_param = {'certainErrorToNaN': {'flag': True}, 'unCertainErrorToNaN': {'flag': False},'data_type': 'air'}
        datawithMoreCertainNaN, datawithMoreUnCertainNaN = DataPreprocessing().get_errorToNaNData(dataframe_by_duration, outlier_param)
    
        result = echart.getEChartFormatResult(datawithMoreCertainNaN)
        
        return json.dumps(result)


DBMSTagKeyValueParser = reqparse.RequestParser()
DBMSTagKeyValueParser.add_argument('db_name',  type=str, help='database name of influxdb', location='json',required=True)
DBMSTagKeyValueParser.add_argument('ms_name',  type=str,help='ms names of DB', location='json',required=True)
DBMSTagKeyValueParser.add_argument('tag_key',  type=str,help='tagkey Name', location='json',required=True)
DBMSTagKeyValueParser.add_argument('tag_value',  type=str,help='tag_value', location='json',required=True)
DBMSTagKeyValueParser.add_argument('days',  type=int, help='days of ingeted data', location='json',required=True)
@DataIngestion.route('/DataCorrelation')
class DataCorrelation2(Resource):
    @DataIngestion.doc("Get Data And Correlation Values by db/MS/Feature/Days/TagKey/TagValue")
    @DataIngestion.expect(DBMSTagKeyValueParser) 
    def post(self):
        """
        # Input Example
        ``` json
        {
            "db_name" : "finance_korean_stock",
            "ms_name" : "stock", 
            "tag_key" : "company", # or "None"
            "tag_value" : "BGF리테일", # or "None"
            "days": 7
        }
        ```
        # Output Example
        ``` json
        {
            "data" : data_json,
            "data_index" : data_index_array, 
            "data_scaled" : data_scaled_json, 
            "corr_matrix" : corr_matrix_array
        }
        ```
        """
        json_result = request.get_json(force=True)  
        db_name = json_result['db_name']
        ms_name = json_result['ms_name']
        #ms_name = json_result['ms_name']
        tag_key = json_result['tag_key']
        tag_value = json_result['tag_value']
        days = json_result['days']


        #### Get Pure Data    
        last_time ={} #??? 
        last_time = db_client.get_last_time(db_name, ms_name)

        
        if tag_key =="None":
            rawData = db_client.get_data_by_days(last_time, days, db_name, ms_name)
        else:
            rawData = db_client.get_data_by_days(last_time, days, db_name, ms_name, tag_key, tag_value)
        

        rawData = rawData[dataScaler.get_scalable_columns(rawData)]

        def resamplingOver1Hour(data):
            # This function change data with low description frequency over 1 hour.
            if len(data)>3:
                from datetime import timedelta
                freq = data.index[-1]-data.index[-2]
                # Data should be resampled over 1 hour
                resample_freq = timedelta(hours=1)
                if freq < resample_freq:
                    #print(freq, resample_freq)
                    data = data.resample(resample_freq).mean()
            return data
        
        
        visualData = resamplingOver1Hour(rawData)
        data_partial_scale = basicTransform.getRobustScaledDF(visualData)
        corr_matrix = basicTransform.get_corrMatrix(data_partial_scale)

        json_data={}
        data_index={} 
        json_data_scaled ={}
        if len(visualData) > 0:
            from KETIAppDataServer.visual_manager import DF_manager
            json_data, data_index = DF_manager.get_jsonDF(visualData)
            json_data_scaled, data_index = DF_manager.get_jsonDF(data_partial_scale)
        # getEChartFormatResult (E Chart 로 변경시 참고할 것)
        result ={"data":json_data,"data_index":data_index, "data_scaled":json_data_scaled, 'corr_matrix':corr_matrix}
        return json.dumps(result)


############ Dataset API End

########### Frequency Start
@DataIngestion.route('/featureListforFirstMS/<string:db_name>')
@DataIngestion.doc(params={'db_name': 'influx DB Name'})
class featureListforFirstMS(Resource):
    @DataIngestion.doc("return feature list of the first ms of the input dbName ")
    def get(self, db_name):
        """
        return feature list of the first ms of the input dbName

        ## Get feature(field) list of the first measurement, database
        # Input Example
        ```json
        {
            "db_name" : "air_indoor_초등학교"
        }
        ```
        
        # Output Example
        ``` json
        {
            "result":["in_ciai", "in_cici", "in_cici_co2"]
        }

        """
        ms_list = db_client.measurement_list(db_name)
        ms_name = ms_list[0]
        feature_list = db_client.get_fieldList(db_name, ms_name)
        result = {'result': feature_list}
        return json.dumps(result)


@DataIngestion.route('/frequency/<string:db_name>/<string:ms_name>')
@DataIngestion.doc(params={'db_name': 'influx DB Name', 'ms_name': 'influx MS Name'})
class getFreq(Resource):
    @DataIngestion.doc("return frequency based on input MS/DB Name ")
    def get(self, db_name, ms_name):
        """
        return frequency based on input MS/DB Name

        ## Get frequency of specific measurement of database
        # Input Example
        ```json
        {
            "db_name" : "air_indoor_초등학교",
            "ms_name" : "ICW0W2000021"
        }
        ```
        
        # Output Example
        ``` json
        {
            "result": "0 days 00:01:00"
        }

        """
        result = db_client.get_freq(db_name,ms_name)
        result = {"result":result}
        return json.dumps(result)


@DataIngestion.route('/frequencyForFirstMS/<string:db_name>')
@DataIngestion.doc(params={'db_name': 'influx DB Name'})
class getFreqFirst(Resource):
    @DataIngestion.doc("return frequency of the first ms of the specific input db name")
    def get(self, db_name):
        """
        return frequency of the first ms of the specific input db name

        ## Get frequency of the first measurement of the specific database
        # Input Example
        ```json
        {
            "db_name" : "air_indoor_초등학교"
        }
        ```
        
        # Output Example
        ``` json
        {
            "result": "0 days 00:01:00"
        }

        """
        ms_list = db_client.measurement_list(db_name)
 
        ms_name = ms_list[0]
        freq = db_client.get_freq(db_name, ms_name)
        result = {"result":freq}
        return json.dumps(result)

########### Frequency End

###########  Start/End Time Start
@DataIngestion.route('/startTime/<string:db_name>/<string:ms_name>')
@DataIngestion.doc(params={'db_name': 'influx DB Name'})
class startTimeForMS(Resource):
    @DataIngestion.doc("return start time index of the specific input db/MS name")
    def get(self, db_name, ms_name):
        """
        return start time index of the specific input db/MS name

        ## Get start time index of the specific measurement of database
        # Input Example
        ```json
        {
            "db_name" : "air_indoor_초등학교",
            "ms_name" : "ICW0W2000021"
        }
        ```
        
        # Output Example
        ``` json
        {
            "result": "2020-03-03 10:23:00"
        }
        
        """
        first_time = db_client.get_first_time(db_name,ms_name)
        first_time = str(first_time.replace(tzinfo=None))
        result = {"result":first_time}
        return json.dumps(result)
@DataIngestion.route('/startTimeForFirstMS/<string:db_name>')
@DataIngestion.doc(params={'db_name': 'influx DB Name'})
class startTimeForFirstMS(Resource):
    @DataIngestion.doc("return start time index of the first ms of the specific input db name")
    def get(self, db_name):
        """
        return start time index of the first ms of the specific input db name

        ## Get start time index of the first measurement of the specific database
        # Input Example
        ```json
        {
            "db_name" : "air_indoor_초등학교"
        }
        ```
        
        # Output Example
        ``` json
        {
            "result": "2020-03-03 10:23:00"
        }
        
        """
        ms_list = db_client.measurement_list(db_name)
        ms_name = ms_list[0]
        first_time = db_client.get_first_time(db_name,ms_name)
        first_time = str(first_time.replace(tzinfo=None))
        result = {"result":first_time}

        return json.dumps(result)


@DataIngestion.route('/lastTime/<string:db_name>/<string:ms_name>')
@DataIngestion.doc(params={'db_name': 'influx DB Name', 'ms_name': 'ms_name'})
class lastTimeForMS(Resource):
    @DataIngestion.doc("return last time index of the specific input db/MS name")
    def get(self, db_name, ms_name):
        """
        return last time index of the specific input db/MS name

        ## Get last time index of the specific measurement of database
        # Input Example
        ```json
        {
            "db_name" : "air_indoor_초등학교",
            "ms_name" : "ICW0W2000021"
        }
        ```
        
        # Output Example
        ``` json
        {
            "result": "2021-08-12 12:11:00"
        }
        
        """
        last_time = db_client.get_last_time(db_name,ms_name)
        last_time = str(last_time.replace(tzinfo=None))
        result = {"result":last_time}
        return json.dumps(result)

@DataIngestion.route('/lastTimeForFirstMS/<string:db_name>')
@DataIngestion.doc(params={'db_name': 'influx DB Name'})
class lastTimeForFirstMS(Resource):
    @DataIngestion.doc("return last time index of the first ms of the specific input db name")
    def get(self, db_name):
        """
        return last time index of the first ms of the specific input db name

        ## Get last time index of the first measurement of the specific database
        # Input Example
        ```json
        {
            "db_name" : "air_indoor_초등학교"
        }
        ```
        
        # Output Example
        ``` json
        {
            "result": "2021-08-12 12:11:00"
        }

        """
        ms_list = db_client.measurement_list(db_name)
        ms_name = ms_list[0]
        last_time = db_client.get_last_time(db_name,ms_name)
        print(last_time)
        last_time = str(last_time.replace(tzinfo=None))
        print(last_time)
        result = {"result":last_time}
        return json.dumps(result)

###########  Start/End Time End

###########  DataSet for View Start
import requests
@DataIngestion.route('/allDBMSSetInfo')
class allDBMSSetInfo(Resource):
    @DataIngestion.doc("return data info list of multiple data_item including Source, DB, MS, and additional information")
    def get(self):
        """
        return data info list of multiple data_item including Source, DB, MS, and additional information

        ## Get data info list of multiple data_item
        
        """
        data_list={"result":[]}
        db_list = dbModel.db_list     
        for db_name in db_list:
            ms_list = db_client.measurement_list_only_start_end(db_name)
            if len(ms_list)>0 :
                for ms_name in ms_list:
                    data_item ={"Source":"CLUST", "DB":db_name, "MS":ms_name, "etc":"http://a"}
                    data_list["result"].append(data_item)
        #result = {"result":data_list}
        return json.dumps(data_list)

@DataIngestion.route('/allDBMSSetInfoByDictType')
class allDBMSSetInfoByDictType(Resource):
    @DataIngestion.doc("return allDBMSSetInfo for graph")
    def get(self):
        """
        return allDBMSSetInfo for graph

        ## Get allDBMSSetInfo for graph
        
        """
        data_list={}
        db_list = dbModel.db_list     
        for db_name in db_list:
            domain = db_name.split("_")[0]
            ms_list = db_client.measurement_list(db_name)
            if len(ms_list)>0 :
                if domain in data_list.keys():
                    data_list[domain][db_name]=ms_list
                else:
                    data_list[domain]={}
                    data_list[domain][db_name]=ms_list
        result = {"result":data_list}
        return json.dumps(result)

