#ifndef DRYKISS_TOKEN_H_
#define DRYKISS_TOKEN_H_

#include "Types.h"

enum TokenType
{
	VARNAME,
	NUMBER,
	PLUS,
	MINUS,
	TIMES,
	DIVIDE,
	EQUALS
};

class Token
{
public:
	TokenType type;
	Token();
	Token(const TokenType&);
};

Token ParseToken(BufferType*);

#endif
