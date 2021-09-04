from utils import lookAhead, lookBehind, lookBehindOutOfBounds, top, printAndExit, preHandleSides, printReducedForm, printIntermediateStep, printSides, getPolynomialDegree, solver
import sys
import functools
import operator
from enums import StateTransitions, NumberStateTransition, VariableStateTransition
from variables import Variable, createVariable


CONTEXT_STATE = StateTransitions.NONE
NUMBER_STATE = NumberStateTransition.NONE
EXPOSANT_STATE = NumberStateTransition.NONE

CONTEXT_STATE_STACK = [(StateTransitions.NONE, -1)]
NUMBER_STATE_STACK = [NumberStateTransition.NONE]
EXPOSANT_STATE_STACK = [VariableStateTransition.NONE]

terms = []


def createState(state, index):
	return (state, index)


def pushGlobalState(state, index):
	stack = CONTEXT_STATE_STACK

	if state == StateTransitions.NONE:
		stack.append(createState(state, index))
		return
	
	poppedState = stack.pop()

	if poppedState[0] != StateTransitions.NONE:
		stack.append(poppedState)
	
	elif poppedState[0] == StateTransitions.NONE and len(stack) > 0:
		poppedState = top(stack)[0]
	
	else:
		poppedState = poppedState[0]

	if state == StateTransitions.OPERATORS:
		if poppedState != StateTransitions.NUMBER and poppedState != StateTransitions.VARIABLES and poppedState != StateTransitions.NUMBERNEG:
			printAndExit("An operator must be preceded by a number or a variable")
	
	if state == StateTransitions.NUMBER:
		if poppedState != StateTransitions.NONE and poppedState != StateTransitions.OPERATORS:
			printAndExit("A number must be preceded by an operator or being the first element in the string")
	
	if state == StateTransitions.NUMBERNEG:
		if poppedState != StateTransitions.NONE and poppedState != StateTransitions.OPERATORS:
			printAndExit("A numberneg must be preceded by an operator or being the first element in the string")
	
	if state == StateTransitions.VARIABLES:
		if poppedState != StateTransitions.NONE and poppedState != StateTransitions.OPERATORS:
			printAndExit("A variable must be preceded by an operator or being the first element in the string")
		
	if state == StateTransitions.NONE:
		if poppedState == StateTransitions.NONE:
			printAndExit("Shouldn't happen...")

	stack.append(createState(state, index))


def pushNumberState(state):
	stack = NUMBER_STATE_STACK
	poppedState = stack.pop()

	
	if state == NumberStateTransition.NEGATIVE:
		if poppedState != NumberStateTransition.NONE:
			printAndExit("When a '-' represent a negative number it can only appear once, behind the number")

	if state == NumberStateTransition.FLOAT:
		if poppedState != NumberStateTransition.DIGIT:
			printAndExit("To input a floating point number, the '.', can only appear once, after a digit")
	
	if state == NumberStateTransition.DIGIT:
		if poppedState == NumberStateTransition.FLOATUNCOVERED:
			stack.append(NumberStateTransition.FLOAT)
			return
		if poppedState == NumberStateTransition.FLOAT:
			stack.append(poppedState)
			return
	
	if state == NumberStateTransition.FLOATUNCOVERED:
		if poppedState != NumberStateTransition.DIGIT:
			printAndExit("To input a floating point number, the '.', can only appear once, after a digit")

	stack.append(state)


def pushExposantNumberState(state):
	stack = EXPOSANT_STATE_STACK
	poppedState = stack.pop()

	if state == VariableStateTransition.FLOAT:
		printAndExit("Exposant cannot be a floating point")
	
	if state == VariableStateTransition.DIGIT:
		if poppedState == VariableStateTransition.EXPUNCOVERED:
			stack.append(VariableStateTransition.EXP)
			return
		elif poppedState != VariableStateTransition.EXP:
			printAndExit("A digit in this context must come after an exposent '^'")

		if poppedState == VariableStateTransition.EXP:
			stack.append(poppedState)
	
	if state == VariableStateTransition.EXPUNCOVERED:
		if poppedState != VariableStateTransition.NONE:
			printAndExit("There cannot be multiple '^' by exponent")

	stack.append(state)


def handleNegativeToken(index):
	ahead = lookAhead(index, equation)
	behind = lookBehind(index, equation)
	NUMVAR = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X']
	OP = ['-', '+', '*']

	#OPERATOR CASE:
	if (behind in NUMVAR and ahead in NUMVAR) or (behind in NUMVAR and ahead in OP):
		pushGlobalState(StateTransitions.OPERATORS, index)

	#SIGN CASE:
	elif (behind == lookBehindOutOfBounds and ahead in NUMVAR) or (behind in OP and ahead in NUMVAR):
		pushGlobalState(StateTransitions.SIGN, index)
	
	else:
		pushGlobalState(StateTransitions.ERROR, f"something unexpected happened at index: {index}")


def findContextAtSign(index, token):
	ahead = lookAhead(index, equation)
	numberHandlingCharset = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

	CONTEXT_STATE_STACK.pop()
	pushGlobalState(StateTransitions.NONE, index)

	if ahead in numberHandlingCharset:
		pushGlobalState(StateTransitions.NUMBERNEG, index)
	
	if ahead == 'X':
		pushGlobalState(StateTransitions.VARIABLES, index)


def findContextAtNone(index, token):
	charset = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '.', 'X', '^', '+', '*']
	numberHandlingCharset = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
	operatorhandlingCharset = ['+', '*']

	if token not in charset:
		printAndExit(f"The character: {token} at index: {index} is not allowed")
	
	if token in numberHandlingCharset:
		pushGlobalState(StateTransitions.NUMBER, index)
	
	elif token == '-':
		handleNegativeToken(index)
	
	elif token in operatorhandlingCharset:
		pushGlobalState(StateTransitions.OPERATORS, index)
	
	elif token == 'X':
		pushGlobalState(StateTransitions.VARIABLES, index)
	
	else:
		pushGlobalState(StateTransitions.ERROR, f"The character: {token} at index: {index} is not making sense")


def error(index, token):
	error = top(CONTEXT_STATE_STACK)[1]
	printAndExit(error)


def findContextAtNumber(index, token):
	digitHandlingCharset = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
	floatHandlingCharset = "."

	if token in digitHandlingCharset:
		pushNumberState(NumberStateTransition.DIGIT)

	elif token in floatHandlingCharset:
		pushNumberState(NumberStateTransition.FLOATUNCOVERED)

	elif top(NUMBER_STATE_STACK) == NumberStateTransition.FLOATUNCOVERED:
		if token not in digitHandlingCharset:
			printAndExit(f"At index: {index} you must specify the decimal for your floating point number")
	
	else:
		pushGlobalState(StateTransitions.SLICE, index)


def findContextAtVariable(index, token):
	digitHandlingCharset = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
	floatHandlingCharset = "."
	exposantHandlingCharset = "^"

	if token in digitHandlingCharset:
		pushExposantNumberState(VariableStateTransition.DIGIT)
	
	elif token == 'X':
		return
	
	elif token in exposantHandlingCharset:
		pushExposantNumberState(VariableStateTransition.EXPUNCOVERED)
	
	elif top(EXPOSANT_STATE_STACK) == VariableStateTransition.EXPUNCOVERED:
		if token not in digitHandlingCharset:
			printAndExit(f"At index: {index} you must give a number after an exponent operator")
	
	elif token in floatHandlingCharset:
		pushExposantNumberState(VariableStateTransition.FLOAT)
	
	else:
		pushGlobalState(StateTransitions.SLICE, index)


def findContextAtNumberNeg(index, token):
	digitHandlingCharset = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
	floatHandlingCharset = "."

	if token in digitHandlingCharset:
		pushNumberState(NumberStateTransition.DIGIT)
	elif token in floatHandlingCharset:
			pushNumberState(NumberStateTransition.FLOATUNCOVERED)
	elif top(NUMBER_STATE_STACK) == NumberStateTransition.FLOATUNCOVERED:
		if token not in digitHandlingCharset:
			printAndExit(f"At index: {index} you must specify the decimal for your floating point number")
	else:
		pushGlobalState(StateTransitions.SLICE, index)


def findContextAtOperators(index, token):
	if top(CONTEXT_STATE_STACK) == (StateTransitions.OPERATORS, index):
		pushGlobalState(StateTransitions.SKIP, index)


def sliceString(index, equation):
	global NUMBER_STATE_STACK
	global EXPOSANT_STATE_STACK
	sliceEnd = CONTEXT_STATE_STACK.pop()[1]
	sliceStart = top(CONTEXT_STATE_STACK)[1]

	if top(CONTEXT_STATE_STACK)[0] == StateTransitions.NUMBER or top(CONTEXT_STATE_STACK)[0] == StateTransitions.NUMBERNEG:

		if top(NUMBER_STATE_STACK) == NumberStateTransition.FLOAT:
			terms.append(float(equation[sliceStart:sliceEnd]))
		elif top(NUMBER_STATE_STACK) == NumberStateTransition.DIGIT:
			terms.append(int(equation[sliceStart:sliceEnd]))

		NUMBER_STATE_STACK = [NumberStateTransition.NONE]
	
	elif top(CONTEXT_STATE_STACK)[0] == StateTransitions.OPERATORS:

		terms.append(equation[sliceStart:sliceEnd])
	
	elif top(CONTEXT_STATE_STACK)[0] == StateTransitions.VARIABLES:
		terms.append(equation[sliceStart:sliceEnd])
		EXPOSANT_STATE_STACK = [VariableStateTransition.NONE]

	pushGlobalState(StateTransitions.NONE, index)


def skip(index, token):
	if top(CONTEXT_STATE_STACK)[0] == StateTransitions.SKIP:
		CONTEXT_STATE_STACK.pop()
		pushGlobalState(StateTransitions.SLICE, index)
	else:
		pass


def execGlobalState(state, index, token):
	execFunctions = {}
	execFunctions[StateTransitions.NONE] = findContextAtNone
	execFunctions[StateTransitions.ERROR] = error
	execFunctions[StateTransitions.NUMBER] = findContextAtNumber
	execFunctions[StateTransitions.NUMBERNEG] = findContextAtNumberNeg
	execFunctions[StateTransitions.OPERATORS] = findContextAtOperators
	execFunctions[StateTransitions.SIGN] = findContextAtSign
	execFunctions[StateTransitions.SKIP] = skip
	execFunctions[StateTransitions.VARIABLES] = findContextAtVariable

	execFunctions[state[0]](index, token)


def recursiveDescent(index, token):
	if top(CONTEXT_STATE_STACK)[0] == StateTransitions.NONE:
		execGlobalState(top(CONTEXT_STATE_STACK), index, token)
		recursiveDescent(index, token)
	else:
		execGlobalState(top(CONTEXT_STATE_STACK), index, token)
	
	if top(CONTEXT_STATE_STACK)[0] == StateTransitions.SLICE:
		sliceString(index, equation)
	
	if top(CONTEXT_STATE_STACK)[0] == StateTransitions.NONE:
		recursiveDescent(index, token)


def parseCommandLine():
	for index, token in enumerate(equation):
		recursiveDescent(index, token)

	recursiveDescent(len(equation), equation[len(equation) - 1])

	if top(CONTEXT_STATE_STACK)[0] not in [StateTransitions.VARIABLES, StateTransitions.NUMBER, StateTransitions.NUMBERNEG]:
		printAndExit(f"Cannot end on: {equation[-1]}")

	pushGlobalState(StateTransitions.SLICE, len(equation))

	sliceString(len(equation), equation)


def extractPower(elem):
	power = 1

	if '^' not in elem:
		power = 1
	else:
		power = int(elem.split('^')[1])
	
	return power

def processSide(side:list, opStack):
	for index, (term, state) in enumerate(zip(side, opStack)):
		if state[0] == StateTransitions.VARIABLES:
			power = extractPower(term)
			if '-' in term:
				toInsert = createVariable(-1, power)
			else:
				toInsert = createVariable(1, power)

			side.pop(index)
			side.insert(index, toInsert)
	
	resultStack = []
	operatorStack = []

	#multiply what you can
	for term, state in zip(side, opStack):
		if state[0] == StateTransitions.OPERATORS:
			if len(operatorStack) > 0:
				if operatorStack[-1] == '*' and term in ['+', '-']:
					a = resultStack.pop()
					b = resultStack.pop()
					resultStack.append(a * b)
					operatorStack.pop()
			operatorStack.append(term)
			
		else:
			resultStack.append(term)

	#change every -
	operatorStack.insert(0, None)
	replaceOper = []
	replaceRes = []

	for i in range(0, len(operatorStack)):
		if operatorStack[i] == None:
			replaceRes.append(resultStack[i])
			continue
		
		if operatorStack[i] == '-':
			replaceOper.append('+')
			replaceRes.append(resultStack[i] * - 1)

		else:
			replaceOper.append(operatorStack[i])
			replaceRes.append(resultStack[i])
	
	#recreate equation
	res = [None] * (len(replaceOper) + len(replaceRes))
	res[::2] = replaceRes
	res[1::2] = replaceOper
	operatorStack = replaceOper
	resultStack = replaceRes

	#muliply the last ones
	while res.count('*') != 0:
		mul = res.index('*')

		termA = res[mul - 1]
		termB = res[mul + 1]

		res.pop(mul - 1)
		res.insert(mul, termA * termB)
		res.pop(mul + 1)
		res.pop(mul - 1)

	total = {}

	#store the variable and coef
	for data in res:
		if data != '+' and isinstance(data, Variable) == False:
			if 0 in total:
				total[0].append(data)
			else:
				total[0] = [data]
		if isinstance(data, Variable):
			key = data.power
			if key in total:
				total[key].append(data)
			else:
				total[key] = [data]
	
	#sum everything
	for key in total.keys():
		total[key] = functools.reduce(operator.add, total[key])
	
	toRemove = []
	for key in total.keys():
		if key > 0:
			if total[key].coef == 0:
				toRemove.append(key)
		if key == 0:
			if total[key] == 0:
				toRemove.append(key)

	#remove the 0
	for key in toRemove:
		total.pop(key)
	
	return total
		


def mergeSides(rside, lside):
	for key in lside.keys():
		lside[key] *= -1

	removeKeyFormLside = []
	for key in rside.keys():
		if key in lside:
			rside[key] = [rside[key], lside[key]]
			removeKeyFormLside.append(key)

	for key in removeKeyFormLside:
		lside.pop(key)
	
	for key in lside.keys():
		rside[key] = [lside[key]]
	

def reduce(side):
	for key in side.keys():
		if isinstance(side[key], list):
			side[key] = functools.reduce(operator.add, side[key])

	toRemove = []
	for key in side.keys():
		if key > 0:
			if side[key].coef == 0:
				toRemove.append(key)
		if key == 0:
			if side[key] == 0:
				toRemove.append(key)

	#remove the 0
	for key in toRemove:
		side.pop(key)

try:
	equation = sys.argv[1:]

	if '=' not in equation[0]:
		printAndExit("Invalid equation, you need to separate both side with a '='")

	split = equation[0].split("=")
	leftSide, rightSide = equation[0].split("=")

	#Separate sides and replace expression like 2X with 2 * X
	rside, lside = preHandleSides(leftSide.replace(" ", ""), rightSide.replace(" ", ""))

	#parse Right Side
	equation = rside
	parseCommandLine()
	rsideStack = CONTEXT_STATE_STACK[:]
	termsRSide = terms[:]

	#parse Left Side
	CONTEXT_STATE_STACK = [(StateTransitions.NONE, -1)]
	equation = lside
	terms = []
	parseCommandLine()
	lsideStack = CONTEXT_STATE_STACK[:]
	termsLSide = terms[:]

	#partially reduce both sides
	reducedEquationRside = processSide(termsRSide, rsideStack)
	reducedEquationLside = processSide(termsLSide, lsideStack)

	#create check if merge didnt change anything
	cpy = reducedEquationRside.copy()

	#print after the partial simplification
	printSides(reducedEquationRside, reducedEquationLside)

	#pretty self explanatory
	mergeSides(reducedEquationRside, reducedEquationLside)

	#print after merging
	printIntermediateStep(reducedEquationRside, cpy == reducedEquationRside)

	#final reduce
	reduce(reducedEquationRside)

	printReducedForm(reducedEquationRside, cpy == reducedEquationRside)

	polynomialDegree = getPolynomialDegree(reducedEquationRside)

	print(f"Polynomial Degree: {polynomialDegree}")

	if polynomialDegree > 2:
		print("The polynomial degree is greater than 2, I can't solve")
	else:
		solver[polynomialDegree](reducedEquationRside)

except:
	print("Error")