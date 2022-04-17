import numpy as np

class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a]!=1:
            a = np.random.randint(self.game.getActionSize())
        return a


class HumanThree_mmPlayer():
	def __init__(self, game):
		self.game = game

	def play(self, board):
		actions = self.game.getValidMoves(board, 1)

		print("==== Available Actions ====")
		actions_str = ''
		action_id = 0

		action_dict = {}
		for i,action in enumerate(actions):
			if action == 1:
				action_loc, piece = self.game.getAction(i)
				actions_str += 'id: ' + str(action_id)+ ' Put piece ' + str(piece) + ' at ' + str(action_loc) + ' \n'
				action_dict[action_id] = i
				action_id += 1

		print(actions_str)

		print('Enter move id:')

		

		while True:
			try:
				input_action = action_dict[int(input())]
				break

			except ValueError:
				print("Not a valid number, try again: ")
			except KeyError:
				print("Not a valid id, try again: ")

		return input_action


