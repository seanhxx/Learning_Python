btn_showSample.onclick = function() {popUp()};
chk_box.onchange = function() {chk_chg()}

function popUp(){
    if(img.style.display == 'block'){
        img.style.display = 'none';
        btn_showSample.innerHTML = "Show Sample";
    }else{
         img.style.display = 'block';
         btn_showSample.innerHTML = "Hide Sample";
    }
}

function chk_chg(){
    if(chk_box.checked){
	lot_input.style.display = 'block';
	file_input.style.display = 'none';
	btn_showSample.style.display = 'none';
	document.getElementById("id_upload_file").required = false;
	document.getElementById("id_lot_ID").required = true;
    }else{
	 lot_input.style.display = 'none';
	 file_input.style.display = 'block';
	 btn_showSample.style.display = 'block';
	 document.getElementById("id_upload_file").required = true;
	 document.getElementById("id_lot_ID").required = false;
    }
}
