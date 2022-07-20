function get_overlap_duration(selected_list,target){
	/*
	input
		selected_list = {
			"air":{
				"indoor_경로당":["IS1111","ID10000"],
				"outdoor_공원":["ED1112","DS2121"]
			},
			"traffic":{
				"seoul_subway":["hongdae"]
			}
		}

		target = $("table")
	*/
	target.empty()
	if(Object.keys(selected_list).length==0){
		target.empty()
		return
	}
	var start_list = []
	var last_list = []
	var db_list = []
	var ms_list = []
	// start time & last time 추출
	for(domain in selected_list){
		for(subdomain in selected_list[domain]){
			var db_name = domain+"_"+subdomain
			for(ms_nameidx in selected_list[domain][subdomain]){
				var ms_name = selected_list[domain][subdomain][ms_nameidx]
				start_time_url = '/DataIngestion/startTime/'+db_name+"/"+ms_name
				start_time = new Date(getValueDataByAjax(start_time_url, {}, "get", "result"))
				console.log(start_time)
				last_time_url = '/DataIngestion/lastTime/'+db_name+"/"+ms_name
				last_time = new Date(getValueDataByAjax(last_time_url, {}, "get", "result"))
				start_list.push(start_time)
				last_list.push(last_time)
				ms_list.push(ms_name)
				db_list.push(db_name)
			}
		}
	}
	first_time = Math.min.apply(null, start_list)
	last_time = Math.max.apply(null, last_list)
	overlap = [Math.max.apply(null, start_list),Math.min.apply(null, last_list)]
	total_area = (last_time-first_time) 
	if(overlap[1]-overlap[0]<=0){
		target.append('<h4 class="font-weight-bold" style="color: red">NO OVERLAP</h4><hr>')
	}
	else{
		target.append('<input type="text" name="daterange" id="config-demo" class="form-control"><br>')
		overlap_start_time = print_Date(new Date(overlap[0]))
		overlap_end_time = print_Date(new Date(overlap[1]))

		/*target.append('<h2 style="color: black">OVERLAP DURATION</h2><hr>')*/
		target.append('<h4 class="small font-weight-bold">'+overlap_start_time+'<span class="float-right">'+overlap_end_time+"</span></h4>")

		start = overlap[0]
		end = overlap[1]
		start_percent = (start-first_time) * 100 / total_area 
		area_percent = ((end-start) * 100) / total_area 

		info = '<div class="progress mb-4">\
					<div class="progress-bar bg-danger" role="progressbar" style="width:'+area_percent+'%; float: left; margin-left: '+start_percent+'%;" \
					aria-valuenow="20" aria-valuemin="0" aria-valuemax="100"></div></div><hr>'

		target.append(info)		
		start_overlap_for_range = new Date(overlap[0])
		end_overlap_for_range = new Date(overlap[1])
		$('input[name="daterange"]').daterangepicker({
			"timePicker": true,
			"minDate":convert_Date_for_range_selection(start_overlap_for_range),
			"maxDate":convert_Date_for_range_selection(end_overlap_for_range),
			"startDate": convert_Date_for_range_selection(start_overlap_for_range),
			"endDate": convert_Date_for_range_selection(end_overlap_for_range)
		}, function(start, end, label) {
			console.log('New date range selected: ' + start.format('YYYY-MM-DD') + ' to ' + end.format('YYYY-MM-DD') + ' (predefined range: ' + label + ')');
		});			
			
	}
	
	for(i=0; i<start_list.length; ++i){
		start = start_list[i]
		end = last_list[i]

		start_percent = (start.getTime()-first_time) * 100 / total_area 
		area_percent = ((end.getTime()-start.getTime()) * 100) / total_area  
		info = '<h4 class="small font-weight-bold">'+db_list[i]+'<span class="float-right">'+ms_list[i]+'</span>'+'<h4 class="small font-weight-bold">'+print_Date(start)+
					'<span class="float-right">'+print_Date(end)+'</span></h4>'+
					'<div class="progress mb-4">\
					<div class="progress-bar bg-info" role="progressbar" style="width: '+area_percent+'%; float: left; margin-left: '+start_percent+'%;"\
											aria-valuenow="20" aria-valuemin="0" aria-valuemax="100"></div></div>'
		target.append(info)
	}
}

function make_with_zero(num){
	new_num = num
	if(num<10){
		new_num = "0"+(new_num)
	}
	return new_num
}

function print_Date(myDate){
	month = make_with_zero(myDate.getMonth()+1)
	day = make_with_zero(myDate.getDate())
	return myDate.getFullYear()+'-'+month+'-'+day + " " //+ myDate.getHours() + ":" + myDate.getMinutes() + ":" + myDate.getSeconds();
}

function convert_Date_for_range_selection(myDate){
	month = make_with_zero(myDate.getMonth()+1)
	day = make_with_zero(myDate.getDate())
	return month+'/'+day + "/"+myDate.getFullYear() 
}

function extract_select_date(date_selection_id){
	// convert date format like 02/05/2021 -> 2021-02-04 from daterangepicker for sending python
	selected_date = $(date_selection_id).val().split("-")
	formatted_selected_date=[]
	selected_date.forEach(element => {
		divided =  element.trim().split("/")
		new_element = divided[2]+"-"+divided[0]+"-"+divided[1]
		formatted_selected_date.push(new_element)
	});
	return formatted_selected_date
}

function make_unselected(db_name, ms_name,domain, sub_domain, ms_idx){
	selected_list[domain][sub_domain].splice(ms_idx, 1)
		if(selected_list[domain][sub_domain].length==0){
			delete selected_list[domain][sub_domain]
			if(Object.keys(selected_list[domain]).length==0){
				delete selected_list[domain]
			}
		}
	$(".ms_item_selected").each(function() {
		var nodes= $(this)
		db_name_s = nodes.find(".db_name_s").html()
		ms_name_s = nodes.find(".ms_name_s").html()
		if(db_name_s==db_name && ms_name_s==ms_name){
			nodes.remove()
		}
	})
}