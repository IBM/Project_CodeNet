# Copyright IBM Corporation 2020
# Written by Geert Janssen <geert@us.ibm.com>

# Required tools/utilities:
# pip install pandoc
# pip install pandoc-codeblock-include
# dot: yum install graphviz
# yum install jq
# npm install -g jgfdot; alt use own jgf2dot
# yajsv: go get neilpa.me/yajsv, or
# wget https://github.com/neilpa/yajsv/releases/download/v1.3.0/yajsv.linux.amd64

.PHONY: all
all: graph-json.pdf validate

%.pdf: %.md digraph.pdf tree.pdf
	env PATH=$(HOME)/anaconda3/bin:/usr/bin pandoc --filter pandoc-codeblock-include -o $@ $<

%.png: %.dot
	dot -Tpng -o $@ $<

%.pdf: %.dot
	dot -Tpdf -o $@ $<

# Convert JSON-Graph to GraphViz dot:
#%.dot: %.json
#	jq '(.graph.edges[]) |= . + { source: .between[0], target: .between[1] } | del(.graph.edges[].between)' $< | jgfdot > $@

%.dot: %.json
	jgf2dot $< > $@

# Convert adjacency to node list:
%.json: %-adj.json
	jq -f convert.jq $< > $@

.PHONY: validate
validate:
	yajsv -s graph-schema.json minimum.json
	yajsv -s graph-schema.json digraph.json
	yajsv -s graph-schema.json tree.json

.PHONY: clean
clean:
	-rm -f *.pdf
