class Variable:
	def __init__(self, coef, power):
		self.coef = coef
		self.power = power
	
	def __mul__(self, other):
		if (isinstance(other, Variable)):
			return Variable(self.coef * other.coef, self.power + other.power)
		return Variable(self.coef * other, self.power)
	
	def __rmul__(self, other):
		if (isinstance(other, Variable)):
			return Variable(self.coef * self.coef, other.power + other.power)
		return Variable(self.coef * other, self.power)
	
	def __add__(self, other):
		if (isinstance(other, Variable)):
			return Variable(self.coef + other.coef, self.power)
	
	def __radd__(self, other):
		if (isinstance(other, Variable)):
			return Variable(self.coef + other.coef, self.power)
	
	def __repr__(self):
		if self.coef == 1:
			return f"X^{self.power}"
		
		if self.coef == -1:
			return f"-X^{self.power}"
		
		# if self.power == 1:
		# 	return f"{self.coef}X"
		
		return f"{self.coef}X^{self.power}"

def createVariable(coef, power):
	if coef == 0:
		return
	
	if power == 0:
		return coef

	return Variable(coef, power)