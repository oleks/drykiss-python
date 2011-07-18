#include <iostream>
#include <fstream>
#include <vector>

#include "Types.h"
#include "Token.h"
#include "Lexer.h"

using namespace std;

const size_t kBufferSize = 512;

inline int lexifyBuffer(BufferType* buffer);
inline int nextLexeme(BufferType **buffer, Token &currentToken);

Lexer::Lexer(const string& filename)
{
	this->filename = filename;
}

int Lexer::lex()
{
	cout << "Lexing " << this->filename << ".." << endl;
	FILE *filePtr = fopen(this->filename.c_str(), "r");
	if (filePtr == NULL)
		return 1;

	BufferType buffer[kBufferSize];
	while(fread(buffer, sizeof(*buffer), kBufferSize, filePtr))
	{
		lexifyBuffer(buffer);
	}
	fclose(filePtr);
	return 0;
}

inline int lexifyBuffer(BufferType *buffer)
{
	vector<Token> lexemes;
	Token currentToken;
	cout << buffer << endl;
	return 0;
};

inline int nextLexeme(BufferType **buffer, Token *currentToken)
{
	int currentLetter = (int)**buffer;
	if (currentLetter >= '0' && currentLetter <= '9')
		currentToken->type = NUMBER;
	return 0;
}
