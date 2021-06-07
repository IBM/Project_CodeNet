# Copyright IBM Corporation 2021
# Written by Geert Janssen <geert@us.ibm.com>

INCLUDES =
CPPFLAGS = $(INCLUDES)
CXXFLAGS =-std=c++11 -O2 -g
LDFLAGS  =
# default linker is CC, need CXX
LINK.o = $(LINK.cc)

PROGS=duplicates

.PHONY: all
all: $(PROGS)

duplicates: duplicates.o
	$(CXX) -o $@ $^

.PHONY: test
test: duplicates
	./duplicates -h
	bash -c 'time ./duplicates test_tokens.tsv'

.PHONY: clean
clean:
	@-rm -f *.o
	@-rm -f $(PROGS)

duplicates.o: duplicates.cpp
