import sys, copy, random
import pygame as pg
from pygame.locals import *
from tqdm import tqdm

difficulty = 'Hard'

def copyBoard(board):
    return [[tile for tile in row] for row in board]

WHITE = (255, 255, 255)
def displayFont(x, y, text, font, color=WHITE, center=False):
    desc = font.render(text, True, color)
    textRect = desc.get_rect()
    textRect.topleft = x, y
    if center:
        textRect.center = x, y
    wSurface.blit(desc, textRect)

def pushList(l, steps):
    for i in range(steps):
        e = l.pop()
        l.insert(0, e)

    return l

def reset(_):
    global board
    board = Board(difficulties[difficulty])

def setDifficulty(params):
    global difficulty
    difficulty = params[0]

def showSol(_):
    board.grid = copyBoard(board.solution)

def rotate(matrix):
    temp_matrix = []
    for column in range(len(matrix)):
        temp = []
        for row in range(len(matrix) - 1, -1, -1):
            temp.append(matrix[row][column])
        temp_matrix.append(temp)
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            matrix[i][j] = temp_matrix[i][j]
    return matrix

class Board():
    def __init__(self, difficulty):
        self.generateGrid(difficulty)
        self.misses = 0
        self.victory = False
        self.maxMisses = 3
        self.lost = False

    def getFullGrid(self):
        r = []
        startingRow = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        random.shuffle(startingRow)

        for i in range(3):
            for j in range(3):
                startingRow = pushList(startingRow, 3)
                r += [[e for e in startingRow]]
            startingRow = pushList(startingRow, 1)


        #Randomly shuffle blocks of rows
        rowSwitch = random.randint(0, 2)
        replaceWith = random.randint(0, 2)
        while replaceWith != rowSwitch:
            replaceWith = random.randint(0, 2)

        oldRows = r[rowSwitch*3:rowSwitch*3+3]
        otherRows = r[replaceWith*3:replaceWith*3+3]
        r[rowSwitch*3:rowSwitch*3+3] = otherRows
        r[replaceWith*3:replaceWith*3+3] = oldRows

        #Randomly flip the board
        ##Combine the two?
        randVal = random.randint(1, 2)
        if randVal == 1:
            new = [[0 for i in range(9)] for j in range(9)]
            for i, row in enumerate(r):
                for j, tile in enumerate(row):
                    new[i][8-j] = tile

            r = copyBoard(new)

        elif randVal == 2:
            new = [[0 for i in range(9)] for j in range(9)]
            for i, row in enumerate(r):
                for j, tile in enumerate(row):
                    new[8-i][j] = tile

            r = copyBoard(new)

        #Randomly rotate the matrix
        for i in range(random.randint(0, 3)):
            r = rotate(r)

        #Replace numbers on the board
        newNums = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        random.shuffle(newNums)
        r = [[newNums[tile-1] for tile in row] for row in r]
        return r

    def generateGrid(self, difficulty):
        self.grid = self.getFullGrid()
        self.solution = copyBoard(self.grid)
        self.playerInput = [[0 for i in range(9)] for j in range(9)]

        self.finGrid = copyBoard(self.grid)
        for i in range(difficulty):
            saveNum = 0
            while saveNum == 0:
                change1 = random.randint(0, 8)
                change2 = random.randint(0, 8)
                saveNum = self.finGrid[change1][change2]

            self.finGrid[change1][change2] = 0
            self.grid = copyBoard(self.finGrid)

            while self.backTrack() != 1:
                self.finGrid[change1][change2] = saveNum

                saveNum = 0
                while saveNum == 0:
                    change1 = random.randint(0, len(self.finGrid)-1)
                    change2 = random.randint(0, len(self.finGrid[change1])-1)
                    saveNum = self.finGrid[change1][change2]

                self.finGrid[change1][change2] = 0
                self.grid = copyBoard(self.finGrid)


        self.backTrack()
        self.grid = copyBoard(self.finGrid)

    def backTrack(self, row=0, col=0, count=0):
        if row >= 8 and col >= 8:
            return 1+count

        if col >= 9:
            row += 1
            col = 0

        if self.grid[row][col] != 0:
            return self.backTrack(row, col+1, count)

        nums = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        random.shuffle(nums)
        for num in nums:
            if self.legalMove(row, col, num):
                self.grid[row][col] = num

                count = self.backTrack(row, col + 1, count)

            self.grid[row][col] = 0

        return count

    def legalMove(self, row, col, number):
        if number in self.grid[row]:
            return False

        for x in range(9):
            if self.grid[x][col] == number:
                return False

        startRow = row//3
        startCol = col//3
        for i in range(3):
            for j in range(3):
                if number == self.grid[i+startRow*3][j+startCol*3]:
                    return False

        return True

    def __repr__(self):
        r = ''
        for row in self.grid:
            for tile in row:
                r += str(tile) + ' '
            r += '\n'
        r += '\n'
        for row in self.solution:
            for tile in row:
                r += str(tile) + ' '
            r += '\n'

        return r

    def draw(self, lines):
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] != 0:
                    displayFont(i*64+36, j*64+32, str(self.grid[i][j]), font)

                if self.playerInput[i][j] != 0:
                    displayFont(i * 64 + 24, j * 64 + 16, str(self.playerInput[i][j]), smallFont, color=RED)

        for line in lines:
            pg.draw.rect(wSurface, BLACK, line)

        if self.victory:
            displayFont(304, 304, 'Victory!', BIGfont, color=GOLD, center=True)

        elif self.lost:
            displayFont(304, 304, 'You Lost!', BIGfont, color=RED, center=True)

    def makeMove(self, row, col):
        if 0 <= row <= 8 and 0 <= col <= 8 and not self.lost:
            if self.playerInput[row][col] == self.solution[row][col]:
                self.grid[row][col] = self.solution[row][col]
                self.playerInput[row][col] = 0

                self.victory = self.vicotria()

            elif self.playerInput[row][col] != 0:
                self.misses += 1
                self.playerInput[row][col] = 0
                self.capitulation()

    def insertTempNum(self, row, col, num):
        if 0 <= row <= 8 and 0 <= col <= 8 and not self.lost:
            if self.grid[row][col] == 0:
                self.playerInput[row][col] = num

    def vicotria(self):
        for row in self.grid:
            for tile in row:
                if tile == 0:
                    return False

        return True

    def capitulation(self):
        if self.misses >= self.maxMisses:
            self.lost = True

class GUIelements():
    def __init__(self):
        self.buttons = []

        rect = pg.Rect(1, 1, 140, 40)
        rect.center = 700, 50
        self.buttons += [Button(rect, 'New Puzzle', WHITE, reset, BGcolor=GREEN)]

        for i, d in enumerate(difficulties):
            rect = pg.Rect(1, 1, 140, 40)
            rect.center = 700, 150+50*i
            self.buttons += [Button(rect, d, WHITE, setDifficulty, params=[d], BGcolor=RED)]

        rect = pg.Rect(1, 1, 222, 40)
        rect.center = 724, 578
        self.buttons += [Button(rect, 'Show Solution', WHITE, showSol, BGcolor=GREEN)]


    def draw(self):
        for i, d in enumerate(difficulties):
            if d == difficulty:
                rect = pg.Rect(1, 1, 140, 40)
                rect.center = 698, 148+50*i
                pg.draw.rect(wSurface, GOLD, rect)

        [button.draw() for button in self.buttons]

        displayFont(725, 475, 'Mistakes:', smallFont, WHITE, center=True)

        for i in range(board.maxMisses):
            rect = (625+i*75, 500, 48, 48)
            pg.draw.rect(wSurface, BLACK, rect)

        for i in range(board.misses):
            rect = (625+12+i*75, 500+12, 24, 24)
            pg.draw.rect(wSurface, RED, rect)


    def hitDetection(self, x, y):
        rect = pg.Rect(x, y, 1, 1)
        [button.trigger(rect) for button in self.buttons]


class Button():
    def __init__(self, rect, text, textColor, linkedFunc, params=[], BGcolor=WHITE):
        self.rect = rect
        self.text = text
        self.textColor = textColor
        self.linkedFunc = linkedFunc
        self.BGcolor = BGcolor
        self.x, self.y = self.rect.center
        self.params = params

    def draw(self):
        pg.draw.rect(wSurface, self.BGcolor, self.rect)
        displayFont(self.x, self.y, self.text, smallFont, color=self.textColor, center=True)

    def trigger(self, rect):
        if self.rect.colliderect(rect):
            self.linkedFunc(self.params)


pg.init()

BGCOLOR = (35, 35, 128)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)

WINDOWIDTH = 860
WINDOWHEIGHT = 608

wSurface = pg.display.set_mode((WINDOWIDTH, WINDOWHEIGHT))

font = pg.font.SysFont('cambira', 48)
smallFont = pg.font.SysFont('cambria', 24)
BIGfont = pg.font.SysFont('cambria', 84)


lines = [pg.Rect(14, 14+i*3*64, 576, 4) for i in range(4)]
lines += [pg.Rect(14+i*3*64, 14, 4, 576) for i in range(4)]
lines += [pg.Rect(15+i*64, 15, 2, 576) for i in range(10)]
lines += [pg.Rect(15, 15+i*64, 576, 2) for i in range(10)]

keyBinds = {K_1:1, K_2:2, K_3:3, K_4:4, K_5:5, K_6:6, K_7:7, K_8:8, K_9:9, K_0:0}

difficulties = {
    'Easy':32,
    'Medium':40,
    'Hard':48,
}

def main():
    global board
    board = Board(difficulties[difficulty])
    GUI = GUIelements()
    while True:
        for event in pg.event.get():
            if event.type == QUIT:
                return

            if event.type == KEYDOWN:
                if event.key in keyBinds:
                    x, y = pg.mouse.get_pos()
                    row = (x-16)//64
                    col = (y-16)//64
                    num = keyBinds[event.key]
                    board.insertTempNum(row, col, num)

            if event.type == MOUSEBUTTONDOWN or (event.type == KEYDOWN and event.key == K_SPACE):
                x, y = pg.mouse.get_pos()
                row = (x - 16) // 64
                col = (y - 16) // 64
                board.makeMove(row, col)
                GUI.hitDetection(x, y)


        wSurface.fill(BGCOLOR)
        board.draw(lines)
        GUI.draw()
        pg.display.update()




if __name__ == '__main__':
    main()
    pg.quit()

