function changeNumber(prefix_id, field){
        changeBackgroundInputs(prefix_id, field)

        if(field == 'number'){
                var input = document.getElementById(prefix_id + '_' + field);
                var volume_size = document.getElementById(prefix_id + '_size');
                if(volume_size){ 
                        if(parseInt(input.value) > parseInt(volume_size.value)){
                            volume_size.value = input.value;
                        }
                        changeBackgroundInputs(prefix_id, 'size');
                }
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
