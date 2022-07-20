from wsgiref.simple_server import WSGIRequestHandler
from flask import request, session
from flask_restx import Resource, Api, Namespace
from flask import render_template, make_response, redirect
import json
##
import sys
sys.path.append("../")
sys.path.append("../..")

from flask_restx import Api, fields
api = Api()
TestPreprocessing = Namespace(name = 'testPreprocessing',  description='Data Preprocessing package test')
html_headers = {'Context-Type':'text/html'}


@TestPreprocessing.route('/testPreprocessing')
class getTestPreproessing(Resource):
    def get(self):
        
        return make_response(render_template('test/testPreProcessing.html'))  

from KETIPreDataIngestion.KETI_setting import influx_setting_KETI as ins
from KETIPreDataIngestion.data_influx import influx_Client_v2 as influx_Client
DBClient = influx_Client.influxClient(ins.CLUSTDataServer)
@TestPreprocessing.route('/getData')
class getDataWithoutCertainOutlier(Resource):
    @TestPreprocessing.doc("Get Data ")
    
    
    def post(self):
    
        """
        #Test 1
        db_name = 'farm_swine_vibes1'
        ms_name = 'O2'
        num = "2000"
        column_name='O2/value'
        input_data = DBClient.get_datafront_by_num(num, db_name, ms_name)[[column_name]]
        """

        db_name = 'air_indoor_경로당'
        ms_list = DBClient.measurement_list(db_name)
        ms_name = ms_list[0]
        print(ms_name)
        num = "20000"
        input_data = DBClient.get_datafront_by_num(num, db_name, ms_name) 
        """
        db_name = "air_indoor_경로당"
        ms_name = "ICL1L2000234"
        number =20000
        input_data = DBClient.get_dataend_by_num(number, db_name, ms_name)

        """
        print("===input_data===")
        print(input_data)

        return  json.dumps(input_data)

