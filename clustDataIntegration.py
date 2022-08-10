from functools import partial
import sys
sys.path.append("../")
sys.path.append("../..")
import datetime
# CLUST Project based custom function

class ClustIntegration():
    """
    Data Integration Class
    """
    def __init__(self):
        pass

    def getIntegratedDataSetByML(self, data_set, transform_param, overlap_duration):
        """ 
        ML을 활용한 데이터 병합 함수
        1. 병합한 데이터에 RNN_AE 를 활용해 변환된 데이터를 반환

        :param  data_set: 병합하고 싶은 데이터들의 셋
        :type intDataInfo: json
            
        :param  transform_param: RNN_AE를 하기 위한 Parameter
        :type process_param: json
        >>> transformParam = {
                "model": 'RNN_AE',
                "model_parameter": {
                    "window_size": 10, # 모델의 input sequence 길이, int(default: 10, 범위: 0 이상 & 원래 데이터의 sequence 길이 이하)
                    "emb_dim": 5, # 변환할 데이터의 차원, int(범위: 16~256)
                    "num_epochs": 50, # 학습 epoch 횟수, int(범위: 1 이상, 수렴 여부 확인 후 적합하게 설정)
                    "batch_size": 128, # batch 크기, int(범위: 1 이상, 컴퓨터 사양에 적합하게 설정)
                    "learning_rate": 0.0001, # learning rate, float(default: 0.0001, 범위: 0.1 이하)
                    "device": 'cpu' # 학습 환경, ["cuda", "cpu"] 중 선택
                }
            }
        
        :param  overlap_duration: 병합하고 싶은 데이터들의 공통 시간 구간
        :type integration_param: json
        >>> overlap_duration = {'start_time': Timestamp('2018-01-03 00:00:00'), 'end_time': Timestamp('2018-01-05 00:00:00')}
                
        :return: integrated_data by transform
        :rtype: DataFrame    
        """
        from ml_integration import RNNAEAlignment
        from meta_integration import data_integration
        
        ## simple integration
        data_int = data_integration.DataIntegration(data_set)
        dintegrated_data = data_int.simple_integration(overlap_duration)
        
        model = transform_param["model"]
        transfomrParam = transform_param['model_parameter']
        if model == "RNN_AE":
            alignment_result = RNNAEAlignment.Alignment().RNN_AE(dintegrated_data, transfomrParam)
        else :
            print('Not Available')
            
        return alignment_result

    def getIntegratedDataSetByMeta(self, data_set, integration_freq_sec, partial_data_info):
        """ 
        Meta(column characteristics)을 활용한 데이터 병합 함수

        :param  data_set: 병합하고 싶은 데이터들의 셋
        :type intDataInfo: json
            
        :param  integration_freq_sec: 조정하고 싶은 second 단위의 Frequency
        :type process_param: json
        
        :param  partial_data_info: column characteristics의 info
        :type integration_param: json
      
        :return: integrated_data
        :rtype: DataFrame    
        """
        ## Integration
        from meta_integration import data_integration
        
        data_it = data_integration.DataIntegration(data_set)
       
        
        re_frequency = datetime.timedelta(seconds= integration_freq_sec)
        integrated_data_resample = data_it.dataIntegrationByMeta(re_frequency, partial_data_info.column_meta)
        
        return integrated_data_resample 
    
    def IntegratedDataSetBySimple(self, data_set, integration_freq_sec, overlap_duration):
        """ 
        Simple한 병합

        :param  data_set: 병합하고 싶은 데이터들의 셋
        :type intDataInfo: json

        :param  integration_freq_sec: 조정하고 싶은 second 단위의 Frequency
        :type process_param: json
            
        :param  overlap_duration: 조정하고 싶은 second 단위의 Frequency
        :type overlap_duration: json
      
        :return: integrated_data
        :rtype: DataFrame    
        """
        ## Integration
        from meta_integration import data_integration
        ## simple integration
        re_frequency = datetime.timedelta(seconds= integration_freq_sec)
        data_int = data_integration.DataIntegration(data_set)
        dintegrated_data = data_int.simple_integration(overlap_duration)
        dintegrated_data = dintegrated_data.resample(re_frequency).mean()
        
        return dintegrated_data





