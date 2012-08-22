function generate_html_for_help() {
    //alert("lol");
    string = "<p> Welcome to Othello, a new MMO game! </p>";
    string = string + "<p> This game is about voting for the moves you think will be the best. After everybody has voted, or the timer runs out, the most popular vote will be the executed move, so think thouroughly where you want to place the tile! </p>";

    string = string + "<br><br><br><br><br>";
    string = string + "when you first play, you will be able to select a team, unless the team balance is too big. If that is the case, you might get your team selected automatically!";
    $("#help_text").html(string);
    //alert("text loaded!");

};

function ready_help() {
    
    $("#help_area").hide();
    
    $("#help_button").click(function () {
            $("#help_area").show();
        });
    
    
    $("#help_area").click(function () {
            $("#help_area").hide();
        });    
};



function logo_button() {
    $("#logo_button").click(function() {
	    window.location = '/index/'
	});
}


$(document).ready(function() {
	//alert("initializing help! :DDD");
	ready_help();
	generate_html_for_help();
	logo_button();
    });