/* Copyright (c) 2020, 2021 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Functionality shared by jgf2dot, jgf2spt, and jsonml2jgf.
*/

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "jgflib.h"

/** Set to 1 to get debug messages to stderr. */
int debug = 0;
int verbose = 0;

/** Global to avoid too much passing around.
    Once allocated and filled, mostly used as read-only.
*/
const char *input;
const char *filename;

static Attr attr_create(jsmntok_t *key, jsmntok_t *value)
{
  Attr a = malloc(sizeof(*a));
  a->key   = key;
  a->value = value;
  a->next  = NULL;
  return a;
}

Attr attr_find(Attr attrs, const char *key)
{
  while (attrs) {
    if (string_eq(attrs->key, key))
      return attrs;
    attrs = attrs->next;
  }
  return NULL;
}

static void graph_add_attr(Graph g, Attr a)
{
  a->next = g->attrs;
  g->attrs = a;
}

static void node_add_attr(Node n, Attr a)
{
  a->next = n->attrs;
  n->attrs = a;
}

jsmntok_t *node_attr_value(Node n, const char *key)
{
  Attr attr = attr_find(n->attrs, key);
  return attr ? attr->value : NULL;
}

unsigned outdegree(Node n)
{
  unsigned count = 0;
  Edge e;
  for (e = n->outgoing; e; e = e->next_adj_out)
    count++;
  return count;
}

static void edge_add_attr(Edge e, Attr a)
{
  a->next = e->attrs;
  e->attrs = a;
}

static Graph graph_create(void)
{
  return calloc(1, sizeof(struct Graph_S));
}

#if 0
static void attrs_free(Attr attrs)
{
  while (attrs) {
    Attr save = attrs->next;
    free(attrs);
    attrs = save;
  }
}

static void graph_free(Graph g)
{
  /* free graph attributes: */
  attrs_free(g->attrs);
  /* free nodes: */
  Node n = g->nodes;
  while (n) {
    Node save = n->next;
    /* free node attributes: */
    attrs_free(n->attrs);
    free(n);
    n = save;
  }
  /* free edges: */
  Edge e = g->edges;
  while (e) {
    Edge save = e->next;
    /* free edge attributes: */
    attrs_free(e->attrs);
    free(e);
    e = save;
  }
  /* free graph: */
  free(g);
}
#endif

static Node node_create(void)
{
  return calloc(1, sizeof(struct Node_S));
}

static void node_add(Graph g, Node n)
{
  if (g->last_node)
    g->last_node->next = n;
  else
    g->nodes = n;
  g->last_node = n;
}

Node node_find(Graph g, jsmntok_t *id)
{
  /* Assumes id is a valid nodeid */
  int len1 = id->end-id->start;
  Node n;
  for (n = g->nodes; n; n = n->next) {
    int len2 = n->id->end-n->id->start;
    if (len1 == len2 && !strncmp(input+id->start, input+n->id->start, len1))
      return n;
  }
  return NULL;
}

static Edge edge_create(void)
{
  return calloc(1, sizeof(struct Edge_S));
}

static void edge_add(Graph g, Edge e)
{
  if (g->last_edge)
    g->last_edge->next = e;
  else
    g->edges = e;
  g->last_edge = e;
}

static void adj_edge_add(Node from, Edge e, Node to)
{
  e->from = from;
  e->to = to;
  if (from->last_out)
    from->last_out->next_adj_out = e;
  else
    from->outgoing = e;
  from->last_out = e;
}

/** Convert (nodelist,edgelist) graph into explicit adjacency structure.
    Assume graph is directed.
*/
void mk_adjacency_graph(Graph g)
{
  Edge e;
  assert(g->directed);
  for (e = g->edges; e; e = e->next) {
    Node from = node_find(g, e->between[0]);
    Node to   = node_find(g, e->between[1]);
    assert(from);
    assert(to);
    adj_edge_add(from, e, to);
  }
}

/** Get input file as one long string in global input.
    Returns number of bytes read.
*/
static size_t read_input(void)
{
  size_t nread = 0;
  size_t nalloc = 1024;
  input = malloc(nalloc);
  char *p = (char *)input;
  int cc;

  while ((cc = getchar()) != EOF) {
    if (nread == nalloc) {
      nalloc <<= 1;
      input = realloc((void *)input, nalloc);
      /* reset p to correct spot in input: */
      p = (char *)input+nread;
    }
    *p++ = cc;
    nread++;
  }
  /* No need for terminating \0 char. */
  if (debug) fprintf(stderr, "(D): Read %u bytes.\n", nread);
  return nread;
}

/** Parse the JSON input (global) into an array of tokens.
    Returns the allocated token array.
    The number of tokens is passed back via num_tokens.
*/
static jsmntok_t *parse(int *num_tokens)
{
  jsmn_parser parser;
  size_t nalloc = 1024;         /* tokens allocated */
  size_t nread = read_input();
  int ntokens;
  jsmntok_t *tokens;

  if (debug)
    fprintf(stderr, "(D): Parsing the input...\n");
  jsmn_init(&parser);
  tokens = malloc(nalloc * sizeof(tokens[0]));

 restart: {
    ntokens = jsmn_parse(&parser, input, nread, tokens, nalloc);
    switch (ntokens) {
    case JSMN_ERROR_NOMEM:
      /* Reallocate and keep going. */
      if (debug)
        fprintf(stderr, "(D): Reallocating tokens array.\n");
      nalloc <<= 1;
      tokens = realloc((void *)tokens, nalloc * sizeof(tokens[0]));
      goto restart;
      
    case JSMN_ERROR_INVAL:
      fprintf(stderr, "(E): Invalid character in input.\n");
      exit(2);
      
    case JSMN_ERROR_PART:
      /* Should never happen! */
      fprintf(stderr, "(E): Incomplete input, more bytes expected.\n");
      exit(3);

    default:
      break;
    }
  }
  *num_tokens = ntokens;
  return tokens;
}

/** Returns string representation for JSON type. */
static const char *type(jsmntype_t t)
{
  switch (t) {
  case JSMN_UNDEFINED:
    return "undefined";
  case JSMN_OBJECT:
    return "object";
  case JSMN_ARRAY:
    return "array";
  case JSMN_STRING:
    return "string";
  case JSMN_PRIMITIVE: /* number, false, true, null */
    return "primitive";
  default:
    return "ERROR";
  }
}

/** Outputs the token to open file fp.
    When do_quote is > 0, output token double-quoted,
    when do_quote is < 0, output token without double-quotes,
    otherwise first investigate and quote appropriately when needed.
*/
void show(FILE *fp, jsmntok_t *tok, int do_quote)
{
  /* start (0-based), end (= 1 beyond last): byte positions in input
     meaning of size depends on token type:
     object: number of keys
     array:  number of elements
     string: 0 for value, 1 for key
     primitive (number,false,true,null): no meaning, 0
  */
  if (!do_quote) {
    /* Observe dot ID syntax; must quote when non-alnum. */
    const char *p;
    for (p = input + tok->start; p < input + tok->end; p++)
      if (isspace(*p) || ispunct(*p) && *p != '_') {
	do_quote = 1;
	break;
      }
  }
  if (do_quote > 0) fputc('"', fp);
  fwrite(input + tok->start, 1, tok->end - tok->start, fp);
  if (do_quote > 0) fputc('"', fp);
}

/** Outputs up to the first 16 chars of token to fp. */
static void show_16(FILE *fp, jsmntok_t *tok)
{
  size_t len = tok->end - tok->start;
  if (len > 16) {
    len = 16;
    fwrite(input + tok->start, 1, len, fp);
    fputs("...", fp);
  }
  else
    fwrite(input + tok->start, 1, len, fp);
}

void show_attrs(FILE *fp, Attr attrs, int need_comma)
{
  for (; attrs; attrs = attrs->next) {
    if (need_comma) fputc(',', fp);
    show(fp, attrs->key, 0);
    fputs("=", fp);
    show(fp, attrs->value, 1);
    need_comma = 1;
  }
}

/** Checks whether (JSMN_STRING) token equals a certain string value. */
int string_eq(jsmntok_t *tok, const char *s) {
  int len = tok->end - tok->start;
  return strlen(s) == len && !strncmp(input + tok->start, s, len);
}

/** Checks whether token start with s. */
int token_startsWith(jsmntok_t *tok, const char *s) {
  int len1 = tok->end - tok->start;
  int len2 = strlen(s);
  return len2 <= len1 && !strncmp(input + tok->start, s, len2);
}

/** Checks whether tokens are equal (same text). */
int token_eq(jsmntok_t *tok1, jsmntok_t *tok2) {
  int len1 = tok1->end - tok1->start;
  int len2 = tok2->end - tok2->start;
  return len1 == len2
    && !strncmp(input + tok1->start, input + tok2->start, len1);
}

static void error(jsmntok_t *tok, const char *msg)
{
  fprintf(stderr, "(E): [pos:%u] Expect %s; got %s (",
          tok->start, msg, type(tok->type));
  show_16(stderr, tok);
  fputs(").\n", stderr);
  exit(6);
}

/** Checks whether token is of a certain type. */
static void expect(jsmntok_t *tok, jsmntype_t t)
{
  if (tok->type != t)
    error(tok, type(t));
}

/** Checks whether token is string or number literal. */
static void expect_nodeid(jsmntok_t *tok)
{
  /* Note: being an integer as opposed to float is not checked! */
  if (!(tok->type == JSMN_STRING && !tok->size ||
        tok->type == JSMN_PRIMITIVE && isdigit(input[tok->start])))
    error(tok, "string or integer literal");
}

/** Checks whether token is a false or true literal. */
static void expect_bool(jsmntok_t *tok)
{
  if (!(tok->type == JSMN_PRIMITIVE && strchr("ft", input[tok->start])))
    error(tok, "boolean value false or true");
}

/** Checks whether token is a string or primitive. */
static void expect_scalar(jsmntok_t *tok)
{
  if (!(tok->type == JSMN_STRING && !tok->size ||
        tok->type == JSMN_PRIMITIVE))
    error(tok, "string or primitive");
}

/** Skips all tokens that form the current token type.
    Returns the token right after.
*/
static jsmntok_t *skip(jsmntok_t *tok)
{
  switch (tok->type) {
  case JSMN_OBJECT: {
    int keys = tok->size; /* this many keys */
    tok++;
    while (keys--) {
      /*key:value*/
      tok = skip(tok+1);
    }
    return tok;
  }
  case JSMN_ARRAY: {
    int elems = tok->size; /** this many elements */
    tok++;
    while (elems--) {
      /*value*/
      tok = skip(tok);
    }
    return tok;
  }
  case JSMN_STRING:
    /* Must be literal value, not a key! */
    assert(!tok->size);
    /*FALL_THROUGH*/
  case JSMN_PRIMITIVE: /* number, false, true, null */
    return tok+1;
  }
  assert(!"(F) Never here!");
}

/** We have an object and are looking for a specific key, ignoring all others.
    If the key is not found, the object itself is considered the value.
    Returns the first token of the value.
*/
static jsmntok_t *lookfor_value_of_key(jsmntok_t *tok, const char *s)
{
  assert(tok->type == JSMN_OBJECT);
  jsmntok_t *save_tok = tok;
  int keys = tok->size; /* this many keys */
  tok++;
  while (keys--) {
    /*key*/
    if (string_eq(tok, s))
      return ++tok;
    /*value*/
    tok = skip(tok+1);
  }
  return save_tok;
}

Graph jgf_parse(void)
{
  int ntokens;
  jsmntok_t *tokens = parse(&ntokens);

  /* Collect all information in internal graph data structure: */
  Graph graph = graph_create();

  if (debug)
    fprintf(stderr, "(D): Parsing the JSON-Graph...\n");

  /* token cursor: */
  jsmntok_t *token = tokens;

  /* input must be an object: */
  expect(token, JSMN_OBJECT); /* ^{ ... } */
  /* look for graph key: */
  token = lookfor_value_of_key(token, "graph");
  /* value must be an object: */
  expect(token, JSMN_OBJECT); /* { "graph": ^{ ... }} */
  int keys = token->size; /* this many keys */
  token++;
  /* Consider all keys of "graph" object: */
  while (keys--) {
    expect(token, JSMN_STRING); /* { "graph": { ^"?": ... }} */

    /* Handle predefined keys: */

    if (string_eq(token, "directed")) {
      /* FIXME: required */
      token++;
      expect_bool(token);
      graph->directed = (input[token->start] == 't');
      token++;
      continue;
    }

    if (string_eq(token, "version")) {
      /* FIXME: required and value "1.0" */
      token++;
      expect(token, JSMN_STRING);
      graph->version = token;
      token++;
      continue;
    }

    if (string_eq(token, "type")) {
      token++;
      expect(token, JSMN_STRING);
      graph->type = token;
      token++;
      continue;
    }

    if (string_eq(token, "root")) {
      token++;
      expect_nodeid(token);
      graph->root = token;
      token++;
      continue;
    }

    if (string_eq(token, "label")) {
      token++;
      expect(token, JSMN_STRING);
      graph->label = token;
      token++;
      continue;
    }

    if (string_eq(token, "nodes")) {
      /* FIXME: required */
      /* get value: */
      token++;
      expect(token, JSMN_ARRAY); /* { "graph": { "nodes": ^[...] }} */
      int elems = token->size; /* this many elements */
      token++;
      while (elems--) {
        Node node = NULL;
        expect(token, JSMN_OBJECT); /* ... "nodes": [ ^{...} ] */
        int keys = token->size; /* this many keys */
        token++;
        while (keys--) {
          expect(token, JSMN_STRING);
          if (string_eq(token, "id")) {
            token++;
            expect_nodeid(token);
            if (!node) node = node_create();
            node->id = token;
            token++;
          }
          else
          if (string_eq(token, "label")) {
            token++;
            expect(token, JSMN_STRING);
            if (!node) node = node_create();
            node->label = token;
            token++;
          }
          else {
            /* any other key add to node attributes: */
            if (!node) node = node_create();
            node_add_attr(node, attr_create(token, token+1));
            token = skip(token+1);
          }
        }
        if (node) node_add(graph, node);
      }
      continue;
    }

    if (string_eq(token, "edges")) {
      /* FIXME: required */
      /* get value: */
      token++;
      expect(token, JSMN_ARRAY); /* { "graph": { "edges": ^[...] }} */
      int elems = token->size; /* this many elements */
      token++;
      while (elems--) {
        Edge edge = NULL;
        expect(token, JSMN_OBJECT); /* ... "edges": [ ^{...} ] */
        int keys = token->size; /* this many keys */
        token++;
        while (keys--) {
          expect(token, JSMN_STRING);
          if (string_eq(token, "between")) {
            token++;
            expect(token, JSMN_ARRAY); /* "between": ^[...] */
            assert(token->size == 2);
            token++;
            expect_nodeid(token);
            if (!edge) edge = edge_create();
            edge->between[0] = token;
            token++;
            expect_nodeid(token);
            edge->between[1] = token;
            token++;
          }
          else
          if (string_eq(token, "label")) {
            token++;
            expect(token, JSMN_STRING);
            if (!edge) edge = edge_create();
            edge->label = token;
            token++;
          }
          else {
            /* any other key add to edge attributes: */
            if (!edge) edge = edge_create();
            edge_add_attr(edge, attr_create(token, token+1));
            token = skip(token+1);
          }
        }
        if (edge) edge_add(graph, edge);
      }
      continue;
    }

    /* any other key add to graph attributes: */
    graph_add_attr(graph, attr_create(token, token+1));
    /* get value: */
    token = skip(token+1);
  }

  /*
  free((void *)input);
  free(tokens);
  */
  return graph;
}

/* Helper for jsonml_parse. */
static jsmntok_t *jsonml_attributes(jsmntok_t *token, Node node)
{
  int keys = token->size;
  token++;
  while (keys--) {
    /* key: scalar (string, number, bool, null) */
    expect(token, JSMN_STRING);
    token++;
    expect_scalar(token);
    node_add_attr(node, attr_create(token-1, token));
    token++;
  }
  return token;
}

/* Helper for jsonml_parse. */
static Node jsonml_element(jsmntok_t **tok, Graph g)
{
  static unsigned node_id = 0;
  jsmntok_t *token = *tok;
  /* Every element corresponds to a (fresh) tree node. */
  Node node = node_create();
  /* Misuse visited as node id: */
  node->visited = node_id++;
  node_add(g, node);
  /* Input must be a non-empty array or scalar: */
  if (token->type == JSMN_ARRAY) {
    int elems = token->size;
    token++; /* skip the [ */
    /* elem 0: string, XML element tag: */
    expect(token, JSMN_STRING);
    node->label = token;
    token++; elems--;
    /* Mind: can have singleton arrays (caused by self-closed XML element) */

    /* elem 1: optional object, XML element attributes */
    if (elems && token->type == JSMN_OBJECT) {
      token = jsonml_attributes(token, node);
      elems--;
    }
    /* Optional array (nested elements) or scalar (text nodes) */
    while (elems--) {
      /* All children of this node. */
      Edge edge = edge_create();
      adj_edge_add(node, edge, jsonml_element(&token, g));
      edge_add(g, edge); // graph edges not really used.
    }
  }
  else {
    expect_scalar(token);
    node->label = token;
    /* Misuse line to indicate this is a token (and not just any leaf). */
    node->line = 1;
    token++;
  }
  *tok = token;
  return node;
}

/* Parse an explicit JSON tree structure consisting of nested arrays and
   scalars elements and optional objects for attributes, the result of
   converting XML to JSON with xml-to-json.
   See JsonML-schema.json.
*/
Graph jsonml_parse(void)
{
  int ntokens;
  jsmntok_t *tokens = parse(&ntokens);

  /* Collect all information in internal graph data structure: */
  Graph graph = graph_create();

  if (debug)
    fprintf(stderr, "(D): Parsing the JsonML...\n");

  jsonml_element(&tokens, graph);

  /*
  free((void *)input);
  */
  return graph;
}
