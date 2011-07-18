#include <iostream>

#include "Token.h"

using namespace std;

Token::Token()
{
}

Token::Token(const TokenType &type)
{
	this->type = type;
}

Token ParseToken(BufferType* buffer)
{
	for(;&buffer != (BufferType)'\0'; buffer++)
		cout << buffer << endl;
}

