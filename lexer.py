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
