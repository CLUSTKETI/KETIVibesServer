import sys
import os
sys.path.append("../")
sys.path.append("../..")

class DataPreprocessing():
    '''This class has interfaces of Data Preprocessing.
    
    **Data Preprocessing Modules**::

            Refine Data, Remove Outlier, Impute Missing Data
    '''
    
    def __init__(self):
        pass
    
    def get_refinedData(self, data, refine_param):
        """
        This function gets refined data with static frequency, without redundency data. 
        It refines data adaptively depending on flag status. (removeDuplication, staticFrequency)
        "removeDuplication" :It removes duplicated data.
        "staticFrequency" :The data will have a constant timestamp index. 
        
        data: DataFrame
            input data
        refine_param: json
            refine_param['removeDuplication']={'flag':(Boolean)} 

            refine_param['staticFrequency'] ={'flag':(Boolean), 'frequency':[None|timeinfo]}

            refine_param['ststicFreeuncy']['frequnecy'] == None -> infer original frequency and make static time stamp.
        
    
        :return data : New refined DataFrame output
        :return data: DataFrame

       Example
        -------
            >>> data = input_data
            >>> from KETIPrePartialDataPreprocessing.data_preprocessing import DataPreprocessing
            >>> refine_param = {'removeDuplication': {'flag': True}, 'staticFrequency': {'flag': True, 'frequency': '1H'}}
            >>> output = DataPreprocessing().get_refinedData(data, refine_param) 

        """
        result = data.copy()
        if refine_param['removeDuplication']['flag']== True:
            from KETIPrePartialDataPreprocessing.data_refine import redundancy
            result = redundancy.ExcludeRedundancy().get_result(result)

        if refine_param['staticFrequency']['flag'] == True:
            from KETIPrePartialDataPreprocessing.data_refine import frequency
            inferred_freq = refine_param['staticFrequency']['frequency']
            result = frequency.RefineFrequency().get_RefinedData(result, inferred_freq)

        self.refinedData = result
        return self.refinedData
    
    def get_errorToNaNData(self, data, outlier_param):

        """
        This function gets data with more NaN. This function converts data identified as errors to NaN. This module finds fake data generated due to network errors, etc., and converts it to NaN.

        Example
        -------
        >>> outlier_param = {'certainErrorToNaN': {'flag': True}, 'unCertainErrorToNaN': {----}}
        >>> datawithMoreCertainNaN, datawithMoreUnCertainNaN = DataPreprocessing().get_errorToNaNData(data, outlier_param)

        data: dataFrame
            input data
        outlier_param: json
            outlier Param

        return: dataFrame
            result

        **Two Outlier Detection Modules**::

            datawithMoreCertainNaN, datawithMoreUnCertainNaN
        
        ``datawithMoreCertainNaN``: Clear Error to NaN

        ``datawithMoreUnCertainNaN``: UnClear Error to NaN

        
            
        """
        from KETIPrePartialDataPreprocessing.error_detection import errorToNaN
        self.datawithMoreCertainNaN = errorToNaN.errorToNaN().getDataWithCertainNaN(data, outlier_param['certainErrorToNaN'])
        self.datawithMoreUnCertainNaN = errorToNaN.errorToNaN().getDataWithUncertainNaN(self.datawithMoreCertainNaN, outlier_param['unCertainErrorToNaN'])
        return self.datawithMoreCertainNaN, self.datawithMoreUnCertainNaN

    def get_imputedData(self, data, imputation_param):
        """ Get imputed data

        :param data: input data
        :type data: DataFrame 
        :param refine_param: imputation_param
        :type refine_param: json
        
        :return: New Dataframe after imputation
        :rtype: DataFrame
        
        example
            >>> imputation_param = {'serialImputation': {'flag': True, 'imputation_method': [{'min': 0, 'max': 3, 'method': 'KNN', 'parameter': {}}, {'min': 4, 'max': 6, 'method': 'mean', 'parameter': {}}], 'totalNonNanRatio': 80}}
            >>> output = DataPreprocessing().get_imputedData(data, outlier_param)
        """
        self.imputedData = data.copy()
        if imputation_param['serialImputation']['flag'] == True:
            from KETIPrePartialDataPreprocessing.data_imputation import Imputation
            self.imputedData = Imputation.SerialImputation().get_dataWithSerialImputationMethods(self.imputedData, imputation_param['serialImputation'])

        return self.imputedData

    # Add New Function

class packagedPartialProcessing(DataPreprocessing):
    '''This class provides funtion having packged preprocessing procedure.
    '''
    def __init__(self, process_param):
        '''Set process_param related to each preprocessing module.

        :param process_param: process_param
        :type process_param: json 

        '''
        
        
        self.refine_param = process_param['refine_param']
        self.outlier_param = process_param['outlier_param']
        self.imputation_param = process_param['imputation_param']
    
    def PartialProcessing(self, input_data, flag):
        """ Produces only one clean data with one preprocessing module.

        :param input_data: input data
        :type input_data: DataFrame 
        :param flag: preprocessing name
        :type flag: string
        
        :return: New Dataframe after one preprocessing (flag)
        :rtype: DataFrame
        
        example
            >>> output = packagedPartialProcessing().PartialProcessing(data, 'refine')
            
        """
        if flag == 'refine':
            result = self.get_refinedData(input_data, self.refine_param)
        elif flag =='errorToNaN':
            result = self.get_errorToNaNData(input_data, self.outlier_param)
        elif flag == 'imputation':
            result = self.get_imputedData(input_data, self.imputation_param)
        elif flag == 'all':
            result = self.allPartialProcessing(input_data)
        return result

    def allPartialProcessing(self, input_data):
        """ Produces partial Processing data depending on process_param

        :param input_data: input data
        :type input_data: DataFrame 
        
        :return: New Dataframe after preprocessing according to the process_param
        :rtype: json (key: process name, value : output DataFrame)
        
        example
            >>> output = packagedPartialProcessing(process_param).allPartialProcessing(data)
            
        """
        ###########
        refined_data = self.get_refinedData(input_data, self.refine_param)
        ###########
        datawithMoreCertainNaN, datawithMoreUnCertainNaN = self.get_errorToNaNData(refined_data, self.outlier_param)
        ###########
        imputed_data = self.get_imputedData(datawithMoreUnCertainNaN, self.imputation_param)
        ###########
        result ={'original':input_data, 'refined_data':refined_data, 'datawithMoreCertainNaN':datawithMoreCertainNaN,
        'datawithMoreUnCertainNaN':datawithMoreUnCertainNaN, 'imputed_data':imputed_data}
        return result

    ## Get Multiple output
    def MultipleDatasetallPartialProcessing(self, multiple_dataset):
        """ Produces multiple DataFrame Processing result depending on process_param

        :param input_data: multiple_dataset
        :type input_data: json (having DataFrame value) 
        
        :return: json having New Dataframe after preprocessing according to the process_param
        :rtype: json (value : output DataFrame)
        
        example
            >>> output = packagedPartialProcessing(process_param).MultipleDatasetallPartialProcessing(multiple_dataset)
        """
        output={}
        for key in list(multiple_dataset.keys()):
            output[key] = self.allPartialProcessing(multiple_dataset[key])
        return output

