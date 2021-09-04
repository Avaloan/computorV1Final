from enum import Enum

class StateTransitions(Enum):
	NONE = 0
	NUMBER = 1
	NUMBERNEG = 10
	OPERATORS = 2
	VARIABLES = 3
	SLICE = 4
	ERROR = 5
	TRANSITION = 6
	SIGN = 8
	SKIP = 9

class NumberStateTransition(Enum):
	NONE = 0
	DIGIT = 1
	NEGATIVE = 2
	FLOAT = 3
	FLOATUNCOVERED = 4

class VariableStateTransition(Enum):
	NONE = 0
	DIGIT = 1
	NEGATIVE = 2
	FLOAT = 3
	EXP = 4
	EXPUNCOVERED = 5