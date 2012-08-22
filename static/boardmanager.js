

/* function that draws the board
@param board
*/


function checkGameOver(board, boardLength) {
  var tempGameState = false;
  for (a = 0; a < boardLength; a++) {
    for (b = 0; b < boardLength; b++) {
      if (board[b][a] == 0) {
      tempGameState = tempGameState || 
                      checkFlippedMoves(board, boardLength, 1, a, b) || 
                      checkFlippedMoves(board, boardLength, 2, a, b);
      if (tempGameState)
        break;
      }
    }
    if (tempGameState)
      break;
  }
  return tempGameState;
}


function isPassTurn (board, boardLength, color) {
  var tempBoolean = true;
  for (c = 0; c < boardLength; c++) {
    for (d = 0; d < boardLength; d++) {
      if (board[d][c] == 0) {
        tempBoolean = tempBoolean && !checkFlippedMoves(board, boardLength, color, c, d);
      }
    }
  }
  return tempBoolean;
}


/* Old function...

function placeTile(board, boardLength, color, x, y) {
      
  if (board[y][x] != 0) {
    alert("I'm sorry, there is already a piece in that place :(");
  } else if (checkAdjecent(board, boardLength, color, x, y)) {
  // is check adjecent unneccesairy maybe??? can't flipp if there is no adjecent square!
  // mainly there to prevent unneccesairy calculations...
    var flippedMoves;
    flippedMoves = checkFlippedMoves(board, boardLength, color, x, y);
    if (flippedMoves) {
      board[y][x] = color; // place a tile on the spot.

      _.each(flippedMoves, function(dimension){
        _.each(dimension, function(move) {
          board[move[1]][move[0]] = color; //flipp all the tiles.
          });
        });
      
    } 
    else { 
      alert("I'm sorry, this is not a valid move, you can't flipp anything over there!");
    }
  } else { 
      alert("I'm sorry, this is not a valid move, there is no adjecent opposing color :(");
  }
}

*/

// not used, but can be used to speed up the game by checking this before checking
// for flipped moves.

function checkAdjecent(board, boardLength, color, x, y) {
  //alert("checkAdjecent STarted! variables x and y are: " + x + ", " + y);
  var xPos = x;
  var yPos = y;
  var adjecentChecked = false;

  // alert("checkAdjecent debug 1");
  
  // will check all adjecent tiles, and skip if checked_tile is out of bounds.
  for (m = -1; m < 2; m++) {
    for (n = -1; n < 2; n++) {
      var tempX = xPos + m;
      var tempY = yPos + n;
      if ((xPos + m >= 0) && (xPos + m < boardLength) && (yPos + n >= 0) && (yPos + n < boardLength)) {
       // take current color - checked_tile, 0 for empty. if checked_tile is empty, will return color, 
       //if same as color, will return 0, else there is a different color.
       var temp = color - board[(yPos + n)][(xPos + m)];
       if (temp != color && temp != 0) // if not same or different
        adjecentChecked = true;
      }
      else {
        //alert("wall detected!");
        continue;
        }
    }
  }
  // alert ("checkAdjecent is complete!");
  return adjecentChecked;
}

function checkFlippedMoves(board, boardLength, color, x, y) {
  
  var y_derivate;
  var x_derivate;
  
  var dataArray = [];
  
  var temp;

  for (k = -1; k < 2; k++) {
    for (q = -1; q < 2; q++) {
      temp = checkOneDimension(board, boardLength, color, x, y, k, q);
      if (temp && temp.length != 0) {
        dataArray.push(temp);
      }
    }  
  }
    
  if (dataArray.length == 0) {
    return false;
  } else {
    return dataArray;
  }
  
}

function checkOneDimension(board, boardLength, color, x, y, x_derivate, y_derivate) {
  if (x_derivate == 0 && y_derivate == 0)
    return false;
  // alert("ch_1_dim: debug 1");
  var goOn = true;
  var dataArraySmall = [];
  for (i = 1; i < boardLength; i++) {

      if ((x + i*x_derivate >= 0) && (x + i*x_derivate < boardLength) 
          && (y + i*y_derivate >= 0) && (y + i*y_derivate < boardLength) 
          && goOn
          && board[y + i*y_derivate][x + i*x_derivate] != 0) { // it can't be zero.
            
            var temp = color - board[y + i*y_derivate][x + i*x_derivate];
            
            if (temp == 0) { // if the same color return array so we can flip the ones inbetween.
              return dataArraySmall;
            } else { // other color!
              dataArraySmall.push([x + i*x_derivate,y + i*y_derivate]);
            }
            
      } else {
          return false;
        }

  }
  return false;

}
