import pandas as pd
import os
# 

## 2. DataSelection
def getSavedIntegratedData(dataSaveMode, dataName, dataFolderPath, db_name=None, db_client = None):
    if dataSaveMode =='CSV':
        fileName = os.path.join(dataFolderPath, dataName +'.csv')
        data = pd.read_csv(fileName, index_col='datetime', infer_datetime_format=True, parse_dates=['datetime'])

    elif dataSaveMode =='influx':
        ms_name = dataName
        data = db_client.get_data(db_name, ms_name)
        
    return data
