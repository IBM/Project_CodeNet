/* Copyright (c) 2021 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Convert JsonML input to JSON-Graph.

   The input is assumed to be valid JSON and moreover must comply with the
   JsonML specification at http://www.jsonml.org/.
   The output complies with the IBM AI4Code JSON-Graph schema.
   All checks immediately cause a program exit upon error.

   Implementation details.
   Graph object fields not used are:
   Graph: version, root, type, label, attrs
   Node : id (visited misused)
   Edge : between, label, attrs
*/

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>		/* getopt() */
#include <libgen.h>		/* basename() */

#define JSMN_HEADER
#include "jgflib.h"

static int keep_comments = 0;
static int nowarn = 0;
static int start_token = 0;

#if 0
DEBUG ONLY
/* Output graph in detailed adjacency list format. */
static void graph_show_adj(Graph g, FILE *fp)
{
  Node n;
  fprintf(stdout, "graph, %sdirected\n", g->directed ? "" : "un");
  for (n = g->nodes; n; n = n->next) {
    Edge e;
    fprintf(fp, "node id: %u, ", n->visited);
    show(fp, n->label, 0);
    fputc('\n', fp);
    show_attrs(fp, n->attrs, 0);
    if (n->attrs) fputc('\n', fp);
    for (e = n->outgoing; e; e = e->next_adj_out) {
      /* Get node ids: */
      fprintf(fp, "%u -%c %u\n",
	      e->from->visited,
	      g->directed ? '>' : '-',
	      e->to->visited);
    }
  }
}
#endif

/* Decode the coordinates attribute. */
static void coords(Attr attr, unsigned *line, unsigned *column)
{
  if (attr) {
    /* Find the colon separator: */
    const char *start = input + attr->value->start;
    const char *end   = input + attr->value->end;
    const char *p;
    for (p = start; p < end; ++p)
      if (*p == ':') {
	/* Get value line:col */
	*line   = atoi(start);
	*column = atoi(p+1);
	return;
      }
  }
}

/* Determine correct coordinates for all tokens (leaf nodes)
   and adjust all labels by removing leading and trailing white-space.
*/
static void det_coords_adjust_labels(Graph g)
{
  /* Coordinates for some punctuators are (a bit) off. */
  unsigned line = 1, column = 0;
  unsigned end_line = 1, end_column = 0;
  Node n;
  for (n = g->nodes; n; n = n->next) {
    /* Strip any white-space at front and back from label.
       Includes real and escaped TABs and LFs that were put in by
       the xml-to-jsonml XSLT program.
       Note: this does not affect any of the token literals.
    */
    const char *start = input + n->label->start;
    const char *end   = input + n->label->end;
    const char *p;
    for (p = start; p < end; ++p)
      if (isspace(*p))
	n->label->start++;
      else if (*p == '\\' && (*(p+1) == 'n' || *(p+1) == 't')) {
	n->label->start += 2;
	++p;
      }
      else
	break;
    start = input + n->label->start;
    for (p = end-1; p >= start; --p)
      if (isspace(*p))
	n->label->end--;
      else if (*(p-1) == '\\' && (*p == 'n' || *p == 't')) {
	n->label->end -= 2;
	--p;
      }
      else
	break;

    /* Fish out any pos:start attribute and decode: */
    coords(attr_find(n->attrs, "pos:start"), &line, &column);

    /* Fish out any pos:end attribute and decode: */
    coords(attr_find(n->attrs, "pos:end"), &end_line, &end_column);

    /* Only keep coordinates for tokens for now; orig column counts from 1. */
    if (n->line) { /* this is a token */
      n->line = line; /* > 0 */
      n->column = column-1;

      line = end_line;
      column = end_column+1;
    }
  }
}

static void graph_show_jgf(Graph g, FILE *fp)
{
  fputs("{\n"
	"  \"graph\": {\n"
	"    \"version\": \"1.0\",\n"
	"    \"directed\": true,\n"
	"    \"type\": \"tree\",\n"
	"    \"root\": 0,\n"
	"    \"order\": \"dfs-preorder\",\n",
	fp);

  if (filename)
    /* assume no need to escape filename */
    fprintf(fp, "    \"label\": \"%s\",\n", filename);

  fputs("    \"nodes\": [\n", fp);

  det_coords_adjust_labels(g);

  Node n;
  for (n = g->nodes; n; n = n->next) {
    fprintf(fp, "      { \"id\":%2u,\"label\":", n->visited);
    show(fp, n->label, 1);
    if (n->line) /* leaf node */
      fprintf(fp, ",\"line\":%u,\"column\":%u", n->line, n->column);
    fputs(" }", fp);
    if (n->next) fputc(',', fp);
    fputc('\n', fp);
  }
  fputs("    ],\n"
	"    \"edges\": [\n", fp);
  int need_comma = 0;
  for (n = g->nodes; n; n = n->next) {
    Edge e;
    for (e = n->outgoing; e; e = e->next_adj_out) {
      if (need_comma) fputs(",\n", fp);
      fprintf(fp, "      { \"between\": [%2u,%2u] }",
	      e->from->visited,
	      e->to->visited);
      need_comma = 1;
    }
  }
  if (need_comma) fputc('\n', fp);
  fputs("    ]\n  }\n}\n", fp);
}

/* Undo JSON escaping: \\ => \. */
static void JSON_unescape(jsmntok_t *tok)
{
  char *last = (char *)input + tok->start;
  const char *p   = last;
  const char *end = input + tok->end;
  for (; p < end; p++) {
    if (*p == '\\' && (*(p+1) == '\\' || *(p+1) == '"')) {
      *last++ = *++p;
      tok->end--;
      continue;
    }
    *last++ = *p;
  }
}

// Escape token for output as CSV string.
static void CSV_escape(FILE *fp, jsmntok_t *tok)
{
  const char *p   = input + tok->start;
  const char *end = input + tok->end;
  /* Check whether quotes are needed: */
  for (; p < end; p++)
    if (*p == ',' || *p == '"') {
      // start CSV string:
      fputc('"', fp);
      /* reset and quote ": */
      for (p = input + tok->start; p < end; p++) {
	if (*p == '"')
	  fputc('"', fp);
	fputc(*p, fp);
      }
      // end CSV string:
      fputc('"', fp);
      return;
    }
  show(fp, tok, -1);
}

/* DFS */
static void show_tokens_aux(Node n, Node p, Node gp, FILE *fp)
{
  if (token_startsWith(n->label, "cpp:"))
    return;

  if (n->line) { /* leaf node */
    /* Forego sequence number; easy to add afterwards. */
    /* line, col, class, token */

    /* A leaf node always has a parent! */
    assert(p);
    /* The parent always has a non-empty label! */
    jsmntok_t *class = p->label;

    /* Do not consider some classes: */
    if (string_eq(class, "unit"))
      return;

    enum { IDENTIFIER, STRING, CHARACTER, NUMBER, COMMENT, OTHER } kind = OTHER;

    if (string_eq(class, "comment")) {
      if (!keep_comments)
	return;
      JSON_unescape(n->label);
      kind = COMMENT;
    }

    fprintf(fp, "%u,%u,", n->line, n->column);

    /* Analyze token literal (label is scalar): */
    char c = input[n->label->start];
    if (isalpha(c) || c == '_')
      kind = IDENTIFIER;
    else if (isdigit(c))
      kind = NUMBER;
    else if (c == '\'') {
      /* Undo JSON escaping in characters, e.g. '\\n' => '\n'; '\\\\' => '\\' */
      JSON_unescape(n->label);
      kind = CHARACTER;
    }
    else if (c == '\\') {
      /* Undo JSON escaping in strings: */
      /* e.g. \"  \\\"graph\\\": {\\n\" => "  \"graph\": {\n" */
      JSON_unescape(n->label);
      kind = STRING;
    }

    /* token class (C):

       [filename]
       [comment]
       keyword
       string
       character
       number
       operator

       identifiers:
       1. point of declaration/introduction (def)
       2. points of usage (use)

       category: variable, function, type, label

       C/C++
       decl (variable declaration)
       name (variable usage) part of "compound" var: s.p->q->r
       expr (variable usage)
       type (usage of type name)
       typedef (name definition)
       struct (name definition)
       union (name definition)
       enum (name definition)
       label (name definition)
       function (name definition)
       call (a function by name)
       goto (label name)

       C++
       class (name definition)
       namespace (name definition)
       parameter (template parameter name)
       using (type name definition)
       expr can refer to a type name
       super (type name usage)
    */

    /* Output class name: */

    if (string_eq(class, "comment"))
      fputs("comment", fp);
    else if (token_eq(class, n->label) ||
	     string_eq(class, "specifier") ||
	     string_eq(class, "return") ||
	     string_eq(class, "if") && string_eq(n->label, "else if"))
      fputs("keyword", fp);
    else if (string_eq(class, "name")) {
      if (gp)
	show(fp, gp->label, 0);
      else
	show(fp, class, 0);
    }
    else if (kind == CHARACTER)
      fputs("character", fp);
    else if (kind == STRING)
      fputs("string", fp);
    else if (kind == NUMBER)
      fputs("number", fp);
    else
      fputs("operator", fp);
    fputc(',', fp);

    /* Output token literal: */

    if (kind == CHARACTER || kind == STRING || kind == COMMENT)
      CSV_escape(fp, n->label);
    /* Weird case "return;" */
    else if (string_eq(class, "return") && string_eq(n->label, "return;"))
      fprintf(fp, "return\n%u,%u,operator,;", n->line, n->column+6);
    /* Another strange case <if type="elseif"> */
    else if (string_eq(class, "if") && string_eq(n->label, "else if"))
      fprintf(fp, "else\n%u,%u,keyword,if", n->line, n->column+5);
    else if (string_eq(n->label, ","))
      fputs("\",\"", fp);
    else
      show(fp, n->label, -1);
    fputc('\n', fp);
  }
  else {
    Edge e;
    for (e = n->outgoing; e; e = e->next_adj_out)
      /* It's a tree; no need for visited flag! */
      show_tokens_aux(e->to, n, p, fp);
  }
}

static void show_tokens(Graph g, FILE *fp)
{
  if (filename && start_token)
    /* assume no need to escape filename */
    fprintf(fp, "0,0,filename,%s\n", filename);

  det_coords_adjust_labels(g);
  /* First node is root of tree. */
  show_tokens_aux(g->nodes, 0, 0, fp);
}

int main(int argc, char *argv[])
{
  extern char *optarg;
  extern int opterr;
  extern int optind;
  int option;
  char const *opt_str = "cdho:stvw";
  char usage_str[80];

  char *outfile = 0;
  enum { CSV, JSON, JSONL, XML, RAW } mode = CSV;
  int output_tokens = 0;

  sprintf(usage_str, "usage: %%s [ -%s ] [ FILE ]\n", opt_str);

  /* Process arguments: */
  while ((option = getopt(argc, argv, opt_str)) != EOF) {
    switch (option) {

    case 'c':
      keep_comments = 1;
      break;

    case 'd':
      debug = verbose = 1;
      break;

    case 'h':
fputs(
"Reads a JsonML file and constructs a JSON-Graph from its tree structure.\n"
"If the JsonML represents a (abstract) syntax tree, e.g. generated by scrML\n"
"then this program can also output a token stream instead.\n\n", stdout);
fprintf(stderr, usage_str, basename(argv[0]));
fputs(
"\nCommand line options are:\n"
"-c       : keep comments in the token output stream.\n"
"-d       : print debug info to stderr; implies -v.\n"
"-h       : print just this text to stderr and stop.\n"
"-o<file> : name for output file (instead of stdout).\n"
"-s       : enable a special start token specifying the filename.\n"
"-t       : output the tokens instead of a graph.\n"
"-v       : print action summary to stderr.\n"
"-w       : suppress all warning messages.\n",
      stderr);
      return 0;

    case 'm':
      if (!strcmp(optarg, "csv"))
        mode = CSV;
      else if (!strcmp(optarg, "json"))
        mode = JSON;
      else if (!strcmp(optarg, "jsonl"))
        mode = JSONL;
      else if (!strcmp(optarg, "xml"))
        mode = XML;
      else if (!strcmp(optarg, "raw"))
        mode = RAW;
      else {
	if (!nowarn)
        fprintf(stderr, "(W): Invalid mode %s (using plain).\n", optarg);
        mode = CSV;
      }
      break;

    case 'o':
      outfile = optarg;
      break;

    case 's':
      start_token = 1;
      break;

    case 't':
      output_tokens = 1;
      break;

    case 'v':
      verbose = 1;
      break;

    case 'w':
      nowarn = 1;
      break;

    case '?':
    default:
      fputs("(F): unknown option. Stop.\n", stderr);
      fprintf(stderr, usage_str, argv[0]);
      return 1;
    }
  }

  if (outfile && outfile[0]) {
    if (!freopen(outfile, "w", stdout)) {
      fprintf(stderr, "(F): cannot open %s for writing.\n", outfile);
      exit(3);
    }
  }

  filename = 0;
  if (optind < argc) {
    filename = argv[optind];
    if (!freopen(filename, "rb", stdin)) {
      fprintf (stderr, "(E): Cannot read file %s.\n", filename);
      exit(4);
    }
    if (debug) fprintf(stderr, "(D): Processing file %s.\n", filename);
  }

  if (debug)
    fprintf(stderr, "(D): Converting JSONML to JSON-Graph...\n");

  Graph graph = jsonml_parse();
  if (output_tokens)
    show_tokens(graph, stdout);
  else
    graph_show_jgf(graph, stdout);

  /*graph_free(graph); */
  return 0;
}
