function update_bar(prefix_id){
	var actual = parseInt(document.getElementById(prefix_id + "_actual").value);
	var max = parseInt(document.getElementById(prefix_id + "_max").value);
	var max_previous = parseInt(document.getElementById(prefix_id + "_max_previous").value);
	var base_max_txt = 89;

	//get SVGs
	var rect_no_border = document.getElementById(prefix_id + '_rect_no_border');
	var rect_base_white = document.getElementById(prefix_id + '_rect_base_white');
	var actual_txt = document.getElementById(prefix_id + '_actual_txt');
	var max_txt = document.getElementById(prefix_id + '_max_txt');

	if(max<actual){
		document.getElementById(prefix_id + "_max").value = actual;
		return false;
	}

	var actual_prt = ((actual * 100) / max);

	rect_no_border.setAttribute("width", actual_prt + "%");

	actual_txt.setAttribute("x", (actual_prt-3) + "%");
	actual_txt.textContent = actual;

	var max_previous_prt = ((max_previous * 100) / max);
	rect_base_white.setAttribute("width", max_previous_prt + "%");

	max_txt.setAttribute("x", base_max_txt + "%");
	max_txt.textContent = max;
	max_txt_color = "black";
	if(max > max_previous){
		max_txt_color = "#00D300";
	}else if (max < max_previous) {
		max_txt_color = "#D0342B";
	}
	max_txt.style.fill = max_txt_color;

	if (max > 99) {
		max_txt.setAttribute("x", (base_max_txt - 5) + "%");
	}
	if (max > 999) {
		max_txt.setAttribute("x", (base_max_txt - 10) + "%");
	}

}

function update_bar_svg_object(prefix_id){
	var actual = parseInt(document.getElementById(prefix_id + "_actual").value);
	var max = parseInt(document.getElementById(prefix_id + "_max").value);
	var max_previous = parseInt(document.getElementById(prefix_id + "_max_previous").value);
	var base_max_txt = 93;

	//get SVGs
	var svg = document.getElementById(prefix_id + "_bar");
	var svgDoc = svg.contentDocument;
	var rect_no_border = svgDoc.getElementById(prefix_id + '_rect_no_border');
	var rect_base_white = svgDoc.getElementById(prefix_id + '_rect_base_white');
	var actual_txt = svgDoc.getElementById(prefix_id + '_actual_txt');
	var max_txt = svgDoc.getElementById(prefix_id + '_max_txt');

	if(max<actual){
		document.getElementById(prefix_id + "_max").value = actual;
		return false;
	}

	var actual_prt = 0;
	if(actual > 0){
		actual_prt = ((actual * 100) / max);
	}

	rect_no_border.setAttribute("width", actual_prt + "%");

	var correction = 3;
	if(actual_prt <= 0){
		correction = 0;
	}
	actual_txt.setAttribute("x", (actual_prt - correction) + "%");
	actual_txt.textContent = actual;

	var max_previous_prt = 0;
	if(max_previous > 0){
		max_previous_prt = ((max_previous * 100) / max);
	}
	if(max == max_previous){
		max_previous_prt = 100;
	}

	rect_base_white.setAttribute("width", max_previous_prt + "%");

	max_txt.setAttribute("x", base_max_txt + "%");
	max_txt.textContent = max;
	max_txt_color = "black";
	if(max > max_previous){
		max_txt_color = "#00D300";
	}else if (max < max_previous) {
		max_txt_color = "#D0342B";
	}
	max_txt.style.fill = max_txt_color;

	if (max > 99) {
		max_txt.setAttribute("x", (base_max_txt - 8) + "%");
	}
	if (max > 999) {
		max_txt.setAttribute("x", (base_max_txt - 9) + "%");
	}

}

function update_bar_up(prefix_id){
	var max = document.getElementById(prefix_id + "_max");
	max.value = (parseInt(max.value) + 1);
	update_bar_svg_object(prefix_id);
}
function update_bar_down(prefix_id){
	var max = document.getElementById(prefix_id + "_max");
	max.value = (parseInt(max.value) - 1);
	update_bar_svg_object(prefix_id);
}

function changeNumber(prefix_id, field){
	changeBackgroundInputs(prefix_id, field)

        if(field == 'number'){
		var input = document.getElementById(prefix_id + '_' + field);
                var volume_size = document.getElementById(prefix_id + '_size');
                if(volume_size && parseInt(input.value) > parseInt(volume_size.value)){
                        volume_size.value = input.value;
                }
		changeBackgroundInputs(prefix_id, 'size')
        }
}

function changeBackgroundInputs(prefix_id, field){
	var input_actual = document.getElementById(prefix_id + '_' + field + '_actual');
        var input = document.getElementById(prefix_id + '_' + field);

        if(parseInt(input.value) > parseInt(input_actual.value)){
                input.style.background = '#2CB04B';
                input.style.color = '#FFFFFF';
        }else if (parseInt(input.value) < parseInt(input_actual.value)) {
                input.style.background = '#7DA6B8'; //#006CCF//darkblue
                input.style.color = '#FFFFFF';
        }else{
                input.style.background = '';
                input.style.color = '#000000';
        }
}
