"""
---------------------------------------------------------------------
| A1(13) | A2(12) | A3(11) | A4(10) | A5(9) | A6(8) | A7(7) | A8(6) |
|        |--------------------------------------------------|       |
| B1(13) | B2(0)  |  B3(1) | B4(2) | B5(3) | B6(4) | B7(5)  | B8(6) |
---------------------------------------------------------------------
"""
import sys
import copy

#def global constants for the different board positions
START_1 = 0
START_2 = 0
MANCALA_1 = 0
MANCALA_2 = 0
END_1 = 0
END_2 = 0
post_to_name = dict()
post_to_name["root"] = "root"
start_player = 0
logList = list()

class Mancala_State:
	def __init__(self, current_player, start, end, mancala, mancala_opponent, depth, cut_off_depth, board, cost):
		self.current_player = current_player
		self.start = start
		self.end = end
		self.mancala = mancala
		self.mancala_opponent = mancala_opponent
		self.depth = depth
		self.cut_off_depth = cut_off_depth
		self.board = board
		self.cost = cost

	def getCurrentPlayer(self):
		return self.current_player

	def getStart(self):
		return self.start

	def getEnd(self):
		return self.end

	def getMancala(self):
		return self.mancala

	def getMancala_Opponent(self):
		return self.mancala_opponent

	def getDepth(self):
		return self.depth

	def getCutOffDepth(self):
		return self.cut_off_depth

	def getBoard(self):
		return self.board

	def setBoard(self, board):
		self.board = board

	def getCost(self):
		return self.cost

	def __repr__(self):
		return "current_player" + str(self.current_player) + " current_player's start pos:" + str(self.start) + " current_player's end pos:" + str(self.end) + " current_player's mancala pos:" + str(self.mancala) + " current_player's stones in mancala:" + str(self.board[self.mancala]) + " game board:" + self.board + " current depth" + str(self.depth) + " cut off depth:" + str(self.cut_off_depth)

	def setCost(self):
		board = self.board
		self.cost = self.cost_eval(board[self.mancala], board[self.mancala_opponent])

	def cost_eval(self, mancala1, mancala2):
		return mancala1 - mancala2

	def check_for_extra_turn(self, pos):
		next_move = copy.deepcopy(self)
		if(pos == self.mancala):
			#extra turn
			next_move = next_move.greedy_mancala()
		return next_move

	def check_for_capture(self, pos):
		next_move = copy.deepcopy(self)
		board = self.board
		if(board[pos] == 1 and pos in range(self.start, self.end + 1)):
			board[pos] = 0
			opponent_capture_pos = len(board) - pos - 2
			total_gain = 1 + board[opponent_capture_pos]
			board[opponent_capture_pos] = 0
			board[self.mancala] = board[self.mancala] + total_gain
			next_move.setBoard(board)
			next_move.setCost()
		return next_move

	def add_stones(self, begin, end):
		count = 0
		for i in range(begin, end):
			count = count + self.board[i]
			self.board[i] = 0
		return count

	def check_if_game_ends_and_update(self):
		board = self.board
		game_end = True
		#checking if game has ended for current player
		for i in range(self.start, self.end + 1):
			if(board[i]):
				game_end = False
				break
		if(game_end):
			self.board[self.mancala_opponent] = self.board[self.mancala_opponent] + self.add_stones((self.mancala + 1)%len(board), self.mancala_opponent)
			return game_end
		else: #checking if game has ended for the opponent
			game_end = True
			for i in range((self.mancala + 1)%len(board), self.mancala_opponent):
				if(board[i]):
					game_end = False
					break
			if(game_end):
				board[self.mancala] = board[self.mancala] + self.add_stones(self.start, self.end + 1)
			return game_end

	def compute_greedy(self, startIndex):
		next_move = copy.deepcopy(self)
		board = next_move.board
		mancala_opponent_pos = self.mancala_opponent
		stones = board[startIndex]
		board[startIndex] = 0
		j = startIndex + 1
		while stones:
			if not j == mancala_opponent_pos:
				board[j] = board[j] + 1
				stones = stones - 1
			j = (j + 1) % len(board)
		last_stone_pos = (j-1) % len(board)
		next_move.setBoard(board)
		next_move.setCost()
		next_move = next_move.check_for_extra_turn(last_stone_pos)
		next_move = next_move.check_for_capture(last_stone_pos)
		game_end = next_move.check_if_game_ends_and_update()
		next_move.setCost()
		return next_move

	def greedy_mancala(self):
		#compute next possible move and cost and then set with the highest returned eval_cost
		max = float("-inf")
		position = float("-inf")
		for i in range(self.start, self.mancala):
			if(self.board[i]):
				board_next_move_state = self.compute_greedy(i)
				cost = board_next_move_state.getCost()
				if(cost > max):
					max = cost
					position = i
					next_state = board_next_move_state
				if(cost == max): #assign positional precedence in case of player 2, automatically handled for player 1
					if(self.current_player == 2 and i > position):
						max = cost
						position = i
						next_state = board_next_move_state
		return next_state

	def find_pos_order(self):
		if(self.current_player == 1):
			return (self.start, self.end + 1, 1)
		else:
			return (self.end, self.start - 1 , -1)

	def change_player(self, current_player):
		if(current_player == 1):
			self.current_player = 2
			self.start = self.mancala + 1
			self.end = len(self.board) - 2
		else:
			self.current_player = 1
			self.start = 0
			self.end = self.mancala_opponent - 1
		temp = self.mancala
		self.mancala = self.mancala_opponent
		self.mancala_opponent = temp

	def assign_cost(self, def_val, depth, cut_off_depth, extraTurn):
		if(depth < cut_off_depth or (depth == cut_off_depth and extraTurn)):
			return def_val
		elif (depth == cut_off_depth and not extraTurn):
			return self.cost_eval(self.board[get_start_player_mancala()], self.board[get_opp_player_mancala()])

	def find_max_move(self, move_pos, current_depth, swap_player, free, alpha, beta, alpha_beta):
		current_max_node = copy.deepcopy(self)
		best_move = self
		if free:
			depth = current_depth
		else:
			depth = current_depth + 1
		if(current_depth < self.cut_off_depth or ((current_depth == self.cut_off_depth) and not swap_player)):
			update_log_file(move_pos, current_depth, current_max_node.cost, alpha, beta, alpha_beta)
			next_node = copy.deepcopy(current_max_node)
			if(swap_player):
				next_node.change_player(current_max_node.current_player)
			begin_pos, end_pos, increment = next_node.find_pos_order()
			no_moves = True
			for i in range(begin_pos, end_pos, increment):
				loop_node = copy.deepcopy(next_node)
				if(loop_node.board[i]):
					no_moves = False
					turn, game_end = loop_node.get_next_move_and_check_for_extra_turn(i)
					if(turn):
						loop_node.cost = loop_node.assign_cost(float("-inf"), depth, loop_node.cut_off_depth, True)
						cost, loop_move = loop_node.find_max_move(i, depth, False, True, alpha, beta, alpha_beta)
					else:
						loop_node.cost = loop_node.assign_cost(float("inf"), depth, loop_node.cut_off_depth, False)
						cost, loop_move = loop_node.find_min_move(i, depth, True, False, alpha, beta, alpha_beta)
					if(game_end):
							cost = loop_node.cost_eval(loop_node.board[get_start_player_mancala()], loop_node.board[get_opp_player_mancala()])
					if(current_max_node.update_max_node_cost(cost)):
						best_move = loop_move if turn else loop_node
					if(alpha_beta):
						alpha_old = alpha
						alpha = max(alpha, current_max_node.cost)
						if(beta <= alpha):
							update_log_file(move_pos, current_depth, current_max_node.cost, alpha_old, beta, alpha_beta)
							break
					update_log_file(move_pos, current_depth, current_max_node.cost, alpha, beta, alpha_beta)
			if(no_moves):
				update_log_file(move_pos, current_depth, current_max_node.cost_eval(current_max_node.board[get_start_player_mancala()], current_max_node.board[get_opp_player_mancala()]), alpha, beta, alpha_beta)
			return current_max_node.cost, best_move

		elif current_depth == self.cut_off_depth:
			diff_op_1 = get_start_player_mancala()
			diff_op_2 = get_opp_player_mancala()
			update_log_file(move_pos, current_depth, current_max_node.cost_eval(current_max_node.board[diff_op_1], current_max_node.board[diff_op_2]), alpha, beta, alpha_beta)
			return current_max_node.cost_eval(current_max_node.board[diff_op_1], current_max_node.board[diff_op_2]), self

	def find_min_move(self, move_pos, current_depth, swap_player, free, alpha, beta, alpha_beta):
		current_min_node = copy.deepcopy(self)
		best_move = self
		if free:
			depth = current_depth
		else:
			depth = current_depth + 1
		if(current_depth < self.cut_off_depth or ((current_depth == self.cut_off_depth) and not swap_player)):
			update_log_file(move_pos, current_depth, current_min_node.cost, alpha, beta, alpha_beta)
			next_node = copy.deepcopy(current_min_node)
			if(swap_player):
				next_node.change_player(current_min_node.current_player)
			begin_pos, end_pos, increment = next_node.find_pos_order()
			no_moves = True
			for i in range(begin_pos, end_pos, increment):
				loop_node = copy.deepcopy(next_node)
				if(loop_node.board[i]):
					no_moves = False
					turn, game_end = loop_node.get_next_move_and_check_for_extra_turn(i)
					if(turn):
						loop_node.cost = loop_node.assign_cost(float("inf"), depth, loop_node.cut_off_depth, True)
						cost, loop_move = loop_node.find_min_move(i, depth, False, True, alpha, beta, alpha_beta)
					else:
						loop_node.cost = loop_node.assign_cost(float("-inf"), depth, loop_node.cut_off_depth, False)
						cost, loop_move = loop_node.find_max_move(i, depth, True, False, alpha, beta, alpha_beta)
					if(game_end):
						cost = loop_node.cost_eval(loop_node.board[get_start_player_mancala()], loop_node.board[get_opp_player_mancala()])
					if(current_min_node.update_min_node_cost(cost)):
						best_move = loop_move if turn else loop_node
					if(alpha_beta):
						beta_old = beta
						beta = min(beta, current_min_node.cost)
						if(beta <= alpha):
							update_log_file(move_pos, current_depth, current_min_node.cost, alpha, beta_old, alpha_beta)
							break
					update_log_file(move_pos, current_depth, current_min_node.cost, alpha, beta, alpha_beta)
			if(no_moves):
				update_log_file(move_pos, current_depth, current_min_node.cost_eval(current_min_node.board[get_start_player_mancala()], current_min_node.board[get_opp_player_mancala()]), alpha, beta, alpha_beta)
			return current_min_node.cost, best_move

		elif current_depth == self.cut_off_depth:
			diff_op_1 = get_start_player_mancala()
			diff_op_2 = get_opp_player_mancala()
			update_log_file(move_pos, current_depth, current_min_node.cost_eval(current_min_node.board[diff_op_1], current_min_node.board[diff_op_2]), alpha, beta, alpha_beta)
			return current_min_node.cost_eval(current_min_node.board[diff_op_1], current_min_node.board[diff_op_2]), self

	def update_max_node_cost(self, cost):
		if(cost > self.cost):
			self.cost = cost
			return True
		return False

	def update_min_node_cost(self, cost):
		if(cost < self.cost):
			self.cost = cost
			return True
		return False

	def capture_if_any(self, pos):
		board = self.board
		if(board[pos] == 1 and pos in range(self.start, self.end + 1)):
			board[pos] = 0
			opponent_capture_pos = len(board) - pos - 2
			total_gain = 1 + board[opponent_capture_pos]
			board[opponent_capture_pos] = 0
			board[self.mancala] = board[self.mancala] + total_gain

	def get_next_move_and_check_for_extra_turn(self, move_pos):
		board = self.board
		stones = board[move_pos]
		board[move_pos] = 0
		j = (move_pos + 1) % len(board)
		while stones:
			if not j == self.mancala_opponent:
				board[j] = board[j] + 1
				stones = stones - 1
			j = (j + 1) % len(board)
		last_stone_pos = (j-1) % len(board)
		self.capture_if_any(last_stone_pos)
		game_end = self.check_if_game_ends_and_update()
		if(last_stone_pos == self.mancala):
			return True, game_end
		else:
			return False, game_end

	def minimax_mancala(self, alpha_beta = False):
		global logList
		root_copy = copy.deepcopy(self)
		best_move = self
		alpha = float("-inf")
		beta = float("inf")
		logFile = open("traverse_log.txt", "w")
		if(alpha_beta):
			logList.append("Node,Depth,Value,Alpha,Beta\n")
		else:
			logList.append("Node,Depth,Value\n")
		node = "root"
		current_depth = 0
		root_copy.cost = float("-inf")
		update_log_file(node, current_depth, root_copy.cost, alpha, beta, alpha_beta)
		begin_pos, end_pos, increment = root_copy.find_pos_order()
		for i in range(begin_pos, end_pos, increment):
			next_move = copy.deepcopy(root_copy)
			if(next_move.board[i]):
				turn, game_end = next_move.get_next_move_and_check_for_extra_turn(i)
				if(turn):
					next_move.cost = float("-inf")
					cost, loop_move = next_move.find_max_move(i, current_depth + 1, False, True, alpha, beta, alpha_beta)
				else:
					next_move.cost = float("inf")
					cost, loop_move = next_move.find_min_move(i, current_depth + 1, True, False, alpha, beta, alpha_beta)
				if(game_end):
					cost = next_move.cost_eval(next_move.board[get_start_player_mancala()], next_move.board[get_opp_player_mancala()])
				if(root_copy.update_max_node_cost(cost)):
					best_move = loop_move if turn else next_move
				if(alpha_beta):
					alpha_old = alpha
					alpha = max(alpha, root_copy.cost)
					if(beta <= alpha):
						update_log_file(node, current_depth, root_copy.cost, alpha_old, beta, alpha_beta)
						break
				update_log_file(node, current_depth, root_copy.cost, alpha, beta, alpha_beta)
		logFile.writelines(["%s" % item  for item in logList])
		logFile.close()
		return best_move
	def minimax_mancala_pruning(self):
		return self.minimax_mancala(alpha_beta = True)

def get_start_player_mancala():
	if(start_player == 1):
		return MANCALA_1
	else:
		return MANCALA_2

def get_opp_player_mancala():
	if(start_player == 1):
		return MANCALA_2
	else:
		return MANCALA_1

def get_text_value(value):
	if(value == float("-inf")):
		return "-Infinity"
	elif(value == float("inf")):
		return "Infinity"
	else:
		return value

def update_log_file(node, depth, value, alpha, beta, alpha_beta = False):
	global post_to_name
	value = get_text_value(value)
	alpha = get_text_value(alpha)
	beta = get_text_value(beta)
	if(alpha_beta):
		logList.append(post_to_name[node] + "," + str(depth) + "," + str(value) + "," + str(alpha) + "," + str(beta) + "\n")
	else:
		logList.append(post_to_name[node] + "," + str(depth) + "," + str(value) + "\n")

def set_board_for_current_player(current_player, cut_off_depth, board):
	if(current_player == 1):
		mancala = Mancala_State(current_player, START_1, END_1, MANCALA_1, MANCALA_2, 0, cut_off_depth, board, float("-inf"))
	else:
		mancala = Mancala_State(current_player, START_2, END_2, MANCALA_2, MANCALA_1, 0, cut_off_depth, board, float("-inf"))
	return mancala

def process_input_file():
	global START_1, START_2, END_1, END_2, MANCALA_1, MANCALA_2, start_player
	textFile = open(sys.argv[2], "r")
	task = int(textFile.readline())
	current_player = int(textFile.readline())
	start_player = current_player
	cut_off_depth = int(textFile.readline())
	board = list()
	board_state_2 = textFile.readline().split()
	board_state_1 = textFile.readline().split()
	mancala_2_val = int(textFile.readline().strip())
	mancala_1_val = int(textFile.readline().strip())
	name_1 = "B"
	name_2 = 2
	index = 0
	for val in board_state_1:
		board.append(int(val))
		post_to_name[index] = name_1 + str(name_2)
		name_2 = name_2 + 1
		index = index + 1
	board.append(mancala_1_val)
	index = index + 1
	name_2 = name_2 - 1
	name_1 = "A"
	board_state_2.reverse()
	for val in board_state_2:
		board.append(int(val))
		post_to_name[index] = name_1 + str(name_2)
		name_2 = name_2 - 1
		index = index + 1
	board.append(mancala_2_val)
	START_1 = 0
	START_2 = len(board_state_1) + 1
	MANCALA_1 = len(board_state_1)
	MANCALA_2 = len(board_state_1) + len(board_state_2) + 1
	END_1 = MANCALA_1 - 1
	END_2 = MANCALA_2 - 1
	textFile.close()
	return (task, current_player, cut_off_depth, board)

def write_next_state_to_file(outputFile, next_state):
	board = next_state.getBoard()
	for i in range(END_2, START_2, -1):
		outputFile.write("%d%s" % (board[i], " "))
	outputFile.write(str(board[START_2]) + "\n")
	for i in range(START_1, END_1, 1):
		outputFile.write("%d%s" % (board[i], " "))
	outputFile.write(str(board[END_1]) + "\n")
	outputFile.write(str(board[MANCALA_2]) + "\n")
	outputFile.write(str(board[MANCALA_1]))

def play_mancala():
	task, current_player, cut_off_depth, board = process_input_file()
	mancala_state = set_board_for_current_player(current_player, cut_off_depth, board)

	task_options = {1: mancala_state.greedy_mancala,
					2: mancala_state.minimax_mancala,
					3: mancala_state.minimax_mancala_pruning
	}
	next_state = task_options[task]()
	outputFile = open("next_state.txt", "w")
	write_next_state_to_file(outputFile, next_state)
	outputFile.close()
play_mancala()