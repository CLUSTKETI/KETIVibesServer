
function DFtoLinePlotDataAll(result){

	result_box = drawCardBox("dataAll");
	$('.result_box').append(result_box);
	

	option = {
		title: {text: ''},
		tooltip: {trigger: 'axis'},
		legend: {data: ''},
		grid: {left: '10%',right: '10%',bottom: '10%',containLabel: true},
		toolbox: {
			feature: {saveAsImage: {}}
		},
		xAxis: []				
		,
		yAxis: [{
			type: 'value',
			min: null,
			max: null	
		}],
		series: [
			

		]
	}

	//color insert, 이름하드코딩
	var colors = {
		'original' : ['rgb(128, 255, 165)', 'rgb(1, 191, 236)'],
		'datawithMoreCertainNaN' : ['rgb(0, 221, 255)', 'rgb(77, 119, 255)'],
		'datawithMoreUnCertainNaN' : ['rgb(55, 162, 255)', 'rgb(116, 21, 219)'],
		'imputed_data' : ['rgb(255, 0, 135)', 'rgb(135, 0, 157)'],
		'refined_data' : ['rgb(255, 191, 0)', 'rgb(224, 62, 76)']

	};
	
	$.each(result, function(key2, item){
		value_data = item['value'];
		index_data = item['index']; // 1번만 넣기
	
		if(key2 !== 'original'){		
			
			if(option['xAxis'].length == 0){
				//x축 값을 맞추기 위한 것으로, original외에 x축 값이 모두 같다는 전제하에 1번만 넣는다. 
				option['xAxis'].push({
					type: 'category',
					boundaryGap: true,
					data: index_data
				})
			};
			
				//Total solar power 1번 회전
				for (key in value_data){
					
					option['series'].push({
						name:key2, 
						type:'line', 
						//stack:'Total', 
						connectNulls:false, 
						data:value_data[key],
						//smooth: true,
						lineStyle: { 
							width: 1,
							color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
								{
									offset: 0,
									color: colors[key2][1]
								}
								])
						},
						areaStyle: {
							opacity: 0.5,
							color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
								{
									offset: 0,
									color: colors[key2][0]
								}
								])
						},
						emphasis: {
							focus: 'series'
						}
						
						
					})
					yAxis_min = option['yAxis']['min']
					yAxis_max = option['yAxis']['max']
					if (yAxis_min == null){
						option['yAxis']['min'] = Math.min(...value_data[key].filter(Number))
						option['yAxis']['max'] = Math.max(...value_data[key].filter(Number))
					}else{
						if (yAxis_min > value_data[key].min) option['yAxis']['min'] = Math.min(...value_data[key].filter(Number))
						if (yAxis_max < value_data[key].max) option['yAxis']['max'] = Math.max(...value_data[key].filter(Number))
					}
				}//end for
		}
	});
	return option;

}

function DFtoLinePlotData(value_data, index_data){
	column_list = Object.keys(value_data)
		
	option = {
		title: {text: ''},
		tooltip: {trigger: 'axis'},
		legend: {data: column_list},
		grid: {left: '10%',right: '10%',bottom: '10%',containLabel: true},
		toolbox: {
			feature: {saveAsImage: {}}
		},
		xAxis: {
			type: 'category',
			boundaryGap: false,
			data: index_data
		},
		yAxis: {
			type: 'value',
			min: null,
			max: null	
		},
		series: [
			

		]
	}
	

	for (key in value_data){
		option['series'].push({
			name:key, 
			type:'line', 
			stack:'Total', 
			connectNulls:false, 
			data:value_data[key]
			
			
		})
		yAxis_min = option['yAxis']['min']
		yAxis_max = option['yAxis']['max']
		if (yAxis_min == null){
			option['yAxis']['min'] = Math.min(...value_data[key].filter(Number))
			option['yAxis']['max'] = Math.max(...value_data[key].filter(Number))
		}
		else{
			if (yAxis_min > value_data[key].min) option['yAxis']['min'] = Math.min(...value_data[key].filter(Number))
			if (yAxis_max < value_data[key].max) option['yAxis']['max'] = Math.max(...value_data[key].filter(Number))
		}
	}
	return option;

}

function DFtoBarPlot(result_xaxis, result_data){
	option = {
		xAxis: {
		  type: 'category',
		  data: result_xaxis
		},
		yAxis: {
		  type: 'value'
		},
		series: [
		  {
			data: result_data,
			type: 'bar'
		  }
		]
	};
	return option;
}