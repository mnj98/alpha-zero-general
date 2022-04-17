from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .three_mmBoard import Board
import numpy as np
import copy

#defined to keep the MCTS from overflowing the stack
MAX_GAME_LENGTH = 30
"""
Game class implementation for the game of TicTacToe.
Based on the OthelloGame then getGameEnded() was adapted to new rules.

Author: Evgeny Tyurin, github.com/evg-tyurin
Date: Jan 5, 2018.

Based on the OthelloGame by Surag Nair.
"""
class three_mmGame(Game):
    def __init__(self, n=3):
        self.n = 3

    def getInitBoard(self):
        # return initial board 
        
        #board has fields:
        #board - 3x3 numpy array
        #turn_count - the number of turns
        return Board()

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.n)

    def getActionSize(self):
        # return number of actions
        return self.n*self.n*3 

    def getAction(self, action):
        #returns action location & piece number from given action id
        
        if action < 9:
             return np.unravel_index(action, self.getBoardSize()), 1
        if action < 18:
            return np.unravel_index(action - 9, self.getBoardSize()), 2
        return np.unravel_index(action - 18, self.getBoardSize()), 3


    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        
        action, piece = self.getAction(action)
        
        #must move to an empy location
        assert board.board[action] == 0


        piece = piece * player
        new_board = Board(copy.deepcopy(board.board), board.turn_count + 1)

        
        old_loc = np.where(board.board == piece)
        if len(old_loc[0]) > 0:
            new_board.board[old_loc[0][0]][old_loc[1][0]] = 0

        new_board.board[action] = piece
        
        return new_board , player * -1

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        #the policy vector has shape 1x27 where:
            #each set of 9 elements represent the valid moves
            #for each of the 3 pieces
    
        valid_locs = (board.board == 0).flatten() * 1

        valid_moves = np.append(valid_locs, np.append(valid_locs, valid_locs))

        if player * 1 not in board.board:
            for i in range(18):
                valid_moves[i + 9] = 0

        elif player * 2 not in board.board:
            for i in range(9):
                valid_moves[i] = 0
            for i in range(9):
                valid_moves[i + 18] = 0

        elif player * 3 not in board.board:
            for i in range(18):
                valid_moves[i] = 0
        return valid_moves

    def getGameEnded(self, board, player):
        #1 if player 1 wins, -1 if player 1 loses
        # 0.00001 for a tie
        if board.turn_count > MAX_GAME_LENGTH:
            return 0.00001
        rows = np.sum(board.board,axis=1)
        columns = np.sum(board.board, axis=0)
        diag1 = np.trace(board.board)
        diag2 = np.trace(np.rot90(board.board))

        if 6 in rows or 6 in columns or diag1 == 6 or diag2 == 6:
            return 1
        if -6 in rows or -6 in columns or diag1 == -6 or diag2 == -6:
            return -1
        return 0


    def getCanonicalForm(self, board, player):
        #print(board)
        # return state if player==1, else return -state if player==-1
        return Board(player * board.board, board.turn_count)
    


    #the next functions are to generate symetric versions of the board and policy vector
    #this adds more equivalent training examples for the NNet
    def map_val(self, num):
        if num == 0: return 0
        if num > 0: return 1
        if num < 0: return -1
    def eqs(self, board):
    
        perms = np.array([[1, 2, 3],[1, 3, 2],[2, 1, 3],[2, 3, 1],[3, 1, 2],[3, 2, 1]])
        boards = np.array([])
        board_flat = np.array([self.map_val(i) for i in board.board.flatten()])
        for i in range(6):
            for j in range(6):
                new_board = np.zeros((9))
                plus = 0
                minus = 0
                for b in range(len(board_flat)):
                    if board_flat[b] == 1:
                        new_board[b] = perms[i][plus]
                        plus += 1
                    if board_flat[b] == -1:
                        new_board[b] = perms[j][minus] * -1
                        minus += 1
                    
                boards = np.append(boards, [Board(new_board.reshape(3,3), board.turn_count)])
        return boards.reshape(36)

    #this does NOT seem efficient at all
    #there may also be duplicates being generated
    def getSymmetries(self, board, pi):
        syms = []

        pi_reshaped = np.array(pi).reshape(3,3,3)
        flip_upDown = (Board(np.flip(board.board, axis = 0), board.turn_count), np.flip(pi_reshaped, axis = 1))
        flip_leftRight = (Board(np.flip(board.board, axis = 1), board.turn_count), np.flip(pi_reshaped, axis = 2))
        transpose = (Board(np.transpose(board.board), board.turn_count), np.transpose(pi_reshaped, axes = (0,2,1)))
        alt_transpose = (Board(np.transpose(np.rot90(np.rot90(board.board))), board.turn_count), np.array([np.transpose(np.rot90(np.rot90(p))) for p in pi_reshaped]))
        rot90 = (Board(np.rot90(board.board), board.turn_count), np.array([np.rot90(p) for p in pi_reshaped]))
        rot180 = (Board(np.rot90(np.rot90(board.board)), board.turn_count), np.array([np.rot90(np.rot90(p)) for p in pi_reshaped]))
        rot270 = (Board(np.rot90(np.rot90(np.rot90(board.board))), board.turn_count), np.array([np.rot90(np.rot90(np.rot90(p))) for p in pi_reshaped]))

        syms += [(a, pi) for a in self.eqs(board)]
        syms += [(a, flip_upDown[1].reshape(27)) for a in self.eqs(flip_upDown[0])]
        syms += [(a, flip_leftRight[1].reshape(27)) for a in self.eqs(flip_leftRight[0])]
        syms += [(a, transpose[1].reshape(27)) for a in self.eqs(transpose[0])]
        syms += [(a, alt_transpose[1].reshape(27)) for a in self.eqs(alt_transpose[0])]
        syms += [(a, rot90[1].reshape(27)) for a in self.eqs(rot90[0])]
        syms += [(a, rot180[1].reshape(27)) for a in self.eqs(rot180[0])]
        syms += [(a, rot270[1].reshape(27)) for a in self.eqs(rot270[0])]


        return syms
    def stringRepresentation(self, board):
        s = ''
        for c in board.board.flatten():
            s += str(c)
        return s + str(board.turn_count)

    @staticmethod
    def display(board):
        print(board.board)
