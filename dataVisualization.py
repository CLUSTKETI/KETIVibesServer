from flask import request, url_for
from flask_restx import Resource, Api, Namespace, reqparse
from flask import render_template, make_response, redirect
import sys
sys.path.append("../")
sys.path.append("../..")
import json
import requests

from pprint import pprint
from flask_restx import Api, fields

api = Api()
DataVisualization = Namespace(name = 'DataVisualization',  description='Data Visualization by DB and measurement')
html_headers = {'Context-Type':'text/html'}

from db_model import dbModel
db_client = dbModel.db_client


@DataVisualization.route('/')
class dataVisualization(Resource):
    def get(self):
        
        """
        Show three graph (line, box, correlation) and related inforamtion. 

        # Description
        ### 1. Select DB, Measurement, Day information.
        ### 2. Redirection (/recentDataForVisualByDBMSDays/<string:db_name>/<string:mm_name>/<int:days>)
        ### 3. Show graph and information of Data in web page
        ### * Defalut page: the 1st measurement of 4th DB. 
  
        # Input Arguments
        ### * None

        """

        ## Make Example URL Page
        # 1. Set DB Name
        db_list = dbModel.db_list 
        db_ex = db_list[3]

        # 2. Set MS Name
        ms_list_URL = "http://"+request.host+'/DataIngestion/measurement_list/'+db_ex
        response = requests.get(ms_list_URL)
        result = json.loads(response.json())
        result = result['result']
        ms_ex = result[0]
        # 3. Set Final URL
        finalURL = "http://"+request.host+'/DataVisualization/recentDataForVisualByDBMSDays/'+db_ex+'/'+ms_ex+'/None/None/7'
        return redirect(finalURL)

@DataVisualization.route('/recentDataForVisualByDBMSDays/<string:db_name>/<string:mm_name>/<string:tagKeyName>/<string:tagValueName>/<int:days>')
@DataVisualization.doc(params={'db_name': 'DB Name', 'mm_name': 'measurement name', 'days': 'Data ingestion period (unit: day)'})
class recentDataForVisualByDBMSDays(Resource):
    def get(self, db_name, mm_name, tagKeyName, tagValueName, days):
        """
        Show graph and information based on 1. DB Name, 2, MS Name, and 3. Days.
        
        # Description
        ## This API shows web page with line/box/correlation graph and NaN/duration information.
        Data should be resampled over 1 hour for reducing time delay.

        # Input Example
        ``` json
        {
            "db_name": "air_indoor_경로당",
            "ms_name": "ICL1L2000236",
            "days": 7
        }
        ```
        """
        param = {
            "db_name":db_name, 
            "ms_name":mm_name, 
            "tag_key":tagKeyName,
            "tag_value":tagValueName,
            "days": days
        }
      
        
        DataCorrelationURL = request.host_url +'/DataIngestion/DataCorrelation'
        response = requests.post(DataCorrelationURL, json = param)
        result = json.loads(response.json())       
         
        return make_response(render_template('dataVisualization/partial_data_visual.html', 
        db_name = db_name, mm_name = mm_name, days = days, tag_key = tagKeyName, tag_value = tagValueName,
        result = result), 200, html_headers)


@DataVisualization.route('/ScrollUItest')
class dataVisualization_test(Resource):
    def get(self):
        """
        UI Test Code
        """
        return make_response(render_template('dataVisualization/scroll_test_original.html'))


