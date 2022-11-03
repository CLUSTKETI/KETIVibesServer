from ast import For
from flask import request
from flask_restx import Resource, Namespace, reqparse
from flask import render_template, make_response
import sys, os
import pandas as pd
import numpy as np
import json
import metaManager

sys.path.append("../")
sys.path.append("../../")

from KETIToolDL.CLUSTTool.common import p1_integratedDataSaving as p1
from KETIToolDL.CLUSTTool.common import p2_dataSelection as p2
from KETIToolDL.CLUSTTool.RNNPrediction import p5_inference as p5

ForecastingInference = Namespace(name = 'ForecastingInference',  description='ForecastingInference')
html_headers = {'Context-Type':'text/html'}


Inference_App_parser = reqparse.RequestParser()
# Inference_App_parser.add_argument('datasetName',  type=str,location='json',required=True)
# Inference_App_parser.add_argument('modelName',  type=str, location='json',required=True)
Inference_App_parser.add_argument('data_value',  type=int, action='append', location='json',required=True)
Inference_App_parser.add_argument('feature_col_list', action='append',location='json',required=True)
Inference_App_parser.add_argument('target_col',  type=str,location='json',required=True)

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
            "target_col": "O2percentage"
        }
        """

        params = request.get_json(force=True)
        

        condition, result = dataInference(params)
        finalResult = {'condition':condition, 'result':result}

        return finalResult






def dataInference(params):

    data_value = params["data_value"]
    featureList = params["featureList"]
    target_col = params["target_col"]
    # cleanParam = params["cleanParam"]
    cleanParam = 'Clean'

    DataMeta = p1.readJsonData(metaManager.IntegratedDataMetaPath)
    datasetName = "SadleCleanTrain"
    dataSaveMode = DataMeta[datasetName]["integrationInfo"]["DataSaveMode"]

    # 2
    ModelMeta =p1.readJsonData(metaManager.trainModelMetaFilePath)
    model_method ="gru"

    if target_col =='COppm':
        modelName = 'COSadleCleanForecasting'
    elif target_col =='H2Sppm':
        modelName = 'H2SSadleCleanForecasting'
    elif target_col =='NH3ppm':
        modelName = 'NH3SadleCleanForecasting'
    elif target_col =='NO2ppm':
        modelName = 'NO2SadleCleanForecasting'
    elif target_col =='O2percentage':
        modelName = 'O2SadleCleanForecasting'

    data = p2.getSavedIntegratedData(dataSaveMode, datasetName, metaManager.IntegratedDataFolderPath)

    # 2. read ModelMeta
    past_step = ModelMeta[modelName]['transformParameter']['past_step']
    featureList = ModelMeta[modelName]['featureList']
    target_col = ModelMeta[modelName]['transformParameter']['target_col']
    scalerParam = ModelMeta[modelName]['scalerParam']
    scalerFilePath = ModelMeta[modelName]['files']['scalerFile']["filePath"]
    modelFilePath = ModelMeta[modelName]['files']['modelFile']["filePath"]
    trainParameter = ModelMeta[modelName]['trainParameter']
    model_method = ModelMeta[modelName]['model_method']

    # 3. Test Value
    data = data[featureList]
    inputData = data[-past_step:][featureList].values

    # 4.Inference
    result = p5.inference(data_value, trainParameter, model_method, modelFilePath, scalerParam, scalerFilePath, featureList, target_col)
    result = float(result)

    if result < 0.0:
        result = 0.0

    condition = resultCondition(target_col, result)

    return condition, result



def resultCondition(target_col, result):

    if target_col == 'COppm':
        if result <= 1.74:
            condition = 'Good'
        elif result >= 1.75 and result <= 7.85:
            condition = 'Normal'
        elif result >= 7.86 and result <= 13.09:
            condition = 'Bad'
        else:
            condition = 'Danger'

    elif target_col == 'H2Sppm':
        if result <= 0.07:
            condition = 'Good'
        elif result >= 0.08 and result <= 0.50:
            condition = 'Normal'
        elif result >= 0.51 and result <= 1.99:
            condition = 'Bad'
        else:
            condition = 'Danger'

    elif target_col == 'NH3ppm':
        if result <= 4.4:
            condition = 'Good'
        elif result >= 4.5 and result <= 20.0:
            condition = 'Normal'
        elif result >= 20.1 and result <= 49.9:
            condition = 'Bad'
        else:
            condition = 'Danger'

    elif target_col == 'NO2ppm':
        if result <= 0.011:
            condition = 'Good'
        elif result >= 0.012 and result <= 0.027:
            condition = 'Normal'
        elif result >= 0.028 and result <= 0.08:
            condition = 'Bad'
        else:
            condition = 'Danger'

    elif target_col == 'O2percentage':
        if result >= 20.1:
            condition = 'Good'
        elif result >= 18.01 and result <= 20.0:
            condition = 'Normal'
        elif result >= 15.01 and result <= 18.0:
            condition = 'Bad'
        else:
            condition = 'Danger'

    return condition