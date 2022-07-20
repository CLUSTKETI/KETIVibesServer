from flask import request
from flask_restx import Resource, Api, Namespace
from flask import render_template, make_response, jsonify

import json, os
import pandas as pd
import sys
sys.path.append("../")
sys.path.append("../..")

DataExploration = Namespace(name = 'DataExploration',  description='Metadata Exploration')
html_headers = {'Context-Type':'text/html'}

@DataExploration.route('/data_table')
class dataSet(Resource):
    def get(self):
        """
        
        DATABASE Name, Measurement Name, Start Time, End Time, Frequency, Nuber of Columns
        """
        from KETIToolMetaManager import ingestion_meta_exploration as ime
            
        exploration_js = ime.get_meta_table()

        return make_response(render_template('dataExploration/data_meta_table.html', json_data_list = exploration_js))

@DataExploration.route('/data_structure')
class test(Resource):
    def get(self):
        return make_response(render_template('dataExploration/data_structure.html'), 200, html_headers)
