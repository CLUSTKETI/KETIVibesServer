from flask_restx import Resource, Api, Namespace
from flask import render_template, make_response
##
import sys
sys.path.append("../")
sys.path.append("../..")

from flask_restx import Api
api = Api()

##
Index = Namespace(name = 'Index',  description='Shor relation strcuture between DB/Measurement in CLUST platform')
html_headers = {'Context-Type':'text/html'}

@Index.route('/')
class index(Resource):
    @api.response(200, 'Success')
    def get(self):
        """
        
        Show relation structure between CLUST DB and Measurement

        # Description
        ### - Render index.html
        ### - index.html makes the relation between CLUST/DB/Measurement with d3.js
  
        # Input Arguments
        ### * None

        """
        return make_response(render_template('/index.html'), 200, html_headers)
