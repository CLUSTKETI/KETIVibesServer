
let eChart  = {

  drawOneEchart : (url, data, location, type, block_no) => {
    
  
    $.ajax({
      url : url,
      method: "POST",
      data : data,
      dataType : "json",
      aync : false,
      beforeSend: function () {
        $("#loading-prograss").show();
        $("#loading-prograss")
          .show()
          .css({
            top: $(document).scrollTop() + $(window).height() / 3 + "px",
            left: $(window).width() / 2.5 + "px",
          });
      },
      success: function (result) {
        
        result = JSON.parse(result);
        result = result["result"];
  
        $(".collapse").removeClass("show"); // 이전 result 화면 모두 닫기
  
        result_box = makeObj.init.makeCardBox(type, block_no);
        $(location).append(result_box);
        option = eChart.getOption(result);

        var myChart = echarts.init(document.getElementById(type));
        myChart.setOption(option);

        let value_data = result["value"];
        let num_length, full_length, count_result;  

        for (data_key in value_data) {
          num_length = value_data[data_key].filter(Number).length;
          full_length = value_data[data_key].length;
          count_result = full_length - num_length;
          
        }
        count_result = Number(count_result).toLocaleString();

        $('.block_'+block_no+'_result_'+type).find(".nan_for_" + type).html(count_result);

      },

      error: function (e) {
        alert("에러를 확인해 주세요. :: \n" + e.statusText);
        console.log("ajax error ::" + e);
      },
      fail: function (echart_manipulation) {
        console.log("ajax fail ::" + e);
      },
      complete: function () {
        $("#loading-prograss").hide();
      },
    });
  }

  ,getOption : (d) => {
    let value_data = d["value"],
      index_data = d["index"];
    column_list = Object.keys(value_data);
  
    option = {
      title: { text: "" },
      tooltip: { trigger: "axis" },
      legend: { data: column_list },
      grid: { left: "10%", right: "10%", bottom: "10%", containLabel: true },
      toolbox: {
        feature: { saveAsImage: {} },
      },
      xAxis: {
        type: "category",
        boundaryGap: false,
        data: index_data,
      },
      yAxis: {
        type: "value",
        min: null,
        max: null,
      },
      series: [],
    };
  
    for (key in value_data) {
      option["series"].push({
        name: key,
        type: "line",
        stack: "Total",
        connectNulls: false,
        data: value_data[key],
      });
      yAxis_min = option["yAxis"]["min"];
      yAxis_max = option["yAxis"]["max"];
      if (yAxis_min == null) {
        option["yAxis"]["min"] = Math.min(...value_data[key].filter(Number));
        option["yAxis"]["max"] = Math.max(...value_data[key].filter(Number));
      } else {
        if (yAxis_min > value_data[key].min)
          option["yAxis"]["min"] = Math.min(...value_data[key].filter(Number));
        if (yAxis_max < value_data[key].max)
          option["yAxis"]["max"] = Math.max(...value_data[key].filter(Number));
      }
    }
    return option;
  }

} //end eChart



let func_paramBar = {


  clickRestartBtn : (e) => {           
       
    let block_no = $(e).attr("data-block-no");  

    makeObj.init.addBlock(block_no);
  

  } 
  , clickSaveBtn : (e) => {    
    
    let url      = '/DataPreprocessing/saveData';
    let block_no = $(e).attr("data-block-no");
    let param    = {"parameter" : block_no};
    param        = JSON.stringify(param);

    $.ajax({
        url : url
        , method : 'post'
        , data : param
        , dataType : 'json'
        , success : function(e){
       
          result = JSON.parse(e);
          result = result["result"];

          alert("csv 파일 저장이 완료되었습니다. \n경로 :: " + result);

          let innerHTML = '<div class="block_complt_inn"><h4>block '+block_no+'</h4><p>'+result+'</p></div>';

          //TODO: 마지막 csv 파일 저장 후 적당한 크기의 블락이 보이도록 
          $("#block_" + block_no).html(innerHTML);
          $("#block_" + block_no).addClass("block_complt");
        }
        , error : function(e){
          console.log(e);
        }

    });    

  }
  ,

  /*
  Refinement frequency parameter toggle
  */
  toggleRefinementParam : (e) => {

    let target = $(e).find("input").attr("id");
  
    if (target === "Auto") {
      //여기서는 frequency Auto
      $("#form_manual").hide();
    } else {
      //여기서는  frequency Manual
      $("#form_manual").show();
  
    }
  }

  , getRefinementParam : (block_no) => {
    /*
      Refinement parament 생성      
    */
     
    let param = {
      "parameter": { 'removeDuplication': { 'flag': "True" }, 'staticFrequency': { 'flag': "True", 'frequency': 'None' } }
    }
  
    let d_flag = $(".paramBar_"+block_no).find("input[id=Duplication]").is(":checked"); //true or false
    let s_flag = $(".paramBar_"+block_no).find("input[id=Frequency]").is(":checked"); //true or false				
    let checked_btn_name = $(".paramBar_"+block_no).find("input[name=options]:checked").attr("id"); //Auto or Manual		
    let p_value;
    
    if (checked_btn_name === "Auto") {
      p_value = 'None';

    } else if (checked_btn_name === "Manual") {
      p_value = $("#form_manual").val();
  
    }
  
    if(d_flag == true){ d_flag = "True" }else{ d_flag = "False"   }
    if(s_flag == true){ s_flag = "True" }else{ s_flag = "False"   }

    param['parameter']['removeDuplication']['flag'] = d_flag;
    param['parameter']['staticFrequency']['flag'] = s_flag;
    param['parameter']['staticFrequency']['frequency'] = p_value;
  
    return param;

  }
  ,getRangeCheckParam : (block_no) =>{
    /*
      RangeCheck parament 생성
    */
      let o_flag = $(".paramBar_"+block_no).find("input[id=OutOfRange]").is(":checked"); //true or false

      if ( o_flag == true){
        param = { "parameter" : {'flag': 'True'} }
      }else{
        param = { "parameter" : {'flag': 'False'} }
      }     

      return param;


  }

  , addOutlierDetectionForm : (d) => {
    
    let block_no = d;
    let html = makeObj.paramBarObj.makeOutlierDetectionForm(block_no);
    $(".paramBar_"+block_no).find(".paramBarInn").append(html);
    let input_name = 'percentile';

    //add event
    func_paramBar.addValidationFunc(input_name, block_no);    
    
  }

  , addImputationForm : (d) => {
    
    let block_no = d;
    let html = makeObj.paramBarObj.makeImputationForm(block_no);
    $(".paramBar_"+block_no).find(".paramBarInn").append(html);    

  }

  ,returnAlgParam : (d1, d2, block_no, cnt) => {

    let algorithm     = d1;
    let percentile    = d2;
    let obj           = {};
    let period        = 24*60; //33-1, if method influx
    
    let algParamValue = ( $("#outlierDetectionForm_" + block_no + "_" + cnt).find(".alg_param_"+block_no)[0] !== undefined ? $(".alg_param_"+block_no)[0].value : 0  )   
     
    if( typeof(algParamValue) == 'string' && (algParamValue !== '')){ algParamValue = parseInt(algParamValue) };

    if( algorithm == "IF" ){
      
      //let IF_estimators = $("#IF_param_" + block_no + "_" + cnt).val();
      if ( algParamValue.length == '' ) algParamValue = 100;

      //IF_estimators 변경
      obj = {
        'IF_estimators': algParamValue, // ensemble에 활용하는 모델 개수, i(default: 100, 데이터 크기에 적합하게 설정) 
        'IF_max_samples': 'auto', // 각 모델에 사용하는 샘플 개수(샘플링 적용), int or float(default: 'auto') 
        'IF_contamination': (100-percentile)/100, //'auto', # 모델 학습시 활용되는 데이터의 outlier 비율, ‘auto’ or float(default: ’auto’, float인 경우 0 초과, 0.5 이하로 설정)
        'IF_max_features': 1.0, // 각 모델에 사용하는 변수 개수(샘플링 적용), int or float(default: 1.0)
        'IF_bootstrap': 'False'
      }

    }else if( algorithm == "KDE" ){
      //test

      //let KDE_leaf_size = $("#KDE_param_" + block_no + "_" + cnt).val();
      if ( algParamValue.length == '' ) algParamValue = 40;

      // Multivariable 변경 
      obj = {
        'KDE_bandwidth': 1.0, //# kernel의 대역폭, float(default: 1.0)
        'KDE_algorithm': 'auto', //# 사용할 tree 알고리즘, {‘kd_tree’,‘ball_tree’,‘auto’}(default: ’auto’) 중 택 1
        'KDE_kernel': 'gaussian', //# kernel 종류, {'gaussian’, ‘tophat’, ‘epanechnikov’, ‘exponential’, ‘linear’, ‘cosine’}(default: ’gaussian’) 중 택 1
        'KDE_metric': 'euclidean', //# 사용할 거리 척도, str(default: ’euclidean’)
        'KDE_breadth_first': 'True', //# breadth(너비) / depth(깊이) 중 우선순위 방식 정의, bool, True: breadth or False: depth
        'KDE_leaf_size': algParamValue
      }

    }else if( algorithm == "LOF" ){

      //Neighbors (1~100) 변경
      //let LOF_neighbors = $("#LOF_param_" + block_no + "_" + cnt).val();
      if ( algParamValue.length == '' ) algParamValue = 20;

      obj = {
        'LOF_neighbors': algParamValue, //# 가까운 이웃 개수, int(default: 20)
        'LOF_algorithm': 'auto', //# 가까운 이웃을 정의하기 위한 알고리즘, {‘auto’, ‘ball_tree’, ‘kd_tree’, ‘brute’}(default: ’auto’) 중 택 1f
        'LOF_leaf_size': 30, //# tree 알고리즘에서의 leaf node 개수, int(default: 30)
        'LOF_metric': 'minkowski', //# 이웃을 정의하기 위한 거리 척도, str or callable(default: ’minkowski’)
        'LOF_contamination':0.1 //# 오염 정도 (default: 0.2) (0~0.2]
      }
    
    }else if( algorithm == "MoG" ){ 

      // Components
      //let MoG_components = $("#MoG_param_" + block_no + "_" + cnt).val();
      if ( algParamValue.length == '' ) algParamValue = 1;

      obj = {
        'MoG_components': algParamValue, //# mixture에 활용하는 component의 개수, int(default: 1)
        'MoG_covariance': 'full', //# {‘full’, ‘tied’, ‘diag’, ‘spherical’}(default: ’full’) 중 택 1
        'MoG_max_iter': 100 //# EM 방법론 반복 횟수, int(default: 100)
      }    

    }else if( algorithm == "SR" ){

      // Multivariable 불가능해 보임
      obj = {
        'SR_series_window_size': parseInt(period/2), //# less than period, int, 데이터 크기에 적합하게 설정
        'SR_spectral_window_size': period, // # as same as period, int, 데이터 크기에 적합하게 설정
        'SR_score_window_size': period *2
      }    
    
    }else if( algorithm == "IQR" ){
      //weight (1~100)
      //let weight = $("#IQR_param_" + block_no + "_" + cnt).val();
      if ( algParamValue.length == '' ) algParamValue = 100;

      obj = {
        'weight':algParamValue
      }
    
    }else if( algorithm == "SD" ){
      //limit (1~100)
      //let limit = $("#SD_param_" + block_no + "_" + cnt).val();
      if ( algParamValue.length == '' ) algParamValue = 15;

      obj = {
        "period":period, 
        "limit":algParamValue
      }
    
    }

    return obj;

  }
  , subtOutlierDetectionForm : (e) => {
  
    let divToRemove = $(e).parent("div").parent("div[id^=outlierDetectionForm]");
    if( divToRemove.length == 1){
      // 이 폼을 삭제할 때 넘길 수 있는 파라미터가 모두 사라지게 된다면, do outlier detection 체크박스 자동 해제
      divToRemove.parent(".paramBarInn").find("input[type=checkbox]").attr("checked", false);
    }
    
    $(divToRemove).remove();

  }

 , subtImputationForm : (e) => {

    let divToRemove = $(e).parent("div").parent("div[id^=imputationForm]");
    if( divToRemove.length == 1){
      // 이 폼을 삭제할 때 넘길 수 있는 파라미터가 모두 사라지게 된다면, do outlier detection 체크박스 자동 해제
      divToRemove.parent(".paramBarInn").find("input[type=checkbox]").attr("checked", false);
    }
    $(divToRemove).remove();
 }


  , clickShowBtn : (e) => {    

    let mode            = $("#mode").attr("data-mode");
    let block_no        = $(e).attr("data-block-no");
    let li_on           = $("#stepblock_"+block_no).find("li[data-checked='on']");
    let li_data_checked = li_on.attr("id");
    let param, url, type;

    let raw_name      = li_data_checked;
    let raw_name_lgth = raw_name.length;    
    raw_name          = li_data_checked.slice(3, raw_name_lgth-2);

    let isExist = $(".block_"+block_no+"_result_"+raw_name).length;
    if(isExist > 0){
      $(".block_"+block_no+"_result_"+raw_name).remove();
    }
      
    /* Original */
    if (li_data_checked == 'li_Original_' + block_no) {
  
        
        param = JSON.stringify({
          "db_name": sessionStorage.getItem('db_name'),
          "ms_name": sessionStorage.getItem('ms_name'),
          "feature_name": sessionStorage.getItem('feature_name'),
          "data_num": sessionStorage.getItem('data_num'),
          "tagKey" : sessionStorage.getItem('tagKey'),
          "tagValue" : sessionStorage.getItem('tagValue') 
          
        });

        type = 'Original';
        if( mode == 'Original' ){
          url = '/DataPreprocessing/getNoProcessedData';          

        }else{
          url = '/DataPreprocessing/getOriginalData';       

        }
        
  
    /* Refinement */
    } else if (li_data_checked === 'li_Refinement_' + block_no) {
  
      param = func_paramBar.getRefinementParam(block_no);      
      param = JSON.stringify(param);
  
      url = '/DataPreprocessing/refinementData';
      type = 'Refinement';
  
    /* RangeCheck */  
    } else if (li_data_checked === 'li_RangeCheck_' + block_no) {

      param =  func_paramBar.getRangeCheckParam(block_no);  
      param = JSON.stringify(param);
  
      url = '/DataPreprocessing/getDataWithoutCertainOutlier';
      type = 'RangeCheck';
  
    /* OutlierDetection */
    } else if (li_data_checked === 'li_OutlierDetection_' + block_no) {
      
      param = {
        parameter : {
            flag : 'False'
            , param : {
                outlierDetectorConfig : []
            }
        }
     }   
    
     let flag = $("#chkbox_OutlierDetection_" + block_no ).is(":checked");
     
     if(flag == true){ 

          param["parameter"]["flag"]  = "True";  

          let al_lnth = $(".algorithm_"  + block_no ).length;

          for( let i = 0; i < al_lnth; i++ ){          

            let al_ = $(".algorithm_"  + block_no )[i].value;
            if (al_ == ''){alert('algorithm을 선택해 주세요.'); return;}    

            let pc_ = $(".percentile_"  + block_no )[i].value;
            if (pc_ == ''){alert('percentile을 입력해 주세요.'); return;} else { pc_ = parseInt(pc_) }
            
            let obj_ = {
              algorithm : al_
              ,percentile : pc_
              ,alg_parameter : func_paramBar.returnAlgParam(al_, pc_, block_no, i)
            }

            param["parameter"]["param"]["outlierDetectorConfig"].push(obj_);

          }//end for                  
    
     }
          
      param = JSON.stringify(param);
  
      url = '/DataPreprocessing/getDataWithoutUnCertainOutlier';
      type = 'OutlierDetection';
  
    /* Imputation */
    } else if (li_data_checked === 'li_Imputation_' + block_no) {

      param = {
        parameter : {
          serialImputation: {
              flag : 'False'
              , imputation_method : []
              , totalNonNanRatio : 100          
          }              
        }
      }

      let flag = $("#chkbox_Imputation_" + block_no ).is(":checked");
      
      if(flag == true){  

        let formLgth = $(".imputationForm_" + block_no).length;          
        
        param["parameter"]["serialImputation"]["flag"]  = "True"; 
        // todo : 각 인풋에서 데이터 가져와서 param 만들기              


        for( let i = 0; i < formLgth; i++){      

            let form    = $(".imputationForm_" + block_no)[i];
            let max_    = $(".imp_param_max_"  + block_no)[i].value;  
            let method_    = ($(".imp_param_method_" + + block_no)[i] !== undefined) ? $(".imp_param_method_" + + block_no)[i].value : '';             
            let totalNonNanRatio_    = $(".totalNonNanRatio_" + + block_no)[i].value;   
            
            if(max_ == ""){
              alert("max값을 지정해 주세요.");
              return;              
            }
            max_        = parseInt(max_); 
            if(totalNonNanRatio_ == ""){
              alert("totalNonNanRatio값을 지정해 주세요.");
              return;              
            }
            totalNonNanRatio_        = parseInt(totalNonNanRatio_);
  
            if(max_ > 100){              
              alert("max값은 100 이하로 설정해 주세요.");              
              return;
            }          

            let obj_       = {};
            obj_["min"]    = (i == 0 ? 0 : (parseInt($(".imp_param_max_"  + block_no )[i-1].value) +1));
            obj_["max"]    = max_;  
            if( obj_["min"] > obj_["max"] ){
              alert("max값을 확인해 주세요.");
              return;
            }

            
            param["parameter"]["serialImputation"]["totalNonNanRatio"] = totalNonNanRatio_;

            obj_["method"] = method_;

            //method 가 knn 이면 parameter 추가하기 
            if ( method_ == "KNN"){              
              obj_["parameter"] = {'n_neighbors': 10, 'weights': 'uniform', 'metric': 'nan_euclidean'};  

              //n_neighbors 받기 
              let n_neighbors = $(form).find(".knn_n_neighbors").val();
              if(n_neighbors == ""){
                alert("n_neighbors값을 지정해 주세요.");
                return;              
              }   

              obj_["parameter"]["n_neighbors"] = parseInt(n_neighbors);
              
            }else{
              obj_["parameter"] = {};
            }      

            param["parameter"]["serialImputation"]["imputation_method"].push(obj_);

        }//end for      
      
            
      }

    
      param = JSON.stringify(param);
  
      url = '/DataPreprocessing/getImputedData';
      type = 'Imputation';
  
    } else {
      alert("점검중 입니다.");
      return;
  
    }
    alert("서버에 넘어가는 파라미터 입니다 :: \n" + param);
    console.log(param);

    eChart.drawOneEchart(url, param, ".result_box", type, block_no);

  }

  , clickConfirmBtn : (e) => {

    let mode = $("#mode").attr("data-mode");    
    let block_step = $(e).attr("data-block-no");
    let li_on, li_data_checked, dataLgth;
 
    li_on               = $("#stepblock_"+block_step).find("li[data-checked='on']");  
    li_data_checked     = li_on.attr("id");
    li_data_checked     = li_data_checked.slice(3);
    dataLgth            = li_data_checked.lastIndexOf("_");
    li_data_checked     = li_data_checked.slice(0,dataLgth);       
   

    $.ajax({
      url: "/DataPreprocessing/getCurrentStep",
      method: "get",
      dataType: "json",
      aync: false,
      success: function (d) {  
        let result = JSON.parse(d);
        result     = result["result"];       

        //mode 별 분기
        if (mode == "Original"){
          makeObj.stepBarObj.changeStep('Original', block_step);

        }else{
          if (li_data_checked == (result)) {
            makeObj.stepBarObj.changeStep(2, block_step);

          } else {          
            alert("Show 이후 Confirm 가능합니다.");
              
          } 
        }         
      },
      error: function (d) {
        console.log(d);

      }
    });
  
  }

  , addValidationFunc : (input_name, block_no) => {
    //input 입력값 유효성 검사를 하는 기능    
    $("."+input_name+"_"+block_no).on('keyup',function(){
            
      let $input = $(this).val();     

      if($input > 100 || $input < 0 ){       
        $(this).val('');
        alert(input_name + " 범위는 1~100 입니다.");

        return;
      }

    });

  }

  , changeImputationMethod : (e, block_no) => {
    //method가 knn일 경우 파라미터 폼 생성

    let $value = $(e).val();
    let knnParam ='';

    if( $value == 'KNN'){  
      knnParam += 
      '<div class="col-sm-12 KNN_param_'+block_no+'" >'
        + '<div class="font-weight-bold mt-2 mb-1">[KNN Parameter]</div>'
        + '<ul>'
        + '<li> <span class="font-weight-bold">n_neighbors :</span> <input type="number" class="form-control knn_n_neighbors" placeholder="ex ) 10"/> </li>'
        + '<li> <span class="font-weight-bold">weights :</span> uniform </li>'
        + '<li> <span class="font-weight-bold">metric :</span> nan_euclidean </li>' 
        + '</ul>'
      + '</div>';

    }else{
      $(e).parent("div").parent(".imputationForm_" + block_no).find(".KNN_param_"+block_no).remove();
    }
  
    //해당 폼에 어펜드
    $(e).parent("div").parent(".imputationForm_" + block_no).append(knnParam); 

  }

 

} 
//end func_paramBar

let makeObj = {

    init : {
      startOriginalStep : (e) => {
        //TODO : 오리지날 데이터가 결과 데이터가 된다. 
        let curBarCount  = e;        
        let innerBlock   = 
        '<div class="row mt-4" id="resultBar_'+curBarCount+'" >'
            + '<div class="col-md-4 " >'
            + '<input type="hidden" id="steplevel_'+curBarCount+'" value="" />'
            +	'<div class="row barWrapper">'
            +		'<div class="stepBar_'+curBarCount+' stepblock mr-2">'
            +			'<ul class="list-group" id="stepblock_'+curBarCount+'">'
            +				'<li class="list-group-item li_step" id="li_Original_'+curBarCount+'" data-checked="on">'
            +					'<span class="fa_span"></span><span>Original</span>'
            +				'</li>'
            +			'</ul>'
            +		'</div>'                
            +		'<div class="stepblock p-4 paramBar_'+curBarCount+'"></div>'
                
            +	'</div>'
            + '</div>'

            +'<div class="col-md-8">'
            +	'<div class="result_box" id="result_box_'+curBarCount+'"></div>'
            +'</div>'
            +'</div>';
            
       $("#searchBar_"+curBarCount ).after(innerBlock);
       
      }
      , makeInner : (nextSearchBarNumber) => {
        let code =        
              '<div class="col-sm-10">'                  
              +'<div class="border bg-white p-3">'    
              +'<div class="form-row clearfix" id="searchBar_'+nextSearchBarNumber+'">'

              +'<div class="form-group col-sm-2">'
                +'<select class=" form-select form-control" id="select1_'+nextSearchBarNumber+'">'
                +'<option>선택</option>'
                +'</select>'
              +'</div>'
              +'<div class="form-group col-sm-2">'
                +'<select class=" form-select form-control" id="select2_'+nextSearchBarNumber+'">'
                +'<option>선택</option>'
                +'</select>'
              +'</div>'

            


              +'<div class="form-group col-sm-1">'
                +'<select class=" form-select form-control" id="select3_'+nextSearchBarNumber+'">'
                +'<option>선택</option>'
                +'</select>'
              +'</div>'

              +'<div class="form-group col-sm-1">'
                +'<input type="date" class="form-control" id="startDt_'+nextSearchBarNumber+'" value="start_'+nextSearchBarNumber+'" />'

              +'</div>'
              +'<div class="form-group col-sm-1">'
                +'<input type="date" class="form-control" id="endDt_'+nextSearchBarNumber+'" value="end_'+nextSearchBarNumber+'" />'
              +'</div>'
              
              +'<div class="form-group col-sm-1">'
              + '<select class="form-control process_mode">'
                + '<option value="Original">Original</option>'
                + '<option value="Auto_P">Auto P</option>'
                + '<option value="Manual_P">Manual P</option>'
              + '</select>'                  
              +'</div>' 

              +'<div class="form-group col-auto">'
                +'<input type="button" class="form-control btn btn-primary" value="Submit" id="submit_'+nextSearchBarNumber+'" />'
              +'</div>'
              +'</div>'

              +'</div>'
            +' </div>';        

        return code;
      }
      
      ,addBlock : (d) =>{

        let curSearchBarCount, nextSearchBarNumber, innerHTML;
        
        let block_length = $("div[id^=block_]").length + 1;

        if ( d === "new"){
          //초기화
          innerHTML = 
          '<div class="row" id="block_'+block_length+'" >'
            + makeObj.init.makeInner(block_length);       
          +'</div>'; 

          $("#init").append(innerHTML);  
          makeObj.init.afterAddBlock(block_length);

        }else{
          //restart 버튼 클릭 시      
          let block_no = d;          
          innerHTML = makeObj.init.makeInner(block_no);           

          $("#block_"+block_no).html(innerHTML);
          makeObj.init.afterAddBlock(block_no);
        }            

      }
      , afterAddBlock : (block_no) => {
      
        makeObj.stepBarObj.changeStep(1, block_no);  
  
        let select_1 = new Promise(function (resolve, reject) {  
            let get_url = '/DataIngestion/db_list';         
    
            $.get(get_url, function (d) {
                let result = JSON.parse(d);
                let data = result['result'];
      
                makeSelect(data, 'select1_'+block_no);
                //$('#select1_'+block_no).val(data[0]);
      
                resolve(data);
            })

        });
  

          let dm = '';
          let ms = '';
          select_1.then(function (result) {
            //MS
            let val1 = $('#select1_'+block_no).val();
            let get_url = '/DataIngestion/measurement_list/' + val1;
            
            return new Promise(function (resolve, reject) {
              
              $.get(get_url, function (d) {
                let result2 = JSON.parse(d);
                let data = result2['result'];
                makeSelect(data, 'select2_'+block_no);
      
                dm = val1; ms = data[0];
                let rs = { "dm": val1, "ms": data[0] };

                resolve(rs);

              });
            });
      
      
          }).then(function (result) {

            let db_name = result["dm"];
            let ms_name = result["ms"];
      
            searchTagList(db_name, ms_name, block_no);
      
          }).then(function (result) {
            /* 태그 키 밸류 검색하기 */
            searchTagValue(result);
      
          }).catch((err) => {
            console.log("에러를 확인해 주세요 :: " + err);
      
          }).then(function (d){
            /* feature */
            let get_url = '/DataIngestion/featureList/' + dm + '/' + ms;
            $.get(get_url, function (d2) {
                let result = JSON.parse(d2);
                let data = result["result"];
                makeSelect(data, 'select3_'+block_no);

                //시작 날짜와 마지막 날짜 매핑하기
                makeObj.init.setDateTime(block_no);        
      
            });
      
          })
      
  
          $('#select1_'+block_no).on('change', function () {

            $("#tagKey_"+block_no).parent().remove(); $("#tagValue_"+block_no).parent().remove();

            val1 = $('#select1_'+block_no).val();
            $('#db_name').html(val1);
            get_url = '/DataIngestion/measurement_list/' + val1;
      
            $.get(get_url, function (result) {
              result = JSON.parse(result);
              data = result['result'];
              var feature2 = data;
              makeSelect(feature2, 'select2_'+block_no, true);
              makeSelect([], 'select3_'+block_no, true);
            })
            
          });
  
          $('#select2_'+block_no).on('change', function () {
            //MS
            val1 = $('#select1_'+block_no).val();
            val2 = $('#select2_'+block_no).val();
            $('#selected_db_name').html(val1);
            $('#selected_ms_name').html(val2);
            get_url = '/DataIngestion/featureList/' + val1 + '/' + val2;

            $("#tagKey_"+block_no).parent().remove(); $("#tagValue_"+block_no).parent().remove();
            makeObj.tagObj.searchTagList(val1, val2, block_no);
      

            $.get(get_url, function (result) {
              /* feature change*/
              result = JSON.parse(result);
              data = result['result'];
              var feature3 = data;
              makeSelect(feature3, 'select3_'+block_no, true);

              makeObj.init.setDateTime(block_no);
            });


          });
  
          $('#select3_'+block_no).on('click', function () {

            selected_feature = $('#select3_'+block_no).val();
            $('#selected_feature_name').html(selected_feature);
      
          });

    
        //제출
        $('#submit_'+block_no).on('click',function (e) {
         
              let val1 = $('#select1_'+block_no).val();
              let val2 = $('#select2_'+block_no).val();
              let val3 = $('#select3_'+block_no).val();
              let val4 = $('#tagKey_'+block_no).val();
              let val5 = $('#tagValue_'+block_no).val();
        
              if (val1 == '선택') {
                alert("대분류를 선택해 주세요.");
                return;
              }
              if (val2 == '선택') {
                alert("중분류를 선택해 주세요.");
                return;
              }
              if (val3 == '선택') {
                alert("소분류를 선택해 주세요.");
                return;
              }

              if( val4 == '선택' || val4 == undefined)  val4 = 'None';
              if( val5 == '선택' || val5 == undefined)  val5 = 'None';

              sessionStorage.setItem('db_name', val1);
              sessionStorage.setItem('ms_name', val2);
              sessionStorage.setItem('feature_name', val3);
              sessionStorage.setItem('data_num', 2000);
              sessionStorage.setItem('tagKey', val4);
              sessionStorage.setItem('tagValue', val5);

              // mode 에 따라서 결과 화면 표출 [Original, Auto, Manual]
              let mode = $("#searchBar_"+block_no).find(".process_mode").val();
              makeObj.init.changeSearchBar(block_no, mode, val1, val2, val3, val4, val5); 

              if( mode === 'Manual_P' ){                       
                makeObj.init.makeResultBar(block_no);          
                makeObj.stepBarObj.changeStep(1, block_no); //스텝 초기화

              }else if( mode === 'Original' ){
                makeObj.init.startOriginalStep(block_no);
                makeObj.stepBarObj.changeStep(1, block_no); 

                let btn = $(".paramBarBtn").find(".saveBtn");
                func_paramBar.clickShowBtn(btn);

              }else if( mode === 'Auto_P'){
                alert("진행 중 입니다."); return;
              }              

              $('#submit_'+block_no).remove();       
  
          });
    
        }
        , setDateTime : (block_no) => {
          //날짜 매핑하기
          let selectedDB = $('#select1_'+block_no).val();
          let selectedMS = $('#select2_'+block_no).val();

          let get_url_1 = '/DataIngestion/startTime/' + selectedDB + '/' + selectedMS;
          $.get(get_url_1, function (data) {
            result = JSON.parse(data)['result']
            $("#startDt_" + block_no).val(result.split(' ')[0]);

          });

          let get_url_2 = '/DataIngestion/lastTime/' + selectedDB + '/' + selectedMS;
          $.get(get_url_2, function (data) {
            result = JSON.parse(data)['result']
            $("#endDt_" + block_no).val(result.split(' ')[0]);

          });
        }

        ,changeSearchBar : (no, mode, val1, val2, val3, val4, val5) => {
            $("#searchBar_"+no).html('');
            let barHTML =

              '<h5 class="col m-0 font-weight-bold clearfix">'
              + '<span>'
              + 'DB Name: <code id="db_name" class="result1 mr-1">' + val1 + '</code>'
              + 'Measurement Name: <code id="ms_name" class="result1 ml-1 mr-1">' + val2 + '</code> '
              + 'Column Name: <code id="column_name" class="result1 mr-1">' + val3 + '</code>';

              if( val4 !== 'None') {
                barHTML += 'Tag Key: <code id="tk_name" class="result1 mr-1">' + val4 + '</code>';
              }
              if( val4 !== 'None') {
                barHTML += 'Tag Value: <code id="tv_name" class="result1 mr-1">' + val5 + '</code>';
              }
              barHTML += '</span>'

              + '<span class="float-right" id="mode" data-mode="'+mode+'" >[mode : '+mode+']</span>'
              + '</h5>';
          

            $("#searchBar_"+no).html(barHTML);
        }

        ,makeResultBar : (e) => {
          
          let curBarCount = e;        
          let innerBlock  = 
          
          '<div class="row mt-4" id="resultBar_'+curBarCount+'" >'
            + '<div class="col-md-4 " >'
            + '<input type="hidden" id="steplevel_'+curBarCount+'" value="" />'
            +	'<div class="row barWrapper">'
            +		'<div class="stepBar_'+curBarCount+' stepblock mr-2">'
            +			'<ul class="list-group" id="stepblock_'+curBarCount+'">'
            +				'<li class="list-group-item li_step" id="li_Original_'+curBarCount+'" data-checked="on">'
            +					'<span class="fa_span"></span><span>Original</span>'
            +				'</li>'
            +				'<li class="list-group-item li_step" id="li_Refinement_'+curBarCount+'" data-checked="off">'
            +					'<span class="fa_span"></span><span>Refinement</span>'
            +				'</li>'
            +				'<li class="list-group-item li_step" id="li_RangeCheck_'+curBarCount+'" data-checked="off">'
            +					'<span class="fa_span"></span><span>RangeCheck</span>'
            +				'</li>'
            +				'<li class="list-group-item li_step" id="li_OutlierDetection_'+curBarCount+'" data-checked="off">'
            +					'<span class="fa_span"></span><span>OutlierDetection</span>'
            +				'</li>'
            +				'<li class="list-group-item li_step" id="li_Imputation_'+curBarCount+'" data-checked="off">'
            +					'<span class="fa_span"></span><span>Imputation</span>'
            +				'</li>'
            +			'</ul>'
            +		'</div>'                
            +		'<div class="stepblock p-4 paramBar_'+curBarCount+'"></div>'
                
            +	'</div>'
            + '</div>'

            +'<div class="col-md-8">'
            +	'<div class="result_box" id="result_box_'+curBarCount+'"></div>'
            +'</div>'
            +'</div>';

        $("#searchBar_"+curBarCount ).after(innerBlock);

    }

    , makeCardBox : (d1, d2) => {
      
      let step_name  = d1;
      let block_no = d2;
      
      let result_box =
          '<div class="block_'+block_no+'_result_'+step_name+'">' +
          '<div class="card shadow mb-4 rounded-0">' +
          '<div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">' +
            '<a class="text-dark btn btn-link" data-toggle="collapse" data-target="#collapse_' + step_name + '" aria-expanded="true" aria-controls="collapse' +
            step_name + '">' + step_name + " result" + "</a>" +
            '<div>NaN : <code class="nan_for_' + step_name + '"></code></div>' +
          "</div>" +
          '<div id="collapse_' + step_name + '" class="collapse show"  data-parent="">' +
          '<div class="card-body">' +
          '<div id="' + step_name + '" style="width: 100%; height:500px"></div>' +
          "</div>" +
          "</div>" +
          "</div>" +
          "</div>";

        return $(result_box);
    }  

    } // end init{}
      
    
    , stepBarObj : {

      changeStep : (d, block_no) => {        

        const firstSet = d;
        // const arr_steps = ['Original', 'Refinement', 'RangeCheck', 'OutlierDetection', 'Imputation'];
      
        let li_on, li_on_index, li_data_checked;      
        if (firstSet == 1) {
            //초기화 시
            li_on = $("#stepblock_"+block_no).find("li[data-checked='on']");
            li_on_index = li_on.index();
            li_data_checked = li_on.attr("id");
      
        } else if (firstSet == 2){      
            //step 변경 시
            //let block_idx = $(e.target).attr("id").substr(-1); //todo: 추후 해당 인덱스 
        
            li_on = $("#stepblock_"+block_no).find("li[data-checked='on']");
            li_on_index = li_on.index();
        
            li_on = $("#stepblock_"+block_no).find("li").eq(li_on_index + 1);
            li_data_checked = li_on.attr("id");
            li_on_index = li_on_index + 1;
        
            //이전 step에 체크아이콘 표시하는 기능
            $(".fa_span").html('');

            for (let i = 0; i < li_on_index; i++) { 
              let faIcon = '<i class="fas fa-check mr-3"></i>';
              $("#stepblock_"+block_no).find("li").eq(i).find("span[class=fa_span]").html(faIcon);

            }        
      
        } else if (firstSet == 'Original') {          
            li_on = $("#stepblock_"+block_no).find("li"); //Original 1개
            li_on_index = 5; //고정
            li_data_checked = li_on.attr("id");

        }
      
        //sessionStorage.setItem('block_step', li_on_index);      
        
        if( li_on_index === 5){li_data_checked = "final"} 
        makeObj.paramBarObj.makeParambarInn(li_data_checked, block_no);
      
        // bar color 변경
        $("#stepblock_"+block_no).find("li").attr("data-checked", "off");
        $("#stepblock_"+block_no).find("li").attr("class", "list-group-item li_step");
        $(".paramBar_"+block_no).attr("class", "paramBar_"+block_no+ " stepblock p-4");
      
        li_on.attr("data-checked", 'on');
        li_on.attr("class", "list-group-item list-group-item-dark");
        $(".paramBar_"+block_no).attr("class", "paramBar_"+block_no+ " stepblock p-4 list-group-item-dark");
  
        // event add
        func_paramBar.addValidationFunc('percentile', block_no); 
      
      }      
  

    }
    , paramBarObj : {     
 
      makeParambarInn : (d, no) => {
        let block_no    = no;
        let block_step  = d;
        let innerBlock  = '<div class="paramBarInn pb-2">';
  
        // 임시 테스트용 고정, 반드시 삭제
        //block_step  = 'li_Imputation_1';  
        let mode = $("#mode").attr("data-mode");
        
        
        if (block_step === ('li_Refinement_'+block_no)) {
          innerBlock
            += '<h5>Refinement</h5>'  
            + '<div class="form-check mt-4">'
      
            + '<input class="form-check-input" type="checkbox" value="" id="Duplication" checked/>'
            + '<label class="form-check-label" for="Duplication">Duplication</label>'
            + '</div>'
            + '<div class="form-check mt-2">'
            + '<input class="form-check-input" type="checkbox" value="" id="Frequency" checked/>'
            + '<label class="form-check-label" for="Frequency">Frequency {m}</label>'
      
            + '</div>'
            + '<div class="mt-3 row">'
            + '<div class="col-md-6">'
      
            + '<div class="btn-group btn-group-toggle" data-toggle="buttons">'
            + '<label class="btn btn-secondary btn-sm active" onClick="func_paramBar.toggleRefinementParam(this)">'
            + '<input class="f_options" type="radio" name="options" id="Auto" autocomplete="on" checked> Auto'
            + '</label>'
            + '<label class="btn btn-secondary btn-sm" onClick="func_paramBar.toggleRefinementParam(this)">'
            + '<input class="f_options" type="radio" name="options" id="Manual" autocomplete="off"  > Manual'
            + '</label>'
            + '</div>'
      
           + '</div>'
            + '<div class="col-md-6">'
            + '<input class="form-control" id="form_manual" type="text" placeholder="ex) 60s" >'
            + '</div>'
      
            + '</div>'
      
        } else if (block_step === ('li_RangeCheck_'+block_no)) {
          innerBlock
            += '<h5>RangeCheck</h5>'  
            + '<div class="form-check mt-4 ">'
            + '<input class="form-check-input" type="checkbox" value="" id="OutOfRange" checked />'
            + '<label class="form-check-label" for="OutOfRange">Delete data out of range</label>'
            + '</div>'
        } else if (block_step === ('li_Original_'+block_no)) {
          
           
            if ( mode == 'Original'){
              innerBlock += '<h5>Final</h5>' ;
              innerBlock += '<div>Original 데이터가 최종 결과가 됩니다.</div>';

            }else{
              innerBlock
              += '<h5>Original</h5>' ; 
            }
  
        } else if (block_step === ('li_OutlierDetection_'+block_no)) {
  
          innerBlock
            += '<h5>OutlierDetection</h5>' 
            + '<div class="form-check mt-4  clearfix">'
              + '<input class="form-check-input" type="checkbox" value="" id="chkbox_OutlierDetection_'+block_no+'" checked />'
              + '<label class="form-check-label" for="chkbox_OutlierDetection_'+block_no+'">do outlier detection</label>'
              + '<span class="float-right cursor-pointer param_add_button" onClick="func_paramBar.addOutlierDetectionForm('+block_no+');"><i class="fa fa-plus-circle" aria-hidden="true"></i></span>'
            + '</div>';  
  
            let odForm = makeObj.paramBarObj.makeOutlierDetectionForm(block_no);  
            innerBlock += odForm;           
  
  
        } else if (block_step === ('li_Imputation_'+block_no)) {
          innerBlock
            += '<h5>Imputation</h5>' 
            + '<div class="form-check mt-4  clearfix">'
             + '<input class="form-check-input" type="checkbox" value="" id="chkbox_Imputation_'+block_no+'" checked />'
             + '<label class="form-check-label" for="chkbox_Imputation_'+block_no+'">do imputation</label>'
             + '<span class="float-right cursor-pointer param_add_button" onClick="func_paramBar.addImputationForm('+block_no+');"><i class="fa fa-plus-circle" aria-hidden="true"></i></span>'
            + '</div>';

            let form = makeObj.paramBarObj.makeImputationForm(block_no);  
            innerBlock += form; 
            
        }  
        innerBlock += "</div>";


        /* 버튼 영역 */

        if (block_step === "final" || mode == 'Original'){
          innerBlock 
          
          += '<div class="paramBarBtn pt-3">'
          + '<input type="button" class=" btn btn-primary mr-1 restartBtn" data-block-no="'+block_no+'" value="RESTART" onClick="func_paramBar.clickRestartBtn(this)"	/>'
          + '<input type="button" class=" btn btn-dark saveBtn" data-block-no="'+block_no+'" value="SAVE" onClick="func_paramBar.clickSaveBtn(this);"   />'
          + '</div>';
          
          $(".paramBar_"+block_no).html(innerBlock);          

        }else{
            
            innerBlock 
            += '<div class="paramBarBtn pt-3">'
              + '<input type="button" class=" btn btn-primary mr-1 showBtn" data-block-no="'+block_no+'" value="Show" onClick="func_paramBar.clickShowBtn(this)"	/>'
              + '<input type="button" class=" btn btn-dark confirmBtn" data-block-no="'+block_no+'" value="Confirm" onClick="func_paramBar.clickConfirmBtn(this);"   />'
              + '</div>';
              
            $(".paramBar_"+block_no).html(innerBlock);

        }     

  
      }
      , makeOutlierDetectionForm : (d) => {

        let block_no = d;
        let cnt = $("div[id^=outlierDetectionForm_" + block_no + "]").length; // cnt는 0부터 시작
        
        if (cnt > 1){ 
          alert("파라미터 폼 생성은 2개 까지 가능합니다.");
          return;

        }
        
        let param = 

              '<div class=" mt-3 p-3 border outlierDetectionForm_'+block_no+'" id="outlierDetectionForm_'+block_no+'_'+ cnt +'">'
                + '<div class=" pb-3 clearfix">'
                + '<span class="float-right" onclick="func_paramBar.subtOutlierDetectionForm(this);" ><i class="fa fa-minus-circle" aria-hidden="true"></i></span>'
                + '</div>'

                + '<div class="row">'
                  + '<div class="col-sm-5">'
                    + '<div>algorithm</div>'
                  + '</div>'
                  + '<div class="col-sm-7">'
                    + '<select class="form-control w-100 algorithm_'+block_no+'" onChange="makeObj.paramBarObj.makeAlgParameter(this, '+block_no+');">'
                        //+ '<option value=""  >선택</option>'
                        + '<option value="IF"  >IF</option>'
                        + '<option value="KDE" >KDE</option>'
                        + '<option value="LOF" >LOF</option>'
                        + '<option value="MoG" >MoG</option>'
                        + '<option value="SR"  >SR</option>'
                        + '<option value="IQR" >IQR</option>'
                        + '<option value="SD"  >SD</option>'
                    + '</select>'
                  + '</div>'
                + '</div>'

                + '<div class="row">'
                  + '<div class="col-sm-5"><div>percentile</div> <div>(1~100)</div></div>'
                  + '<div class="col-sm-7">'
                    + '<input class="form-control w-100 percentile_'+block_no+'" type="number" value="99" maxlength="3"/>'
                  + '</div>' 
                + '</div>'

                + '<div class="col-md-12 mt-3 alg_param_wrap_'+block_no+'" >'
                  + '<span>[IF] estimators</span>'
                  + '<input class="form-control alg_param_'+block_no+'" type="number" placeholder="Range) 1~100"  />'
                + '</div>'             
  
              + '</div>';
            
        return param;


      }
      , makeAlgParameter : (e, block_no) => {
  
          let param = $(e).val();
          let innerBlock = '';
          let paramArr =  
            {'IF' : 'estimators (1~100)', 
            'KDE' : 'leafSize (1~100)', 
            'LOF' : 'Neighbors (1~100)' , 
            'MoG' : 'Components (1~100)' , 
            'IQR' : 'weight (1~100)' , 
            'SD' : 'limit (1~100)' 
          }             
         
          if (paramArr[param] != undefined){
            innerBlock 
            += '<span>['+param+'] '+paramArr[param]+'</span>'
            + '<input class="form-control alg_param_'+block_no+'" type="number" placeholder="Range) 1~100"  />';
            //algorithm에 따른 파라미터 박스 생성  

          }else{
            innerBlock = '';
          }

          $(e).parents(".outlierDetectionForm_"+block_no).find(".alg_param_wrap_"+block_no).html(innerBlock); 

          //add event
          func_paramBar.addValidationFunc('alg_param', block_no);
          
  
      }

      , makeImputationForm : (block_no) => {

          let cnt = $("div[id^=imputationForm_" + block_no + "]").length; // cnt는 0부터 시작

          let formHTML 
              = '<div class="row border p-2 mt-4 mb-4 imputationForm_'+block_no+'" id="imputationForm_'+block_no+'_'+cnt+'" >'
              + '<div class="col-md-12 pb-3 clearfix">'
                + '<span class="float-right" onclick="func_paramBar.subtImputationForm(this, '+block_no+');" ><i class="fa fa-minus-circle" aria-hidden="true"></i></span>'
              + '</div>'
              + '<div class="col-sm-12 mt-1"><label>max</label><input type="number" class="form-control imp_param_max_'+block_no+'"  value=""  /></div>'
              + '<div class="col-sm-12 mt-1"><label>method</label>'
                    + '<select class="btn btn-secondary dropdown no-arrow rounded-0 form-control imp_param_method_'+block_no+'" onChange="func_paramBar.changeImputationMethod(this, '+block_no+');">'
                      //+ '<option value="">선택</option>'  
                      + '<option value="KNN">KNN</option>'
                      + '<option value="MICE">MICE</option>'
                      + '<option value="most_frequent">most_frequent</option>'
                      + '<option value="mean">mean</option>'
                      + '<option value="median">median</option>'
                      + '<option value="constant">constant</option>'
                      + '<option value="bfill">bfill</option>'
                      + '<option value="ffill">ffill</option>'
                      + '<option value="linear">linear</option>'
                      + '<option value="time">time</option>'
                      + '<option value="nearest">nearest</option>'
                      + '<option value="zero">zero</option>'
                      + '<option value="slinear">slinear</option>'
                      + '<option value="quadratic">quadratic</option>'
                      + '<option value="cubic">cubic</option>'
                      + '<option value="barycentric">barycentric</option>'
                      + '<option value="polynomial">polynomial</option>'
                      + '<option value="spline">spline</option>'              
                    + '</select>'                
               + '</div>'   
               + '<div class="col-sm-12 mt-1"><label>totalNonNanRatio</label>'
                + '<input type="number" class="form-control totalNonNanRatio_'+block_no+'"  value=""  />'
               + '</div>'


                + '<div class="col-sm-12 KNN_param_'+block_no+'" >'
                  + '<div class="font-weight-bold mt-2 mb-1">[KNN Parameter]</div>'
                  + '<ul>'
                  + '<li> <span class="font-weight-bold">n_neighbors :</span> <input type="number" class="form-control knn_n_neighbors" placeholder="ex ) 10"/> </li>'
                  + '<li> <span class="font-weight-bold">weights :</span> uniform </li>'
                  + '<li> <span class="font-weight-bold">metric :</span> nan_euclidean </li>' 
                  + '</ul>'
                + '</div>'   

              + '</div>';
      
          return formHTML;   
       
    
      }


    }//end paraBarObj
    
    ,tagObj : {

      searchTagList : (db_name, ms_name, block_no) => {

       
        let  ClassTxt = 'form-select form-control'; 
            
        if (db_name == undefined || ms_name == undefined) {
          throw new Error('no Tag');
        }
        
        let params = { db_name: db_name, ms_name: ms_name };
      
        /* 태그 키 검색하기 */
        let url = '/DataIngestion/tagList';
      
        $.ajax({
          method: 'post'
          , async : false
          , url: url
          , data: JSON.stringify(params)
          , dataType: 'json'
          , contentType: "application/json"
          , success: function (d) {
           
            let result = JSON.parse(d);
            result = result["result"];
            //makeSelect(result, tagKeyid, true, false);
            
            if (result.length != 0) {
             
              makeObj.tagObj.makeTagSelectBoxHTML("#select2_"+block_no, "tagKey_"+block_no, result);
              makeSelect(result, "tagKey_"+block_no, true, false);
                   
      
              $("#tagKey_"+block_no).on('change', function (e) {
                
                $("#tagValue_"+block_no).parent().remove();

                let tag_key = $(e.target).val();
                makeObj.tagObj.searchTagValue(db_name, ms_name, tag_key, block_no);
                if(tag_key !== '') $("#tagKey_"+block_no).val(tag_key);
              });

             
            }
      
           
      
            return result[0];
      
          }
          , error: function (e) {
            console.log("error occured :: " + e);
          }
      
        });


    }
    ,searchTagValue : (db_name, ms_name, tag_key, block_no) => {

      
      let  ClassTxt = 'btn btn-secondary dropdown no-arrow rounded-0 mr-1 ml-1'; 
      
      
      /*
      TagKey 선택 시, TagValue selectBox만드는 함수
      */
      //let $this = $(e.target).val();
      let $this = tag_key;
    
      let url = '/DataIngestion/distinctTagValue';
      let params = {
        db_name: db_name
        , ms_name: ms_name
        , tag_key: $this
      };
    
      $.ajax({
        method: 'post'
        , async : false
        , url: url
        , data: JSON.stringify(params)
        , dataType: 'json'
        , success: function (d) {
          let result = JSON.parse(d);
          result = result["result"];        
    
          if (result.length != 0) {            
            makeObj.tagObj.makeTagSelectBoxHTML("#tagKey_"+block_no, "tagValue_"+block_no, result);   
             makeSelect(result, "tagValue_"+block_no, true, false); 
              
    
          }
        }
      });
    }
    , makeTagSelectBoxHTML : ( existing, newBox, dataArr ) => {
        /*
        Domain과 Measurement 선택시, tagList가 있으면 
        selectBox html을 만들어주는 함수
        */
        let wrap = $(existing).parent();
        
        let ClassTxt = 'form-select form-control ';        
      
        let selectHTML = "<div class='form-group col-sm-1'><select id='"+newBox+"' class='"+ClassTxt+"' >";
      
        dataArr.map(function(e,i){
          selectHTML += "<option class='btn btn-secondary' value='"+e+"'>"+e+"</option>"
        });
      
        selectHTML += "</select></div>";
      
        $(wrap).after(selectHTML);
    
    
    }
    
   

    
  }
   
    

  
}

