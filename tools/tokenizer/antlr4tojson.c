/* Copyright (c) 2020 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Interpret ANTLR4 token output format and convert to more
   standard formats. Expects one ANTLR4 token descriptor per line.

   Syntax:

   token ::= "[@" seqnr ","
                  start ":" stop "=" text ","
                  class ","
                  [ channel "," ]
                  line ":" column "]" .
   where

   seqnr   ::= [0-9]+ .
   start   ::= [0-9]+ .
   stop    ::= [0-9]+ .
   text    ::= "'" char* "'" .
   class   ::= "<" (identifier | [0-9]+) | text ">" .
   channel ::= "channel" "=" [1-9][0-9]* .
   line    ::= [1-9][0-9]* .
   column  ::= [0-9]+ .

   Examples:

   [@59,323:326='char',<Keyword>,24:2]
   [@60,328:328='S',<Identifier>,24:7]
   [@61,329:329='[',<Punctuator>,24:8]
   [@62,330:330=']',<Punctuator>,24:9]
   [@63,332:332='=',<Punctuator>,24:11]
   [@64,334:350='"Hello, World!\n"',<StringLiteral>,24:13]
   [@65,351:351=';',<Punctuator>,24:30]
   [@66,353:353='}',<Punctuator>,25:0]

   Approach: Input is read line by line. The ANTLR4 token format is captured
   by a single regular expression (token_RE). Each line is matched against
   that RE. The various parts of the format are captured by their own sub-REs.
   For each part we know the class and the literal value. These are then output
   in the requested format.
*/

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>
#include <unistd.h>             /* getopt() */
#include <libgen.h>             /* basename() */
#include <ctype.h>              /* tolower() */

// POSIX Extended Regular Expressions for all parts of token output.

/* Can we use non-capturing groups? No!
   Define REs here with the least grouping, i.e., avoid ()
   Postpone the necessity of () as long as possible.
*/

// Any amount of white-space:
#define ws_RE     "[ \t\n\r]*"

// An ANTRL4 rule name identifier (must start with a capital letter):
#define ident_RE  "[A-Z][a-zA-Z_0-9]*"

// Unsigned (no leading zeroes except 0) integer:
//#define int_RE  "0|[1-9][0-9]*"
#define int_RE    "[0-9]+"
#define posint_RE "[1-9][0-9]*"

// Any character but control character:
#define char_RE   "[^[:cntrl:]]"
// A (possible empty) single quoted string:
#define string_RE "'(" char_RE ")*'"

#define seqnr_RE  int_RE
#define start_RE  int_RE
#define stop_RE   int_RE
#define line_RE   posint_RE
#define column_RE int_RE
#define rulenr_RE int_RE

#define text_RE   string_RE
#define class_RE  "<((" ident_RE ")|(" string_RE ")|(" rulenr_RE "))>"

#define token_RE  "^\\[@(" seqnr_RE "),("\
  start_RE "):(" stop_RE ")=(" text_RE "),("\
  class_RE "),(channel=(" posint_RE "),)?(" line_RE "):(" column_RE ")\\]$"

// Program option settings:
static int debug = 0;           // when 1 debug output to stderr
static int verbose = 0;         // when 1 info output to stderr
static int nowarn = 0;          // when 1 warnings are suppressed
static int start_token = 0;     // when 1 start filename pseudo-token
static int continuous_files = 0;// when 1 do not reset after each file

// Program globals:
static char *filename = "stdin";// current file being parsed
static unsigned num_files = 0;  // number of files read
static unsigned linenr = 1;     // line number counted from 1
static enum { CSV, JSON, JSONL, RAW } mode = JSON;

// Token class match positions in token_RE:
enum {
  INPUT   = 0, // [@5,20:26='hello there',<IDENTIFIER>,channel=2,11:43]
  SEQNR   = 1, // 5
  START   = 2, // 20
  STOP    = 3, // 26
  TEXT    = 4, // 'hello there'
  IGNORE1 = 5, // last character of 4
  CLASS   = 6, // <IDENTIFIER>
  IGNORE2 = 7,
  CLASS_IDENT = 8, // IDENTIFIER
  CLASS_STRING = 9, // 'hello'
  IGNORE3 = 10, // last character of 9
  CLASS_RULENR = 11, // 123
  IGNORE4 = 12, // channel=2
  CHANNEL = 13, // 2
  LINE    = 14, // 11
  COLUMN  = 15, // 43
  NMATCH  = 16
};

static const char *fields[] = {
  /*  0 */ 0,
  /*  1 */ "seqnr",
  /*  2 */ "start",
  /*  3 */ "stop",
  /*  4 */ "text", // single-quoted string, quotes inclusive
  /*  5 */ 0,
  /*  6 */ 0,
  /*  7 */ 0,
  /*  8 */ "class", // rule name, like: Identifier
  /*  9 */ "class", // string, like a keyword 'while'
  /* 10 */ 0,
  /* 11 */ "class", // rule number, like 12
  /* 12 */ 0,
  /* 13 */ "channel",
  /* 14 */ "line",
  /* 15 */ "column"
};

// Pre-compile the token_RE regular expression.
static regex_t *precompile(void)
{
  regex_t *re = malloc(sizeof(regex_t));
  int errcode = regcomp(re, token_RE, REG_EXTENDED|REG_NEWLINE);
  if (errcode) { // Really should never happen...
    char buf[BUFSIZ];
    regerror(errcode, re, buf, sizeof(buf));
    fprintf(stderr, "(F) Pattern for token_RE does not compile.\n");
    regfree(re);
    free(re);
    exit(1);
  }
  return re;
}

static regex_t *compiled_token_RE;

/* ANTRL4 turns LF, CR, and TAB chars into \ n, \ r, \ t, 2-char combinations
   Unfortunately this is irreversible! Now an existing \ n in a comment can
   no longer be distinguished. Note: typically no hard LF, CR or TAB should
   occur inside string literals.
*/

// Escape token for output as JSON string.
static void JSON_escape(FILE *out, const char *p, unsigned len)
{
  for (; len; len--, p++) {
    char c = *p;
    // A " which is not yet escaped, will be escaped:
    if (c == '"')
      // Insert a backslash before the double quote:
      fputc('\\', out);
    else
    // A \ which is not followed by the JSON expected, is escaped
    if (c == '\\') {
      const char anything_but_valid_escape = '0'; // [^\\\"bfnrt]
      const char peek = len ? *(p+1) : anything_but_valid_escape; // look ahead
      fputc('\\', out);
      if (strchr("\\\"bfnrt", peek)) {
        // An valid JSON escape. Output it and skip peek:
        c = peek;
        p++;
        len--;
      }
      //else Not a correct JSON escape, a standalone backslash; double it.
    }
    //else Not a " or \; default action. 
    fputc(c, out);
  }
}

// Escape token for output as CSV string.
static void CSV_escape(FILE *out, const char *p, unsigned len)
{
  for (; len; len--, p++) {
    if (*p == '"')
      // Double the double quote:
      fputc('\"', out);
    //else Not a "; default action. 
    fputc(*p, out);
  }
}

// Returns length of matched token (ws inclusive) or 0 when in error.
static unsigned get(char const *text)
{
  if (!*text) return 0;
  regex_t *re = compiled_token_RE;
  size_t nmatch = NMATCH;
  regmatch_t pmatch[NMATCH];

  if (regexec(re, text, nmatch, pmatch, REG_NOTEOL) == REG_NOMATCH) {
    // Warn about the failed match:
    fprintf(stderr, "(W) [%s:%u] not a valid token; skipped.\n",
            filename, linenr);
    // Cannot recover; no more input.
    return 0;
  }
  // Here: a valid token recognized.

  // Total length matched (leading white-space inclusive):
  assert(pmatch[INPUT].rm_so == 0);
  unsigned skiplen = pmatch[INPUT].rm_eo;

  int need_comma = 0;
  unsigned i;
  if (mode == JSON || mode == JSONL)
    fputc('{', stdout);
  int channel_absent = 1;
  for (i = 0; i < NMATCH; i++) {

    if (i == LINE && channel_absent && mode == CSV) {
      // no channel; insert default 0:
      fputs(",0", stdout);
    }

    const char *key = fields[i];
    if (!key) continue;
    int offset = pmatch[i].rm_so;
    unsigned len = pmatch[i].rm_eo - offset;
    char const *p = text + offset;
    if (!len) continue;
    if (need_comma)
      fputc(',', stdout);
    // For CSV output don't show key.
    if (mode == JSON || mode == JSONL)
      fprintf(stdout, "\"%s\":", key);
    // values can be: integer, identifier, single-quoted string
    // use JSON values: integer, "identifier", "'...'"

    // Special treatment for text and some class key values;
    // must escape some chars to comply with JSON string!
    switch (i) {
    case CLASS_IDENT:
      // CSV output does not need the quoting. 
      if (mode == JSON || mode == JSONL)
        fputc('"', stdout);
      // Undo the capitalization?
      fputc(tolower(*p), stdout);
      fwrite(p+1, 1, len-1, stdout);
      if (mode == JSON || mode == JSONL)
        fputc('"', stdout);
      break;
    case TEXT:
      // CSV output benefits from quoting; must escape the "
      fputc('"', stdout);
      // Strip off the enclosing single quotes.
      if (mode == JSON || mode == JSONL)
        JSON_escape(stdout, p+1, len-2);
      else
      if (mode == CSV)
        CSV_escape(stdout, p+1, len-2);
      fputc('"', stdout);
      break;
    case CLASS_STRING:
      // CSV output benefits from quoting; must escape the "
      // value is single-quoted string; might contain ", ', \
      // LF, CR and TAB chars are escaped by ANTLR4 to \n, \r, \t
      // Keep the enclosing single quotes!
      fputc('"', stdout);
      if (mode == JSON || mode == JSONL)
        JSON_escape(stdout, p, len);
      else
      if (mode == CSV)
        CSV_escape(stdout, p, len);
      fputc('"', stdout);
      break;
    case CHANNEL:
      channel_absent = 0;
      /*FALL THROUGH*/
    default:
      fwrite(p, 1, len, stdout);
      break;
    }
    need_comma = 1;
  }
  if (mode == JSON || mode == JSONL)
    fputc('}', stdout);
  // Never outputs trailing comma and/or newline.

  return skiplen;
}

int
main(int argc, char *argv[])
{
  extern char *optarg;
  extern int opterr;
  extern int optind;
  int option;
  char const *opt_str = "1dhm:o:rsvw";
  char usage_str[80];
  char *outfile = 0;
  int first_time = 1;
  char *line = NULL;
  size_t len;

  sprintf(usage_str, "usage: %%s [ -%s ] [ FILES ]\n", opt_str);

  /* Process arguments: */
  while ((option = getopt(argc, argv, opt_str)) != EOF) {
    switch (option) {

    case '1':
      continuous_files = 1;
      break;

    case 'd':
      debug = verbose = 1;
      break;

    case 'h':
fputs(
"A converter for the ANTLR4 token output format.\n\n", stderr);
 fprintf(stderr, usage_str, basename(argv[0]));
fputs(
"\nCommand line options are:\n"
"-d       : print debug info to stderr; implies -v.\n"
"-h       : print just this text to stderr and stop.\n"
"-m<mode> : output mode either plain, csv, json (default), or jsonl.\n"
"-o<file> : name for output file (instead of stdout).\n"
"-s       : enable a special start token specifying the filename.\n"
"-1       : treat all filename arguments as a continuous single input.\n"
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
      else if (!strcmp(optarg, "raw"))
        mode = RAW;
      else {
        if (!nowarn)
        fprintf(stderr, "(W): Invalid mode %s (using csv).\n", optarg);
        mode = CSV;
      }
      break;

    case 'o':
      outfile = optarg;
      break;

    case 's':
      start_token = 1;
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

  compiled_token_RE = precompile();

  if (outfile && outfile[0]) {
    if (!freopen(outfile, "w", stdout)) {
      fprintf(stderr, "(F): cannot open %s for writing.\n", outfile);
      exit(3);
    }
  }

  if (optind == argc)
    goto doit;

  do {
    filename = argv[optind];
    if (!freopen (filename, "r", stdin)) {
      if (!nowarn)
      fprintf (stderr, "(W): Cannot read file %s.\n", filename);
      continue;
    }

  doit:
    if (verbose) fprintf (stderr, "(I): Processing file %s...\n", filename);
    num_files++;

    // Header:
    switch (mode) {
    case RAW:
      // Maybe prepend with line comment listing filename?
      break;
    case CSV:
      if (!continuous_files || num_files == 1)
        fputs("seqnr,start,stop,text,class,channel,line,column\n", stdout);
      else {
        fputc('\n', stdout);
        first_time = 1;
      }
      if (start_token) {
        fprintf(stdout, "0,0,0,%s,File,0,1,0\n", filename);
      }
      break;
    case JSON:
    case JSONL:
      if (!continuous_files || num_files == 1) {
        if (mode == JSON) fputs("[\n", stdout);
      }
      else {
        if (mode == JSON) fputc(',', stdout);
        fputc('\n', stdout);
        first_time = 1;
      }
      if (start_token) {
        // Must quote filename:
        fprintf(stdout,
            "{\"seqnr\":0, \"start\":0, \"stop\":0, \"text\":\"%s\","
            " \"class\":\"File\", \"line\":1, \"column\":0}",
                filename);
        first_time = 0;
      }
      break;
    }

    while (getline(&line, &len, stdin) != -1) {
      // If already did some output must close that previous line:
      if (first_time)
        first_time = 0;
      else {
        switch (mode) {
        case RAW:
          break;
        case JSON:
          fputc(',', stdout);
          /*FALL THROUGH*/
        case CSV:
        case JSONL:
          fputc('\n', stdout);
          break;
        }
      }
      get(line); // no , and/or \n output yet
      linenr++;
    }

    // If reading more files must still close the previous output.

    if (!continuous_files) {
      // Trailer:
      switch (mode) {
      case RAW:
        break;
      case JSON:
        // no last comma!
        fputs("\n]", stdout);
        /*FALL THROUGH*/
      case CSV:
      case JSONL:
        fputc('\n', stdout);
        break;
      }
      first_time = 1;
    }

  } while (++optind < argc);

  if (line) free(line);

  if (continuous_files) {
    // Trailer:
    switch (mode) {
    case RAW:
      break;
    case JSON:
      fputs("\n]", stdout);
      /*FALL THROUGH*/
    case CSV:
    case JSONL:
      fputc('\n', stdout);
      break;
    }
  }

  if (num_files > 1 && verbose)
    fprintf(stderr, "(I): Total number of files processed: %u\n", num_files);

  return 0;
}
