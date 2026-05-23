import pygame
import distinctipy

# Game Params
gridDim = 75
blockSize = 10

turn = 0
currentSwitch = 0
currentRound = 0
currSimStep = 0

# How many cells do players get to put down each time it is their turn
turnsPerSwitch = 20
# How many times do you cycle through players before doing a simulation round
switchesPerRound = 1
# How many simuilation rounds do you have before the game ends
roundsPerGame = 5
# How long do you run the simulation for each sim step
simStepsPerRound = 50

headerSize = 50
cellMargin = 1
# How many people are playing
playerCount = 2
currentPlayer = 1
borderWidth = 10
colors = [(255,255,255)]
mouseDown = False
finished = False
simFinished = False
# Do opponents take other players resources
aggressivePlayers = False
for color in distinctipy.get_colors(playerCount):
    colors.append((int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)))

gameBoard = [[0 for i in range(gridDim)] for j in range(gridDim)]

# Setup
pygame.init()
screen = pygame.display.set_mode((gridDim*blockSize + (2 * borderWidth), gridDim*blockSize + headerSize + (borderWidth * 2)))
clock = pygame.time.Clock()
running = True
pygame.font.init()
mainHeader = pygame.font.SysFont('Arial', 30)
scoreText = pygame.font.SysFont('Arial', 12)


# Helper functions
def drawGrid():
    for x in range(len(gameBoard)):
        for y in range(len(gameBoard[x])):
            rect = pygame.Rect(x * blockSize + cellMargin + borderWidth, y * blockSize + cellMargin + headerSize + borderWidth, blockSize - (2 * cellMargin), blockSize - (2 * cellMargin))
            pygame.draw.rect(screen, colors[gameBoard[x][y]], rect)

def stepBoard(gameBoard):
    newBoard = [[0 for i in range(gridDim)] for j in range(gridDim)]
    playerScores = [0 for i in range(playerCount)]
    for x in range(gridDim):
        for y in range(gridDim):
            cell = gameBoard[x][y]
            if cell == 0:
                capturingPlayer = 0
                for i in range(1, playerCount+1):
                    cellResources = 0
                    if aggressivePlayers:
                        cellResources = getCellResourcesAggresive(x, y, i)
                    else:
                        cellResources = getCellResources(x, y, i)
                    if cellResources == 3:
                        if capturingPlayer:
                            capturingPlayer = 0
                            break
                        else:
                            capturingPlayer = i
                newBoard[x][y] = capturingPlayer
                if capturingPlayer != 0:
                    playerScores[capturingPlayer -1 ] += 1
            else:
                cellResources = getCellResourcesAggresive(x, y, cell) if aggressivePlayers else getCellResources(x, y, cell)
                if cellResources > 3:
                    newBoard[x][y] = 0
                if cellResources == 3 or cellResources == 2:
                    newBoard[x][y] = cell
                    playerScores[cell - 1] += 1
                if cellResources < 2:
                    newBoard[x][y] = 0
    return newBoard, playerScores

def getCellResources(x, y, player):
    resources = 0 if x == 0 or y == 0 or gameBoard[x-1][y-1] != player else 1 
    resources += 0 if y == 0 or gameBoard[x][y-1] != player else 1
    resources += 0 if x == gridDim-1 or y == 0 or gameBoard[x+1][y-1] != player else 1
    resources += 0 if x == 0 or gameBoard[x-1][y] != player else 1
    resources += 0 if x == gridDim-1 or gameBoard[x+1][y] != player else 1
    resources += 0 if x == 0 or y == gridDim-1 or gameBoard[x-1][y+1] != player else 1
    resources += 0 if y == gridDim-1 or gameBoard[x][y+1] != player else 1
    resources += 0 if x == gridDim-1 or y == gridDim-1 or gameBoard[x+1][y+1] != player else 1
    return resources

def getCellResourcesAggresive(x, y, player):
    resources = 0 if x == 0 or y == 0 or gameBoard[x-1][y-1] == 0 else -1 if gameBoard[x-1][y-1] != player else 1 
    resources += 0 if y == 0 or gameBoard[x][y-1] == 0 else -1 if gameBoard[x][y-1] != player else 1
    resources += 0 if x == gridDim-1 or y == 0 or gameBoard[x+1][y-1] == 0 else -1 if gameBoard[x+1][y-1] != player else 1
    resources += 0 if x == 0 or gameBoard[x-1][y] == 0 else -1 if gameBoard[x-1][y] != player else 1
    resources += 0 if x == gridDim-1 or gameBoard[x+1][y] == 0 else -1 if gameBoard[x+1][y] != player else 1
    resources += 0 if x == 0 or y == gridDim-1 or gameBoard[x-1][y+1] == 0 else -1 if gameBoard[x-1][y+1] != player else 1
    resources += 0 if y == gridDim-1 or gameBoard[x][y+1] == 0 else -1 if gameBoard[x][y+1] != player else 1
    resources += 0 if x == gridDim-1 or y == gridDim-1 or gameBoard[x+1][y+1] == 0 else -1 if gameBoard[x+1][y+1] == 0 else 1
    return resources

def getPlayerScores():
    playerScores = [0 for i in range(playerCount)]
    for x in range(gridDim):
        for y in range(gridDim):
            cell = gameBoard[x][y]
            if cell != 0:
                playerScores[cell - 1] += 1
    return playerScores

#Game Loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseDown = True
        if event.type == pygame.MOUSEBUTTONUP:
            mouseDown = False
        if mouseDown and currentPlayer != 0:
            pos = pygame.mouse.get_pos()
            xInd = (pos[0] - borderWidth) // blockSize
            yInd = (pos[1] - headerSize - borderWidth) // blockSize
            if xInd < gridDim and yInd < gridDim:
                if gameBoard[xInd][yInd] == 0: 
                    gameBoard[xInd][yInd] = currentPlayer
                    turn += 1
                elif gameBoard[xInd][yInd] == currentPlayer:
                    gameBoard[xInd][yInd] = 0
                    turn -= 1
                    if turn < 0:
                        turn = 0
    
    if simFinished:
        continue

    if turn == turnsPerSwitch:
        turn = 0
        currentPlayer = ((currentPlayer + 1) % (playerCount + 1))
        mouseDown = False
        if currentPlayer == 0:
            currentSwitch += 1
            if currentSwitch != switchesPerRound:
                currentPlayer = 1
            else:
                currentSwitch = 0
                currentRound += 1
    
    if currentRound == roundsPerGame:
        finished = True

    playerScores = []
    if currentPlayer == 0:
        gameBoard, playerScores = stepBoard(gameBoard)
        currSimStep += 1
        if currSimStep == simStepsPerRound:
            currSimStep = 0
            currentPlayer = 1
            mouseDown = False
    else:
        playerScores = getPlayerScores()
        if finished:
            simFinished = True

    screen.fill("#123456")
    
    if currentPlayer != 0:
        text_surface = mainHeader.render("Player #" + str(currentPlayer) + "'s Turn", True, (220, 220, 220))
        screen.blit(text_surface, ((gridDim*blockSize/2) - (text_surface.get_width() / 2), 10))
    else:
        text_surface = mainHeader.render("Simulating, Please Wait.", True, (220, 220, 220))
        screen.blit(text_surface, ((gridDim*blockSize/2) - (text_surface.get_width() / 2), 10))

    drawGrid()

    maxPlayer = 0
    maxScore = 0
    for player in range(len(playerScores)):
        text_surface = scoreText.render("Player #" + str(player + 1) + " Score: " + str(playerScores[player]), True, colors[player + 1])
        screen.blit(text_surface, (10, player * 20))
        if simFinished and maxScore < playerScores[player]:
            maxPlayer = player
            maxScore = playerScores[player]
    if simFinished:
        win_text = mainHeader.render("Player #" + str(maxPlayer + 1) + " Wins!", True, (0,0,0))
        score_text = mainHeader.render("Score: " + str(maxScore), True, (0,0,0))
        rect = pygame.Rect((min((gridDim*blockSize/2) - (win_text.get_width() / 2), (gridDim*blockSize/2) - (score_text.get_width() / 2)) - 25), 175, max(win_text.get_width(), score_text.get_width()) + 50, 125)
        pygame.draw.rect(screen, (200, 200, 200), rect)
        screen.blit(win_text, ((gridDim*blockSize/2) - (win_text.get_width() / 2), 200))
        screen.blit(score_text, ((gridDim*blockSize/2) - (score_text.get_width() / 2), 250))

    pygame.display.flip()

    clock.tick(60)

pygame.quit()

