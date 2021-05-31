import random
import numpy as np



LEARNING_RATE = .01

layers = [128,100,100,100,1]



def sigmoid(z):
    return 1/(1+np.exp(-z))

class CheckersEval:
    def __init__(self, dna=None):
        self.weights = []
        self.dWeights = [None for i in range(len(layers)-1)]
        self.biases = []
        self.dBiases = [None for i in range(len(layers)-1)]
        self.layers = layers
        self.cacheLayers = [None for i in range(len(layers)-1)]
        if dna:
            self.readIn(dna)
        else:
            self.fillRandom()

    
    def fillRandom(self):
        layers = self.layers
        self.weights = []
        self.biases = []
        for i in range(len(layers)-1):
            self.weights.append(np.random.randn(layers[i+1], layers[i])*.01)
            self.biases.append(np.zeros((layers[i+1], 1)))

    
    def cost(self, A, Y):
        logprobs = np.multiply(np.log(A), Y) + np.multiply((1-Y), np.log(1 - A))
        cost = - np.sum(logprobs)
        cost = float(np.squeeze(cost))
        return cost

    
    def backProp(self, X, Y):
        m = X.shape[1]
        dZ = self.cacheLayers[-1]-Y
        for i in range(len(self.layers)-3):
            i += 2
            print(i)
            self.dWeights[-i] = np.dot(dZ, self.cacheLayers[-i-1].T)/m
            self.dBiases[-i] = np.sum(dZ, axis=1, keepdims=True)/m
            dZ = np.multiply(np.dot(self.weights[-i+1].T, dZ), 1 - np.power(self.cacheLayers[-i-1], 2))


    def gradient_descent(self):
        for i in range(len(self.weights)):
            self.weights[i] -= self.weights[i]-(LEARNING_RATE*self.dWeights[i])
            self.biases[i] -= self.biases[i]-(LEARNING_RATE*self.dBiases[i])

        

    def writeOut(self, outfile):
        np.save(outfile, (self.weights, self.biases))


    def readIn(self, infile):
        self.weights,self.biases = np.load(infile, allow_pickle=True)


    def forwardProp(self, X):
        Z = X
        for i in range(len(self.layers)-2):
            Z = np.tanh(np.dot(self.weights[i], Z)+self.biases[i])
            self.cacheLayers[i] = Z.copy()
        Z = sigmoid(np.dot(self.weights[-1], Z)+self.biases[-1])
        self.cacheLayers[-1] = Z
        return Z


    def boardToX(self, board):
        X = np.zeros((128, 1), dtype=np.float32)
        win = [True, True]
        for i in range(32):
            i0 = int(board[i])-1
            if i0>=0:
                win[i0//2] = False
                X[32*i0+i] = 1.0
        return X, win


    def round(self, expected, board):
        X, _ = self.boardToX(board)
        print(X)
        A = self.forwardProp(X)
        print("HERE")
        Y = expected
        cost = self.cost(A, Y)
        print(f'cost is {cost}')
        self.backProp(X, Y)
        self.gradient_descent()

    
    def boardEval(self, board):
        X, win = self.boardToX(board[:32])
        if win[0]:
            return -1000
        if win[1]:
            return 1000
        return self.forwardProp(X)
        





















