CC = g++
LDFLAGS = -lm
DEBUG = -g
COMPILE_FLAGS = -Wall -c $(DEBUG)
LINKING_FLAGS = -Wall

all: Token.o Lexer.o main.o
	$(CC) $(LINKING_FLAGS) main.o Lexer.o $(LDFLAGS) -o kiss

main.o: Types.h Token.h Lexer.h main.cpp
	$(CC) $(COMPILE_FLAGS) main.cpp

Lexer.o: Types.h Token.h Lexer.h Lexer.cpp
	$(CC) $(COMPILE_FLAGS) Lexer.cpp

Token.o: Types.h Token.h Token.cpp
	$(CC) $(COMPILE_FLAGS) Token.cpp

clean:
	-rm -f *.o 
