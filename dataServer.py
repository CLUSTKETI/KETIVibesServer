 ############## 
# Main CLUST Server Application
# - Run This page for starting CLUST Server.
# - This server is implemented based on Flask Python framework.
##############
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from flask import Flask, session, request, g
from flask_bootstrap import Bootstrap
from flask_restx import Api

app = Flask(__name__, static_url_path='')
Bootstrap(app)
app.secret_key = "super secret key"
api = Api(app)

##### JW
from db_model import dbModel
dbModel.DB_init()

## Session Parameter Initialization ##
# session['integration_param'] : multiple data를 integration 하기 위한 기본 parameter

from index import Index
api.add_namespace(Index)

from dataVisualization import DataVisualization
api.add_namespace(DataVisualization)

from dataIntegration import DataIntegration, integratedData
api.add_namespace(DataIntegration)

from dataIngestion import DataIngestion
api.add_namespace(DataIngestion)

from dataInference import DataInference
api.add_namespace(DataInference)

from dataExploration import DataExploration
api.add_namespace(DataExploration)

from dataFeatureVisualization import DataFeatureVisualization
api.add_namespace(DataFeatureVisualization)

from dataLearning import DataLearning
api.add_namespace(DataLearning)

from dataDomainExploration import DataDomainExploration
api.add_namespace(DataDomainExploration)

from dataCycleExploration import DataCycleExploration
api.add_namespace(DataCycleExploration)

from dataPreprocessing import DataPreprocessing
api.add_namespace(DataPreprocessing)

from testPreprocessing import TestPreprocessing
api.add_namespace(TestPreprocessing)

from dataStatistics import DataStatistics
api.add_namespace(DataStatistics)
#####

from KETIVibesServer.dataModelInference import DataModelInference
api.add_namespace(DataModelInference)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='9005')