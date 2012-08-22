function ready_game_button() {

    space = $("#game_button");
    // alert("before click assignment");
    space.click(function (e) {
	    //alert("you clicked!" );
	    window.location = '/show_game/';
	    
	});

    // alert("after click assignment!");

}

function ready_instructions_button() {
    space = $("#instructions_button");
    // alert("before click assignment");
    space.click(function (e) {
            //alert("you clicked!" );
            window.location = '/instructions/';

        });

    // alert("after click assignment!");

}




$(document).ready(function() {
	$("#help_button").hide();
	ready_game_button();
	ready_instructions_button();
	// alert($SCRIPT_ROOT+"/app/");
    });