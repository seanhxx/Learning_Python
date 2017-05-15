var ws = new WebSocket("ws://" + window.location.host + "/channel/" + jobID);
var txt_result = document.getElementById("result");

ws.onmessage = function(e) {
    txt_result.innerHTML = txt_result.innerHTML + e.data + "<br />";
    txt_result.scrollTop = txt_result.scrollHeight;
    progress(e.data);
}

ws.onopen = function() {
    ws.send(jobID);
}
if (ws.readyState == WebSocket.OPEN) ws.onopen();

var my_bar = document.getElementById("myBar");
var width = 1;
var stepWidth = 0;
var num1 = 0;
var num2 = 0;

var btn_download1 = document.getElementById("btn_download1");
var btn_download2 = document.getElementById("btn_download2");
var btn_download3 = document.getElementById("btn_download3");

function progress(text){

patt0 = /Starting\sremoting/;
if (patt0.test(text) == true){
    var id = setInterval(grow, 1, 3);
}

patt1 = /Connected\sto\smetastore/;
if (patt1.test(text) == true){
    var id = setInterval(grow, 1, 7);
}

patt2 = /Parse\sCompleted/;
if (patt2.test(text) == true){
    var id = setInterval(grow, 1, 10);
}

patt3 = /Generate\w+Projection/;
if (patt3.test(text) == true){
    var id = setInterval(grow, 1, 15);
}

patt4 = /\(\d+\/\d+\)/;
if (patt4.test(text) == true){
    string = patt4.exec(text)[0].slice(1, -1);
    pos = string.indexOf("/");
    num1 = Number(string.slice(0,pos));
    num2 = Number(string.slice(pos+1));
    if (num1 < num2){
        stepWidth = 15+num1*(80/num2).toFixed(2);
        var id = setInterval(grow, 1, stepWidth);
    }
}

patt_partComplete = /Analysis\sPartly\sComplete/;
if (patt_partComplete.test(text) == true){
    var id1 = setInterval(grow, 1, 100);
    var id2 = setTimeout(part_finish, 1000);
}

patt_complete = /Analysis\sComplete/;
if (patt_complete.test(text) == true){
    var id1 = setInterval(grow, 1, 100);
    var id2 = setTimeout(finish, 1000);
}

patt_fail = /Analysis\sFail/;
if (patt_fail.test(text) == true){
    var id = setTimeout(fail, 1000);
}

function grow(ceiling) {
    if (width >= ceiling) {
        clearInterval(id);
    } else {
        width++;
        my_bar.style.width = width + '%';
        my_bar.innerHTML = width * 1  + '%';
    }
}

function part_finish(){
    btn_download1.disabled = false;
    btn_download2.disabled = false;
    btn_download3.disabled = false;
    ws.close();
    alert('Warning: Analysis Partly Complete! Fail in Kruskal-Wallis function! Please extend the date range and make sure the input lot IDs are valid, then try again or contact Admin!');
}

function finish(){
    btn_download1.disabled = false;
    btn_download2.disabled = false;
    btn_download3.disabled = false;
    ws.close();
    alert('Info: Analysis Complete!');
}

function fail(){
    ws.close();
    alert('Error: Analysis Fail! Please make sure the input date range covers all lot IDs and make sure the input lot IDs are valid, then try again or contact Admin!');
}

}

