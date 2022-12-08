/* Copyright (c) 2021, 2022 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Tokenizer for C, C++ and Java with output as annotated XML,
   much like srcML annotates a parse tree. Any white-space (including
   newlines) is output as is, without any special XML element.
   All other tokens (even comments) are output as a stream of XML
   elements with tag names indicating the type/kind/class of
   token provided as the enclosed text node.

   <?xml version='1.0' encoding='UTF-8'?>
   <source language='' filename=''>
   <@kind@ line='' col='' len=''>...</@kind@>
   </source>

   Note that end-of-line characters (\r, \n) and sequences (\r \n) are
   normalized and will always be output as a LINEFEED (LF, 0x0A).

   The characters <, >, and & will be replaced by the special XML entities
   &lt;, &gt; and &amp; respectively.

   To undo the XML annotation in <file>.xml use either:
   (this will also correctly revert the XML entities)
   xmlstarlet sel -T -t -v 'source' <file>.xml, or
   xidel -s -e 'source' <file>.xml

   Useful xpath queries:
   (the results show all occurrences and these are not necessarily unique)
   - all identifiers: //identifier
   - the length of the last identifier: //identifier[last()]/@len
   - the value of the first integer: //integer[1]
   - all comments starting at the beginning of a line:
     //line_comment[@col=0]|//block_comment[@col=0]
   - all while keywords: /keyword[text()="while"]
   - identifiers of length greater than 10: //identifier[@len>10]
   - tokens immediately following a long identifier:
     //identifier[@len>15]/following-sibling::*[1]
   - tokens immediately following the keyword static:
     //keyword[text()="static"]/following-sibling::*[1]
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
  char const *opt_str = "1acdhl:o:rvw";
  char usage_str[80];

  const char *token;
  enum TokenClass type;
  unsigned line;
  unsigned col;
  unsigned pos;
  unsigned token_len;
  unsigned num_files = 0;    // number of files read
  int continuous_files = 0;  // when 1 do not reset after each file

  char *outfile = 0;
  Language source;
  int explicit_source = 0;
  int append = 0;

  comment_token = 1;
  whitespace_token = 1;

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
"A tokenizer for C/C++ (and Java) source code with output in XML.\n"
"Recognizes the following token classes: keyword, identifier, integer,\n"
"floating, string, character, operator, preprocessor, line_comment,\n"
"and block_comment.\n\n", stderr);
fprintf(stderr, usage_str, basename(argv[0]));
fputs(
"\nCommand line options are:\n"
"-a       : append to output file instead of create or overwrite.\n"
"-c       : treat a # character as the start of a line comment.\n"
"-d       : print debug info to stderr; implies -v.\n"
"-h       : print just this text to stderr and stop.\n"
"-l<lang> : specify language explicitly (C, C++, Java).\n"
"-o<file> : write output to this file (instead of stdout).\n"
"-1       : treat all filename arguments as a continuous single input.\n"
"-v       : print action summary to stderr.\n"
"-w       : suppress all warning messages.\n",
      stderr);
      return 0;

    case 'l':
       source = set_or_detect_lang(optarg);
       explicit_source = 1;
      break;

    case 'o':
      outfile = optarg;
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
    if (!continuous_files || num_files == 1) {
      fputs("<?xml version='1.0' encoding='UTF-8'?>\n", stdout);
      // standalone="yes"
      fprintf(stdout, "<source language='%s' filename='%s'>",
	      lang_name(source), filename);
    }

    while ((token_len = C_tokenize_int(&token, &type, &line, &col, &pos))) {
      if (type == WHITESPACE) {
	fputs(token, stdout);
	continue;
      }
      fprintf(stdout, "<%s line='%u' col='%u' len='%u'>",
	      token_class[type], line, col, token_len);
      if (type == STRING ||
	  type == CHARACTER ||
	  type == OPERATOR ||
	  type == LINE_COMMENT ||
	  type == BLOCK_COMMENT)
	XML_escape(stdout, token);
      else
	fputs(token, stdout);
      fprintf(stdout, "</%s>", token_class[type]);
    }

    if (!continuous_files) {
      // Trailer:
      fputs("</source>\n", stdout);

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
    }
  } while (++optind < argc);

  if (continuous_files) {
    // Trailer:
    fputs("</source>\n", stdout);

    if (verbose)
      fprintf(stderr, "(I): %u bytes, %u (UTF-8 encoded) unicode characters.\n",
              char_count, utf8_count);
  }

  if (num_files > 1 && verbose)
    fprintf(stderr, "(I): Total number of files processed: %u\n", num_files);

  return (illegals || unexpect_eof) ? 1 : 0;
}
