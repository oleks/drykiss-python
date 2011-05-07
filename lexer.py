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
	def __init__(self, match):
		super(Newline, self).__init__(match)
		self.count = 1

	def __str__(self):
		return "%s (%i)" % (super(Newline, self).__str__(), self.count)

class Tab(Token):
	pass

class Include(Token):
	def __init__(self, match):
		super(Include, self).__init__(match)
		self.libraries = []

	def append(self, element):
		self.libraries.append(element)

	def __str__(self):
		return super(Include, self).__str__() + str(self.libraries)

class Function(Token):
	def __init__(self, match):
		super(Function, self).__init__(match)
		self.nameList = []
		self.parameterList = []

	def __str__(self):
		base = super(Function, self).__str__()
		if len(self.nameList) == 0 and len(self.parameterList) == 0:
			return base

		parameters = []
		for parameter in self.parameterList:
			parameters.append(str(parameter))
		
		return "%s %s [%s]" % (base, str(self.nameList), ", ".join(parameters))

class Nil(Token):
	pass

class Boolean(Token):
	def __init__(self, match):
		super(Boolean, self).__init__(match)
		self.value = match.group(0) == 'true'

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

class Colon(Token):
	pass

class Semicolon(Token):
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
		self.type = None

	def __str__(self):
		return "%s : %s : %s" % (self.name, self.raw, self.type)

class Tokens:
	SPLITTER = rc(r" +")

	ALL = [\
		(Newline,  rc(r"\r?\n")),\
		(Tab,      rc(r"\t")),\
		(Include,  rc(r"include")),\
		(Function, rc(r"fun")),\
		(Nil,      rc(r"nil")),\
		(Boolean,  rc(r"true|false")),\
		(Varname,  rc(r"[a-zA-Z]+")),\
		(LeftBracket,  rc(r"{")),\
		(RightBracket, rc(r"}")),\
		(LeftBrace,    rc(r"\(")),\
		(RightBrace,   rc(r"\)")),\
		(Dot,     rc(r"\.")),\
		(Colon,   rc(r":")),\
		(Semicolon, rc(r";")),\
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
				if len(self.tokens) > 0 and \
					self.tokens[-1].__class__ == Newline and	\
					token.__class__ == Newline:
					self.tokens[-1].count += 1
				else:
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

def main():
	if len(sys.argv) != 2:
		raise "You must always provide a filename to lex!"
	lexer = Lexer(sys.argv[1])
	for token in lexer.tokens:
		print token

if __name__ == "__main__":
	main()
