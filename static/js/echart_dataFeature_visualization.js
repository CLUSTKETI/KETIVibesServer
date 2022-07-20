function IDListEmpty(empty_id_list){
	empty_id_list.forEach(function(item,index){ $(item).empty()})
}

function makeMetaDescription(id_root, dataset){
	if(dataset){
        let title = '';
        let blockDiv;
		$.each(dataset, function(key, value_list){
            blockDiv = $('<div></div>');
			title = $('<dt class="btn btn-outline-dark btn-sm"></dt>').html(key.toUpperCase());
			blockDiv.append(title);
			
            if (Array.isArray(value_list)){
				value_list.forEach(function(value) {
					var info = $('<code></code>').html(value + ' ');
					blockDiv.append(info);
                    
				});	
                id_root.append(blockDiv);
			}else {
				var info = $('<span></span>').html(value_list);
				blockDiv.append(info);
                id_root.append(blockDiv);
			}
            

		});
	}else {
        id_root.append("<p>No Information</p>");
    }
}

function getPieChartOption(dataSet){
    var option = {
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend:{
            top: 'top',
            left: 'center'
        },
        series: [
            
            {
            name: 'Access From',
            type: 'pie',
            radius: ['45%', '60%'],
            labelLine: {
                length: 30
            },
            label: {
                formatter: '{a|{a}}{abg|}\n{hr|}\n  {b|{b}：}{c}  {per|{d}%}  ',
                backgroundColor: '#F6F8FC',
                borderColor: '#8C8D8E',
                borderWidth: 1,
                borderRadius: 4,
                rich: {
                a: {
                    color: '#6E7079',
                    lineHeight: 22,
                    align: 'center'
                },
                hr: {
                    borderColor: '#8C8D8E',
                    width: '100%',
                    borderWidth: 1,
                    height: 0
                },
                b: {
                    color: '#4C5058',
                    fontSize: 14,
                    fontWeight: 'bold',
                    lineHeight: 33
                },
                per: {
                    color: '#fff',
                    backgroundColor: '#4C5058',
                    padding: [3, 4],
                    borderRadius: 4
                }
                }
            },
            data: dataSet
            }
        ]
        };
        return option
}

function getBar2ChartOption(legend_data, xaxis_data, yaxis_name, yaxis_formatter, dataset1, dataset2){
    // 두개의 데이터를 비교하는 막대 그래프를 생성하는 함수
    var option;
    option = {
        tooltip: {
            show: true,
            trigger: 'axis',
            formatter: '{a} <br/>{b}: {c}'
        },
        legend: {
            left:'center',
            top:'93%',
            data: legend_data
        },
        xAxis: {
            type: 'category',
            data: xaxis_data
        },
        yAxis: {
            type:'value',
            name: yaxis_name,
            axisLabel: {
                formatter: '{value} '+yaxis_formatter
            }
        },
        series: [
            {
            name: 'All',
            label: {
                formatter: '{a} <br/>{b}: {c}',
                backgroundColor: '#F6F8FC',
                borderColor: '#DDDDDD',
                borderWidth: 1,
                borderRadius: 4,
                rich: {
                a: {
                    color: '#6E7079',
                    lineHeight: 22,
                    align: 'center'
                },
                hr: {
                    borderColor: '#DDDDDD',
                    width: '100%',
                    borderWidth: 1,
                    height: 0
                },
                b: {
                    color: '#4C5058',
                    fontSize: 14,
                    fontWeight: 'bold',
                    lineHeight: 33
                },
                }
            },
            data: dataset1,
            type: 'bar',
            color:'#DDDDDD'
            },
            {
            name: 'This Measurement',
            label: {
                formatter: '{a} <br/>{b}: {c}',
                backgroundColor: '#F6F8FC',
                borderColor: '#8C8D8E',
                borderWidth: 1,
                borderRadius: 4,
                rich: {
                  a: {
                      color: '#6E7079',
                      lineHeight: 22,
                      align: 'center'
                  },
                  b: {
                      color: '#4C5058',
                      fontSize: 24,
                      fontWeight: 'bold',
                      lineHeight: 33
                  }
                }
            },
            data: dataset2,
            type: 'bar',
            color:'#D9ADAD'
            }
        ]
    };
    return option
}

function getLinePointoneMeanChartOption(label, xaxis_name, yaxis_name, yaxis_formatter, line_dataset, point_idx, point_data){
    // 하나의 line Chart 와 하나의 (x,y) 값을 Point로 그리며 line Chart의 평균값 그려주는 함수
    var option;
    option = {
        title: {
            text: label,
            left: 'center',
            top: 'top',
            textStyle:{fontSize:20}
            },
        xAxis: {
            type:'category',
            name:xaxis_name,
            axisLabel: {
                show: false
            },
            axisTick: {
                show: false
            }
        },
        yAxis: {
            type: 'value',
            name:yaxis_name,
            axisLabel: {
                formatter: '{value} '+yaxis_formatter
              }
        },
        series: [
            {
                data: line_dataset,
                type: 'line',
                itemStyle: { color: 'rgba(98, 109, 126, 1)' },
                markLine: {
                data: [{ type: 'average', name: 'Avg' }]
                }
            },
            {
                data: [[point_idx, point_data]],
                type: 'line',
                itemStyle: { color: 'rgba(249, 247, 124, 1)' },
                markPoint: {
                data: [
                    {
                    type: 'max',
                    name: 'data'
                    }
                ],
                symbol: 'pin',
                symbolSize: 45,
                itemStyle: { color: 'rgba(249, 247, 124, 1)' }
                }
            }
        ]
    };
    return option
}

function getLinesPointoneChartOption(legend_data, dataset, xaxis_name, yaxis_name, yaxis_formatter, point_data){
    // 여러개의 line 데이터와 point data 해야함 -> 여러개 데이터를 받아 여러개의 data를 그리는 걸로 수정해야함. 현재 2개로 한정되어있음. - 모든 ms, label 별로 여러개 line 그릴때 사용할것
    var option;
    option = {
        legend: {
            left:'center',
            top:'93%',
            data: legend_data
        },
        xAxis: {
            type:'category',
            name:xaxis_name,
            axisLabel: {
                show: false
            },
            axisTick: {
                show: false
            }
        },
        yAxis: {
            type: 'value',
            name: yaxis_name,
            axisLabel: {
                formatter: '{value} '+ yaxis_formatter
                }
        },
        series: getLinesSeries(dataset, point_data, legend_data)

    };
    return option
}


function getLinesSeries(arguments, point_data, legend_data){
    var line_series = []

    for(var i in arguments){
        line_series.push({
            name: legend_data[i],
            data: arguments[i],
            type: 'line'
        })
    }
    line_series.push({
        type: 'effectScatter',
        symbolSize: 10,
        data: point_data
    })

    return line_series
}

function DbMsColumnInfo(db_id, ms_id, column_id, db_name, ms_name, selectedCO, dbmscolumninfo_get_url){
	//console.log("DB/Ms/Column Info Function")
    const param = {'db_name':db_name, 'ms_name':ms_name, 'column_name':selectedCO};
	$.ajax({
		type    : "POST",
		url        : dbmscolumninfo_get_url,
		contentType: "application/json",
		dataType:"JSON" ,
		data: JSON.stringify(param)
	   })
	   .done(function (response) {
            var data = response
            data_js =JSON.parse(data)
            //console.log(data_js)
			var db_info_set = $("#" + db_id)
			var ms_info_set = $("#" + ms_id)
			var column_info_set = $("#" + column_id)
			makeMetaDescription(db_info_set, data_js.db_info)
			makeMetaDescription(ms_info_set, data_js.ms_info)
			makeMetaDescription(column_info_set, data_js.column_info)
       })
       .fail(function(data, textStatus, errorThrown){
        console.log("fail in get addr");
        console.log(textStatus)
        console.log(errorThrown)
        console.log(data)
    });
}

function AnalysisResult(data_feature_analysis_info_id, db_name, ms_name, column, labelmeta_get_url, analyzer_name, time_key, clicked_value){
    var feature_analysis_set = $("#" + data_feature_analysis_info_id).addClass('feature_labelInformation col-xl-12 col-lg-12')
	param = {'db_name':db_name, 'ms_name':ms_name, 'column_name':column, 'analyzer_name':analyzer_name, 'time_key':time_key}
    var no_information = $('<div><h2 class="m-0 font-weight-bold text-black">There is no Information</h2></div>')
	$.ajax({
		type: "POST",
		url: labelmeta_get_url,
		contentType: "application/json",
		dataType:"JSON" ,
		data: JSON.stringify(param)
	   })
	   .done(function (response) {
		    console.log("success")
		   	var data = response
            data_js =JSON.parse(data)
            console.log(data_js)

            if(clicked_value === "Label Information"){
                LabelInformation(feature_analysis_set, data_js, no_information, column)
            }else{
                TimeInformation(feature_analysis_set, data_js, no_information, ms_name, column, time_key)
            }
        }).fail(function(data, textStatus, errorThrown){
            console.log("fail in get addr");
            console.log(textStatus)
            console.log(errorThrown)
            console.log(data)
            });
}

function LabelInformation(feature_analysis_set, data_js, no_information, column){
    console.log(data_js.ms_meta[0])
    if (data_js.ms_meta[0] !== null){
        var feature_level_label_chart = $('<canvas></canvas>').attr('id', column+"_labelcount_chart")
        feature_analysis_set.append(feature_level_label_chart) 
        
            var chartDom = document.getElementById(column+"_labelcount_chart");
            var myChart = echarts.init(chartDom);
            var dataSet = data_js.ms_meta
            var option = getPieChartOption(dataSet)
            chartSize(myChart, $('.feature_labelInformation').width(), $('.feature_labelInformation').width()/3*2)
            myChart.setOption(option);
    }else{
        feature_analysis_set.append(no_information) // 실행이 안됨
    }
}

function TimeInformation(feature_analysis_set, data_js, no_information, ms_name, column, time_key){
    var feature_timeInfo_bar_chart_row = $('<div></div>').addClass('feature_timeInfo_bar_chart row col-xl-12 col-lg-12')
    feature_analysis_set.append(feature_timeInfo_bar_chart_row)
    
    if(data_js.number_of_datas === "None" || data_js.number_of_datas === null){ // 아무 데이터도 없을 경우 or 데이터가 하나뿐인데 해당 데이터가 모두 None 일때
        console.log("No Data")
        feature_timeInfo_bar_chart_row.append(no_information)
    }else{ // 데이터가 존재할 시
        var feature_timeInfo_total_line_chart_row = $('<div></div>').addClass('feature_timeInfo_total_line_chart row col-xl-12 col-lg-12')
        var feature_timeInfo_line_chart_row = $('<div></div>').addClass('feature_timeInfo_line_chart_row col-xl-12 col-lg-12')
        feature_analysis_set.append($('<hr class="sidebar-divider"></hr>'))
        feature_analysis_set.append(feature_timeInfo_total_line_chart_row)
        feature_analysis_set.append($('<hr class="sidebar-divider"></hr>'))
        feature_analysis_set.append(feature_timeInfo_line_chart_row)

        var timeInform_bar_chart = $('<canvas></canvas>').attr('id', "timeInfo_bar_chart").addClass('col-xl-8 col-lg-8')
        var timeInform_bar_explain_box = $('<div></div>').addClass('col-xl-4 col-lg-4')
        feature_timeInfo_bar_chart_row.append(timeInform_bar_chart)
        feature_timeInfo_bar_chart_row.append(timeInform_bar_explain_box)
        if(data_js.db_meta){ // DB 데이터 존재할 시
            if(data_js.number_of_datas === 1 || data_js.number_of_datas >=100){ // 비교대상이 없고 선택한 데이터만 존재할 경우 or 비교대상 데이터 갯수가 100개 이상일 경우 - db,ms bar
                console.log("datas 1")   // 아직 코드 안짬 -> 케이웨더는 제외 경우임으로 차후에 짤 계획
            }else{ // 비교대상의 데이터가 존재하며 1~99개 일때 - db,ms bar + ms line
                //bar chart
                var chartDom = document.getElementById('timeInfo_bar_chart');
                var myChart = echarts.init(chartDom);
               
                var legend_data = ['All', 'This Measurement']
                var xaxis_data = data_js.db_meta.label
                var yaxis_name = column+" Mean"
                var dataset1 = data_js.db_meta.resultValue.map(listRound)
                var dataset2 = Object.values(data_js.ms_meta).map(listRound)
                var yaxis_formatter = unitNone(data_js.column_info.unit)
                var option = getBar2ChartOption(legend_data, xaxis_data, yaxis_name, yaxis_formatter, dataset1, dataset2)
                
                chartSize(myChart, $('#timeInfo_bar_chart').width(), $('#timeInfo_bar_chart').height())
                option && myChart.setOption(option);
                getExplainBox(timeInform_bar_explain_box, "bar", column, ms_name, data_js, time_key)
                
                // All MS 여러 Line
                var timeInform_total_line_chart = $('<canvas></canvas>').attr('id', label+"timeInfo_total_line_chart").addClass('col-xl-8 col-lg-8')
                var timeInform_total_line_explain_box = $('<div></div>').addClass('col-xl-4 col-lg-4')
                feature_timeInfo_total_line_chart_row.append(timeInform_total_line_chart)
                feature_timeInfo_total_line_chart_row.append(timeInform_total_line_explain_box)

                var chartDom = document.getElementById(label+"timeInfo_total_line_chart");
                var myChart = echarts.init(chartDom);
                var legend_data = []
                var dataset = []
                var point_dataset = []
                for(var l in data_js.notSort_None_total_ms_meta){
                    console.log(l)
                    legend_data.push(l)
                    dataset.push(data_js.notSort_None_total_ms_meta[l].values)
                    point_dataset.push([data_js.notSort_None_total_ms_meta[l].idx, data_js.ms_meta[l]])
                }
                var option =  getLinesPointoneChartOption(legend_data, dataset, xaxis_name, yaxis_name, yaxis_formatter, point_dataset)
                
                chartSize(myChart, $('#'+label+'timeInfo_total_line_chart').width(), $('#'+label+'timeInfo_total_line_chart').height())
                option && myChart.setOption(option);
                getExplainBox(timeInform_total_line_explain_box, "total_line", column, ms_name)

                // 단독 Line 그래프
                getExplainBox(feature_timeInfo_line_chart_row, "line", column, ms_name, data_js)
                for (var label in data_js.total_ms_meta){
                    if(data_js.total_ms_meta[label].values !== null){
                        var timeInform_line_chart = $('<canvas></canvas>').attr('id', label+"timeInfo_line_chart").addClass('col-xl-6 col-lg-6')
                        feature_timeInfo_line_chart_row.append(timeInform_line_chart)
                        
                        round_datas = data_js.total_ms_meta[label].values.map(listRound)
                        round_data = Math.round(data_js.ms_meta[label]*100)/100
                        
                        var chartDom = document.getElementById(label+"timeInfo_line_chart");
                        var myChart = echarts.init(chartDom);
                        
                        var xaxis_name = 'Measurements'
                        var line_dataset = round_datas
                        var point_idx = data_js.total_ms_meta[label].idx
                        var point_data = round_data

                        var option = getLinePointoneMeanChartOption(label, xaxis_name, yaxis_name, yaxis_formatter, line_dataset, point_idx, point_data)
                        
                        chartSize(myChart, $('.feature_timeInfo_line_chart_row').width(), $('#'+label+'timeInfo_line_chart').height())
                        option && myChart.setOption(option);
                    }
                }
            }
        }else{// DB 데이터 없음
            console.log("db 없음")   // 아직 코드 안짬.
                                    // DB 없이 MS들만 존재할 경우 MS의 결과값만 표출 예정
        }
    }
}

function unitNone(unit_meta){
    if(unit_meta){
        var yaxis_formatter = unit_meta
    }else{
        var yaxis_formatter = ""
    }
    return yaxis_formatter
}
function listRound(each_element){
    return Math.round(each_element*100)/100
}

function barExplain(column, time_key, labels){
    if(time_key === "holiday"){
        return column+" 에 대해 Holiday 와 notHoliday 에 따른 평균 값을 All 평균 값과 비교한 결과이다."
    }else if(time_key === "work"){
        return column+" 에 대해 Work Time 과 notWork Time 에 따른 평균 값을 All 평균 값과 비교한 결과이다."
    }else if(time_key === "time_step"){
        
        return column+" 에 대해 시간 구간을 "+labels+ " 으로 나눈 후 그에 따른 평균 값을 All 평균 값과 비교한 결과이다."
    }
}

function getExplainBox(box_name, chart_type, column=null, ms_name=null, data_js=null, time_key=null){
    //var timeInform_explain_title = $('<h5 class="mb-2 explain_title">Explain</h5>')
    //box_name.append(timeInform_explain_title)

    var timeInform_explain = $('<div class="explain"></div>')
    box_name.append(timeInform_explain)

    if(chart_type === "bar"){
        timeInform_explain.html(barExplain(column, time_key, Object.keys(data_js.ms_meta)))
    }else if(chart_type === "line"){
        timeInform_explain.html("선택한 "+ms_name+" 에서 "+column+" 의 시간에 따른 평균값 순위는 아래와 같다.<br>- "+lineExplain(data_js)+" 이다.")
    }else if(chart_type === "total_line"){
        timeInform_explain.html("선택한 "+column+" 을 갖는 모든 데이터들의 시간 구간에 따른 평균 값을 시간별로 나열한 그래프이다. 그래프에 표시된 Point가 " +ms_name+ " 을 의미한다.")
    }
}

function lineExplain(data_js){
    var line_explain_str = []
    for (var label in data_js.total_ms_meta){
        if(data_js.total_ms_meta[label].values !== null){
            var x = data_js.total_ms_meta[label].idx + 1
            line_explain_str.push(label+" 에서는 "+x+" 번째 ")
        }
    }
    console.log(line_explain_str)
    return line_explain_str
}

function chartSize(myChart, canvas_width, canvas_height){
    window.onresize=function(){
        myChart.resize();
    }
    //canvas_width =$(canvas_id).width()
    //console.log("canvas_height : "+ canvas_height)
    myChart.resize({
            width: canvas_width,
            height: canvas_height
            });
}