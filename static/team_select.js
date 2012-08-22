function prepare_picker(picker) {
    picker_name ="#" + picker + "_picker";
    // alert(picker_name);
    var space = $(picker_name);
    space.html("I'll be " + picker);
 
    
    space.click(function(e) {
	    //alert("you clicked!");
	    
	    $.getJSON('/_add_to_team/' + picker, 
		      {}, 
		      function (data) {
			  window.location = '/show_game/';
		      });
	    // because we have to get a facebook post request...
	    //alert("now redirecting!");
	    //window.location = '/show_game/';
	    //alert("redirection complete!");
	});
    

    
}


$(document).ready(function () {
	// alert("preparing blue");
	prepare_picker("red");
	prepare_picker("blue");
	// alert("blue prepared! :D");


    });