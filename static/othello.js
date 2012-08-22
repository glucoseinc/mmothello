/* main class */

var random = [];

for (i=0;i<65;i++) {
    
    random.push(Math.floor(Math.random()*5 +1));
};

//alert(random);


var Othello = {
  // inner variables
    
    board_length : 8, // standard value, overwritten as soon as game loads.
    
    timer_id : 0,
    time_left_id : 0,
    // functions

    
    fever_level_4 : 90,
    fever_level_3 : 80,
    fever_level_2 : 70,
    fever_level_1 : 50,


    load_board : function (load) {
	// alert("calling load board!");
	
	if (load) {
	    show_loading();
	}
        $.getJSON($SCRIPT_ROOT + '/_load_board', 
		  function (data2) {
		      // alert("load_board functioning!");
		      self.board_length = data2.board.length;
		      Othello.generate_board_html(data2);
		      // alert("showing board!");
		      if (load) {
			  show_board();
		      }
		  });
	
    },
    
    
    generate_board_html : function(data) {
	
	// generate the board html code... Also used as reset function (same functionality).
	// alert("trying to generate html!");
	var board = data.board;
	var board_length = data.board.length;
	
	var board_table = '<table id="board_table" border="0px" cellpadding="0px" \
      cellspacing="0px" align="center">'
	var counter = 0;
	var mid = board_length/2;
	
	var x_locations = [];
	var o_locations = [];
	
	$("#board").css('visibility','hidden');
      
      for (i = 0;i<board_length; i++) {      
        // for each row:
        board_table = board_table.concat('<tr>');
        
        for (j=0; j < board_length; j++) {
          board_table = board_table.concat('<td class="boardcell" id="ttt' + 
                                           counter + 
                                           '">&nbsp;</td>');
          if(board[i][j] == 1) {
            x_locations.push(counter);
          } else if (board[i][j] == 2) {
            o_locations.push(counter);
          }
          counter++;
        }
        
        board_table = board_table.concat('</tr>');
        
      }
      board_table = board_table.concat('</table>');
      
      $("#board").html(board_table);
      $("#menu_container").hide();
      
      // setup starting board space.
      
      var temp_id = 0;
      var space = $("#ttt" + temp_id);
	var counter = 0;
      
      _.each(x_locations, function(temp) {
              // generate a random number between 1 - 5
              var picture_url = 'url("/static/images/piece-red';
              picture_url = picture_url + random[temp];
              picture_url = picture_url + '.png")';

	      space = $("#ttt" + temp);
	      // space.html("X");
	      // space.css('font-size','25px');
	      space.css('color','#FFFFFF');
              space.css('background-image', picture_url);
	      //space.css('background-image', 'url("/static/red.png")');
	      // space.css('background-image', 'url("/static/black_tile.jpg")');
	      // space.css('background-size', '95%');
	  });
     
      
      _.each(o_locations, function(temp_id) {
	      // generate a random number between 1 - 5
	      var picture_url = 'url("/static/images/piece-blue';
	      picture_url = picture_url + random[temp_id];
	      picture_url = picture_url + '.png")';

	      

	      space = $("#ttt" + temp_id);
	      // space.css('font-size','25px');
	      space.css('color','#000000');
	      space.css('background-image', picture_url);
	      //space.css('background-image', 'url("/static/blue.png")');
	      // space.css('background-image', 'url("/static/white_tile.jpg")');
	      // space.css('background-size', '95%');
	      // space.html("O");
	  });



	set_fever_level(data);


      // alert("it is now players turn: " + data.players_turn);
	//$("#welcome_message").show();
	if(!data.players_turn) {
	    $("#welcome_message").html("It is currently the other teams turn.");
	} else if(data.has_voted) { // else if players turn but already voted.
	    $("#welcome_message").html("You have already voted, please come back later.");
	} else {
	    $("#welcome_message").html("It is now your turn, please click one of the marked tiles to vote.");
	    
	    //$("#board td").click(function(e) {
	    //	    Othello.move( e.target.id );
	    //	});	  
	}  
	
        $("#welcome_message").show();

      _.each(data.helper_moves, function(move) {
	      id = (move[1]) * board_length + move[0];
	      space = $("#ttt" + id);
              // space.html(move[2]);
	      // space.css('background-color', '#BBFFBB');
	      // space.css('font-size','11px');
	      // space.css('color','#AAAAAA');
	      // space.css('background-image', 'url("/static/helper_tile.jpg")');
	      space.css('background-image', 'url("/static/images/question_big.png")');
	      space.css('background-size','200%');
	      // space.css('opacity',Math.min(move[2]+0.2 , 1))
	      // cool opacity effect, +0.2 to ensure a minimum opacity.
              // space.html(move[2].toFixed(1));
	      if (data.players_turn && !data.has_voted) {
		  space.click(function(e) {
			  Othello.move( e.target.id );
		      });
	      }

		  
	      
	  });


	
	// connect the user score with the board!

	$("#user_round_score").html(data.round_score);
	$("#user_total_score").html(data.total_score);
	
	
	
	
	var start_of_game = this.update_score(data);
	if (start_of_game) {
	    $("#blue_turn_keeper").show();
	    $("#red_turn_keeper").hide();
	} else {
	    this.next_turn(data)
	}
	
	// // alert("game state is: " + data.game_state);
	// if (!data.game_state) {
	//   // alert("GAME OVER!");
	//  this.end_game();
	// }
	
	
        $("#board").css('visibility','visible');
	
	
	update_meters(data);
	
	
	
	
    },
    
    move : function(id) {
	
	var space = $("#" + id);  // Board space table element
	var num = id.replace("ttt", ""); // representing the space on the board
	
	var self = this;
	
	var x_coordinate = num % self.board_length;
	var y_coordinate = (num - x_coordinate) / self.board_length;
	
	//alert("move_debug 1! " + x_coordinate + " " + y_coordinate);
	//alert($SCRIPT_ROOT);
	//show_loading();


	$.getJSON($SCRIPT_ROOT + '/_move', {"x_coordinate" : x_coordinate, 
		    "y_coordinate": y_coordinate}, 
	    function (result) {
		
		//alert("move_debug 2!");
		
		if (!result.players_turn && result.id == "undefined") {
		    // this case doesn't happen because now we disable board
		    // when not our turn :)
		    alert("Ehm... it wasn't your turn, you know!");
		    // do nothing, because we clicked when it wasn't 
		    // our turn, so no need to update! :)
		} else {
		    //alert("move_debug 3!");
		    $("#board").html("");
		    self.load_board(true);
		    //self.generate_board_html(result);
		    //self.next_turn(result);
		}
		//show_board();
	    });
	    
	

	//alert("move_debug 4!");
	
	
	
    },
    
    next_turn : function (result) {
        self = this;
        self.update_score(result); // we want to update even if game ends.
        // alert("game state is now: TROLLOLLOLL!! LOL " + result.game_state)
	if (!result.game_state) {
          self.end_game();
        } else {
          var space_red = $("#red_turn_keeper");
	  var space_blue = $("#blue_turn_keeper");
	  
          
          if (result.current_turn == "O") {
	      space_blue.show();
	      // alert("debug before hide red!");
	      space_red.hide();
          } else if (result.current_turn == "X") {
	      space_red.show();
	      // alert("debug before hide blue");
	      space_blue.hide();
          }
        }
    },
    
    
    update_score : function (result) { // dictionary!
        $("#red_game_score").html(result.x_score);
	$("#blue_game_score").html(result.o_score);
	this.x_score = result.x_score;
	this.o_score = result.o_score
        if (result.x_score == 2 && result.o_score == 2) {
            return true;
        } else {
            return false;
        }
    },
    
    
    end_game : function () {
	// alert("Scores are now: O/X = " + this.o_score + "/" + this.x_score);

	// alert("Timer ID is now: " + this.timer_id);

	clearInterval(this.timer_id);

	// alert("timer cleared!");
	
	var endMessage = "";
	if (this.x_score == this.o_score) {
	    endMessage = "It is a draw!";
	} else if (this.x_score > this.o_score) {
	    endMessage = "X wins with " + this.x_score + " points!";
	} else {
	    endMessage = "O wins with " + this.o_score + " points!";
	}
	$("#menu").html(endMessage);
	
	$("#menu").append("<div id='play_again'><u>To Menu</u></div>");

	// disable all buttons :)

	
	$("#board td").click(function(e) {
		// do nothing!
	    });
	
	
	// Button for playing again.
	$("#play_again").click(function () { 
		window.location = '/index/';
	    });

	$("#menu_container").show();
	this.win = false;

	$("#welcome_message").hide();

	// right now we don't want to delete the board... ^^
	// $.getJSON($SCRIPT_ROOT + '/delete_current_board/', function (data) {
	//     
	//    });
	
    },
    
    check_for_update : function() {
	
	
	$.getJSON($SCRIPT_ROOT + '/_check_for_update', {
	    }, function (data) {
		if (data.update) {
		    Othello.load_board(false)
		} else {
		    alert("TROLLOLLOLLOLLOLLL OLLLOLLOLLL");
		}
	    });
	
	
    },
    
    new_game : function () {
	
    }
    
    
};

function post_board( board, 
                    board_length,
                    player1_score,
                    player2_score,
                    turn,
                    color) {
                                        
  $.getJSON($SCRIPT_ROOT + '/_save_board', {
      board: JSON.stringify(board),
      board_length : board_length,
      player1_score : player1_score,
      player2_score : player2_score,
      turn : turn, 
      color : color}, function (data) {
      });
}

function update_timer() {
    //alert("starting timer_update!");
    $.getJSON($SCRIPT_ROOT + '/_get_timer/', {}, function(data) {
	    // alert("ipdating timer! :D");
	    if (data.status) {
		// html_string = "Vote Ends: <br>";
		html_string = /* html_string  + */  data.hours + ":";
		html_string = html_string + data.minutes + ":";
		html_string = html_string + data.seconds;
		//html_string = html_string + "<br> board: ";
		//html_string = html_string + data.board_id;
	    } else {
		html_string = "Working...";
	    }

            $("#timer").html(html_string)
        });

}


function show_loading() {
    // alert("now displaying loading screen...");
    $("#loading_screen").show();
    $(".turn_keeper").hide();
    // $("#board").hide();
}

function show_board() {
    // alert("now displaying board! :D");
    $("#loading_screen").hide();
    // $("#board").show();

}


function update_meters(data) {
    //alert("lol update_meters start!");
    // get height of fever_meter and remove "px" from string.
    var total_height = parseInt($(".fever_meter").css('height').slice(0,-2))-2;
    //$("#fever_meter_keeper").html(height+1);
    var self_bar = $("#self_team_bar");
    var opponent_bar = $("#opponent_team_bar");
    //alert("update_meters: debug 1!");
    
    var self_percent = Math.min(5,data.self_fever_points/100);
    var self_height = total_height * self_percent;
    
    //alert("update_meters: debug 1,5!");
    
    var opponent_percent = Math.min(5,data.enemy_fever_points/100);
    var opponent_height = total_height * opponent_percent;
    
    //alert("update_meters: debug 2!");
    
    // if procent is over 50 %, we are in fever mode!
    
    if (self_percent >= 0.5) {
	self_bar.css('background-image',
		     'url("/static/images/fever_bar_red2.png")');
    } else {
	self_bar.css('background-image',
		     'url("/static/images/fever_bar_white2.png")');
    }
    
    if (opponent_percent >= 0.5) {
        opponent_bar.css('background-image',
			 'url("/static/images/fever_bar_red2.png")');
    } else {
        opponent_bar.css('background-image',
			 'url("/static/images/fever_bar_white2.png")');
    }
    
	
    //alert("lol meters debug 2.5!" + self_height + " " + opponent_height);
	
	
    self_bar.css('height',String(self_height)+"px");
    self_bar.css('margin-top',String(total_height-self_height)+"px");
    
    opponent_bar.css('height', String(opponent_height)+"px");
    opponent_bar.css('margin-top',String(total_height-opponent_height)+"px");
    
    //$(".fever_meter").css('z-index',1);

    
    //alert("update_meters: debug 3!");

}



function set_fever_level(data) {
    //space = $("#welcome_name");
    var level = 0;
    //var fever_level_4 = 90;
    //var fever_level_3 = 80;
    //var fever_level_2 = 70;
    //var fever_level_1 = 50;
    
    
    
    //alert(data);
    
    
      
    if (data.self_fever_points >= Othello.fever_level_4) {
	level = 4;
    } else if (data.self_fever_points >= Othello.fever_level_3) {
	level = 3;
    } else if (data.self_fever_points > Othello.fever_level_2) {
	level = 2;
    } else if (data.self_fever_points > Othello.fever_level_1) {
	level = 1;
    } else {
	return false; //break out!
    }
    
    
    
    //space.html("FEVER LEVEL " + level);
    //space.css('font-family','copperplate gothic');
    //space.css('size','20px');

    
}



function ready_help() {

    $("#help_area").hide();

    $("#help_button").click(function () {
	    $("#help_area").show();
	});


    $("#help_area").click(function () {
	    $("#help_area").hide();
	});


}



function resetServer() {
    $.getJSON($SCRIPT_ROOT + '/_create_new_board', {}, function() {
	    Othello.load_board(true);
	});
}

$(document).ready(function() {
	// Start a game
	
        // alert("Cache Test! LOLOLOL !");
	
	//resetServer();
	$("#menu_container").hide();
	//ready_help();
	Othello.load_board(true);

	Othello.timer_id = setInterval('Othello.check_for_update()',2000);
	Othello.time_left_id = setInterval('update_timer()',200);
	// alert("starting game! :D" + Othello.timer_id);
	$("#user_score_keeper").hide();
    });