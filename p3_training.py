import os, sys
sys.path.append("../")

import p1_integratedDataSaving as p1
import pandas as pd

def deleteLowQualityTrainValidationData(train, val, cleanTrainDataParam, integration_freq_sec, NaNProcessingParam):
    if cleanTrainDataParam =='Clean':
        import datetime
        timedelta_frequency_sec = datetime.timedelta(seconds= integration_freq_sec)
        train = cleanNaNDF(train, NaNProcessingParam, timedelta_frequency_sec)
        val = cleanNaNDF(val, NaNProcessingParam, timedelta_frequency_sec)

    else:
        pass
    return train, val

def getTrainValData(data, featureList, scalerRootPath, splitRatio, scalerParam, mode = None):
    trainval, scalerFilePath = getScaledData(scalerParam, scalerRootPath, data[featureList])
    import machineLearning as ML
    train, val = ML.splitDataByRatio(trainval, splitRatio, mode)
    
    return train, val, scalerFilePath

def getScaledData(scalerParam, scalerRootpath, data):
    if scalerParam=='scale':
        from dataScaler import DataScaler
        DS = DataScaler('minmax', scalerRootpath )
        #from KETIPreDataTransformation.general_transformation import dataScaler
        #feature_col_list = dataScaler.get_scalable_columns(train_o)
        DS.setScaleColumns(list(data.columns))
        DS.setNewScaler(data)
        resultData = DS.transform(data)
        scalerFilePath = DS.scalerFilePath
    else:
        resultData = data.copy()
        scalerFilePath=None

    return resultData, scalerFilePath

def cleanNaNDF(dataSet, NaNProcessingParam, timedelta_frequency_sec):
    feature_cycle=NaNProcessingParam['feature_cycle']
    feature_cycle_times=NaNProcessingParam['feature_cycle_times']
    NanInfoForCleanData=NaNProcessingParam['NanInfoForCleanData']

    feature_list = dataSet.columns
    from dataByCondition import cycle_Module

    dayCycle = cycle_Module.getCycleSelectDataSet(dataSet, feature_cycle, feature_cycle_times, timedelta_frequency_sec)
    import matplotlib.pyplot as plt

    import clean_feature_data
    CMS = clean_feature_data.CleanFeatureData(feature_list, timedelta_frequency_sec)
    refinedData, filterImputedData = CMS.getMultipleCleanDataSetsByDF(dayCycle, NanInfoForCleanData)
    CleanData = pd.concat(filterImputedData.values())
    return CleanData

def getModelFilePath(trainDataPathList, model_method):

    import modelInfo
    MI = modelInfo.ModelFileManager()
    modelFilePath = MI.getModelFilePath(trainDataPathList, model_method)
    return modelFilePath
    
def updateModelMetaData(ModelName, modelInfoMeta, trainModelMetaFilePath):
    modelMeta = p1.readJsonData(trainModelMetaFilePath)
    modelMeta[ModelName]=modelInfoMeta
    p1.writeJsonData(trainModelMetaFilePath, modelMeta)
    return modelInfoMeta