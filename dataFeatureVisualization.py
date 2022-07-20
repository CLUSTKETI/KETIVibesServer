from flask import request, url_for
from flask_restx import Resource, Api, Namespace
from flask import render_template, make_response, redirect
##
import sys
sys.path.append("../")
sys.path.append("../..")

import requests
from KETIPreDataTransformation.general_transformation import basicTransform
from KETIToolMetaManager.metaDataManager import collector
import simplejson
from pprint import pprint

from flask_restx import Api, fields
api = Api()

DataFeatureVisualization = Namespace(name = 'DataFeatureVisualization',  description='Data Feature Visualization by DB, measurement, column')
html_headers = {'Context-Type':'text/html'}

from db_model import dbModel
db_client = dbModel.db_client

@DataFeatureVisualization.route('/features')
class dataVisualization_features_basic(Resource):
    def get(self):
        """
        This API just make html response showing feature Data information
        
        # Description
        HTML template has the empty html framework which consists of DB, correlation values and summary.
        """
        return make_response(render_template('dataVisualization/partial_data_visual_features.html'), 200, html_headers)
    
@DataFeatureVisualization.route('/features_meta')
class featureDataMeta(Resource):    
    def post(self):
        from KETIToolMetaManager.metaDataManager import wizMongoDbApi as wiz
        import simplejson

        json_result = request.json
        db_name = json_result['db_name']
        ms_name = json_result['ms_name']
        column_name = json_result['column_name']
        analyzer_name = json_result['analyzer_name']

        domain = db_name.split("_", maxsplit=1)[0]
        sub_domain = db_name.split("_", maxsplit=1)[1]
        
        result = {}
        ms_meta = collector.ReadData(db_client, db_name, ms_name).get_ms_meta() # ms_doc

        try:
            result["ms_meta"] = ms_meta["analysisResult"][analyzer_name][column_name]

            if analyzer_name == "CountByFeatureLabel": # Label Information
                # result["ms_meta"] = []
                if result["ms_meta"][0] == "None":
                    result["ms_meta"]= None
            else: # Time Analysis (Holiday, WorkingTime, Time Step)
                # result["ms_meta"] = {}
                db_meta = collector.ReadData(db_client, db_name).get_db_meta() # db_doc
 
                mongodb_c = wiz.WizApiMongoMeta()
                ms_metas = mongodb_c.get_database_collection_documents(domain, sub_domain) #ms_docs
                if db_meta:
                    db_idx = [idx for idx, doc in enumerate(ms_metas) if doc["table_name"] == "db_information"][0]
                    result = db_column_info(db_meta, column_name, result)
                    result["db_meta"] = [analysis_result for analysis_result in db_meta["analysisResult"] if (analysis_result["columnName"] == column_name)&(analysis_result["analyzerName"]==analyzer_name)][0]
                    result = ms_result(ms_metas, ms_meta, result, analyzer_name, column_name, db_idx)
                else:
                    result = ms_result(ms_metas, ms_meta, result, analyzer_name, column_name) # total_ms_meta, number of datas
        except KeyError:
            result["ms_meta"] = None
            result["number_of_datas"] = None
        return simplejson.dumps(result, ignore_nan=True)

@DataFeatureVisualization.route('/db_ms_column_information')
class databaseMeasurementColumnInfo(Resource):   ## 해결
    def post(self):
        """
        This API makes inforamtion on DataBase, Measurment, Column into Json data.
        """
        
        json_result = request.json
        db_name = json_result['db_name']
        ms_name = json_result['ms_name']
        column_name = json_result['column_name']
        
        result = {}
        
        db_meta = collector.ReadData(db_client, db_name).get_db_meta()
        ms_meta = collector.ReadData(db_client, db_name, ms_name).get_ms_meta()

        result = db_column_info(db_meta, column_name, result)
        result = ms_info(ms_meta, result)
                
        return simplejson.dumps(result, ignore_nan=True)

def total_ms_result(ms_metas, result, analyzer_name, column_name, same_numberofcolumns_tablename):
    labelaverage_dict = {}
    notsortaverage_dict = {}

    labels = list(result["ms_meta"].keys())
    values = list(result["ms_meta"].values())

    for label, value in zip(labels, values):
        if value == "None":
            labelaverage_dict[label] ={"values":None}
            notsortaverage_dict[label] = {"values":None, "idx":None}
        else:
            value_ls = []
            for table_name in same_numberofcolumns_tablename:
                for doc in ms_metas:
                    if doc["table_name"] == table_name:
                        doc_analysis_result = doc["analysisResult"][analyzer_name][column_name].keys()
                        value_ls.append(doc["analysisResult"][analyzer_name][column_name][label])
            notsortaverage_dict[label] = {"values":value_ls, "idx":value_ls.index(value)}
            
            except_none_value_ls = [x for x in value_ls if x != 'None']
            except_none_value_ls.sort(reverse=True)
            select_ms_idx = except_none_value_ls.index(value)
            labelaverage_dict[label] = {"values":except_none_value_ls, "idx":select_ms_idx, "number_of_notNoneDatas":len(except_none_value_ls)}
            
    result["total_ms_meta"] = labelaverage_dict
    result["notSort_None_total_ms_meta"] = notsortaverage_dict
    return result

def ms_result(ms_metas, ms_meta, result, analyzer_name, column_name, db_idx=None):
    same_numberofcolumns_tablename = []
    if db_idx != None:
        del ms_metas[db_idx]
    
    select_ms_number_of_columns = ms_meta["numberOfColumns"] # 해당 ms의 number of columns 랑 비교해야하니
    
    if len(ms_metas) == 1: # db information제외 한개의 ms만 존재할 시
        if all([True if value == "None" else None for value in result["ms_meta"].values()]):
            result["number_of_datas"] = None
        else:
            result["number_of_datas"] = 1
            for label in result["ms_meta"].keys():
                result["total_ms_meta"][label] = {"number_of_notNoneDatas":1}
    else: # db_information 존재 및 Data 2개 이상 존재 (2-2)
        for doc in ms_metas: # same_numberofcolumns_tablename 추출 (columns같은 아이 추출)
            if select_ms_number_of_columns == doc["numberOfColumns"]:
                same_numberofcolumns_tablename.append(doc["table_name"])
        # 추출한 same_numberofcolumns_tablename에서 result 생성 (전체겹침+일부겹침 or 하나도 안겹침)
        if len(same_numberofcolumns_tablename) >= 2: # 겹치는 ms들이 존재할때 데이터 갯수를 비교해서 result 저장
            result["number_of_datas"] = len(same_numberofcolumns_tablename)
            if len(same_numberofcolumns_tablename) < 100:
                #(3-1 function)
                result = total_ms_result(ms_metas, result, analyzer_name, column_name, same_numberofcolumns_tablename)
            else:# 100개 이상일 때 db, ms 막대 그래프만 그리기 -> .js 에서 경우의 수 따져서 해줄 것임
                for label in result["ms_meta"].keys():
                    result["total_ms_meta"][label] = {"number_of_notNoneDatas":len(same_numberofcolumns_tablename)}
        else:
            # 정말 어떠한 데이터하고도 column이 겹치지 않을때 - 혼자 막대그래프 ## 코드 확인해보기
            result["number_of_datas"] = 1 # 이 경우를 쉽게 확인하기 위해 number_of_datas가 존재해야함.
    return result

def transform_none(value):
    if value == "None":
        value = None
    return value

def db_column_info(db_meta, column_name, result):
    column_info_dict = {}
    # db info
    result["db_info"] = None
    result["column_info"] = None
    if db_meta:
        result["db_info"] = {"description" : db_meta["description"]}
        # column info
        for info in db_meta["columnInformation"]:
            if info["columnName"] == column_name:
                column_info_ls = [x for x in ["description", "tag", "unit", "min", "max"] if x in list(info.keys())]
                if column_info_ls != []:
                    result["column_info"] = info
    
    return result

def ms_info(ms_meta, result):
    ms_info_dict = {}

    result["ms_info"] = None
    if ms_meta:
        ms_info_ls = [x for x in ["description", "tag", "frequency"] if x in list(ms_meta.keys())]
        if ms_info_ls:
            for info_key in ms_info_ls:
                ms_info_dict[info_key] = ms_meta[info_key]
            result["ms_info"] = ms_info_dict
    return result