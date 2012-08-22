function ready_how_to_button() {
    //alert("readying how_to");
    $("#how_to").click(function () {
	    //alert("you clicked how_to button!");
	    $("#instructions_menu").hide();
	    $.get('/static/how_to.txt', function (data) {
		    $("#content_text").html(data);
		});
            $("#content_container").show();
        });
    
    //alert("readyed how_to");

};


function ready_point_system_button() {
    //alert("readying how_to");
    $("#point_system").click(function () {
            //alert("you clicked how_to button!");
            $("#instructions_menu").hide();
            $.get('/static/point_system.txt', function (data) {
                    $("#content_text").html(data);
                });
            $("#content_container").show();
        });

    //alert("readyed how_to");

};


function ready_point_system_button() {
    //alert("readying how_to");
    $("#point_system").click(function () {
            //alert("you clicked how_to button!");
            $("#instructions_menu").hide();
            $.get('/static/point_system.txt', function (data) {
                    $("#content_text").html(data);
                });
            $("#content_container").show();
        });

    //alert("readyed how_to");

};




function ready_beta_tester_button() {
    //alert("readying how_to");
    $("#beta_tester").click(function () {
            //alert("you clicked how_to button!");
            $("#instructions_menu").hide();
            $.get('/static/beta_tester.txt', function (data) {
                    $("#content_text").html(data);
                });
            $("#content_container").show();
        });

    //alert("readyed how_to");

};


function ready_back_to_menu_button() {
    $("#back_to_menu").click(function () {
	    window.location = '/index/';
	    
	}); 
    
    
}


function ready_content_container() {
    
    //alert("preparing content_container");

    $("#content_container").hide();



    $("#back_button").click(function () {
	    //alert("you clicked back_button! :D");
            $("#content_container").hide();
            $("#instructions_menu").show();

        });

    //alert("content_container done");

};





$(document).ready(function() {
        //alert("initializing help! :DDD");
        $("#help_button").hide();
	

	ready_content_container();
	ready_how_to_button();
	ready_back_to_menu_button();
	ready_point_system_button();
	//ready_beta_tester_button();
    });
