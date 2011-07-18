import re, sys, tokens
from collections import deque
from tokens import Tokens

class Lexer:
	def __init__(self, filename):
		self.tokens = deque()
		for line in open(filename):
			self.lex(line)

	def lex(self, line):
		words = Tokens.SPLITTER.split(line)
		for word in words:
			for token in self.tokenize(word):
				if len(self.tokens) > 0 and (\
				self.isNewlineContinuation(token) or \
				self.isTabContinuation(token)):
					self.tokens[-1].count += 1
				else:
					self.tokens.append(token)

	def isNewlineContinuation(self, token):
		return self.tokens[-1].__class__ == tokens.Newline and \
			token.__class__ == tokens.Newline

	def isTabContinuation(self, token):
		return self.tokens[-1].__class__ == tokens.Tab and \
			token.__class__ == tokens.Tab

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
