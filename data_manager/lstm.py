import time
from datetime import timedelta
from warnings import catch_warnings

import matplotlib
from numpy.lib.shape_base import tile
matplotlib.use('agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from KETIAppMachineLearning.training import learn_testML
from KETIAppMachineLearning.ML import inference
from KETIAppMachineLearning.ML.settings import learning_setting
from KETIPreDataIntegration.clustDataIntegration import ClustIntegration
from KETIPreDataSelection.data_selection import setSelectionParameter
import sys
sys.path.append("../")
sys.path.append("../..")
from db_model import dbModel
db_client = dbModel.db_client

refine_param = {'removeDuplication': {'flag': True}, 'staticFrequency': {'flag': True, 'frequency': None}}
CertainParam= {'flag': True}
uncertainParam= {'flag': False, "param":{}}
outlier_param ={
    "certainErrorToNaN":CertainParam, 
    "unCertainErrorToNaN":uncertainParam
}
imputation_param =imputation_param = {
"serialImputation":{
    "flag":True,
    "imputation_method":[{"min":0,"max":30,"method":"linear", "parameter":{}}], 
    "totalNonNanRatio":40}
}

process_param = {'refine_param':refine_param, 'outlier_param':outlier_param, 'imputation_param':imputation_param}

def run(intDataInfo,params,root_path=None,integrated_data=None):
    """This is the function for running training of a lstm model.

    Learning process is divides to three steps.

    1. integrate partial data

    2. preprocess input data for learning
    
    3. learning lstm model

    :param intDataInfo: It is needed for integration process.
    :type intDataInfo: dictionary
    :param params: model learning parameter
    :type params: dictionary
    :param root_path: root directory for model file, defaults to None
    :type root_path: str, optional
    :param integrated_data: if it is not None, integration step is skipped, defaults to None
    :type integrated_data: class:`pandas.DataFrame`, optional
    :returns: learning result
    :rtype: dictionary

    prameter ``intDataInfo`` example
    docstring::
        {
            "db_info":
                [
                    {'db_name': 'farm_inner_air',
                    'measurement': 'ms11',
                    'start': '2020-09-11 00:00:00',
                    'end': '2020-10-13 00:00:00'},
                    
                    {'db_name': 'farm_outdoor_air',
                    'measurement': 'ms10',
                    'start': '2020-09-11 00:00:00',
                    'end': '2020-10-13 00:00:00'},
                ]
        }
    
    return example
    docstring::
        {
            'mid_data':{
                'partial_dataset_type' : '123456',
                'file_path' : '/user/model/123456/'
            }, 
            'img':figdata,
            'rmse':{
                'Train' : [0.234, 0.123, ...],
                'Validation' : [0.142, 0.112, ...]
            }
        }
    
    when an error raises
    docstring::
        {
            'mid_data':{
                'partial_dataset_type' : '123456',
                'file_path' : '/user/model/123456/'
            }, 
            'errMsg' : Expect x to be a non-empty array or dataset."
        }
    
    """
    learning_info = {
        "learning_method": params['learning_method'],
        "future_min": int(params['future_min']),
        "past_min" : int(params['past_min']),
        "re_frequency_min": int(params['re_freq_min']),
        "target_feature" : params['target_feature'],
        "feature_list" : params['feature_list'],
        "learning_parameter": {
                                "first_unit_num":64,
                                "second_unit_num":64,
                                "CNN_filter":64,
                                "ConvLSTM2D":64, 
                                "epochs_num":50,
                                'train_length_ratio':0.8
                            },
        "scale_method": ['scale'], 
        "target_data_preparation_method": 'mean',
        "integration_info":intDataInfo
    }
    
    VI= learning_setting.LearningSetting(learning_info,root_path)
    RP = learning_setting.Reporting_param(VI)
    

    LTM,train_X,train_y,val_X,val_y,learning_information= preprocessing(integrated_data, VI)

    mid_data = {
        "partial_dataset_type":VI.get_partial_dataset_type_name(),
        "file_path":VI.get_model_file_name(),
    }
    time.sleep(1)

    try:
        res = training(LTM,RP,train_X,train_y,val_X,val_y,learning_information)
    except ValueError as e:
        res = {"errMsg": str(e)}

    res["mid_data"] = mid_data
    return res

def integrate(intDataInfo, re_frequency_min):
    """
    This is the function to integrate partial data.

    :param intDataInfo: It has integration information such as database name, measurement name etc.
    :type intDataInfo: dictionary
    :param re_frequency_min: It is a resample frequency minute. It is one of the integration parameters.
    :type re_frequency_min: int

    :returns: result integrated data table
        
    :rtype: class:`pandas.DataFrame`
    """
    integrationParam={}
    integration_param = {
        "granularity_sec":re_frequency_min*60,
        "param":integrationParam,
        "method":"meta"
    }

    result = ClustIntegration().clustIntegrationFromInfluxSource(db_client, intDataInfo, process_param, integration_param )

    return result

def preprocessing(basicDataSet, VI):
    """
    This is the function to preprocess integrated data

    :param basicDataSet: integrated table
    :type basicDataSet: class:`pandas.DataFrame`
    :param VI: This Object has all of learning parameters. 
    :type VI: class:`KETIAppMachineLearning.ML.settings.learning_setting.LearningSetting`

    :returns: training data and parameter
        
    :rtype: tuple
    """
    LTM = learn_testML.MLDataPreparation(VI)
    scaled_dataset, scaler, scale_column = LTM.MLPreprocessing(basicDataSet)
    train, val = LTM.get_train_test_by_ratio(scaled_dataset, VI.train_length_ratio)
    train_X, train_y, learning_information = LTM.get_transformed_Data(train)
    val_X, val_y, learning_information = LTM.get_transformed_Data(val)
    return LTM,train_X,train_y,val_X,val_y,learning_information

def training(LTM,RP,train_X, train_y, val_X, val_y, learning_information, test_range=1):
    """
    This is the function to train a lstm model

    :param LTM: MLDataPreparation Object
    :type LTM: class:`KETIAppMachineLearning.training.learn_testML.MLDataPreparation`
    :param RP: It records learning information.
    :type RP: class:`KETIAppMachineLearning.ML.settings.learning_setting.Reporting_param`
    :param train_X: train data
    :type train_X: class:`pandas.DataFrame`
    :param train_y: train label data
    :type train_y: class:`pandas.DataFrame`
    :param val_X: validation data
    :type val_X: class:`pandas.DataFrame`
    :param val_y: validation label data
    :type val_y: class:`pandas.DataFrame`
    :param learning_information: learning information data
    :type learning_information: dictionary
    :param test_range: test iteration count ,default to 1
    :type test_range: int

    :returns: learning result (rmse graph , rmse values)
        
    :rtype: dictionary
    """
    for i in range(test_range):
        # 5) LSTM Training
        print("====TEST",i,"====")
        history = LTM.train_validation_LSTM(train_X, train_y, val_X, val_y, learning_information, False)
        RP.set_values("training_rmse", history.history['rmse'])
        RP.set_values("validation_rmse", history.history['val_rmse'])
        # print(RP.get_value("training_rmse"))
        # print(RP.get_value("validation_rmse"))
    lines = {
        "Train":history.history['loss'],
        "Validation":history.history['val_loss']
    }
    return {"img": plotting_res(lines), "rmse" : lines}

def plotting_res(lines,title="Learning Result"):
    """
    plot a line graph for learning result
    """
    plt.rcParams.update({'font.size': 15})
    plt.figure(figsize=(10,5))
    for line_label in lines.keys():
        plt.plot(lines[line_label], label=line_label)
    return plt_to_png(title,'epoch','RMSE')

def plotting_infer_res(line,scatter,target_name,title="Original Inferenced Result",marker_size=800,line_color="wheat"):
    """
    plot a line and scatter graph for inference result
    """
    plt.rcParams.update({'font.size': 15})
    plt.figure(figsize=(20,10))
    plt.plot(line['x'], line['y'], color=line_color,linewidth=2.0, label='Test Data')
    plt.scatter(scatter['x'],scatter['y'], color='b', s=marker_size, marker='*', label="Inferenced Data")
    plt.axhline(scatter['y'], 0.02, 0.98, color='blue', linestyle='--', linewidth=0.8)
    plt.axvline(scatter['x'], 0.02, 0.98, color='blue', linestyle='--', linewidth=0.8)
    return plt_to_png(title,"datetime",target_name)

def plt_to_png(title,xlabel,ylabel):
    """
    convert a pyplot graph to encoding of png image
    """
    title_font = {
    'fontsize': 14,
    'fontweight': 'bold'
    }
    plt.title(title,fontdict=title_font)
    plt.grid(True)
    plt.legend()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    return image_base64

def run_inference(learning_info,test_duration,root_path=None):
    """
    This is the function to run lstm Inference process.

    Inference process is divides to three steps.

    1. integration of inference data

    2. predict value at a specific time

    3. draw result graph, if the number of data is bigger than min_limit, draw a zoomed graph

    :param learning_info: integration info
    :type learning_info: dictionary
    :param test_duration: learning parameter
    :type test_duration: dictionary
    :param root_path: root directory for model file
    :type root_path: str, default to None
               
    :returns: inference result
        
    :rtype: dictionary
    
    """
    # 1. integration of inference data
    intDataInfo = setSelectionParameter.set_integratedDataInfoByDBSet(test_duration['start'], test_duration['end'], learning_info["integration_info"]["db_info"])
    learning_info["integration_info"] = intDataInfo
    VI=learning_setting.LearningSetting(learning_info,root_path)
    basicDataSet=integrate(intDataInfo, VI.get_learning_information()['re_frequency_min'])
    # 2. predict value at a specific time
    input_x = basicDataSet[-VI.X_row_num:]
    inv_yhat= inference.inference(input_x, VI) 
    # 3. draw result graph
    target_name = VI.get_learning_information()['target_feature']
    target_table = basicDataSet[[target_name]]
    last_time = target_table.index[-1]
    final_time = last_time + timedelta(minutes=learning_info['future_num']*learning_info['re_frequency_min'])
    line = { "x" : target_table.index, "y" : target_table[target_name] }
    scatter = { "x" : final_time, "y" : inv_yhat }
    original_img = plotting_infer_res(line,scatter,target_name)
    # if the number of data is bigger than min_limit, draw a zoomed graph
    minimal_img = None
    min_limit =  30
    if(len(target_table)>min_limit):
        target_table2 = target_table.iloc[-min_limit:,:]
        line['x'] = target_table2.index
        line['y'] = target_table2[target_name]
        minimal_img = plotting_infer_res(line,scatter,target_name,"Zoomed Graph",700,"black")
    return {"ori_img":original_img,"mini_img":minimal_img, "result_date":str(final_time),"result_value":inv_yhat}

