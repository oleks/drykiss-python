import os, re, sys

from collections import deque

import lexer, parser
from lexer import Lexer
from parser import Parser

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
	lexer = Lexer(filename)
	parser = Parser(lexer.tokens)

	#Compiler(syntree)

def main():
	if len(sys.argv) != 2:
		raise Exception("You must (only) supply a file to kiss.")
	kiss(sys.argv[1])
	
if __name__ == "__main__":
	main()
