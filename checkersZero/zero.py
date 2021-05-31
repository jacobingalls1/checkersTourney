#!/usr/bin/env python3
import sys
import timeit
from board import Board
import board
from checkersEval import CheckersEval


CE = CheckersEval(sys.argv[1])

class Tree(object):
    def __init__(self, board, move):
        self.board = board
        self.children = {}
        self.hasChildren = False


    def populate(self, children):
        j = 0
        for i in children:
            self.hasChildren = True
            self.children[j] = Tree(i[1], i[0])
            j += 1 

    
    def popWithMoves(self, moves2children):
        j = 0
        for i in moves2children:
            self.children[j] = Tree(i[0],i[1])
            j += 1


    def find_minimax(self, minFirst, alpha, beta):
        if not self.hasChildren:
            return CE.boardEval(self.board)
        if minFirst:
            mini = float("inf")
            for c in self.children.values():
                mm = c.find_minimax(False, alpha, beta)
                mini = min(mini, mm)
                beta = min(beta, mm)
                if beta <= alpha:
                    break
            return mini
        else:
            maxi = float("-inf")
            for c in self.children.values():
                mm = c.find_minimax(True, alpha, beta)
                maxi = max(maxi, mm)
                alpha = max(alpha, mm)
                if beta <= alpha:
                    break
            return maxi
   

b=Board()
t=Tree(board.startState, None)

def runRound(board, tree, depth=1):
    m = board.possMoves()
    s = board.getStates(m)
    moves2children = []
    for i in range(len(s)):
        moves2children.append((board.stateOut(s[i]), m[i]))
    tree.popWithMoves(moves2children)
    if not depth:
        return
    for c in tree.children.values():
        board.popBoard(c.board)
        board.nextTurn()
        runRound(board, c, depth-1)


#singleKing = '000000000030000200000000000000001'
b.popBoard(board.startState)
#b.popBoard(singleKing)
runRound(b,t,3)
b.printBoard()
print('\n\n\n')
#print(CE.boardEval(b.stateOut()))
#expected = t.find_minimax(b.turn==1, float('-inf'), float('inf'))

CE.round(0, t.board)

CE.writeOut('nets/100x3_1')






