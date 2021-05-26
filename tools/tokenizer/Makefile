# Copyright IBM Corporation 2020, 2021
# Written by Geert Janssen <geert@us.ibm.com>

INCLUDES =
CPPFLAGS = $(INCLUDES)
CFLAGS   = -O2
LDFLAGS  =

PROGS = tokenize antlr4tojson pytokenize jstokenize

.PHONY: all
all: $(PROGS)

tokenize: tokenize.o
tokenize.o: tokenize.c

antlr4tojson: antlr4tojson.o
antlr4tojson.o: antlr4tojson.c

pytokenize: pytokenize.o token_common.o
pytokenize.o: pytokenize.c token_common.h

jstokenize: jstokenize.o token_common.o
jstokenize.o: jstokenize.c token_common.h

token_common.o: token_common.c token_common.h

.PHONY: clean
clean:
	@-rm -f *.o
	@-rm -f $(PROGS)
