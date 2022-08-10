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


from dataModelInference import DataModelInference
api.add_namespace(DataModelInference)


from forecastingInference import ForecastingInference
api.add_namespace(ForecastingInference)




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='9005')