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
tokenize.o: tokenize.c cpp_keywords.h java_keywords.h
antlr4tojson: antlr4tojson.o
antlr4tojson.o: antlr4tojson.c
pytokenize: pytokenize.o token_common.o
pytokenize.o: pytokenize.c token_common.h
jstokenize: jstokenize.o token_common.o
jstokenize.o: jstokenize.c token_common.h

token_common.o: token_common.c token_common.h

cpp_keywords.h: c++20.kw
	gperf -LC -Nis_cpp_keyword -Hcpp_hash -c -C -I -m1 --output-file=$@ $<

java_keywords.h: java.kw
	gperf -LC -Nis_java_keyword -Hjava_hash -c -C -I -m1 --output-file=$@ $<
	# must change some global names:
	sed -i \
	-e 's/TOTAL_KEYWORDS/JAVA_TOTAL_KEYWORDS/g' \
	-e 's/MIN_WORD_LENGTH/JAVA_MIN_WORD_LENGTH/g' \
	-e 's/MAX_WORD_LENGTH/JAVA_MAX_WORD_LENGTH/g' \
	-e 's/MIN_HASH_VALUE/JAVA_MIN_HASH_VALUE/g' \
	-e 's/MAX_HASH_VALUE/JAVA_MAX_HASH_VALUE/g' $@

.PHONY: clean
clean:
	@-rm -f *.o
	@-rm -f $(PROGS)
