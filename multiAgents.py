# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for 
# educational purposes provided that (1) you do not distribute or publish 
# solutions, (2) you retain this notice, and (3) you provide clear 
# attribution to UC Berkeley, including a link to 
# http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero 
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and 
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util, math

from game import Agent

def getAllFood(foodGrid, top, right):
  """
  This function finds out what are the food that are yet to be consumed
  """
  foodPoints = []
  for i in range(1, right + 1):
    for j in range(1, top + 1):
      if foodGrid[i][j] is True:
        foodPoints.append((i,j))
  return foodPoints    #Return as list of tupples of the coordinates of the food that are still to be consumed


class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def getManDistance(self, cood1, cood2):

        return math.fabs((cood1[0] - cood2[0])) + math.fabs((cood1[1] - cood2[1]))
        

    def evaluationFunction(self, currentGameState, action):
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        #print dir(successorGameState)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        foodLocations = getAllFood(newFood, (newFood.height-2), (newFood.width-2));
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        #Penalty if staying in the same place
        if currentGameState.getPacmanPosition() == newPos:
          return -100

        #Get the maximum distance that the agent can possibly travel
        MaxManhattenDistance = newFood.height + newFood.width - 4
        
        score = 0
        maxDistScore = -500

        #Calculate some kind of score based on the nearest food
        for foodLocation in foodLocations:
          distanceScore = MaxManhattenDistance - self.getManDistance(newPos, foodLocation)
          if distanceScore > maxDistScore:
            maxDistScore = distanceScore

        #Calculate the score
        score = score + maxDistScore + 5000/(successorGameState.getNumFood() + 1)

        for ghost in newGhostStates:
          #Find the distance to this ghost
          ghostManDist = self.getManDistance(newPos, ghost.getPosition())

          #If the ghost is scared, give the pacman, greater incentive to go towards it.
          if ghost.scaredTimer >= ghostManDist:
            score += 1000

          #If the ghost can reach this position in the next move, give it a very negative score.
          if ghostManDist == 0:
            return -999999

          #If none of the above cases apply to this position, then give it a score based on how near it is
          #to the ghost. Closer it is to a active ghost, the more negative the score.
          score -= MaxManhattenDistance/(ghostManDist + 1)
          
        return score

def scoreEvaluationFunction(currentGameState):
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)
        
class MinimaxAgent(MultiAgentSearchAgent):

    def getAction(self, gameState):

        #Starting with ourself        
        weightedActions = []
        
        for action in gameState.getLegalActions(0):
          #For all possible actions from this spot, we calculate the best action
          sucessorState = gameState.generateSuccessor(0, action)
          #Add an action and the corresponding score to a weighted list
          weightedActions.append((action, self.minimax(sucessorState, self.depth, 0, 1)))
          
        return getBestAction(weightedActions)

    def minimax(self, gameState, depth, levelBool, agent) :

        #List to store the values of each outcome
        agentValue = []

        #Base case, terminate here.
        #This is invoked at the leaves of the tree
        if depth <= 0 or gameState.isWin() or gameState.isLose() :
          return self.evaluationFunction(gameState)

        #Recursing based on the state
        for action in gameState.getLegalActions(agent):
          sucessorState = gameState.generateSuccessor(agent, action)
          if levelBool == 0:
            #Level at parity 0, we start from here
            agentValue.append(self.minimax(sucessorState, depth, 1, agent+1))
          else : 
            if (agent == gameState.getNumAgents()-1):
              #Backing up by one level as the current level has been exhausted
              #And start again with agent 0
              agentValue.append(self.minimax(sucessorState, depth-1, 0, 0))
            else :
              agentValue.append(self.minimax(sucessorState, depth, 1, agent+1))

        if levelBool == 0 :
          #At even parity, we take the maximum of that level
          return max(agentValue)
        else :
          #At odd parity, we take the minimum of that level
          return min(agentValue)        

"""
Convenience global function that gives the best action given a weighted list of
actions and values.
"""
def getBestAction(weightedActions) :
        maxVal = -99999
        for action, weight in weightedActions :
          if weight >= maxVal :
            maxVal = weight
            bestAction = action

        return bestAction

class AlphaBetaAgent(MultiAgentSearchAgent):

    def getAction(self, gameState):
        weightedAction = []

        #For all possible actions from a given state
        for action in gameState.getLegalActions(0):
          sucessorState = gameState.generateSuccessor(0, action)
          #We invoke the minmaxPrune function with the default values
          value = self.minimaxPrune(sucessorState, self.depth, 1, 1, -99999, 99999)
          #Add all values with their corresponding actions to a list
          weightedAction.append((action, value))

          try:
            alpha
          except NameError:
            alpha = -99999
          #Keep updating alpha. We are not interested in Beta at this level
          alpha = max(alpha, value)

        #Return the action which has the maximum value in the weightes list
        return getBestAction(weightedAction)
            

    def minimaxPrune(self, gameState, depth, levelBool, agent, alpha, beta):

      #Base case. We terminate here.
      if depth <= 0 or gameState.isWin() or gameState.isLose() :
        return self.evaluationFunction(gameState)

      #Recursing
      for action in gameState.getLegalActions(agent):
        sucessorState = gameState.generateSuccessor(agent, action)
        #Level at parity zero
        if levelBool == 0:

          try:
            value
          except NameError:
            value = -99999
          
          value = max(value, self.minimaxPrune(sucessorState, depth, 1, (agent+1), alpha, beta))

          # Updating the alpha value
          if value > beta:
            return value
          alpha = max (alpha, value)
          
        else:
          #Now, we have to go up the tree by one level and then start from agent 0
          if agent == gameState.getNumAgents()-1:

            try:
              value
            except NameError:
              value = 99999
            
            value = min(value, self.minimaxPrune(sucessorState, depth - 1, 0, 0, alpha, beta))  
          else:
            #We continue to compute the values for the next agent
            try:
              value
            except NameError:
              value = 99999
            value = min(value, self.minimaxPrune(sucessorState, depth, 1, (agent+1),alpha, beta))

          # Updating the beta value
          if value < alpha:
            return value
          beta = min(beta, value)
      return value

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

class ContestAgent(MultiAgentSearchAgent):
    """
      Your agent for the mini-contest
    """

    def getAction(self, gameState):
        """
          Returns an action.  You can use any method you want and search to any depth you want.
          Just remember that the mini-contest is timed, so you have to trade off speed and computation.

          Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
          just make a beeline straight towards Pacman (or away from him if they're scared!)
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

