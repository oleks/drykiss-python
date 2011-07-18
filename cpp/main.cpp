#include <iostream>

#include "Lexer.h"

using namespace std;

const string kExtension = ".dry";
const string kDefaultFileName = "me";
const uint32_t kIndexOfFileNameArgument = 1;

inline string resolveFilename(uint32_t argumentCount, char* arguments[]);

int main(int argumentCount, char* arguments[])
{
	string filename = resolveFilename((uint32_t)argumentCount, arguments);
	Lexer lexer(filename);
	cout << lexer.lex() << endl;
	return 0;
}

inline string resolveFilename(uint32_t argumentCount, char* arguments[])
{
	if (argumentCount <= kIndexOfFileNameArgument)
		return string(kDefaultFileName) + kExtension;

	string filename = arguments[kIndexOfFileNameArgument];
	if (
		filename.length() < kExtension.length() ||
		filename.find(kExtension) != filename.length() - kExtension.length()
	)
		filename += kExtension;

	return filename;
}

