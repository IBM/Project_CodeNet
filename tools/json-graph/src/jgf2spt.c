/* Copyright (c) 2021 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Convert JSON-Graph to Aroma Simplified Parse Tree (SPT) JSON format.

   The JSON-Graph must comply with the restricted SPT schema `spt-schema.json`.
   The graph will in fact be a tree with integer ids in breadth-first order,
   i.e., the root has id 0, its children from left-to-right are 1, 2, 3, etc.
   This is also the order of the nodes in the nodes list. Leaf nodes represent
   tokens and are separately numbered via a "token_id" key. The token_id
   value corresponds with the "seqnr" in the token CSV file.

   Using a third-party JSON parser (JSMN) that produces an array of tokens
   from an input character array. (https://github.com/zserge/jsmn)
   The expected JSON-Graph schema is hard-coded into the program logic.
   First constructs a nodelist and edgelist graph from the input which
   is subsequently converted to an adjacency structure and then traversed
   in depth-first order from the root node to produce the output.

   All checks immediately cause a program exit upon error.
*/

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define JSMN_HEADER
#include "jgflib.h"

static int pprint = 0;		 // to pretty-print or not

static int node_info(Node u)
{
  fprintf(stderr, "node: ");
  show(stderr, u->id, 0);
  fprintf(stderr, " children: %u ", outdegree(u));
  jsmntok_t *val = node_attr_value(u, "token_id");
  if (val) {
    fprintf(stderr, " token_id: ");
    show(stderr, val, 0);
  }
  jsmntok_t *type = node_attr_value(u, "node-type");
  if (type && string_eq(type, "Token")) {
    fprintf(stderr, " token: ");
    show(stderr, u->label, 1);
  }
  else {
    fprintf(stderr, " nonterm: ");
    show(stderr, u->label, 1);
  }
  fputc('\n', stderr);
  return 1;
}

static int edge_info(Edge e)
{
  fprintf(stderr, "edge ");
  if (e->label)
    show(stderr, e->label, 0);
  fputc('[', stderr);
  show(stderr, e->from->id, 0);
  fputc(',', stderr);
  show(stderr, e->to->id, 0);
  fputs("]\n", stderr);
  return 1;
}

/** Return true for a tree, false for anything else.
*/
static int check_tree(Node u)
{
  Edge e;
  u->visited = 1;
  for (e = u->outgoing; e; e = e->next_adj_out)
    if (e->to->visited || !check_tree(e->to))
      return 0;
  return 1;
}

static void show_spt_aux(Node u, unsigned indent, FILE *fp)
{
  unsigned degree = outdegree(u);

  if (debug) node_info(u);

  assert(degree != 1);
  if (degree == 0) {
    jsmntok_t *type = node_attr_value(u, "node-type");
    assert(type && string_eq(type, "Token"));

    fprintf(fp, "%*s{", indent, "");
    if (pprint) {
      fputc('\n', fp);
      indent += 2;
    }
    /* Fake line, leading, trailing: */
    fprintf(fp, "%*s\"line\":", indent, "");
    jsmntok_t *line = node_attr_value(u, "line");
    if (line)
      show(fp, line, 0);
    else
      fputs("2", fp);
    fputc(',', fp);
    if (pprint) fputc('\n', fp);
    fprintf(fp, "%*s\"leading\":\" \",", indent, "");
    if (pprint) fputc('\n', fp);
    fprintf(fp, "%*s\"trailing\":\" \",", indent, "");
    if (pprint) fputc('\n', fp);
    fprintf(fp, "%*s\"token\":", indent, "");
    show(fp, u->label, 1);
    /* if identifier signal as leaf: */
    type = node_attr_value(u, "type-rule-name");
    if (type && string_eq(type, "Identifier")) {
      fputc(',', fp);
      if (pprint) fputc('\n', fp);
      fprintf(fp, "%*s\"leaf\":true", indent, "");
      /* if identifier used as variable signal as var: */
      if (0) {
	fputc(',', fp);
	if (pprint) fputc('\n', fp);
	fprintf(fp, "%*s\"var\":true", indent, "");
      }
    }
    if (pprint) {
      fputc('\n', fp);
      indent -= 2;
    }
    fprintf(fp, "%*s}", indent, "");
  }
  else {
    fprintf(fp, "%*s[", indent, "");
    if (pprint) {
      fputc('\n', fp);
      indent += 2;
    }
    fprintf(fp, "%*s", indent, "");
    show(fp, u->label, 1);
    fputc(',', fp);
    if (pprint) fputc('\n', fp);

    Edge e;
    for (e = u->outgoing; e; e = e->next_adj_out) {
      show_spt_aux(e->to, indent, fp);
      if (e->next_adj_out)
	fputc(',', fp);
      if (pprint) fputc('\n', fp);
    }

    if (pprint) indent -= 2;
    fprintf(fp, "%*s]", indent, "");
  }
}

/** Output tree in Aroma SPT JSON format. See aroma-schema.json.
*/
static void show_spt(Graph g, FILE *fp)
{
  unsigned indent = 0;
  Node root = g->root ? node_find(g, g->root) : NULL;
  if (!root || !check_tree(root)) {
    fprintf(stderr, "(F): Graph has no root, or is not a tree.\n");
    exit(7);
  }

  fputc('{', fp);
  if (pprint) {
    fputc('\n', fp);
    indent = 2;
  }
  fprintf(fp, "%*s\"path\":", indent, "");
  if (filename) {
    fputc('"', fp);
    fputs(filename, fp); /* assume no need to escape any char */
    fputc('"', fp);
  }
  else
  if (g->label)
    show(fp, g->label, 1);
  else
    fputs("\"jgf2spt\"", fp);
  fputc(',', fp);
  if (pprint) fputc('\n', fp);
  /* Fake class, method, beginline, endline: */
  fprintf(fp, "%*s\"class\":\"MyClass\",", indent, "");
  if (pprint) fputc('\n', fp);
  fprintf(fp, "%*s\"method\":\"MyMethod\",", indent, "");
  if (pprint) fputc('\n', fp);
  fprintf(fp, "%*s\"beginline\":1,", indent, "");
  if (pprint) fputc('\n', fp);
  fprintf(fp, "%*s\"endline\":10,", indent, "");
  if (pprint) fputc('\n', fp);

  fprintf(fp, "%*s\"ast\":", indent, "");
  show_spt_aux(root, indent, fp);
  if (pprint) fputc('\n', fp);
  fputs("}\n", fp);
}

int main(int argc, char *argv[])
{
  filename = "stdin";

  /* Read from a file argument or stdin: */
  while (argc > 1 && argv[1]) {
    if (!strcmp(argv[1], "-d")) {
      debug = 1;
      /*shift*/
      argc--; argv[1] = argv[2]; argv[2] = argv[3];
    }
    else
    if (!strcmp(argv[1], "-p")) {
      pprint = 1;
      /*shift*/
      argc--; argv[1] = argv[2]; argv[2] = argv[3];
    }
    if (*argv[1] != '-') {
      filename = argv[1];
      if (!freopen (filename, "r", stdin)) {
	fprintf (stderr, "(E): Cannot read file %s.\n", filename);
	exit(4);
      }
      break;
    }
  }

  if (debug) fprintf(stderr, "(D): Processing file %s.\n", filename);

  Graph graph = jgf_parse();

  if (debug)
    fprintf(stderr, "(D): Converting JSON-Graph to Aroma SPT JSON...\n");

  mk_adjacency_graph(graph);
  show_spt(graph, stdout);

  /*graph_free(graph); */
  return 0;
}
