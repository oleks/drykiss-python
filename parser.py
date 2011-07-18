import re, sys, tokens
from collections import deque
from lexer import Lexer

class Grammar:
	def __init__(self, tokens):
		self.tokens = tokens
		self.all = [ \
			# TODO: remove these top two..
			self.newline, \
			self.tab, \
			self.include, \
			self.statement \
		]

		self.statements = [ \
			self.boolean, \
			self.number, \
			self.varname, \
			#self.function,\
			#self.call,\
			#self.variable]
		]


		self.operatorstack = deque()

	def parse(self, skipTab = False, level = 0):
		if len(self.tokens) == 0:
			return None
		
		skip = ["Newline"]
		if skipTab:
			skip.append("Tab")

		for fun in self.all:
			result = fun()

			if result in skip:
				if len(self.tokens) == 0:
					return None
				continue
			
			if result != None:
				return result
		
		return None

	def peak(self, index = 0):
		if index >= len(self.tokens):
			return None
		return self.tokens[index]

	def advance(self):
		return self.tokens.popleft()

	def newline(self):
		if self.peak() != "Newline":
			return None
		return self.advance()

	def tab(self):
		if self.peak() != "Tab":
			return None
		return self.advance()

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

	def statement(self):
		statement = None
		for fun in self.statements:
			statement = fun()
			if statement != None:
				break

		return statement
		
	def varname(self):
		
		varname = self.peak()

		if varname != "Varname":
			return

		varname.nameList = [self.advance().raw]
		varname.varList = []

		while True:

			if self.peak() == "LeftBrace":
				self.advance()
				
				varList = self.varList()
				
				if self.peak() != "RightBrace":
					raise Exception("Invalid parameter list end!")
				self.advance()

				if len(varList) == 0:
					return varname
				varname.varList.append(varList)
			
			if self.peak() != "Varname":
				break
			varname.nameList.append(self.advance().raw)

		if self.peak() == "Assign":
			return self.assignment(varname)
		
		# TODO: perhaps varname can spread lines?
		return varname

	def varList(self):

		variables = []

		while True:

			if self.peak() != "Varname":
				return variables

			variable = self.variable()
			if variable == None:
				raise Exception("Bad Variable!")

			variables.append(variable)

			if self.peak() == "Comma":
				self.advance()

	def variable(self):
		
		if self.peak() != "Varname":
			return None

		variable = self.advance()

		if len(self.tokens) > 1 and self.peak() == "Colon" and self.peak(1) == "Varname":
			self.advance()
			variable.type = self.advance().raw

		return variable
	
	def assignment(self, varname):
		assignment = self.advance()
		assignment.varname = varname
	
		next = self.peak()

		if next == "Newline":
			self.advance()
			print "ADVANCE"
			assignment.expression = self.block()
		elif next == "LeftBracket":	
			assignment.expression = self.block(next, startsOnSameLine = True)
		else:
			assignment.expression = self.expression(next)

		return assignment

	def skipNewline(self):
		self.newline()

	def block(self, next = None, startsOnSameLine = False):
		if next == None:
			next = self.peak()
		
		print next

		if startsOnSameLine or next == "LeftBracket":
			return self.bracketBlock()
		elif next == "Tab":
			return self.indentBlock()
		else:
			raise Exception("Invalid block!")

	def bracketBlock(self):
		self.advance()
		statements = []
		while True:
			syntree = self.parse(skipTab = True)
			if syntree != None:
				statements.append(syntree)
				continue

			print self.peak()

			if self.peak() != "RightBracket":
				raise Exception("Bad bracketed block!")
			self.advance()

			return statements

	
	def indentBlock(self, level = 1):
		statements = []
		while True:
			tab = self.peak()
			if tab.__class__ != tokens.Tab or tab.count != level:
				return statements	
			self.advance()
			syntree = self.parse()
			if self.peak() == "Newline":
				self.advance()
			if syntree != None:
				statements.append(syntree)
				continue

			return statements

	def expression(self, previousOperator = None):
		operators = [\
			tokens.BooleanAnd,\
			tokens.BooleanOr,\
			tokens.BinaryAnd,\
			tokens.BinaryOr,\
			tokens.Plus,\
			tokens.Minus,\
			tokens.Times,\
			tokens.Divide,\
		]


		statement = self.statement()

		return statement

		for fun in expressions:
			subexpression = fun()
			if subexpression:
				break
	
		if not subexpression:
			return

		if self.tokens[0].__class__ in operators:
			if len(self.operatorstack) == 0:
				self.operatorstack.append(self.tokens.popleft())
			#else:
				
	

		if not self.tokens[0].__class__ in continuators:
			if previousOperator != None:
				previousOperator.addOperand(subexpression)
			return subexpression

		operator = self.tokens.popleft()
		print operator, previousOperator
		
		if previousOperator == None or operator.precedance < previousOperator.precedance:
			operator.addOperand(subexpression)
		else:
			previousOperator.addOperand(subexpression)
			operator.addOperand(previousOperator)
		
		otherExpression = self.expression(operator)
		if otherExpression == None:
			raise Exception("Invalid expression!")
		return operator


	def boolean(self):
		if self.tokens[0] != "Boolean":
			return
		return self.tokens.popleft()

	def number(self):
		if self.tokens[0] != "Number":
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
		self.grammar = Grammar(self.tokens)
		self.parse()

	def parse(self):
		while True:
			syntree = self.grammar.parse()
			if syntree != None:
				self.syntree.append(syntree)
				continue

			self.dropTrailingWhitespace()
			if len(self.tokens) > 0:
				raise Exception("Wild token %s!" % self.tokens[0])
			return

	def dropTrailingWhitespace(self):
		whitespace = ["Newline", "Tab"]
		while len(self.tokens) > 0 and self.tokens[0] in whitespace:
			self.tokens.popleft()

def main():
	if len(sys.argv) != 2:
		raise "You must always provide a filename to lex!"
	lexer = Lexer(sys.argv[1])
	parser = Parser(lexer.tokens)
	for element in parser.syntree:
		print element
	
if __name__ == "__main__":
	main()
