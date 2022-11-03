from flask_restx import Resource, Api, Namespace
##
import json
import sys, os
sys.path.append("../")
sys.path.append("../../")

# from db_model import dbModel
# db_client = dbModel.db_client
##
MetaManager = Namespace(name = 'MetaManager',  description='Read And Write Meta')

dir_root = os.path.abspath(os.path.dirname(__file__))
IntegratedDataMetaPath = os.path.join(dir_root,'metaFiles',"integratedData.json")
trainModelMetaFilePath = os.path.join(dir_root,'metaFiles',"model.json")
IntegratedDataFolderName = "data_integrated_result"
IntegratedDataFolderPath = os.path.join(dir_root,IntegratedDataFolderName)
ModelFilePath = os.path.join(dir_root,'Models')
scalerDataFolderName ='scaler'
scalerDataFolderPath = os.path.join('.',scalerDataFolderName)

integratedDataDBName = 'ml_data_integration'


from KETIToolDL.CLUSTTool.common import p1_integratedDataSaving as p1
@MetaManager.route('/readIntegratedDataMeta')
class readIntegratedDataMeta(Resource):
    def get(self):
        """
        ReadIntegratedData
        
        # Description
        This API return Meta Info of integratedData 
        """
        # 1 (p2부분 1. Data Selection)
        DataMeta = p1.readJsonData(IntegratedDataMetaPath)
        dataList =  list(DataMeta.keys())

        return json.dumps(DataMeta)

@MetaManager.route('/readModelMeta')
class readModelMeta(Resource):
    def get(self):
        """
        Read Models
        
        # Description
        This API return Meta Info of integratedData 
        """
        # 2. select Model 
        ModelMeta = p1.readJsonData(trainModelMetaFilePath)
        modelList = list(ModelMeta.keys())
        print(modelList)
        return json.dumps(ModelMeta)


@MetaManager.route('/readRegressionModels')
class readRegressionModels(Resource):
    def get(self):
        """
        ReadIntegratedData
        
        # Description
        This API return Meta Info of integratedData 
        """
        result =""
        return result