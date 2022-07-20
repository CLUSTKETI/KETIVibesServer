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
          "data_value": [[214.03333333],
       [214.21666667],
       [214.01666667],
       [213.9       ],
       [213.75      ],
       [213.21666667],
       [213.00],
       [212.8       ],
       [212.23333333],
       [212.00],
       [212.00],
       [212.00],
       [212.00],
       [212.00],
       [211.96666667],
       [211.65      ],
       [211.9       ],
       [211.91666667],
       [212.00],
       [212.7       ],
       [213.36666667],
       [214.00],
       [214.53333333],
       [215.00]],
          "clean_param": "Clean",
          "scaler_param": "scale",
          "model_method": "gru",
          "integrationFreq_min": 60,
          "feature_col_list": ["O2/value"],
          "target_col": "O2/value",
          "dataInfo": [["farm_swine_air", "sadle"]],
          "future_step": 1,
          "past_step": 24
        }
        ```

        # ex. Output
        ``` json
            {
            "Result": 213.67172241210938,
            "Condition": "very bad"
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
    if element_name == 'CO/value':
        if inference_result <= 1.74:
            condition = 'good'
        elif inference_result >= 1.75 and inference_result <= 7.85:
            condition = 'normal'
        elif inference_result >= 7.86 and inference_result <= 13.09:
            condition = 'bad'
        else:
            condition = 'very bad'

    elif element_name == 'H2S/value':
        if inference_result <= 0.07:
            condition = 'good'
        elif inference_result >= 0.08 and inference_result <= 0.50:
            condition = 'normal'
        elif inference_result >= 0.51 and inference_result <= 1.99:
            condition = 'bad'
        else:
            condition = 'very bad'

    elif element_name == 'NH3/value':
        if inference_result <= 4.4:
            condition = 'good'
        elif inference_result >= 4.5 and inference_result <= 20.0:
            condition = 'normal'
        elif inference_result >= 20.1 and inference_result <= 49.9:
            condition = 'bad'
        else:
            condition = 'very bad'

    elif element_name == 'NO2/value':
        if inference_result <= 0.011:
            condition = 'good'
        elif inference_result >= 0.012 and inference_result <= 0.027:
            condition = 'normal'
        elif inference_result >= 0.028 and inference_result <= 0.08:
            condition = 'bad'
        else:
            condition = 'very bad'

    elif element_name == 'O2/value':
        if inference_result <= 23.0:
            condition = 'good'
        elif inference_result >= 18.01 and inference_result <= 22.99:
            condition = 'normal'
        elif inference_result >= 15.01 and inference_result <= 18.0:
            condition = 'bad'
        else:
            condition = 'very bad'


    finalResult ={'Result':inference_result, 'Condition':condition}

    return finalResult
    

