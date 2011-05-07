import re, sys, tokens
from collections import deque
from lexer import Lexer

class Grammar:
	def __init__(self, tokens):
		self.tokens = tokens
		self.ALL = [\
			# TODO: remove this top one..
			self.newline,\
			self.include,\
			self.function,\
			self.assign,\
			#self.expression]
		]

	def newline(self):
		while len(self.tokens) > 0 and self.tokens[0] == "Newline":
			self.tokens.popleft()

	def include(self):
		
		if self.tokens[0] != "Include":
			return
		
		include = self.tokens.popleft()
		
		while True:
			
			if self.tokens[0] == "Varname":
				include.append(self.tokens.popleft().raw)
			else:
				raise Exception("Invalid include clause!")
			
			if self.tokens[0] == "Comma":
				self.tokens.popleft()
				if self.tokens[0] == "Newline":
					self.tokens.popleft()
			elif self.tokens[0] == "Newline":
				self.tokens.popleft()
				return include
			else:
				raise Exception("Malformed import!")

	def function(self):
		if self.tokens[0] != "Function":
			return

		function = self.tokens.popleft()

		function.nameList, function.parameterList = self.functionName()

		return function

	def functionName(self):
		
		names = []
		parameters = []

		if self.tokens[0] != "Varname":
			raise Exception("Invalid function name!")

		while True:
			
			if self.tokens[0] != "Varname":
				return names, parameters

			names.append(self.tokens.popleft().raw)

			if self.tokens[0] != "LeftBrace":
				return names, parameters
			
			self.tokens.popleft()

			if self.tokens[0] == "RightBrace":
				self.tokens.popleft()
				return names, parameters

			latestParameters = self.variableList()

			if self.tokens[0] != "RightBrace":
				raise Exception("Invalid function name!")

			self.tokens.popleft()

			if len(latestParameters) == 0:
				return names, parameters
			else:
				parameters.extend(latestParameters)
				

	def variableList(self):

		variables = []

		if self.tokens[0] != "Varname":
			return

		while True:

			if self.tokens[0] != "Varname":
				raise Exception("Invalid parameter list speicification!")

			variable = self.variable()
			if variable == None:
				raise Exception("Bad Variable!")

			variables.append(variable)

			if self.tokens[0] != "Comma":
				return variables

			self.tokens.popleft()

	def variable(self):
		
		if self.tokens[0] != "Varname":
			return

		variable = self.tokens.popleft()

		if len(self.tokens) > 1 and self.tokens[0] == "Colon" and self.tokens[1] == "Varname":
			self.tokens.popleft()
			variable.type = self.tokens.popleft().raw

		return variable

	def assign(self):
		variable = self.variable()
		if variable == None:
			return

		if self.tokens[0] != "Assign":
			return

		assign = self.tokens.popleft()
		assign.variable = variable
		assign.expression = self.expression()

		if self.tokens[0] == "Newline":
			self.tokens.popleft()

		return assign

	def expression(self, previousOperator = None):
		expressions = [\
			self.boolean
			#self.function,\
			#self.call,\
			#self.variable]
		]

		continuators = [\
			tokens.BooleanAnd,\
			tokens.BooleanOr,\
			tokens.BinaryAnd,\
			tokens.BinaryOr,\
		]

		subexpression = None

		for fun in expressions:
			subexpression = fun()
			if subexpression:
				break
		
		if not subexpression:
			return

		if not self.tokens[0].__class__ in continuators:
			if previousOperator != None:
				previousOperator.addOperand(subexpression)
			return subexpression

		operator = self.tokens.popleft()
		
		if previousOperator == None or  operator.precedance < previousOperator.precedance:
			operator.addOperand(subexpression)
			otherExpression = self.expression(operator)
			if otherExpression == None:
				raise Exception("Invalid expression!")
		else:
			previousOperator.addOperand(subexpression)
			operator.addOperand(previousOperator)
			
		return operator


	def boolean(self):
		if self.tokens[0] != "Boolean":
			return
		return self.tokens.popleft()


	def expressions(self, tokens):
		result = []
		while True:
			expression = self.expression(tokens)
			if expression:
				result.append(expression)
			else:
				return result

	def function2(self, tokens):
		if tokens[0] != "Varname" or tokens[1] != "MapsTo":
			return

		mapsto = tokens[1]
		mapsto.parameters.append(tokens[0].raw)
		# TODO: allow several parameters
		
		tokens.popleft()
		tokens.popleft()

		mapsto.expressions = self.expressions(tokens)
		return mapsto

	def call(self, tokens):
		path = []
		popped = False
		while tokens[0] == "Varname" and tokens[1] == "Dot":
			path.append(tokens[0].raw)
			tokens.popleft()
			tokens.popleft()
			popped = True
		if not tokens[0] == "Varname" or not tokens[1] == "LeftBrace":
			if popped:
				raise Exception("Malformed funcion call!")
			else:
				return
		path.append(tokens[0].raw)
		tokens.popleft()
		tokens.popleft()
		
		args = []

		while len(tokens) > 0 and tokens[0] != "RightBrace":
			args.append(self.expression(tokens))
			if tokens[0] == "Comma":
				tokens.popleft()

		if tokens[0] == "RightBrace":
			tokens.popleft()
		else:
			raise Exception("Malformed function call!") 

		return Call(path, args)

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.syntree = deque()
		while len(self.tokens) > 0:
			self.advance()
			
	def advance(self):
		for grammar in Grammar(self.tokens).ALL:
			if len(self.tokens) == 0:
				return
			syntree = grammar()
			if syntree:
				return self.syntree.append(syntree)
		raise Exception("Wild token %s!" % self.tokens[0])

def main():
	if len(sys.argv) != 2:
		raise "You must always provide a filename to lex!"
	lexer = Lexer(sys.argv[1])
	parser = Parser(lexer.tokens)
	for element in parser.syntree:
		print element
	
if __name__ == "__main__":
	main()
