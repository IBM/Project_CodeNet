/* Copyright (c) 2021, 2022 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Simple C/C++ and Java Tokenizer.
   For the most part assumes that the input source text is grammatically
   correct C, C++, or Java code.
   (Since Java at the lexical level is very close to C, we here sort of misuse
   it as a Java tokenizer, albeit that not all of its keywords
   and some literal pecularities are not recognized.)

   Recognizes the following lexeme classes:
   - identifier
   - reserved word/keyword
   - binary, octal, decimal, hexadecimal and floating-point numbers
   - double-quoted string literal (double quotes inclusive)
   - single-quoted character literal (single quotes inclusive)
   - all single, double, and triple operator and punctuation symbols
   - the preprocessor tokens # and ## (unless interpreted as comment)

   A newline is defined as a single linefeed character \n or the combination
   carriage return \r followed by linefeed \n. Officialy a carriage return
   by itself (not followed by \n) is also interpreted as a newline.
   A line continuation is a backslash \ immediately followed by a newline.
   Line continuations are handled at the character input level, so the token
   recognizers will only see logical lines and never encounter a \ at the end
   of a line.

   For each correctly recognized token determines its class/type and
   the exact coordinates (line number and column) in the input text of
   its starting character. Line and column reflect positions in the
   physical line structure, not the logical one.
   All token literals are output exactly as they appear in the source text,
   without any interpretation of escaped characters etc. However, the particular
   output format will enforce certain escaping as needed.

   Moreover, white-space, control characters and comments are normally skipped
   and anything left over is flagged as illegal characters.

   See these refs for details on the lexical definitions:
   C++14 Final Working Draft: n4140.pdf
   https://www.ibm.com/support/knowledgecenter/en/SSGH3R_13.1.3/com.ibm.xlcpp1313.aix.doc/language_ref/lexcvn.html

   Shortcomings:
   Column position gets confused when TABs and CRs are present in the input.
   (A TAB is counted as a single character position. A CR causes a transition
   to a new line.)
   No trigraph sequences (??x) are recognized.
   No universal characters (\u and \U) in an identifier.
   Raw strings with R prefix are not supported.
   No preprocessing is attempted: phrases like #include <stdio.h> are
   broken in the tokens # include < stdio . h >
   (or completely ignored when # is considered start of a line comment).
   Multiple > are probably handled incorrectly for C++ (and Java).
   We will always find the longest match, so >> is the shift-right operator
   and >>> is a Java operator.

   Multiple output formats are supported:
   - plain text, nice looking but hard to parse
   - CSV, but need to properly escape quotes
     (https://tools.ietf.org/html/rfc4180)
   - JSON, again mind the proper escaping
   - XML, again mind the proper escaping
  (- maybe add the ANTLR4 format?)

   Run with -h to get a list of all command line options.

   Program exit codes:
   0: success
   1: illegal character(s) or premature EOF detected
   2: look-ahead buffer overflow
   3: output file cannot be opened
   4: could not (re-)allocate token buffer

   C++ Token categories as Regular Expressions:
   (\b = [01], \o = [0-7], \d = [0-9], \x = [a-fA-F0-9],
    \s = [uU](l|L|ll|LL)?|[lL][uU]?|(ll|LL)[uU]?

   - keyword   : one of the list of keywords in c++20.kw
   - identifier: [_a-zA-Z][_a-zA-Z0-9]*
   - integer   : 0[bB]\b('?\b])*\s?
               | 0('?\o)*\s?
               | 0[xX]\x('?\x)*\s?
               | [1-9]('?\d)*\s?
   - floating  : .\d('?\d)*([eE][-+]?\d('?\d)*)?[fFlL]?
               | \d('?\d)*.(\d('?\d)*)?([eE][-+]?\d('?\d)*)?[fFlL]?
               | \d('?\d)*[eE][-+]?\d('?\d)*[fFlL]?
   - string    : [uUL]?"([^"\\\n]|\\.|\\\n)*"
   - character : [uUL]?'([^']|\\.)'
   - operator  : one of these operator and punctuation symbols:
                 { } [ ] ( ) ; : ? . ~ ! + - * / % ^ = & | < > ,
                 <: :> <% %> :: .* -> += -= *= /= %= ^= &= |= == !=
                 <= >= && || << >> ++ -- ... ->* <=> <<= >>=
   - preprocessor : # | ##
*/

#include <unistd.h>             /* getopt() */
#include <libgen.h>             /* basename() */

#include "libtoken.h"

int main(int argc, char *argv[])
{
  extern char *optarg;
  extern int opterr;
  extern int optind;
  int option;
  char const *opt_str = "1acdhjkl:m:nNo:rsvwW";
  char usage_str[80];

  const char *token;
  enum TokenClass type;
  unsigned line;
  unsigned col;
  unsigned pos;
  unsigned token_len;
  unsigned num_files = 0;    // number of files read
  int start_token = 0;       // when 1 start filename pseudo-token
  int continuous_files = 0;  // when 1 do not reset after each file

  char *outfile = 0;
  enum { PLAIN, CSV, JSON, JSONL, XML, RAW } mode = PLAIN;
  int first_time = 1;
  Language source;
  int explicit_source = 0;
  int append = 0;
  int suppress_newline = 0;

  sprintf(usage_str, "usage: %%s [ -%s ] [ FILES ]\n", opt_str);

  /* Process arguments: */
  while ((option = getopt(argc, argv, opt_str)) != EOF) {
    switch (option) {

    case '1':
      continuous_files = 1;
      break;

    case 'a':
      append = 1;
      break;

    case 'c':
      hash_as_comment = 1;
      break;

    case 'd':
      debug = verbose = 1;
      break;

    case 'h':
fputs(
"A tokenizer for C/C++ (and Java) source code with output in 6 formats.\n"
"Recognizes the following token classes: keyword, identifier, integer,\n"
"floating, string, character, operator, and preprocessor.\n\n", stderr);
fprintf(stderr, usage_str, basename(argv[0]));
fputs(
"\nCommand line options are:\n"
"-a       : append to output file instead of create or overwrite.\n"
"-c       : treat a # character as the start of a line comment.\n"
"-d       : print debug info to stderr; implies -v.\n"
"-h       : print just this text to stderr and stop.\n"
"-j       : assume input is Java (deprecated: use -l Java or .java).\n"
"-k       : output line and block comments as tokens.\n"
"-l<lang> : specify language explicitly (C, C++, Java).\n"
"-m<mode> : output mode either plain (default), csv, json, jsonl, xml, or raw.\n"
"-n       : output newlines as a special pseudo token.\n"
"-N       : output line continuations as a special pseudo token.\n"
"-o<file> : write output to this file (instead of stdout).\n"
"-r       : suppress newline after each token in raw mode.\n"
"-s       : enable a special start token specifying the filename.\n"
"-1       : treat all filename arguments as a continuous single input.\n"
"-v       : print action summary to stderr.\n"
"-w       : suppress all warning messages.\n"
"-W       : output adjacent white-space as a token.\n",
      stderr);
      return 0;

    case 'j':
      source = set_or_detect_lang("Java");
      explicit_source = 1;
      break;

    case 'k':
      comment_token = 1;
      break;

    case 'l':
       source = set_or_detect_lang(optarg);
       explicit_source = 1;
      break;

    case 'm':
      if (!strcmp(optarg, "plain"))
        mode = PLAIN;
      else if (!strcmp(optarg, "csv"))
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
        mode = PLAIN;
      }
      break;

    case 'n':
      newline_token = 1;
      break;

    case 'N':
      continuation_token = 1;
      break;

    case 'o':
      outfile = optarg;
      break;

    case 'r':
      suppress_newline = 1;
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

    case 'W':
      whitespace_token = 1;
      break;

    case '?':
    default:
      fputs("(F): unknown option. Stop.\n", stderr);
      fprintf(stderr, usage_str, argv[0]);
      return 1;
    }
  }

  if (outfile && outfile[0]) {
    if (!freopen(outfile, append ? "a" : "w", stdout)) {
      fprintf(stderr, "(F): cannot open %s for writing.\n", outfile);
      exit(3);
    }
  }

  if (optind == argc)
    goto doit;

  do {
    filename = argv[optind];
    if (!freopen(filename, "r", stdin)) {
      if (!nowarn)
      fprintf(stderr, "(W): Cannot read file %s.\n", filename);
      continue;
    }

    if (!explicit_source)
      source = set_or_detect_lang(0);

  doit:
    if (verbose) fprintf(stderr, "(I): Processing file %s...\n", filename);
    num_files++;

    // Header:
    switch (mode) {
    case RAW:
      // Maybe prepend with line comment listing filename?
      break;
    case PLAIN:
      if (start_token)
        fprintf(stdout, "(   0,  0) filename: %s\n", filename);
      break;
    case CSV:
      if (!continuous_files || num_files == 1)
        fputs("line,column,class,token\n", stdout);
      if (start_token)
        fprintf(stdout, "0,0,filename,\"%s\"\n", filename);
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
        fprintf(stdout,
                "{ \"line\": 0, \"column\": 0, "
                "\"class\": \"filename\", \"length\": %d, \"token\": \"%s\" }",
                strlen(filename), filename);
        first_time = 0;
      }
      break;
    case XML:
      if (!continuous_files || num_files == 1) {
        fputs("<?xml version='1.0' encoding='UTF-8'?>\n", stdout);
        // standalone='yes'
        fputs("<tokens>\n", stdout);
      }
      if (start_token) {
        fprintf(stdout,
                "<token line='0' column='0' class='filename' length='%d'>",
                strlen(filename));
        XML_escape(stdout, filename);
        fputs("</token>\n", stdout);
      }
      break;
    }

    while ((token_len = C_tokenize_int(&token, &type, &line, &col, &pos))) {
      switch (mode) {
      case RAW:
        fputs(token, stdout);
        if (!suppress_newline) fputc('\n', stdout);
        break;
      case PLAIN:
        fprintf(stdout, "(%4u,%3u;%6u:%3u) %s: %s\n",
		line, col, pos, token_len, token_class[type], token);
        break;
      case CSV:
        // Escape , " in token
        // csvkit treats . as null fields even as ".".
        fprintf(stdout, "%u,%u,%s,", line, col, token_class[type]);
        if (type == STRING ||
            // Do we need this too? Yes!
	    type == CHARACTER && (strchr(token, '"') || strchr(token, ',')) ||
            type == WHITESPACE && strchr(token, '\n') ||
            type == NEWLINE ||
            type == CONTINUATION ||
            comment_token && (type == LINE_COMMENT || type == BLOCK_COMMENT))
          CSV_escape(stdout, token);
        else if (!strcmp(token, ","))
          fputs("\",\"", stdout);
        else
          fputs(token, stdout);
        fputc('\n', stdout);
        break;
      case JSON:
      case JSONL:
        if (first_time)
          first_time = 0;
        else {
          if (mode == JSON) fputc(',', stdout);
          fputc('\n', stdout);
        }
        fprintf(stdout,
                "{ \"line\": %u, \"column\": %u, "
                "\"class\": \"%s\", \"length\": %u, \"token\": \"",
                line, col, token_class[type], token_len);
        // token value is always a JSON string.
        if (type == STRING  || type == CHARACTER ||
            type == NEWLINE || type == WHITESPACE ||
            type == CONTINUATION)
          JSON_escape(stdout, token);
        else
          fputs(token, stdout);
        fputs("\" }", stdout);
        break;
      case XML:
        fprintf(stdout, "<token line='%u' column='%u' class='%s' length='%u'>",
                line, col, token_class[type], token_len);
	if (type == STRING ||
	    type == CHARACTER ||
	    type == OPERATOR ||
	    comment_token && (type == LINE_COMMENT ||
			      type == BLOCK_COMMENT))
          XML_escape(stdout, token);
        else
          fputs(token, stdout);
        fputs("</token>\n", stdout);
        break;
      }
    }

    if (!continuous_files) {
      // Trailer:
      switch (mode) {
      case RAW:
        break;
      case PLAIN:
        break;
      case CSV:
        break;
      case JSON:
        fputs("\n]", stdout);
        /*FALL THROUGH*/
      case JSONL:
        fputc('\n', stdout);
        break;
      case XML:
        fputs("</tokens>\n", stdout);
        break;
      }

      if (verbose)
        fprintf (stderr, "(I): %u bytes, %u UTF-8 encoded chars.\n",
                 char_count, utf8_count);

      // Reset globals:
      char_count = 0;
      utf8_count = 0;
      linenr = 1;
      column = 0;
      buffered = 0;
      saved_col = 0;
      first_time = 1;
    }
  } while (++optind < argc);

  if (continuous_files) {
    // Trailer:
    switch (mode) {
    case RAW:
      break;
    case PLAIN:
      break;
    case CSV:
      break;
    case JSON:
      fputs("\n]", stdout);
      /*FALL THROUGH*/
    case JSONL:
      fputc('\n', stdout);
      break;
    case XML:
      fputs("</tokens>\n", stdout);
      break;
    }

    if (verbose)
      fprintf(stderr, "(I): %u bytes, %u (UTF-8 encoded) unicode characters.\n",
              char_count, utf8_count);
  }

  if (num_files > 1 && verbose)
    fprintf(stderr, "(I): Total number of files processed: %u\n", num_files);

  return (illegals || unexpect_eof) ? 1 : 0;
}
