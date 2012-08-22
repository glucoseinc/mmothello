function set_number(number) {
    
    var space = $("#number");
    //alert("redirect debug 3");

    space.html(number);


    //alert("redirect debug 4");

}



function teleport() {

    url = "https://www.facebook.com/dialog/oauth/";
    url = url + "?client_id=" + "259989740776579";
    url = url + "&redirect_uri=" + "http://apps.facebook.com/mmothello";

    window.top.location = url;

	

}



$(document).ready(function() {
	// for some reason, this does not work in a for loop...
	$("#number").html(5);
	window.setTimeout(function () {set_number(4)},1000);
        window.setTimeout(function () {set_number(3)},2000);
        window.setTimeout(function () {set_number(2)},3000);
        window.setTimeout(function () {set_number(1)},4000);
        window.setTimeout(function () {set_number(0)},5000);


	window.setTimeout(function() {teleport()}, 5100);
	
    });
