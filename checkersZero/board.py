startState = '111111111111000000003333333333330'
spacing = '  '

codes = {0:'- ',1:'m ', 2:'k ', 3:'M ', 4:'K `'}
moves = {1:[2,3], 2:[0,1,2,3], 3:[0,1], 4:[0,1,2,3]}
enemies = {1:[3,4], 2:[3,4], 3:[1,2], 4:[1,2]}
turns = {0:[1,2], 1:[3,4]}

class Board(object):
    def __init__(self):
        self.spaces = [0 for i in range(32)]
        self.adj = {i:[-1 for i in range(4)] for i in range(32)}#[space][ul, ur, dr, dl], thus, they are opposed to the second successor
        self.turn = 0
        for i in range(32):
            j = (i//4)
            if j%2:
                if i>3:
                    if (i+4)%8:
                        self.adj[i][0]=i-5
                    self.adj[i][1]=i-4
                if i<28:
                    if (i+4)%8:
                        self.adj[i][3]=i+3
                    self.adj[i][2]=i+4
            else:
                if i>3:
                    if (i+5)%8:
                        self.adj[i][1]=i-3
                    self.adj[i][0]=i-4
                if i<28:
                    if (i+5)%8:
                        self.adj[i][2]=i+5
                    self.adj[i][3]=i+4

 
    def popBoard(self, state):
        if len(state) != 33:
            print("Invalid state '%s' with len of %i"%(state, len(state)))
            print("board states are 32 squares followed by the turn")

        for i in range(32):
            self.spaces[i] = int(state[i])
        self.turn = int(state[-1])


    def printBoard(self, board=None):
        if not board:
            board=self.spaces
        for i in range(len(spacing)*5):
            print('--', end='')
        print()
        for i in range(8):
            print('|', end='')
            if not i%2:
                print(spacing, end='')
            for j in range(4):
                #print(4*i+j, end=spacing)
                print(codes[board[4*i+j]], end=spacing)
            if i%2:
                print(spacing, end='')
            print('|')


    def stateOut(self, board=None):
        if not board:
            board = self.spaces
        return ''.join([str(i) for i in (board+[self.turn])])


    def getTarg(self, move, jump=False):
        if jump:
            return self.getTarg((self.getTarg(move), move[1]))
        ret= self.adj[move[0]][move[1]]
        return ret


    def mPiece(self, move, board=None):
        if not board:
            board = self.spaces.copy()
        if type(move) == tuple:
            board[self.getTarg(move)] = board[move[0]]
            board[move[0]] = 0
            return board, 0
        for m in move:
            board[self.getTarg(m)] = 0
        board[self.getTarg(move[-1], True)] = board[move[-1][0]]
        board[move[0][0]] = 0
        return board, len(move)


    def furtherJumps(self, jump, board):
        jumps = []
        piece = board[jump[0][0]]
        for adj in moves[piece]:
            if adj == (jump[-1][1]+2)%4:
                print('backtrack')
                continue
            targ = self.getTarg(jump[-1], True)
            if self.adj[targ][adj] != -1:
                if (board[self.adj[targ][adj]] in enemies[piece]) and not board[self.adj[self.adj[targ][adj]][adj]]:
                    jumps.append(jump+[(targ, adj)])
        if jumps:
            ret = []
            for j in jumps:
                ret += self.furtherJumps(j, board)
            return ret
        return [jump]


    def possMoves(self, board=None):
        normMoves = []
        jumps = []
        if not board:
            board = self.spaces
        for i in range(32):
            piece = board[i]
            if self.spaces[i] in turns[self.turn%2]:
                for adj in moves[piece]:
                    if self.adj[i][adj] != -1:
                        if self.adj[self.adj[i][adj]][adj] != -1 and (board[self.adj[i][adj]] in enemies[piece]) and not board[self.adj[self.adj[i][adj]][adj]]:
                            jumps.append([(i, adj)])
                        if not jumps and not board[self.adj[i][adj]]:
                            normMoves.append((i, adj))
        if not jumps:
            return normMoves
        ret = []
        for j in jumps:
            ret += self.furtherJumps(j, board)
        return ret


    def getStates(self, moves, board=None):
        if not board:
            board = self.spaces
        ret = []
        for m in moves:
            ret.append(self.mPiece(m)[0])
        return ret

    
    def nextTurn(self):
        self.turn = (self.turn+1)%2





