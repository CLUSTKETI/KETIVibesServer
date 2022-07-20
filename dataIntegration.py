from flask import request, session
from flask_restx import Resource, Api, Namespace
from flask import render_template, make_response
from flask import jsonify
##
import sys
sys.path.append("../")
sys.path.append("../..")

import requests
from urllib.parse import urljoin

from db_model import dbModel
db_client = dbModel.db_client
##
DataIntegration = Namespace(name = 'DataIntegration',  description='Integrated data analysis from multiple sources')
html_headers = {'Context-Type':'text/html'}

###### TODO JW
refine_param = {
    "removeDuplication":{"flag":True},
    "staticFrequency":{"flag":True, "frequency":None}
}
outlier_param  = {"certainErrorToNaN":{"flag":True},"unCertainErrorToNaN":{"flag":False,"param":{}}}

uncertainParam= {'flag': False, "param":{}}
CertainParam= {'flag': True}
outlier_param ={
    "certainErrorToNaN":CertainParam, 
    "unCertainErrorToNaN":uncertainParam
}

imputation_param = {
    "serialImputation":{
        "flag":True,
        "imputation_method":[{"min":0,"max":50,"method":"linear" , "parameter":{}}],
        "totalNonNanRatio":80
    }
}
process_param = {'refine_param':refine_param, 'outlier_param':outlier_param, 'imputation_param':imputation_param}
######

@DataIntegration.route('/dataSelection')
class dataSelection(Resource):
    def get(self):
        """
        Show data selection page
        
        # Description
        This API shows the page that can control multiple data selction and integration procedure.

        # Input Dta
        * None
        """
        return make_response(render_template('manipulation/dataSelection.html'), 200, html_headers)

# Pure get integrated Data
@DataIntegration.route('/integratedData')
class integratedData(Resource):
    def post(self):
        print("====Get integratedData====")
        integration_param = session.get('integration_param') 
        print("====Get integration_param====")
        print(integration_param)
        #integration_param = request.get_json(force=True)
        json_data={}
        data_index={}
        if integration_param:
            integrated_data_resample = get_integratedData(integration_param)
            from KETIAppDataServer.visual_manager import DF_manager
            json_data, data_index = DF_manager.get_jsonDF(integrated_data_resample)
        payload = {
            "json_data": json_data,
            "data_index": data_index
        }
        return payload

# Pure get integrated Data
@DataIntegration.route('/integratedData_view')
class integratedData_view(Resource):
    def post(self):
        print("====Post integratedData_view====")
        param = request.get_json(force=True)
        session['integration_param'] = param
        print("parameter", param)
        if param:
            from KETIAppDataServer.data_manager import echart
            integrated_data_resample = get_integratedData(param)
            print(integrated_data_resample)
            result = echart.getEChartFormatResult(integrated_data_resample)
            return make_response(render_template('manipulation/integratedData.html', param = param, result =result), 200, html_headers)
        else :
            return make_response(render_template('manipulation/integratedData.html'), 200, html_headers)

    def get(self):
        print("Get integratedData_view")    
        param =session.get('integration_param')
        if param:
            from KETIAppDataServer.data_manager import echart
            integrated_data_resample = get_integratedData(param)
            result = echart.getEChartFormatResult(integrated_data_resample)
            return make_response(render_template('manipulation/integratedData.html', param = param, result =result), 200, html_headers)
        else:
            return make_response(render_template('manipulation/integratedData.html'), 200, html_headers)
        
def get_integratedData(result):
    re_frequency_sec = result['re_frequency_sec']
    intDataInfo = result['intDataInfo']
    ## Preprocessing and Integration use custom function
    from KETIPreDataIntegration.clustDataIntegration import ClustIntegration
    integrationParam={}
    integration_param = {
        "granularity_sec":re_frequency_sec,
        "param":integrationParam,
        "method":"meta"
    }

    result = ClustIntegration().clustIntegrationFromInfluxSource(db_client, intDataInfo, process_param, integration_param )

    return result


