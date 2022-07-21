from KETIPreDataIngestion.data_influx import influx_Client_v2 as iC
def DB_init():
    global db_client
    global db_list
    server = "2"
    if server == "1":   # Azure
        from KETIPreDataIngestion.KETI_setting.influx_setting_KETI import VibeDataServer as ins
    elif server =="2":   # Sangam(WorkStation)
        from KETIPreDataIngestion.KETI_setting.influx_setting_KETI import VibeDataServer2 as ins
    db_client = iC.influxClient(ins)
    db_list = db_client.get_DBList()

