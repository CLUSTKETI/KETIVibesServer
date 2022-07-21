from cmath import inf
from crypt import methods
from unittest import result
from flask import request
from flask_restx import Resource, Namespace, reqparse
from flask import render_template, make_response
import sys, os
import pandas as pd
import numpy as np
import json

from sqlalchemy import between
sys.path.append("../")
sys.path.append("../../")


base_root = os.path.dirname(os.path.abspath(__file__))
base_folder = 'model_Inference'



DataModelInference = Namespace(name = 'DataModelInference',  description='DataModelInference')
html_headers = {'Context-Type':'text/html'}


@DataModelInference.route('/')
@DataModelInference.doc("Get dataModelInference Index page")
class DataModelInference_index(Resource):
    @DataModelInference.doc("Get dataModelInference Index page")
    def get(self):
        """
        Return data Model Inference page
        """
        return make_response(render_template('dataModelInference/dataModelInference.html'), 200, html_headers) 



Inference_App_parser = reqparse.RequestParser()
Inference_App_parser.add_argument('data_value',  type=int, action='append', location='json',required=True)
Inference_App_parser.add_argument('clean_param',  type=str, location='json',required=True)
Inference_App_parser.add_argument('scaler_param',  type=str, location='json',required=True)
Inference_App_parser.add_argument('scale_method',  type=str,location='json',required=True)
Inference_App_parser.add_argument('model_method',  type=str,location='json',required=True)
Inference_App_parser.add_argument('integrationFreq_min',  type=int,location='json',required=True)
Inference_App_parser.add_argument('feature_col_list', action='append',location='json',required=True)
Inference_App_parser.add_argument('target_col',  type=str,location='json',required=True)
Inference_App_parser.add_argument('dataInfo', action='append', location='json', required=True)
Inference_App_parser.add_argument('future_step',  type=int, location='json',required=True)
Inference_App_parser.add_argument('past_step',  type=int,location='json',required=True)
@DataModelInference.doc("DataModelInference")
@DataModelInference.route('/dataModelInference')
class ModelInference(Resource):
    @DataModelInference.doc("DataModelInference")
    @DataModelInference.expect(Inference_App_parser) 
    def post(get):

        """
        text text


        # ex. Input
        ``` json
        {
        "data_value": [[21.403333333], [21.421666667], [21.401666667], [21.39       ], [21.375      ], [21.321666667], [21.300], [21.28       ], [21.223333333], [21.200], [21.200],
        [21.200], [21.200], [21.200], [21.196666667], [21.165      ], [21.19       ], [21.191666667], [21.200], [21.27       ], [21.336666667], [21.400], [21.453333333], [21.500]],
        "clean_param": "Clean",
        "scaler_param": "scale",
        "model_method": "gru",
        "integrationFreq_min": 60,
        "feature_col_list": ["O2percentage"],
        "target_col": "O2percentage",
        "dataInfo": [["farm_swine_air", "Sadle"]],
        "future_step": 1,
        "past_step": 24
        }
        ```

        # ex. Output
        ``` json
            {
            "Result": 21.312096,
            "Condition": "normal"
            }
        ```

        """
        params = request.json
        inference_result = dataInference(params)
        element_name = params['target_col']
        finalResult = checkResultCondition(inference_result, element_name)

        return finalResult










def dataInference(params):
    """
    
    """
    data_value = params['data_value']
    data_value = np.array(data_value)
    cleanParam = params['clean_param']
    scalerParam = params['scaler_param']
    scale_method = 'minmax'
    model_method = params['model_method']
    integrationFreq_min = params['integrationFreq_min']
    feature_col_list = params['feature_col_list']
    target_col = params['target_col']
    future_step = params['future_step']
    past_step = params['past_step']

    trainDataPathList, scalerRootPath, file_RootName, transformParameter, trainParameter = dataPathParameter(params)

    ##
    from KETIPreDataTransformation.general_transformation import dataScaler 
    from KETIPreDataTransformation.general_transformation.dataScaler import DataInverseScaler
    if scalerParam =='scale':
        inputData = dataScaler.getScaledData(data_value, feature_col_list, scalerRootPath, scale_method)
    else:
        inputData = pd.DataFrame(data_value, columns=feature_col_list, index=range(len(data_value)))

    ##
    from KETIToolDL.PredictionTool.RNNStyleModel.inference import RNNStyleModelInfernce
    Inference = RNNStyleModelInfernce()
    input_DTensor = Inference.getTensorInput(inputData)
    Inference.setData(input_DTensor)

    from KETIToolDL import modelInfo
    MI = modelInfo.ModelFileManager()
    modelFilePath = MI.getModelFilePath(trainDataPathList, model_method)

    Inference.setModel(trainParameter, model_method, modelFilePath)
    inference_result = Inference.get_result()

    ##
    if scalerParam =='scale':
        baseDFforInverse= pd.DataFrame(columns=feature_col_list, index=range(len(input_DTensor)))
        DIS = DataInverseScaler(scale_method, scalerRootPath)
        DIS.setScaleColumns(feature_col_list)
        baseDFforInverse[target_col] = inference_result
        finalResult = DIS.transform(baseDFforInverse)[target_col]
        finalResult = finalResult[0]
    else:
        finalResult = inference_result[0][0]

    finalResult = finalResult.item()
    
    return finalResult




def dataPathParameter(params):
    """

    """
    future_step = params['future_step']
    past_step = params['past_step']
    cleanParam = params['clean_param']
    scalerParam = params['scaler_param']
    integrationFreq_min = params['integrationFreq_min']
    integration_freq_sec = 60 * integrationFreq_min
    feature_col_list = params['feature_col_list']
    target_col = params['target_col']
    dataInfo = params['dataInfo']

    from KETIPreDataTransformation.general_transformation.dataScaler import encodeHashStyle
    hashedDataList = encodeHashStyle(dataInfo)
    print(hashedDataList)

    transformParameter = { 'future_step':future_step,
                            'past_step':past_step,
                            'feature_col_list':feature_col_list,
                            'target_col':target_col}
    
    trainParameter = {'input_dim':len(feature_col_list),
                        'hidden_dim':256,
                        'layer_dim':3,
                        'output_dim':1,
                        'dropout_prob':0.2}


    stepInfo = "futureStep_"+str(future_step)+"_pastStep_"+str(past_step)+"_FreqSec_"+str(integration_freq_sec)
    trainDataPathList=[hashedDataList, str(feature_col_list).replace('/',''), target_col.replace('/',''), stepInfo] 
    trainDataPathList.insert(0, cleanParam)

    scalerRootAddress = os.path.join(base_root, base_folder, 'scaler')
    scalerRootPath = os.path.join(scalerRootAddress, hashedDataList, cleanParam)

    file_RootName = scalerParam+ cleanParam+ hashedDataList

    return trainDataPathList, scalerRootPath, file_RootName, transformParameter, trainParameter







def checkResultCondition(inference_result, element_name):
    if element_name == 'COppm':
        if inference_result <= 1.74 and inference_result >= 0.0 :
            condition = 'Good'
        elif inference_result >= 1.75 and inference_result <= 7.85:
            condition = 'Normal'
        elif inference_result >= 7.86 and inference_result <= 13.09:
            condition = 'Bad'
        elif inference_result >= 13.10:
            condition = 'Danger'
        else:
            condition ='Error'

    elif element_name == 'H2Sppm':
        if inference_result <= 0.07 and inference_result >= 0.0:
            condition = 'Good'
        elif inference_result >= 0.08 and inference_result <= 0.50:
            condition = 'Normal'
        elif inference_result >= 0.51 and inference_result <= 1.99:
            condition = 'Bad'
        elif inference_result >= 2.0:
            condition = 'Danger'
        else:
            condition ='Error'

    elif element_name == 'NH3ppm':
        if inference_result <= 4.4 and inference_result >= 0.0:
            condition = 'Good'
        elif inference_result >= 4.5 and inference_result <= 20.0:
            condition = 'Normal'
        elif inference_result >= 20.1 and inference_result <= 49.9:
            condition = 'Bad'
        elif inference_result >= 50.0:
            condition = 'Danger'
        else:
            condition ='Error'

    elif element_name == 'NO2ppm':
        if inference_result <= 0.011 and inference_result >= 0.0:
            condition = 'Good'
        elif inference_result >= 0.012 and inference_result <= 0.027:
            condition = 'Normal'
        elif inference_result >= 0.028 and inference_result <= 0.08:
            condition = 'Bad'
        elif inference_result >= 0.081:
            condition = 'Danger'
        else:
            condition ='Error'


    elif element_name == 'O2percentage':
        if inference_result >= 20.1:
            condition = 'Good'
        elif inference_result >= 18.01 and inference_result <= 20.0:
            condition = 'Normal'
        elif inference_result >= 15.01 and inference_result <= 18.0:
            condition = 'Bad'
        elif inference_result >= 12.1 and inference_result <= 15.00:
            condition = 'Danger'
        else:
            condition ='Error'



    finalResult ={'Result':inference_result, 'Condition':condition}

    return finalResult
    

