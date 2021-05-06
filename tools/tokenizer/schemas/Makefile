# Copyright IBM Corporation 2020
# Written by Geert Janssen <geert@us.ibm.com>

# Requires jing & trang: https://github.com/relaxng/jing-trang

# XML validate
#jing -c schema.rnc $<

# JSON validate
#yajsv -s schema.json $<

# Generate .rng from .rnc:
%.rng: %.rnc
	@trang $< $@

# Generate .xsd from .rnc:
%.xsd: %.rnc
	@trang $< $@

.PHONY: clean

clean:
	@-rm -f *.xsd
	@-rm -f *.rng
