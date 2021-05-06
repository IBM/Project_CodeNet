/* Copyright (c) 2020, 2021 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Convert JSON-Graph to GraphViz Dot.

   Simple-minded approach: using a third-party JSON parser (JSMN) that
   produces an array of tokens from an input character array.
   (https://github.com/zserge/jsmn)
   The expected schema is hard-coded into the program logic.
   First constructs a graph from the input and afterwards traverses
   the graph to produce the dot formatted output.

   The input is assumed to be valid JSON and moreover must comply with the
   IBM AI4Code JSON-Graph schema. Even in its strict mode, the JSMN parser
   seems to be lenient and/or not follow the JSON standard.
   For instance, the primitives false, true and null are only checked
   for their first character.
   All checks immediately cause a program exit upon error.
*/

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define JSMN_HEADER
#include "jgflib.h"

/* Output graph in GraphViz dot format. */
static void graph_show_list_dot(Graph g, FILE *fp)
{
  fprintf(fp, "%sgraph ", g->directed ? "di" : "");
  if (g->label)
    show(fp, g->label, 1);
  else
    fputs("\"jgf2dot\"", fp);
  fputs(" {\n", fp);
  /* graph atributes: */
  int attrs = g->version || g->root || g->type || g->label || g->attrs;
  if (attrs) {
    int need_comma = 0;
    fputs("  graph [", fp);
    /* Predefined attributes: */
    if (g->version) {
      fputs("version=", fp);
      show(fp, g->version, 1);
      need_comma = 1;
    }
    if (g->root) {
      if (need_comma) fputc(',', fp);
      fputs("root=", fp);
      show(fp, g->root, 1);
      need_comma = 1;
    }
    if (g->type) {
      if (need_comma) fputc(',', fp);
      fputs("type=", fp);
      show(fp, g->type, 1);
      need_comma = 1;
    }
    if (g->label) {
      if (need_comma) fputc(',', fp);
      fputs("label=", fp);
      show(fp, g->label, 1);
      need_comma = 1;
    }
    /* Any other attributes: */
    show_attrs(fp, g->attrs, need_comma);
    fputs("];\n", fp);
  }

  Node n;
  for (n = g->nodes; n; n = n->next) {
    fputs("  ", fp);
    show(fp, n->id, 0);
    int attrs = n->label || n->attrs;
    if (attrs) {
      int need_comma = 0;
      fputs(" [", fp);
      if (n->label) {
        fputs("label=", fp);
        show(fp, n->label, 1);
        need_comma = 1;
      }
      /* Any other attributes: */
      show_attrs(fp, n->attrs, need_comma);
      fputc(']', fp);
    }
    fputs(";\n", fp);
  }

  Edge e;
  for (e = g->edges; e; e = e->next) {
    fputs("  ", fp);
    show(fp, e->between[0], 0);
    fprintf(fp, " -%c ", g->directed ? '>' : '-');
    show(fp, e->between[1], 0);
    /* edge atributes: */
    int attrs = e->label || e->attrs;
    if (attrs) {
      int need_comma = 0;
      fputs(" [", fp);
      if (e->label) {
        fputs("label=", fp);
        show(fp, e->label, 1);
        need_comma = 1;
      }
      /* Any other attributes: */
      show_attrs(fp, e->attrs, need_comma);
      fputc(']', fp);
    }
    fputs(";\n", fp);
  }
  fputs("}\n", fp);
}

int main(int argc, char *argv[])
{
  /* Read from a file argument or stdin: */
  if (argc > 1 && argv[1]) {
    if (!strcmp(argv[1], "-d")) {
      debug = 1;
      /*shift*/
      argc--; argv[1] = argv[2];
    }
  }
  if (argc > 1 && argv[1]) {
    if (!freopen (argv[1], "rb", stdin)) {
      fprintf (stderr, "(E): Cannot read file %s.\n", argv[1]);
      exit(4);
    }
    if (debug) fprintf(stderr, "(D): Processing file %s.\n", argv[1]);
  }

  if (debug)
    fprintf(stderr, "(D): Converting JSON to GraphViz Dot...\n");

  Graph graph = jgf_parse();
  graph_show_list_dot(graph, stdout);

  /*graph_free(graph); */
  return 0;
}
