# Main class file for python board.

class Board():
    # internal variables
    board = [   [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 2, 1, 0, 0, 0],
                [0, 0, 0, 1, 2, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0] ]


#    board = [   [1, 1, 1, 1, 1, 2, 2, 2],
#                [1, 1, 1, 1, 1, 2, 2, 2],
#                [1, 1, 1, 1, 1, 2, 2, 2],
#                [1, 2, 1, 1, 0, 2, 2, 1],
#                [1, 1, 1, 1, 1, 2, 2, 2],
#                [1, 1, 1, 1, 1, 2, 2, 2],
#                [1, 1, 1, 1, 1, 2, 2, 2],
#                [1, 1, 1, 1, 1, 1, 1, 1] ]









    _board_length = 8
    
    x_score = 2
    o_score = 2
    
    game_state = True
    
    # constants
    
    X_COLOR = 1
    O_COLOR = 2
    
    X_TURN = "X"
    O_TURN = "O"
    
    # current turn, O starts the game
    
    current_color = O_COLOR
    current_turn = O_TURN
    
    helper_moves = []
    
    def __init__(self):
        # To update the helper moves when created        
        self._santas_little_helper()
    
    def load_board(self,board, current_turn, current_color, game_state):
        self.board = board
        self.current_turn = current_turn
        self.current_color = current_color
        self.game_state = game_state
        self._update_score()
        self._santas_little_helper()
    
    def print_board(self):
        print "   A  B  C  D  E  F  G  H"
        for i in range(0,self._board_length):
            print str(i+1) + ":" + str(self.board[i]) \
                                    .replace(str(self.O_COLOR),self.O_TURN)\
                                    .replace(str(self.X_COLOR),self.X_TURN)\
                                    .replace("0"," ")\
                                    .replace(",","|")
                                       
    
    def _check_one_dimension (self, x, y, x_derivate, y_derivate, color):
        # checks one dimension!
        if ((x_derivate == 0 and y_derivate == 0) or self.board[y][x] != 0):
            return False
        dataListSmall = []
        for n in range(1,self._board_length):
            x_value = x + n*x_derivate
            y_value = y + n*y_derivate
            if ((x_value >= 0) and 
                    (x_value < self._board_length) and 
                    (y_value >= 0) and 
                    (y_value < self._board_length) and 
                    (self.board[y_value][x_value] != 0)):
                temp = color - self.board[y_value][x_value];
                if (temp == 0): 
                    # It is the same color if temp is 0.
                    return dataListSmall
                else:
                    dataListSmall.append([x_value,y_value])
            else:
                return False
    
    def _check_flipped_moves(self, x, y, color):
        dataList = []
        for k in range(-1,1+1): #from -1 to 1
            for q in range(-1,1+1): # from -1 to 1
                temp = self._check_one_dimension(x, y, k, q, color)
                if temp and len(temp) != 0:
                    dataList.append(temp)
        return dataList #empty list is false!
        
    def _santas_little_helper(self):
        # generates the helper moves, hence the name :) 
        helper_moves = []
        if self.current_color == self.X_COLOR:
            other_color = self.O_COLOR
        elif self.current_color == self.O_COLOR:
            other_color = self.X_COLOR
        for i in range(self._board_length):
            for j in range(self._board_length):
                if self.board[j][i] == other_color:
                
                    for a in range(-1,1+1): #from -1 to 1
                        for b in range(-1,1+1): # from -1 to 1
                            # don't do if these are too big!
                            if i+a >= self._board_length or i+a < 0:
                                pass
                            elif j+b >= self._board_length or j+b < 0:
                                pass
                            # only does if indexes are within bounds.
                            elif(self._check_flipped_moves(i+a,
                                                         j+b, 
                                                         self.current_color)):
                                if not [i+a,j+b] in helper_moves:
                                    # print helper_moves
                                    # print [i+a,j+b]
                                    helper_moves.append([i+a,j+b])
        self.helper_moves = helper_moves
                            
                    

    def _is_pass_turn(self, color):
        tempBoolean = True
        for c in range(self._board_length):
            for d in range(self._board_length):
                if self.board[d][c] == 0:
                    tempBoolean = (tempBoolean and not
                                  self._check_flipped_moves(c, d, color))
        return tempBoolean
    
    def place_tile(self, x_coordinate, y_coordinate):
        # Interface affected!
        if (x_coordinate == -1 or y_coordinate == -1):
            return dict(status= -1, board=self.board)
  
        flippedMoves = self._check_flipped_moves(x_coordinate, 
                                                y_coordinate, 
                                                self.current_color)
        if flippedMoves and self.board[y_coordinate][x_coordinate] == 0:
            # self.board[y_coordinate][x_coordinate] = self.current_color
            flippedMoves.append([[x_coordinate,y_coordinate]])
            for dimension in flippedMoves:
                for move in dimension:
                    self.board[move[1]][move[0]] = self.current_color # flipp all the moves!
            self._next_turn()
        
        
        return dict(status=0, board=self.board)
    
    def _next_turn(self):
        self._update_score()
        
        is_pass_turn_x = self._is_pass_turn(self.X_COLOR)
        is_pass_turn_o = self._is_pass_turn(self.O_COLOR)
        
        print "is pass turn x? ", is_pass_turn_x
        print "is pass turn o? ", is_pass_turn_o
        
        is_game_over = is_pass_turn_x and is_pass_turn_o
        
        print "is game over? ", is_game_over
        
        if is_game_over:
            self._game_over() #We will change the voting thing to zero!
            
        elif not((self.current_color == self.O_COLOR and is_pass_turn_x) or 
                    (self.current_color == self.X_COLOR and is_pass_turn_o)):
            self._change_turn()
        else:
            pass
            # do nothing, it is the same players turn.
        self._santas_little_helper()
            
    def get_board_data(self):
        #self._debug_print_all()
        return dict(    board=self.board,
                        current_turn=self.current_turn,
                        current_color=self.current_color, 
                        x_score=self.x_score, 
                        o_score=self.o_score, 
                        game_state=self.game_state,
                        helper_moves=self.helper_moves)
        
        
    def _change_turn(self):
        if self.current_color == self.O_COLOR:
            self.current_color = self.X_COLOR
            self.current_turn = self.X_TURN
        else:
            self.current_color = self.O_COLOR
            self.current_turn = self.O_TURN
        
    # maybe we need to do something else when it is game over!
    def _game_over(self):
        print "game is now ovaaah!!"
        self.game_state = False
        
    def _update_score(self):
        # is there a more elegant way to do this?
        # maybe always add 1, and subtract flipped moves from one while
        # adding to the other directly into flipped tile? if memory
        # is an issue this could be done.
        self.x_score = 0
        self.o_score = 0
        for rows in self.board:
            for tile in rows:
                if tile == self.X_COLOR:
                    self.x_score += 1
                elif tile == self.O_COLOR:
                    self.o_score += 1
    
    def _debug_print_all(self):
        self.print_board()
        print "game state is now ", self.game_state
        print "x_score is now ", self.x_score
        print "o_score is now ", self.o_score
        print "helper_moves is now ", self.helper_moves
        print "current_color is now ", self.current_color
        print "current_turn is now " + self.current_turn
        

# test runs:        
  
# board = Board()
# board._update_score()
# board._debug_print_all()
# board.place_tile(3,2)
# board.next_turn()
# board._debug_print_all()
# board.place_tile(4,1)
# board.next_turn()
# print board.get_board_data()
# board._debug_print_all()
