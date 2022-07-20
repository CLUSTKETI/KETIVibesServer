from flask import request
from flask_restx import Resource, Namespace, reqparse
from flask import render_template, make_response
import numpy as np
import json
import simplejson
import requests
DataStatistics = Namespace(name = 'DataStatistics',  description='dataStatistics')
html_headers = {'Context-Type':'text/html'}

from KETIAppDataServer.data_manager import echart
from db_model import dbModel
db_client = dbModel.db_client

DBMSParser = reqparse.RequestParser()
DBMSParser.add_argument('db_name',  type=str, help='database name of influxdb', location='json',required=True)
DBMSParser.add_argument('ms_name',  type=str,help='ms names of DB', location='json',required=True)

"""
JW Coding
"""
DBMSFeatureDaysParser = DBMSParser
DBMSFeatureDaysParser.add_argument('feature',  type=str, help='feature name', location='json',required=True)
DBMSFeatureDaysParser.add_argument('days',  type=int, help='days of ingeted data', location='json',required=True)

from KETIPreDataTransformation.general_transformation import basicTransform
@DataStatistics.route('/CorrelationValueByfeatures/InfluxDB')
#for Get @DataStatistics.doc(params={'db_name': 'DB Name', 'ms_name': 'measurement name',  'feature':'feature name','days': 'Data ingestion period (unit: day)'})
class CorrelationValueByfeatures(Resource):
    @DataStatistics.doc("Get Correlation Values by db/MS/Feature/Days")
    @DataStatistics.expect(DBMSFeatureDaysParser) 
    def post(self):
        """
        This API supports data correlation value list for a specific feature.
        
        # Description
        
        Make correlation value based on the specific feature data. 
        ### 1. Ingest Data (by DB, measurement, day information)
        ### 2. Make pearson correlation values.
        ### 3. Filter values by featue name.
        ### 4. Sort by value size.

        # Input
        ``` json
        {
            "db_name": "air_indoor_경로당",
            "ms_name": "ICL1L2000236",
            "feature": "in_pm10",
            "days": 7
        }
        ```
        # Output 
        ``` json
        {
            "indi_corr": Array result of correlation matrix.,
            "indi_corr_index": Index values of correlation matrix.,
            "feature": feature name
        }
        ```
        """
        json_result = request.json
        db_name = json_result['db_name']
        ms_name = json_result['ms_name']
        feature = json_result['feature']
        days = json_result['days']
        print(days)

        last_time = db_client.get_last_time(db_name, ms_name)
        rawData = db_client.get_data_by_days(last_time, str(days)+"d", db_name, ms_name).resample('1H').mean()
        scaledData = basicTransform.getRobustScaledDF(rawData)
        data = scaledData
        indi_corr = (data.corrwith(data[feature]).sort_values()).drop(feature)
        
        result={'indi_corr':list(round(indi_corr, 2)),
                'indi_corr_index' :list(indi_corr.index),
                'feature': feature}
        print(result)
        #result = simplejson.dumps(result, ignore_nan=True)
        return json.dumps(result)

# TODO Not Avaliable
@DataStatistics.route('/CorrelationValue/Data')
class CorrelationValueByfeatures(Resource):
    @DataStatistics.doc("Get Correlation Values by Data")
    def post(self):
        """
        This API supports data correlation result for input data

        # Input
        ``` json 
        {
            "data": 
        }
        """
        json_result = request.json
        print(json_result)
        data = json_result['data']
        
        corr_matrix = basicTransform.get_corrMatrix(data) # data = DataFrame, Not Available
        result ={"corr_matrix":corr_matrix}
        print(result)

        return json.dumps(result)



"""
JW Coding End
"""
# /minMax/InfluxDB (DB, MS)
# /minMax/Data
# /histogram/InfluxDB(DB, MS)
# /histogram/Data

"""
JS Coding
"""
DBMSParser2 = reqparse.RequestParser()
DBMSParser2.add_argument('db_name',  type=str, help='database name of influxdb', location='json',required=True)
DBMSParser2.add_argument('ms_name',  type=str,help='ms names of DB', location='json',required=True)
DBMSParser2.add_argument('number',  type=int, help='number of ingested data', location='json',required=True)

@DataStatistics.route('/histogram/InfluxDB')
class DBMSHistorgram(Resource):
    @DataStatistics.doc("Get histogram result by column based on DB and MS name")
    @DataStatistics.expect(DBMSParser2) 
    def post(self):
        """
        Get histogram result by column based on DB and MS name
        
        # Input
        ``` json
        {
            "db_name" : "air_indoor_초등학교",
            "ms_name" : "ICW0W2000021",
            "number" : 10
        }
        ```
        
        # Output 
        ``` json
        {
            "result" : 
            {
                'column_name1':{"value":[histogram result values], "bins":[histogram bins]},
                'column_name2':{"value":[histogram result values], "bins":[histogram bins]},
                'column_name3':{"value":[histogram result values], "bins":[histogram bins]}
            }
        }
        ```
        """
        json_result = request.json
        db_name = json_result['db_name']
        ms_name = json_result['ms_name']
        number = json_result['number']
        histogram_result = {}
        
        global data_dict
        url = "http://localhost:9008/DataIngestion/dataIngestionByNum/{}/{}/{}".format(db_name, ms_name, number) # url 주소 변경 요망
        response = requests.get(url, headers={'accept': 'application/json'})
        data_dict = json.loads(response.json())
        
        for column in data_dict["value"]:
            values = {}
            value = [x for x in data_dict["value"][column] if x != None]   
            if value:
                if isinstance(value[0], (int, float)):
                    histogram_value = np.histogram(np.array(value))
                    values["value"] = [float(x) for x in histogram_value[0]]
                    values["bins"] = [float(x) for x in histogram_value[1]]
                    histogram_result[column] = values
            
        return json.dumps({"result":histogram_result})

DBMSParser3 = reqparse.RequestParser()
DBMSParser3.add_argument('db_name',  type=str, help='database name of influxdb', location='json',required=True)
DBMSParser3.add_argument('ms_name',  type=str, help='ms names of DB', location='json',required=True)
DBMSParser3.add_argument('InfluxDB Connect',  type=bool, help='Get dataset via influxdb connection. True or False', location='json',required=True)
@DataStatistics.route('/minMax/InfluxDB')
class DBMSMinMax(Resource):
    @DataStatistics.doc("Get min&max result by column based on DB and MS name")
    @DataStatistics.expect(DBMSParser3) 
    def post(self):
        """
        Get min&max result by column based on DB and MS name
        If 'InfluxDB Connect' is True, then 10000 datasets are fetched.
        
        # Input
        ``` json
        {
            "db_name" : "air_indoor_초등학교",
            "ms_name" : "ICW0W2000021",
            "InfluxDB Connect" : false
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
        global data_dict

        json_result = request.json
        influxdb_connect = json_result['InfluxDB Connect']
        
        if influxdb_connect:
            db_name = json_result['db_name']
            ms_name = json_result['ms_name']    
            url = "http://localhost:9008/DataIngestion/dataIngestionByNum/{}/{}/{}".format(db_name, ms_name, 10000) # url 주소 변경 요망
            response = requests.get(url, headers={'accept': 'application/json'})
            data_dict = json.loads(response.json())
            
        minmax_result = {}
        for column in data_dict["value"]:
            value = [x for x in data_dict["value"][column] if x != None]
            values = {"min":"There is no value", "max":"There is no value"}
            if len(value) != 0:
                values["min"] = min(value)
                values["max"] = max(value)
            minmax_result[column] = values
        
        return json.dumps({"result":minmax_result})

"""
JS Coding End
"""