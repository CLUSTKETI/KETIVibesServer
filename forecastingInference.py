from flask import request
from flask_restx import Resource, Namespace, reqparse
from flask import render_template, make_response
import sys, os
import pandas as pd
import numpy as np
import json

sys.path.append("../")
sys.path.append("../../")

import p1_integratedDataSaving as p1
import p2_dataSelection as p2

import p5_inference as p5
import pathSetting


dir_root = os.path.abspath(os.path.dirname(__file__))
IntegratedDataMetaPath = os.path.join(dir_root,'metaFiles',"integratedData.json")
trainModelMetaFilePath = os.path.join(dir_root,'metaFiles',"model.json")
IntegratedDataFolderName = "data_integrated_result"
IntegratedDataFolderPath = os.path.join(dir_root,IntegratedDataFolderName)
ModelFilePath = os.path.join(dir_root,'Models')


ForecastingInference = Namespace(name = 'ForecastingInference',  description='ForecastingInference')
html_headers = {'Context-Type':'text/html'}


Inference_App_parser = reqparse.RequestParser()
Inference_App_parser.add_argument('data_value',  type=int, action='append', location='json',required=True)
Inference_App_parser.add_argument('feature_col_list', action='append',location='json',required=True)
Inference_App_parser.add_argument('target_col',  type=str,location='json',required=True)
Inference_App_parser.add_argument('clean_param',  type=str, location='json',required=True)
@ForecastingInference.doc("ForecastingInference")
@ForecastingInference.route('/forecastingInference')
class ModelInference(Resource):
    @ForecastingInference.doc("ForecastingInference")
    @ForecastingInference.expect(Inference_App_parser) 
    def post(get):
        """

        ForecastingInference

        # ex. Input
        ``` json
        {
            "data_value": [[212.71666667],
                [212.75      ],
                [213.00      ],
                [213.11666667],
                [213.58333333],
                [213.71666667],
                [213.53333333],
                [213.00      ],
                [213.16666667],
                [212.96666667],
                [213.00      ],
                [213.00      ],
                [213.00      ],
                [213.00      ],
                [213.00      ],
                [213.00      ],
                [213.00      ],
                [213.00      ],
                [212.58333333],
                [212.18333333],
                [212.00      ],
                [212.00      ],
                [212.03333333],
                [212.00      ]],
            "featureList": ["O2percentage"],
            "target_col": "O2percentage",
            "cleanParam": "Clean"
        }
        """

        params = request.json
        inference_result = dataInference(params)
        element_name = params['target_col']

        if inference_result < 0.0:
            inference_result = 0.0

        finalResult = checkResultCondition(inference_result, element_name)

        return finalResult




def dataInference(params):
    data_value = params["data_value"]
    featureList = params["featureList"]
    target_col = params["target_col"]
    cleanParam = params["cleanParam"]

    print(dir_root)
    print(trainModelMetaFilePath)

    ModelMeta = p1.readJsonData(trainModelMetaFilePath)
    modelName = findModelName(target_col, cleanParam, ModelMeta)
    print(modelName)


    scalerFilePath = ModelMeta[modelName]['files']['scalerFile']["filePath"]
    modelFilePath = ModelMeta[modelName]['files']['modelFile']["filePath"]
    trainParameter = ModelMeta[modelName]['trainParameter']
    model_method = ModelMeta[modelName]['model_method']
    scalerParam = ModelMeta[modelName]['scalerParam']

    inference_result = p5.inference(data_value, trainParameter, model_method, modelFilePath, scalerParam, scalerFilePath, featureList, target_col)
    inference_result = float(inference_result)

    return inference_result



#global m_name
def findModelName(target_col, cleanParam, ModelMeta):
    
    modelList = list(ModelMeta.keys())

    for name in modelList:
        if target_col == ModelMeta[name]["transformParameter"]["target_col"]:
            if cleanParam == ModelMeta[name]["trainDataInfo"]["cleanParam"]:
                return name






def checkResultCondition(inference_result, element_name):
    if element_name == 'COppm':
        if inference_result <= 1.74:
            condition = 'Good'
        elif inference_result >= 1.75 and inference_result <= 7.85:
            condition = 'Normal'
        elif inference_result >= 7.86 and inference_result <= 13.09:
            condition = 'Bad'
        else:
            condition = 'Danger'


    elif element_name == 'H2Sppm':
        if inference_result <= 0.07:
            condition = 'Good'
        elif inference_result >= 0.08 and inference_result <= 0.50:
            condition = 'Normal'
        elif inference_result >= 0.51 and inference_result <= 1.99:
            condition = 'Bad'
        else:
            condition = 'Danger'


    elif element_name == 'NH3ppm':
        if inference_result <= 4.4:
            condition = 'Good'
        elif inference_result >= 4.5 and inference_result <= 20.0:
            condition = 'Normal'
        elif inference_result >= 20.1 and inference_result <= 49.9:
            condition = 'Bad'
        else:
            condition = 'Danger'


    elif element_name == 'NO2ppm':
        if inference_result <= 0.011:
            condition = 'Good'
        elif inference_result >= 0.012 and inference_result <= 0.027:
            condition = 'Normal'
        elif inference_result >= 0.028 and inference_result <= 0.08:
            condition = 'Bad'
        else:
            condition = 'Danger'



    elif element_name == 'O2percentage':
        if inference_result >= 20.1:
            condition = 'Good'
        elif inference_result >= 18.01 and inference_result <= 20.0:
            condition = 'Normal'
        elif inference_result >= 15.01 and inference_result <= 18.0:
            condition = 'Bad'
        else:
            condition = 'Danger'


    finalResult ={'Result':inference_result, 'Condition':condition}

    return finalResult
    
