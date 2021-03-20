#!/usr/bin/env python3
import sys
import timeit

#['./bitwise.py', 'board.txt', 'bitwisefocus', '0', '1']
_, boardloc, focus, turn, player, output, timeLim = sys.argv

print(timeLim)
player=int(player)
timeLim = int(timeLim)
#0 empty, 1 p1, 2 p2, 3 p1k, 4 p2k

#100k runs at 2.68s
def readBoardBulk(board):

    pieces = [0,    0,    0,     0]

    f = open(board,'r')
    
    b = ''.join(f.read().splitlines())
    topB = b.replace('2','0').replace('4','0')
    botB = b.replace('1','0').replace('3','0')

    pieces[0] = int(topB.replace('3','0'),2)
    pieces[2] = int(topB.replace('1','0').replace('3','1'),2)
    pieces[1] = int(botB.replace('4','0').replace('2','1'),2)
    pieces[3] = int(botB.replace('2','0').replace('4','1'),2)
    f.close()
    return pieces

#100k runs at 4.55s
def readBoardBitwise(board):

    pieces = [0,    0,    0,     0]
    f = open(board,'r')
    
    b = ''.join(f.read().splitlines())
    
    trace = 1<<63

    pieces = [0,0,0,0]

    while b:
        if b[0] != '0':
            pieces[int(b[0])-1] |= trace
        b = b[1:]
        trace >>= 1

    f.close()

''' BULK WAS FASTER
n = 100000
print("Bulk:",timeit.timeit(lambda: readBoardBulk(board), number=n))
print("Bitwise:",timeit.timeit(lambda: readBoardBitwise(board), number=n))
'''


fullmask = int('1111111111111111111111111111111111111111111111111111111111111111',2)
home = (int('0000000000000000000000000000000000000000000000000000000011111111',2),
        int('1111111100000000000000000000000000000000000000000000000000000000',2))
notleft = (fullmask-int('1000000010000000100000001000000010000000100000001000000010000000',2),
        fullmask-int('0000000100000001000000010000000100000001000000010000000100000001',2))
notright =(fullmask-int('0000000100000001000000010000000100000001000000010000000100000001',2),
        fullmask-int('1000000010000000100000001000000010000000100000001000000010000000',2))
left = (int('1000000010000000100000001000000010000000100000001000000010000000',2),
        int('0000000100000001000000010000000100000001000000010000000100000001',2))
right =(int('0000000100000001000000010000000100000001000000010000000100000001',2),
        int('1000000010000000100000001000000010000000100000001000000010000000',2))
home = (int('1111111100000000000000000000000000000000000000000000000000000000',2), 
        int('0000000000000000000000000000000000000000000000000000000011111111',2))
shifts = (0,64,128,172)
moves = []

def board2pieces(board):
    pieces = [0,0,0,0]
    for i in range(4):
        pieces[i] = board&fullmask
        board>>=64
    return pieces

def pieces2board(pieces):
    board = 0
    for i in range(4):
        board<<=64
        board+=pieces[3-i]
    return board

#0 empty, 1 p1, 2 p2, 3 p1k, 4 p2k

def printLong(n):
    if isinstance(n, int):
        n = [n]
    for i in n:
        print(format(i, '#0166b'))

def msb(n):#for long
    r = 0
    while n:
        n >>= 1
        r += 1
        if n == 1:
            return r

import math
def msbLog(n):#for long
    n |= n>>1
    n |= n>>2
    n |= n>>4
    n |= n>>8
    n |= n>>16
    n |= n>>32
    n |= n>>64
    n = (n+1)>>1
    return math.log2(n)

def msbBin(n):
    return len(bin(n))-3

def king(board,player):
    toking = (home[player-1]<<(shifts[player]))&(board)
    board -= toking<<shifts[player]
    board += toking<<shifts[player+2]
    return board

def furtherJumps(moves, board, player): #return list of possible jumps, if none are possible, return []
    pieces = board2pieces(board)
    playerPieces = pieces[player]|pieces[player+2]
    notPlayerPieces = (fullmask-playerPieces)
    enemyPieces = pieces[player+1]|pieces[player-1]
    emptySpace = fullmask - (playerPieces + enemyPieces)
    
    fl = (moves[0](notright[player]&playerPieces))&(notPlayerPieces)
    fr = (moves[1](notleft[player]&playerPieces))&(notPlayerPieces)
    bl = 0
    br = 0

    if pieces[player+2]:
        bl = (moves[2]((notright[player])&playerPieces))&(notPlayerPieces)
        br = (moves[3]((notleft[player])&playerPieces))&(notPlayerPieces)

    #shifted by 1 move
    flJ = moves[4]((moves[0](fl&enemyPieces&notleft[player]))&emptySpace)
    frJ = moves[5]((moves[1](fr&enemyPieces&notright[player]))&emptySpace)
    blJ = moves[6]((moves[2](bl&enemyPieces&notleft[player]))&emptySpace)
    brJ = moves[7]((moves[3](br&enemyPieces&notright[player]))&emptySpace)
   
    jump=False
    if flJ or frJ or blJ or brJ:

        fl,fr,bl,br = flJ,frJ,blJ,brJ
        jump=True

    else:
        return []
    j = 1
    flO = moves[4](fl)
    frO = moves[5](fr)
    blO = moves[6](bl)
    brO = moves[7](br)
    #these are now original copies
    #[fb][lr] are now all pieces, labeled by how they can move
    fourDir = (flO,frO,blO,brO)
    if jump:
        return handleJumps(fourDir, moves, board, player)
    return []

def handleJumps(fourDir, moves, board, player):
    pieces = board2pieces(board)
    ret = []
    for m in range(4):
        mask = 1
        move = fourDir[m]
        while move:
            if move&1:
                moved1 = moves[m](mask)
                moved2 = moves[m](moved1)
                jumpedPiece = (board&moved1)|(board&(moved1<<64))|(board&(moved1<<128))|(board&(moved1<<172))
                if mask&pieces[player]:#if man

                    #boards.append((moves[m](mask)<<64)+(mask),(board+((moves[m](mask)<<shifts[player])-(mask<<shifts[player]))))
                    ret.append(((moved2<<64)+mask, board-(mask<<shifts[player])+(moved2<<shifts[player])-jumpedPiece))
                else: 
                    ret.append(((moved2<<64)+mask, board-(mask<<shifts[player+2])+(moved2<<shifts[player+2])-jumpedPiece))
            mask <<= 1
            move >>= 1
    #TODO check for double jumps
    while True:
        newRet = []
        done = True
        for b in range(len(ret)):
            ret[b] = (ret[b][0], king(ret[b][1], player))
            fJ = furtherJumps(moves, ret[b][1], player)
            if fJ:
                done = False
                newRet += fJ
            else:
                newRet.append(ret[b])
        ret = newRet
        if done:
            break
    for b in range(len(ret)):
        ret[b] = (ret[b][0], king(ret[b][1], player))       
    return ret


def possMoves(board, player):
    pieces = board2pieces(board)
    playerPieces = pieces[player]|pieces[player+2]
    notPlayerPieces = (fullmask-playerPieces)
    enemyPieces = pieces[player+1]|pieces[player-1]
    emptySpace = fullmask - (playerPieces + enemyPieces)
    #fl, fr, bl, br
    moves = (lambda x:x>>9, lambda x:x>>7, lambda x:x<<7, lambda x:x<<9, lambda x:x<<9, lambda x:x<<7, lambda x:x>>7, lambda x:x>>9)
    if player == 2:
        #the same
        moves = (lambda x:x<<9, lambda x:x<<7, lambda x:x>>7, lambda x:x>>9, lambda x:x>>9, lambda x:x>>7, lambda x:x<<7, lambda x:x<<9 )
    fl = (moves[0](notright[player]&playerPieces))&(notPlayerPieces)
    fr = (moves[1](notleft[player]&playerPieces))&(notPlayerPieces)
    bl = 0
    br = 0

    if pieces[player+2]:
        bl = (moves[2]((notright[player])&playerPieces))&(notPlayerPieces)
        br = (moves[3]((notleft[player])&playerPieces))&(notPlayerPieces)

    #shifted by 1 move
    flJ = moves[4]((moves[0](fl&enemyPieces&notleft[player]))&emptySpace)
    frJ = moves[5]((moves[1](fr&enemyPieces&notright[player]))&emptySpace)
    blJ = moves[6]((moves[2](bl&enemyPieces&notleft[player]))&emptySpace)
    brJ = moves[7]((moves[3](br&enemyPieces&notright[player]))&emptySpace)
    jump=False
    if flJ or frJ or blJ or brJ:
        fl,fr,bl,br = flJ,frJ,blJ,brJ
        jump=True

    j = 1
    flO = moves[4](fl)
    frO = moves[5](fr)
    blO = moves[6](bl)
    brO = moves[7](br)
    #these are now original copies
    if jump:
        j = 2
    #[fb][lr] are now all pieces, labeled by how they can move
    fourDir = (flO,frO,blO,brO)
    if jump:
        return handleJumps(fourDir, moves, board, player)
    '''
    printBoard(fl)
    print()
    print()
    print()
    printBoard(fr)
    '''
    boards = []
    for m in range(4):
        mask = 1
        move = fourDir[m]
        while move:
            if move&1:
                #shifts = (0,64,128,172)
                if mask&pieces[player]:#if man
                    boards.append(((moves[m](mask)<<64)+(mask),(board+((moves[m](mask)<<shifts[player])-(mask<<shifts[player])))))
                else:
                    boards.append(((moves[m](mask)<<64)+(mask),(board+((moves[m](mask)<<shifts[player+2])-(mask<<shifts[player+2])))))
            mask <<= 1
            move >>= 1
    for b in range(len(boards)):
        boards[b] = (boards[b][0], king(boards[b][1], player))
    return boards
    
def printBoard(board):
    pieces = board2pieces(board)
    b = [c for c in '----------------------------------------------------------------']
    tracker = 0
    mask = 1<<63
    for i in range(64):
        for j in range(len(pieces)):
            if mask&pieces[j]:
                b[tracker]='RBKG'[j]
                break
        tracker += 1
        mask >>= 1
    for i in range(8):
        print(' '.join(b[8*i:8*(i+1)]))
    print()
    print()

'''
import random
n = 100000
print("rand():",timeit.timeit(lambda: random.randint(0,18446744073709551616), number=n))
print("msb():",timeit.timeit(lambda: msb(random.randint(0,18446744073709551616)), number=n))
print("msbLog():",timeit.timeit(lambda: msbLog(random.randint(0,18446744073709551616)), number=n))
print("msbBin():",timeit.timeit(lambda: msbBin(random.randint(0,18446744073709551616)), number=n))
exit()
'''

def evalBoard(board): # currently just counts pieces, kings are double
    p = board2pieces(board)
    print(p)
    if player == 0:
        return (2*bin(p[2]).count('1')+bin(p[0]).count('1')) - (2*bin(p[3]).count('1')+bin(p[3]).count('1'))
    return (2*bin(p[3]).count('1')+bin(p[1]).count('1')) - (2*bin(p[2]).count('1')+bin(p[0]).count('1'))


class Tree(object):
    def __init__(self, board=0, val=None):
        self.board = board
        self.val = val
        printLong(self.val)
        self.children = {}
        self.hasChildren = False

    def populate(self, children):
        for i in children:
            self.children[i[0]] = Tree(i[1], i[0])
            

    def find_minimax(self, minFirst, alpha, beta):
        if len(self.children) == 0:
            return (evalBoard(self.board), self.val)
        if minFirst:
            mini = float("inf")
            for c in self.children.values():
                mm = c.find_minimax(False, alpha, beta)[0]
                mini = min(mini, mm)
                beta = min(beta, mm)
                if beta <= alpha:
                    break
            return (mini, self.val)
        else:
            maxi = float("-inf")
            for c in self.children.values():
                mm = c.find_minimax(True, alpha, beta)[0]
                maxi = max(maxi, mm)
                alpha = max(alpha, mm)
                if beta <= alpha:
                    break
            return (maxi, self.val)
        return self.val

board = pieces2board(readBoardBulk(boardloc))
printBoard(board)
for pm in possMoves(board, player+1):
    printBoard(pm[1])
    print()
    print()
    print()
exit()
'''

    for PM in possMoves(pm[1], player+1):
        printBoard(PM[1])
        print()
        print()
        print()
exit()
'''

def popPoss(tree, player, trace=5):
    if trace == 0:
        return
    tree.populate(possMoves(tree.board, player))
    np = (player+1)%2
    for c in tree.children.values():
        popPoss(c, np, trace-1)
        


n = 10000000
print("possMoves():",timeit.timeit(lambda: possMoves(board,player), number=n), 'per 100k')
exit()
root = Tree(board, 0)
popPoss(root, player)
print(root.find_minimax(False, float("-inf"), float("inf")))
    
    







