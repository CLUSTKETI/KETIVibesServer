import datetime as dt

def get_jsonDF(input_data):

    input_data.index.name = 'index'
    input_data.index= input_data.index.strftime('%Y-%m-%d %H:%M:%S')
    data_index = list(input_data.index)
    input_data = input_data.reset_index().drop('index', axis=1)
    input_data_dict = input_data.to_dict('list')
    new_dict = {}
    for key in input_data_dict.keys():
        new_dict[str(key)]=input_data_dict[key]

    return new_dict, data_index
