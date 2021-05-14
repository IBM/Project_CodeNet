# Copyright IBM Corporation 2020
# Written by Geert Janssen <geert@us.ibm.com>


# Convert dot to png:
%.png: %.dot
	dot -Tpng -o $@ $<

# Convert dot to pdf:
%.pdf: %.dot
	dot -Tpdf -o $@ $<

.PHONY: clean
clean:
	-rm -f *.o *.png
