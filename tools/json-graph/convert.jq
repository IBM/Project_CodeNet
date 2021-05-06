# Copyright IBM Corporation 2020
# Written by Geert Janssen <geert@us.ibm.com>

# JQ Script to convert adjacency to node list graph format.
# Run as: jq -f convert.jq input.json > output.json.
# Modify the "graph" object by adding an "edges" list created from the "edges"
# adjacency list in each node under "nodes". See the schema.
# Assumes .nodes.edges is an array of node ids or objects.

.graph = del(.graph.nodes[].edges).graph + {edges:
# the new "edges" property is an array:
[
# all the node objects:
.graph.nodes[]|
# pass on the node objects that have edges with non-empty array:
select(.edges and (.edges|length))|
# remember the id of the node:
.id as $id|
# get the non-empty edges array from the node object:
.edges|
# combine remembered node id and each edge node id.
# check whether value is array of node ids or array of objects;
# for array of objects, select value of "on" (also a node id):
# (copy over rest of edge data .on exclusive)
map({between:[$id,.on?//.]}+(if type=="object" then del(.on) else null end))
# close the array:
]|
# make sure all arrays are merged into 1:
add
# now close the result object:
}
