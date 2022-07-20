from flask import request
from flask_restx import Resource, Api, Namespace
from flask import render_template, make_response

html_headers = {'Context-Type':'text/html'}
DataCollection = Namespace(name = 'DataCollection',  description='Data Collection & Storage')
        
@DataCollection.route('/ts_upload_parameter_registration')
class datacollection(Resource):
    def get(self):
        return make_response(render_template('ts_upload_parameter_registration.html'), 200, html_headers)

"""
from dataCollection import DataCollection
api.add_namespace(DataCollection)


INFO_FILE_NAME = 'Data_Input_Parameter.json'


@app.route('/ts_parameter_upload', methods=['POST','GET'])
def ts_parameter_upload(): 
    print('upload') 
    data_folder = request.args['data_path']
    return render_template("ts_parameter_upload.html", data = data_folder)  


@app.route('/Dir_make_General', methods=['POST','GET'])
def makeDir_infofile():
    import time
    data = request.get_json(silent=True)

    data_para = data['collection']
    data_main_domain = data_para['main_domain']
    data_sub_domain = data_para['sub_domain']
    data_para["createdAt"]=str(time.time())
    # using time module
    hashID=createId(str(data_para).encode("utf-8"))
    data_path = os.path.join("Data",data_main_domain, data_sub_domain, hashID)
    
    # data_path 폴더 생성
    os.makedirs(data_path, exist_ok=True)
    
    # data_path 폴더안에 INFO_FILE_NAME 으로 json 파일 생성
    info_json_path = os.path.join(data_path, INFO_FILE_NAME)
    with open(info_json_path, 'w') as f:
        json.dump(data, f) 
    return data_path

def createId(content):
    import hashlib
    return hashlib.sha224(content).hexdigest()

@app.route('/data_upload_success', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':  
        folder = request.form.get('folder')  
        data_file = request.files['file']  

        filename=(data_file.filename)
        data_file.save(os.path.join(folder, filename))

        from KETIPreDataCollection.data_collection.influxdb_management import influx_setting_KETI as ifs
        from KETIPreDataCollection.data_collection.influxdb_management.influx_crud import InfluxCRUD
        from KETIPreDataCollection.data_collection import selected_column_csv_collector as sc
        from KETIPreDataCollection.data_collection import selected_data_csv_collector as sd

        jsonfile_path = folder + "/" + INFO_FILE_NAME
        with open(jsonfile_path, "r", encoding="utf8") as input_json:
            p = json.load(input_json)

        parameters = p["collection"]
        filepath = str(folder) + "/" + filename
        hashID = str(folder).split(os.path.sep)[3]

        keti = InfluxCRUD(ifs.host_, ifs.port_, ifs.user_, ifs.pass_, parameters["main_domain"] + "_" + parameters["sub_domain"], ifs.protocol)
        root = os.path.dirname(os.path.abspath(__file__))
            
        test = sc.ColumnsSelectCollector(filepath, keti, hashID, parameters["select_time"], parameters["encoding"])
        test.collect()

        return render_template("data_upload_success.html", file_name = filename, file_folder = folder)
"""