# Copyright IBM Corporation 2020, 2021
# Written by Geert Janssen <geert@us.ibm.com>

INCLUDES =
CPPFLAGS = $(INCLUDES)
CFLAGS   = -O2 -g
LDFLAGS  =

.PHONY: all
all: jgf2dot jgf2spt jsonml2jgf

jgf2dot: jgf2dot.o jgflib.o
jgf2dot.o: jgf2dot.c jgflib.h jsmn.h
jgf2spt: jgf2spt.o jgflib.o
jgf2spt.o: jgf2spt.c jgflib.h jsmn.h
jsonml2jgf: jsonml2jgf.o jgflib.o
jsonml2jgf.o: jsonml2jgf.c jgflib.h jsmn.h
jgflib.o: jgflib.c jgflib.h jsmn.h

# Convert dot to png:
%.png: %.dot
	dot -Tpng -o $@ $<

# Convert dot to pdf:
%.pdf: %.dot
	dot -Tpdf -o $@ $<

# Convert IBM AI4Code JSON-Graph to GraphViz dot:
%.dot: %.json
	./jgf2dot $< > $@
%.dot: %.jgf
	./jgf2dot $< > $@

# Convert IBM AI4Code JSON-Graph to Aroma SPT:
%.spt: %.json
	./jgf2spt $< > $@
%.spt: %.jgf
	./jgf2spt $< > $@

%.jgf: %.jsonml
	./jsonml2jgf $< > $@

.PHONY: clean
clean:
	-rm -f *.o jgf2dot jgf2spt jsonml2jgf
