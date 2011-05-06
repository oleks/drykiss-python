import os, re, sys

from collections import deque

rc = re.compile

class SyntaxObject(object):
	def __eq__(self, other):
		if not other.__class__.__name__ == 'str':
			return False
		return self.__class__.__name__ == other

	def __ne__(self, other):
		return not self.__eq__(other)

class Token(SyntaxObject):
	def __init__(self, match=None):
		self.name = self.__class__.__name__
		if match:
			self.raw = match.group(0)

	def __str__(self):
		return self.name

class Newline(Token):
	pass

class Tab(Token):
	pass

class Include(Token):
	def __init__(self, match):
		super(Include, self).__init__(match)
		self.libraries = []

	def append(self, element):
		self.libraries.append(element)

class Class(Token):
	pass

class LeftBracket(Token):
	pass

class RightBracket(Token):
	pass

class LeftBrace(Token):
	pass

class RightBrace(Token):
	pass

class Assign(Token):
	pass

class Dot(Token):
	pass

class Comma(Token):
	pass

class MapsTo(Token):
	def __init__(self, match):
		super(MapsTo, self).__init__(match)
		self.parameters = []
		self.expressions = []


class Call(SyntaxObject):
	def __init__(self, path, args):
		self.path = path
		self.args = args

	def __str__(self):
		return ".".join(self.path)

class Varname(Token):
	def __init__(self, match):
		super(Varname, self).__init__(match)

	def __str__(self):
		return self.name + " : " + self.raw

class Tokens:
	SPLITTER = rc(r" +")

	ALL = [\
		(Newline, rc(r"\r?\n")),\
		(Tab,     rc(r"\t")),\
		(Include, rc(r"include")),\
		(Varname, rc(r"[a-zA-Z]+")),\
		(Class,   rc(r"class")),\
		(LeftBracket,  rc(r"{")),\
		(RightBracket, rc(r"}")),\
		(LeftBrace,    rc(r"\(")),\
		(RightBrace,   rc(r"\)")),\
		(Dot,     rc(r"\.")),\
		(Comma,   rc(r",")),\
		(MapsTo,  rc("=>")),\
		(Assign,  rc(r"="))]

class Lexer:
	def __init__(self, filename):
		self.tokens = deque()
		for line in open(filename):
			self.lex(line)

	def lex(self, line):
		words = Tokens.SPLITTER.split(line)
		for word in words:
			for token in self.tokenize(word):
				self.tokens.append(token)

	def tokenize(self, word):
		while len(word) > 0:
			(token, word) = self.match(word)
			yield token
	
	def match(self, word):
		for fun, regex in Tokens.ALL:
			match = regex.match(word)
			if match:
				return (fun(match), word[match.end():])
		raise Exception("Unmatched token %s!" % word)

class Grammar:
	def __init__(self):
		self.ALL = [\
			# TODO: remove this top one..
			self.newline,\
			self.include,\
			self.assign,\
			self.expression]

	def newline(self, tokens):
		while len(tokens) > 0 and tokens[0] == "Newline":
			tokens.popleft()

	def include(self, tokens):
		if tokens[0] != "Include":
			return
		include = tokens[0]
		tokens.popleft()
		while True:
			if tokens[0] == "Varname":
				include.append(tokens[0].raw)
			tokens.popleft()
			if tokens[0] == "Comma":
				tokens.popleft()
			elif tokens[0] == "Newline":
				tokens.popleft()
				return include
			else:
				raise Exception("Malformed import!")

	def expression(self, tokens):
		expressions = [\
			self.function,\
			self.call,\
			self.variable]

		for fun in expressions:
			result = fun(tokens)
			if result: 
				return result

	def expressions(self, tokens):
		result = []
		while True:
			expression = self.expression(tokens)
			if expression:
				result.append(expression)
			else:
				return result

	def function(self, tokens):
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

	def variable(self, tokens):
		if tokens[0] != "Varname":
			return
		variable = tokens[0]
		tokens.popleft()
		return variable

	def assign(self, tokens):
		if len(tokens) < 3 or \
			tokens[0] != "Varname" or \
			tokens[1] != "Assign":
			return
		assign = tokens[1]
		assign.variable = tokens[0].raw
		tokens.popleft()
		tokens.popleft()
		assign.value = self.expression(tokens)

		if tokens[0] == "Newline":
			tokens.popleft()

		return assign

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.syntree = deque()
		while len(self.tokens) > 0:
			self.advance()
			
	def advance(self):
		for match in Grammar().ALL:
			if len(self.tokens) == 0:
				return
			syntree = match(self.tokens)
			if syntree:
				self.syntree.append(syntree)
				return
		raise Exception("Wild token %s!" % self.tokens[0])

class Compiler:
	def __init__(self, syntree):
		self.compilers = [\
			self.include,\
			self.assign,\
			self.function,\
			self.expressions]

		w = open("output.js", "w")
		w.write(self.compile(syntree))

	def compile(self, syntree):
		result = []
		prev = -1
		while len(syntree) > 0 and prev != len(syntree):
			prev = len(syntree)
			for compiler in self.compilers:
				part = compiler(syntree)
				if part:
					result.append(part)
					syntree.popleft()
		return "".join(result)

	def include(self, syntree):
		if syntree[0] != "Include":
			return
		
		libraries = []
		for library in syntree[0].libraries:
			libraries.append("%s=require('%s')" % (library, library))
		return "".join(["var ", ",".join(libraries), ";"])

	def assign(self, syntree):
		if syntree[0] != "Assign":
			return

		return "var %s=%s;" % (syntree[0].variable, self.expression(syntree[0].value))

	def expressions(self, syntree):
		exps = []
		for node in syntree:
			pass		

	def expression(self, node):
		expressions = [\
			self.function,\
			self.call,\
			self.variable]
		for fun in expressions:
			if fun == self.variable:
				print "VARIABLE? ", syntree
			result = fun(syntree)
			if result:
				return result

	def call(self, node):
		if node != "Call":
			return
		args = []
		for arg in node.args:
			args.append(self.expression(arg))
		return "".join([".".join(node.path), "(", ",".join(args), ")"])

	def variable(self, node):
		if node != "Varname":
			return

		return node.raw

	def function(self, node):
		if node != "MapsTo":
			return
		
		print len(node.expressions)

		return "function(%s){%s}" % (",".join(node.parameters), self.compile(node.expressions))

def kiss(filename):
	tokens = Lexer(filename).tokens
	#for token in tokens:
	#	print token
	#syntree = Parser(tokens).syntree
	
	#for expression in syntree[1]:
	#	print expression

	#Compiler(syntree)

def main():
	if len(sys.argv) != 2:
		raise Exception("You must (only) supply a file to kiss.")
	kiss(sys.argv[1])
	
if __name__ == "__main__":
	main()
