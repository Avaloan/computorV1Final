import re
import math

lookBehindOutOfBounds = "BOB"
lookAheadOutOfBounds = "AOB"

def printAndExit(reason):
	print(reason)
	exit()


def lookBehind(index, string):
	index = index - 1

	if index < 0:
		return lookBehindOutOfBounds
	
	return string[index]


def lookAhead(index, string):
	index = index + 1

	if index >= len(string):
		return lookAheadOutOfBounds
	
	return string[index]


def top(stack):
	if len(stack) == 0:
		printAndExit("Stack should not be empty at this point")
	
	top = stack.pop()
	stack.append(top)
	
	return top


def preHandleSides(rside, lside):
	if isMatch := re.search(r"X\^\d+X", rside):
		printAndExit(f"A variable cannot use another variable as exponent {isMatch.group(0)}")
	
	if isMatch := re.search(r"X\^\d+X", lside):
		printAndExit(f"A variable cannot use another variable as exponent {isMatch.group(0)}")
	
	if isMatch := re.search(r"X\^X", rside):
		printAndExit(f"A variable cannot use another variable as exponent {isMatch.group(0)}")
	
	if isMatch := re.search(r"X\^X", lside):
		printAndExit(f"A variable cannot use another variable as exponent {isMatch.group(0)}")
	
	rside = re.sub(r"x", "X", rside)
	lside = re.sub(r"x", "X", lside)

	def repl(match):
		split = match.group(0).split('X')
		return f"{split[0]}*X"

	return (re.sub(r"\d+X", repl, rside), re.sub(r"\d+X", repl, lside))


def printSides(side, side2):
	toPrint = ""
	for key in side.keys():
		toPrint += str(side[key])
		toPrint += " "
		toPrint += "+"
		toPrint += " "
	
	if toPrint != "":
		toPrint = toPrint[:-2]
	else:
		toPrint += '0 '
	
	toPrint += "= "
	
	toPrint2 = ""
	for key in side2.keys():
		toPrint2 += str(side2[key])
		toPrint2 += " "
		toPrint2 += "+"
		toPrint2 += " "
	
	if toPrint2 == "":
		toPrint2 += '0'
		print(f"Form after simplification: {toPrint + toPrint2}")
	else:
		print(f"Form after simplification: {toPrint + toPrint2[:-2]}")


def printIntermediateStep(side, same):
	toPrint = ""

	if side == {} or same:
		print("Form after simplification is already reduced, there is no more intermediate step")
		return

	for key in side.keys():
		if isinstance(side[key], list):
			for item in side[key]:
				toPrint += str(item)
				toPrint += " + "
		else:
			toPrint += str(side[key])
			toPrint += " + "

	if toPrint:
		toPrint = toPrint[:-2]
	
	toPrint += "= 0"
	print(f"Intermediate form: {toPrint}")


def printReducedForm(side, same):
	toPrint = ""

	if side == {} or same:
		print("Form after simplification was already reduced")
		return

	for key in side.keys():
		if isinstance(side[key], list):
			for item in side[key]:
				toPrint += str(item)
				toPrint += " + "
		else:
			toPrint += str(side[key])
			toPrint += " + "

	if toPrint:
		toPrint = toPrint[:-2]
	
	toPrint += "= 0"
	print(f"Reduced form: {toPrint}")


def getPolynomialDegree(side):
	if side:
		return max(side.keys())

	return 0


def sqrt(n):
	lo = min(1, n)
	hi = max(1, n)

	for _ in range(0, 100):
		mid = (lo+hi)/2
		
		if (mid * mid) == n:
			return mid
		
		if (mid * mid) > n:
			hi = mid
		
		else:
			lo = mid
	
	return mid


def solveDegreeZero(equation):
	if equation == {}:
		print("All real numbers are solutions")
	else:
		print("Invalid equation")


def solveDegreeOne(equation):
	if 0 in equation:
		consts = equation[0] * -1
	else:
		consts = 0

	var = equation[1]

	solution = ""

	if consts / var.coef != consts // var.coef:
		if consts < 0 and var.coef < 0:
			solution = f"{consts * -1}/{var.coef * -1}"
		elif consts < 0:
			solution = f"-({consts * -1}/{var.coef})"
		elif var.coef < 0:
			solution = f"-({consts}/{var.coef * -1})"
		else:
			solution = f"{consts}/{var.coef}"
	else:
		solution = round(consts / var.coef, 6)
	
	print("The solution is:", solution)


def solveDegreeTwo(equation):
	if 0 in equation:
		c = equation[0]
	else:
		c = 0
	
	if 1 in equation:
		b = equation[1].coef
	else:
		b = 0
	
	a = equation[2].coef

	delta = (b * b) - 4 * (a * c)

	if delta == 0:
		solution = -b / (2 * a)

		print("Le discriminant est egal a 0, le polynome admet une seule solution:", round(solution, 6))
	
	elif delta > 0:
		solution1 = (-b - sqrt(delta)) / (2 * a)
		solution2 = (-b + sqrt(delta)) / (2 * a)

		print(f"Le discriminant est superieur a 0, le polynome admets 2 solutions:")
		print(round(solution1, 6))
		print(round(solution2, 6))
	
	else:
		print(f"Le discriminant est negatif, le polynome admets 2 solutions complexes:")
		print(f"{round((-b)/(2 * a), 6)} + i * {round(sqrt(-delta)/ (2 * a), 6)}")
		print(f"{round((-b)/(2 * a), 6)} - i * {round(sqrt(-delta)/ (2 * a), 6)}")
		

solver = {
	0:solveDegreeZero,
	1:solveDegreeOne,
	2:solveDegreeTwo
}
