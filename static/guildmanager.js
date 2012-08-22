
var Guildmanager = {
    
    request_guild : function () {
	alert("request_guild! testing session variable!");
	$.getJSON($SCRIPT_ROOT + '/_get_session', {id: 1}, function(data) {
		alert("recieved response fron server lol!");
		if (true) { // data.has_guild) {
		    $("#guild").html("Guildmanager has inputted this text! You have a guild, but we are looking into implementing stuff here :DDD");
		} else {
		    // Guildmanager.generate_html_for_create_guild()
		}
	    });
    },

    generate_html_for_create_guild : function() {
	alert("generating create_guild page! :) ");
    },

    generate_html_for_guild_options : function() {
	alert("generating guild options :)");
    }
};

$(document).ready(function() {
	// Guildmanager.request_guild();
	// alert("Guild manager started!");
    });