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

patt3 = /GenerateMutableProjection/;
if (patt3.test(text) == true){
    var id = setInterval(grow, 1, 15);
}

patt4 = /on\slocalhost\s\(\d+\/\d+\)/;
if (patt4.test(text) == true){
    string = patt4.exec(text)[0].slice(14, -1);
    pos = string.indexOf("/");
    num1 = Number(string.slice(0,pos));
    num2 = Number(string.slice(pos+1));
    if (num1 < num2){
        stepWidth = 15+num1*(80/num2).toFixed(2);
        var id = setInterval(grow, 1, stepWidth);
    }
}

patt5 = /Shutdown\shook\scalled/;
if (patt5.test(text) == true){
    var id = setInterval(grow, 1, 100);
}

patt6 = /Analysis\sComplete/;
if (patt6.test(text) == true){
    var id = setTimeout(finish, 1000);
}

patt_except = /Analysis\sFail/
if (patt_except.test(text) == true){
    var id = setTimeout(exception, 1000);
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

function finish(){
    btn_download1.disabled = false;
    btn_download2.disabled = false;
    ws.close();
    alert('Analysis Complete!');
}

function exception(){
    ws.close();
    alert('Error: Analysis Fail! Please extend the date range and try again or contact admin!');
}

}

