/* Copyright (c) 2020, 2021 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Functionality shared by jgf2dot and jgf2spt.
*/
#ifndef JGFLIB_H
#define JGFLIB_H

#include <stdio.h>

/* Enforce strict JSON standard adherence: */
#define JSMN_STRICT
/* Use stack instead of backtracking over tokens: */
#define JSMN_PARENT_LINKS
#include "jsmn.h"

/* Simple graph data structure using pointers. */
typedef struct Attr_S *Attr;
typedef struct Edge_S *Edge;
typedef struct Node_S *Node;
typedef struct Graph_S *Graph;
enum { undirected, directed };

/* An atribute is a key:value pair of token pointers. */
struct Attr_S {
  jsmntok_t *key;               /* attribute key */
  jsmntok_t *value;             /* attribute value */
  Attr next;                    /* next attribute in list */
};

/* a graph */
struct Graph_S {
  int directed;                 /* 1: directed, 0: undirected */
  jsmntok_t *version;           /* standard required attributes */
  jsmntok_t *root;              /* ,, */
  jsmntok_t *type;              /* ,, */
  jsmntok_t *label;             /* ,, */
  Attr attrs;                   /* optional attributes */
  Node nodes;                   /* list of nodes */
  Node last_node;               /* last node or 0 */
  Edge edges;                   /* list of edges */
  Edge last_edge;               /* last edge or 0 */
};

/* (list of) nodes */
struct Node_S {
  jsmntok_t *id;                /* unique identifier */
  jsmntok_t *label;             /* human-readable name */
  int visited;			/* visited flag for traversal */
  unsigned line;		/* 1-based line number */
  unsigned column;		/* 0-based column position */
  Attr attrs;                   /* optional attributes */
  Node next;                    /* next in list of nodes */

  /*derived adjacency list*/
  Edge outgoing;		/* outgoing adjacency list */
  Edge last_out;
};

/* (list of) edges */
struct Edge_S {
  jsmntok_t *between[2];        /* endpoint nodes of the edge */
  jsmntok_t *label;             /* human-readable name */
  Attr attrs;                   /* optional attributes */
  Edge next;                    /* next in list of edges */

  /*derived adjacency list*/
  Node from;
  Node to;
  Edge next_adj_out;		/* in node.outgoing */
};

extern int debug;
extern int verbose;
extern const char *input;
extern const char *filename;

extern jsmntok_t *node_attr_value(Node n, const char *key);
extern void show_attrs(FILE *fp, Attr attrs, int need_comma);
extern Attr attr_find(Attr attrs, const char *key);
extern Node node_find(Graph g, jsmntok_t *id);
extern unsigned outdegree(Node n);
extern void mk_adjacency_graph(Graph g);

extern void show(FILE *fp, jsmntok_t *tok, int do_quote);
extern int string_eq(jsmntok_t *tok, const char *s);
extern int token_startsWith(jsmntok_t *tok, const char *s);
extern int token_eq(jsmntok_t *tok1, jsmntok_t *tok2);
extern Graph jgf_parse(void);
extern Graph jsonml_parse(void);

#endif // JGFLIB_H
