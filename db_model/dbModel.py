def DB_init():
    global db_client
    global db_list
    version = "2" #"2"
    if version == "1":
        from KETIPreDataIngestion.KETI_setting.influx_setting_KETI import VibeDataServer as ins
        from KETIPreDataIngestion.data_influx import influx_Client as iC
    elif version =="2":
        from KETIPreDataIngestion.KETI_setting.influx_setting_KETI import VibeDataServer2 as ins
        from KETIPreDataIngestion.data_influx import influx_Client_v2 as iC
    db_client = iC.influxClient(ins)
    db_list = db_client.get_DBList()

