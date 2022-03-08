# Copyright IBM Corporation 2020, 2021
# Written by Geert Janssen <geert@us.ibm.com>

INCLUDES =
CPPFLAGS = $(INCLUDES)
CFLAGS   = -g -O2 -fPIC
LDFLAGS  =

PROGS = tokenize antlr4tojson pytokenize jstokenize tokml libtoken.so

.PHONY: all
all: $(PROGS)

tokenize: tokenize.o libtoken.a
tokenize.o: tokenize.c libtoken.h

tokml: tokml.o libtoken.a
tokml.o: tokml.c libtoken.h

libtoken.o: libtoken.c libtoken.h

.PHONY: lib
lib: libtoken.a libtoken.so

libtoken.a: libtoken.o
	ar r $@ $^
	ranlib $@

libtoken.so: libtoken.o
	$(CC) -shared -Wl,-soname,$@.1 -o $@ $^

antlr4tojson: antlr4tojson.o
antlr4tojson.o: antlr4tojson.c

pytokenize: pytokenize.o token_common.o
pytokenize.o: pytokenize.c token_common.h

jstokenize: jstokenize.o token_common.o
jstokenize.o: jstokenize.c token_common.h

token_common.o: token_common.c token_common.h

.PHONY: clean
clean:
	@-rm -f *.o *.a
	@-rm -f $(PROGS)
