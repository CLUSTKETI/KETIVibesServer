const db_domain_pattern = {
  air: { icon: "fa-wind", color_style: "btn-warning" },
  weather: { icon: "fa-cloud-moon-rain", color_style: "btn-success" },
  farm: { icon: "fa-tractor", color_style: "btn-secondary" },
  energy: { icon: "fa-battery-full", color_style: "btn-danger" },
  bio: { icon: "fa-heartbeat", color_style: "btn-info" },
};


function get_db_style(item) {
/*
@ url example : /Index
@ return example: {icon_style:'fa-wind', color_style:'btn-warning'} 
@ how to use : DOMAIN 버튼 디자인
*/
  let icon_style = "fa-flag";
  let color_style = "btn-primary";
  const domain_pattern_keys = Object.keys(db_domain_pattern);

  domain_pattern_keys.forEach(function (domain_pattern_item) {
    if (item.includes(domain_pattern_item)) {
      icon_style = db_domain_pattern[domain_pattern_item]["icon"];
      color_style = db_domain_pattern[domain_pattern_item]["color_style"];
    }
  });

  return { icon_style: icon_style, color_style: color_style };
}


function check_selected(domain, sub_domain, ms_name) {
/*
	@ url example : /DataIntegration/dataSelection
	@ parameter example: ('air', 'indoor_중학교', 'ICW0W2000010')
	@ how to use : DOMAIN을 새로 선택 시, 기존에 이미 선택 되어있던 구역 정보가 담긴 버튼을 빨간색으로 표시하는 기능이다. 
*/
  if (domain in selected_list && sub_domain in selected_list[domain]) {
    ms_idx = selected_list[domain][sub_domain].indexOf(ms_name);
    if (ms_idx !== -1) return true;
  } else {
    return false;
  }
}


function make_name_onebutton(element, a_tag_class, i_tag_class) {
  /* 
	@ url example : /DataIntegration/dataSelection
	@ return example: 
	@ how to use : 장소 이름을 담은 MEASUREMENT LIST의 버튼 생성
*/
  const a_tag = $("<a></a>");
  const i_tag = $("<i></i>");

  a_tag.attr("data", element);

  a_tag.addClass("d-none d-sm-inline-block btn btn-sm rounded-0 button_ms");
  a_tag.addClass(a_tag_class);
  i_tag.addClass("fas fa-sm text-white");
  i_tag.addClass(i_tag_class);
  i_tag.html(element);
  a_tag.append(i_tag);

  return a_tag;
}

//ms_button_list.append(make_title_name_button("DB",selectedDB))
//ms_button_list.append(make_title_name_button("MS",selectedMS))
/*
 @url : 현재 사용하는 페이지 없는 함수 
 @ how to use : 컨펌 후 삭제 예정

function make_title_name_button(icon_text, name_text){
    const main_button = $('<a></a>');
    main_button.addClass("btn btn-primary text-white btn-icon-split");
    
	const icon = $('<span></span>');
    icon.addClass("icon");
    icon.html('<i>'+icon_text+'<i>');
    
	const name = $('<span></span>');
    name.addClass('text');
    name.html(name_text);
    main_button.append(icon);
    main_button.append(name);
    
	return main_button;
}
*/


function makeSelect(feature, select, btn = true, noChosenOption = false) {
  /*
	@ url : /DataDomainExploration/
	@ how to use : Measurement 블록의 DOMAIN SelectBox를 생성하는 함수
*/
  $("#"+select).empty();
  let option = $("<option >선택</option>");

  
  $("#"+select).append(option);

  if (Array.isArray(feature)) {
    feature.forEach(function (item, i) {
      option = $("<option></option>");
      if (btn) $(option).addClass("btn btn-secondary");

      if (i == 0 && noChosenOption == true) {
        $(option).attr("selected", true);
      } else {
        $(option).attr("selected", false);
      }

      $(option).val(item);
      $(option).html(item);

      $("#"+select).append(option);
    });
  }
}



function setValueDataInIDByAjax(
  urlAddress,
  parameter,
  ajax_method,
  Selector,
  ResultKey
) {
  /* 
 @ how to use : 
 - urlAddress 에서 Post/Get으로 받아온 json Data에 대해 ResultKey의 Value 값을 읽음. 
 - 읽어온 값은 html에 설정된 Selector의 html 값으로 할당함
*/
  $.ajax({
    url: urlAddress,
    data: parameter,
    dataType: "json",
    method: ajax_method,
    success: function (data) {
      result = JSON.parse(data);

      //console.log(result);
      text = result[ResultKey];
      $(Selector).html(text);
    },
    error: function (xhr, status, error) {
      alert(error);
    },
  });
}

function getValueDataByAjax(urlAddress, parameter, ajax_method, ResultKey) {
  text = "No";
  $.ajax({
    url: urlAddress,
    data: parameter,
    dataType: "json",
    method: ajax_method,
    contentType: "application/json",
    async: false,
    success: function (data) {
      result = JSON.parse(data);
      text = result[ResultKey];
    },
    error: function (xhr, status, error) {
      alert(error);
    },
  });
  return text;
}


function request_post(request_url, params, complete_func, datatype = "json") {
// post request using ajax
// params is dictionary type
/*
@url : /DataDomainExploration/ 등 
@how to use : paramter를 받아 ajax 진행
*/
  $.ajax({
    type: "POST",
    url: request_url,
    data: JSON.stringify(params),
    contentType: "application/json",
    dataType: datatype,
    error: function (error) {
      console.log(error);
    },
    success: function (data) {
      console.log("request success");
    },
    complete: complete_func,
  });
}


function makeSearchSelectBoxes(d) {
  /*
 @url : /DataVisualization
 @how to use : 상단 도메인 검색용 selectBox html 리턴
*/
  let selectBox = "";
  let boxArr = d;

  selectBox +=
    '<nav class="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow">' +
    '<ul class="navbar-nav ml-auto">' +
    '<div id="i_option" class="btn-group " role="group"></div>' +
    "<div>";

    boxArr.map(function(e,i){
      selectBox 
        += '<div class="d-inline-block searchBox"><select id ="' + e + '" class="btn btn-secondary dropdown no-arrow rounded-0 mr-1 ml-1"><option>선택</option></select></div>'; 
    });

    selectBox +=

      '<a href="#" class="btn btn-success dropdown no-arrow rounded-0 ml-1" id="submit">' 
        + 'submit<i class="fas fa-check"></i>' 
      + "</a>" 
      + "</div>" 

      + "</ul>" 
      + "</nav>";


  return selectBox;
}


function makeSelectBoxesWithBar(id1, id2, barId, Tag) {

/*
 @url : /DataVisualization
 @how to use : 상단 도메인 검색용 selectBox html 리턴, bar html 추가, tag_key, tag_value도 추가
*/
  let selectBox = "";
  selectBox +=
    '<nav class="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow">' +
    '<div class="navbar-nav ml-auto">' +
    '<div id="i_option" class="btn-group " role="group">' +
      '<select id ="' + id1 + '" class="btn btn-secondary form-control dropdown no-arrow rounded-0 mr-1 ">' +
      "</select>" +
      '<select id ="' + id2 + '" class="btn btn-secondary form-control dropdown no-arrow rounded-0 mr-1 ml-1 ">' +
      "</select>" ;

    if (Tag == true){     

      selectBox +=
      '<select id ="tagKey" class="btn btn-secondary form-control dropdown no-arrow rounded-0 mr-1 ml-1">' +
      "</select>" +
      '<select id ="tagValue" class="btn btn-secondary form-control dropdown no-arrow rounded-0 mr-1 ml-1 ">' +
      "</select>" ;

    }
    
      selectBox +=
    '<div class="slidecontainer ml-4">' +
      '<input type="range" min="1" max="5000" value="50" class="slider form-control text-xs " id="' + barId + '">' +
      '<span class="text-xs" >Data Number:</span> <span id="demo" class="text-xs"></span>' +
    "</div>" +
    '<a href="#" class="btn btn-success form-control dropdown no-arrow rounded-0 ml-4 " id="submit">' +
    'submit<i class="fas fa-check"></i>' +
    "</a>" +
    "</div>" +
    "</div>" +
    "</nav>";

  return selectBox;
}

function drawOneEchartData(url, data, location) {
 
  $.ajax({
    url: url,
    method: "POST",
    data: data,
    dataType: "json",
    //aync:false,
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
      $(location).empty();
      result = JSON.parse(result);

      //All 데이터 표출 card 생성
      option = DFtoLinePlotDataAll(result);
      var myChart = echarts.init(document.getElementById("dataAll"));
      myChart.setOption(option);
      let dataAllHeadText = "";

      //개별 데이터 표출 card 생성
      $.each(result, function (key, item) {
        result_box = drawCardBox(key);
        $(location).append(result_box);
        value_data = item["value"];
        index_data = item["index"];

        option = DFtoLinePlotData(value_data, index_data);
        var myChart = echarts.init(document.getElementById(key));
        myChart.setOption(option);

        //var count_result = value_data.filter(x=>x===null).length
        for (data_key in value_data) {
          num_length = value_data[data_key].filter(Number).length;
          full_length = value_data[data_key].length;
          count_result = full_length - num_length;
        }
        count_result = Number(count_result).toLocaleString();
        dataAllHeadText +=
          '<p class=""><span class="mr-2 font-weight-bold text-info">' +
          key +
          "</span>" +
          count_result +
          "</p>";
        $("#" + key + "_nanCount").html(count_result);
      }); //end each

      //$("#dataAll").parents(".card ").find("#dataAll_nanCount").html(dataAllHeadText);
      $("#dataAllResult").html(dataAllHeadText);
    },
    error: function (e) {
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

function makeTagSelectBoxHTML(existing, newBox, dataArr, SetClass=false, ClassTxt = '' ){
  /*
   Domain과 Measurement 선택시, tagList가 있으면 
   selectBox html을 만들어주는 함수
  */
  
  if(SetClass == false){
    ClassTxt = 'btn btn-secondary form-control dropdown no-arrow rounded-0 mr-1 ml-1 ';
  }

  let selectHTML = "<select id='"+newBox+"' class='"+ClassTxt+"' >";

  dataArr.map(function(e,i){
    selectHTML += "<option class='btn btn-secondary' value='"+e+"'>"+e+"</option>"
  });

  selectHTML += "</select>";

  //console.log(selectHTML);

  $(existing).after(selectHTML);


}

function searchTagList(db_name, ms_name, tag_key='', ClassTxt, tagKeyid='tagKey') {

  

  if(ClassTxt == undefined){
    ClassTxt = 'btn btn-secondary dropdown no-arrow rounded-0 mr-1 ml-1'; 
  }

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
        
       
        makeTagSelectBoxHTML("#measurement", tagKeyid, result, SetClass = true, ClassTxt = ClassTxt);
        makeSelect(result, tagKeyid, true, false);
        let idx = tagKeyid.lastIndexOf("_");
        let block_no = '';
        let tagValueId = 'tagValue';
        if(idx !== -1){
          block_no = tagKeyid.slice(idx + 1);
          
        }


        $("#"+tagKeyid).on('change', function (e) {
          $("#tagValue").remove();
          let tag_key = $(e.target).val();
          searchTagValue(db_name, ms_name, tag_key, block_no);
        });
      }

      if(tag_key !== '') $("#"+tagKeyid).val(tag_key);

      return result[0];

    }
    , error: function (e) {
      console.log("error occured :: " + e);
    }

  });

}

function searchTagValue(db_name, ms_name, tag_key, block_no='') {

  
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
        let tagKeyId = 'tagKey';
        let tagValueId = 'tagValue';
        if( block_no !== ''){
          tagKeyId = tagKeyId + '_' + block_no;
          tagValueId = tagValueId + '_' + block_no;
        }
      
         makeTagSelectBoxHTML("#"+tagKeyId, tagValueId, result, SetClass = true, ClassTxt = ClassTxt);   
         makeSelect(result, tagValueId, true, false); 

        //if(tag_value !== '') $(tagValueId).val(tag_value);

      }
    }
  });
}
