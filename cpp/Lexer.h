#ifndef DRYKISS_LEXER_H_
#define DRYKISS_LEXER_H_

#include <iostream>
#include <fstream>
#include <vector>

#include "Token.h"

using std::string; using std::vector;

typedef vector<Token> TokenVector;

class Lexer
{
	string filename;
public:
	vector<TokenVector> tokens;
	Lexer	(const string& filename);
	int lex	();
};

#endif
