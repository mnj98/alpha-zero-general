import numpy as np


class Board():
	def __init__(self, board = np.zeros((3, 3), dtype='int8'), count = 0):
		self.n = 3
		self.turn_count = count
		self.board = board
