/* Copyright (c) 2021 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Tokenizer for JavaScript. Based on:
   "Draft ECMA-262 / January 16, 2021, ECMAScript® 2021 Language Specification"
   https://tc39.es/ecma262/#sec-ecmascript-language-lexical-grammar

   See also: https://github.com/mikesamuel/es5-lexer

   Token classes:
   - identifier
   - keyword
   - nullliteral? now keyword
   - booleanliteral? now keyword
   - string
   - template? now string
   - regex
   - integer
   - bigint? now integer
   - floating maybe combine with integer to number?
   - operator

   Restrictions:
   - rudimentatry support for Unicode; input encoding assumed to be UTF-8
     identifiers may contain Unicode but exact ranges are not checked
   - no interpretation of escaped characters and string interpolation

   The method for determination of whether / starts a regex literal or
   is the division operator is borrowed from:
   https://github.com/mikesamuel/es5-lexer/blob/master/src/guess_is_regexp.js
*/

#include <unistd.h>             /* getopt() */
#include <libgen.h>             /* basename() */
#include "token_common.h"

static int start_token = 0;       // when 1 start filename pseudo-token
static int continuous_files = 0;  // when 1 do not reset after each file

/* Includes future reserved keywords, strict mode reserved words and module
   code reserved words, as well as all the older standards future reserved
   words, and the literals null, false, and true.
*/
static const char *keywords[] = {
  "abstract", "await",      "boolean",   "break",        "byte",
  "case",     "catch",      "char",      "class",        "const",
  "continue", "debugger",   "default",   "delete",       "do",
  "double",   "else",       "enum",      "export",       "extends",
  "false",    "final",      "finally",   "float",        "for",
  "function", "goto",       "if",        "implements",   "import",
  "in",       "instanceof", "int",       "interface",    "let",
  "long",     "native",     "new",       "null",         "package",
  "private",  "protected",  "public",    "return",       "short",
  "static",   "super",      "switch",    "synchronized", "this",
  "throw",    "throws",     "transient", "true",         "try",
  "typeof",   "var",        "void",      "volatile",     "while",
  "with",     "yield"
};

static const unsigned num_keywords = sizeof(keywords)/sizeof(keywords[0]);

// All keywords that correctly may precede a regex literal.
static const char *regex_preceders[] = {
  "break", "case", "continue", "delete", "do", "else", "finally",
  "in", "instanceof", "return", "throw", "try", "typeof", "void"
};

static const unsigned num_preceders =
  sizeof(regex_preceders)/sizeof(regex_preceders[0]);

// Global flag to signal token locations at which a regex literal may occur. 
static int regex_ok = 1;

/* Tokenization of JavaScript programming language source text.
   Returns 1 when a next valid token is recognized.
   Then the token is made avaliable in the NUL-terminated string `token`,
   and its token class is indicated via `type` and its start location in the
   source via `line` and `col`.
   Returns 0 upon EOF or error.
*/
static int tokenize(char *token, const char **type,
                    unsigned *line, unsigned *col)
{
  unsigned len;
  int cc;
  *type = "unknown";

  do { // infinite loop; after token recognized breaks out.
    len = 0;
    cc = get();

  restart:
    // cc already read.

    /*** WHITE-SPACE ***/

    while (strchr(" \t\n\r\f\v", cc))
      cc = get();
    // cc !in [ \t\n\r\f\v], maybe EOF
    if (cc == EOF)
      return 0;

    /*** LINE COMMENT AND BLOCK COMMENT ***/

    if (cc == '/') {
      cc = get();
      if (cc == '/') {
        // Skip till end-of-line (\n exclusive):
        while ((cc = get()) != EOF && cc != '\n' && cc != '\r')
          ;
        // cc == '\n' || cc == '\r' || cc == EOF
        if (cc == '\r') {
          if (!nowarn)
            fprintf(stderr,
                    "(W): Unexpected continuation in line comment.\n");
          // Effectively ignore any \ and terminate logical line:
          cc == '\n';
        }
        goto restart;
      }

      if (cc == '*') {
        // Remember start position:
        unsigned lin = linenr;

        // Skip till */ inclusive:
        int nc = get(); // if EOF next get will be EOF too
        do {
          cc = nc;
          nc = get();
          if (nc == EOF) { // Error!
            fprintf(stderr,
                    "(E): [%s:%u] Unexpected end-of-file in /* comment.\n",
                    filename, lin);
            unexpect_eof++;
            return 0;
          }
        } while (cc != '*' || nc != '/');
        // cc == '*' && nc == '/'
        cc = get();
        goto restart;
      }
      // seen / but not // or /*
      unget(cc); // char after /
      cc = '/'; // restore /
    }

    /*** HASHBANG COMMENT (only at absolute beginning of file) ***/

    if (cc == '#' && linenr == 1 && column == 1) {
      cc = get();
      if (cc == '!') {
        // Skip till end-of-line (\n exclusive):
        while ((cc = get()) != EOF && cc != '\n' && cc != '\r')
          ;
        if (cc == '\r') {
          if (!nowarn)
            fprintf(stderr,
                    "(W): Unexpected continuation in hashbang comment.\n");
          // Effectively ignore any \ and terminate logical line:
          cc == '\n';
        }
        goto restart;
      }
      // seen # but not #!
      unget(cc);
      cc = '#';
    }

    // Start collecting a token.
    // Token should finish with cc being last char of token!
    *line = linenr;
    *col  = column-1; // 1 char lookahead

#if 0
    /*** ANY (test only) ***/
    while (!strchr(" \t\n\r\f\v#", cc)) {
      token_add(cc);
      cc = get();
    }
    *type = "any";
    break;
#endif

    /*** REGULAR EXPRESSION LITERAL ***/

    /* Tricky to recognize a regular expression literal.
       We use a reasonable heuristic.
       Can occur as first token and after these (complete) tokens:

       break case continue delete do else finally
       in instanceof return throw try typeof void
       + - . / , *

       or after token with last character one of:

       ! % & ( : ; < = > ? [ ^ { | } ~
    */
    if (cc == '/' && regex_ok) { // Note: // already recognized
      // /non-empty body/flags: gimsuy
      int pc;
      do {
        token_add(cc);
        pc = cc;
        cc = get();
        if (cc == '\r') {
          if (!nowarn)
            fprintf(stderr,
                    "(W): Unexpected continuation in regex literal.\n");
          // Effectively ignore:
          cc = get();
        }

        if (cc == '\n') {
          if (!nowarn)
            fprintf(stderr,
                    "(W): Unexpected newline in regular expression literal.\n");
          // discard:
          cc = get();     
        }

        if (cc == EOF) {
          if (!nowarn)
            fprintf(stderr,
                    "(W): Unexpected EOF in regular expression literal.\n");
          unexpect_eof++;
          break;
        }
      } while (cc != '/' || pc == '\\');
      token_add(cc); // the /
      cc = get();
      while (strchr("gimsuy", cc)) {
        token_add(cc);
        cc = get();
      }
      unget(cc);
      *type = "regex";
      regex_ok = 0;
      break;
    }

    regex_ok = 0;

    /*** STRING LITERAL / TEMPLATE LITERAL ***/

    if (cc == '\'' || cc == '"' || cc == '`') { // a first, starting quote
      int qc = cc;
      token_add(cc);
      if ((cc = get()) == qc) { // a second qc
        token_add(cc);
        // qc qc: empty string
        *type = "string";
        break;
      }

      // string, cc != qc
      // start string contents
      int pc = '\0';
      int nesting = 0; // keep track of ${} nesting
      do {
        token_add(cc);
        // For template can have nesting inside placeholder ${...}
        // FIXME: no check for nested paired ``; same for {}
        if (qc == '`') {
          if (pc == '$' && cc == '{')
            nesting++;
          else
          if (cc == '}')
            nesting--;
        }

        // Assume \ is not escaped itself.
        if (pc != '\\' && cc == qc && !nesting) { // unescaped quote
          *type = "string";
          break;
        }
        pc = cc;
        cc = get();

        while (cc == '\r') // explicit line continuation
          // discard
          cc = get();

        if (cc == '\n' && qc != '`') { // Ok in template
          if (!nowarn)
            fprintf(stderr,
                    "(W): Unexpected unescaped newline in string.\n");
          // discard
          cc = get();
        }

        if (cc == EOF) {
          if (!nowarn)
            fprintf(stderr,
                    "(W): Unexpected EOF in string/template.\n");
          unexpect_eof++;
          break;
        }
      } while (1);
      break;
    }

    /*** IDENTIFIER and KEYWORD ***/

    // Simplistic solution to allowing Unicode: allow any char >= 128 without
    // actual checking for UTF-8.
    if (isalpha(cc) || cc == '_' || cc == '$' || cc & 0x80) {
      token_add(cc);
    ident_token:
      while (isalnum(cc = get()) || cc == '_' || cc == '$' || cc & 0x80)
        token_add(cc);
      unget(cc);
      token[len] = '\0';
      if (is_keyword(token, keywords, num_keywords)) {
        *type = "keyword";
        regex_ok = !!is_keyword(token, regex_preceders, num_preceders);
      }
      else
        *type = "identifier";
      break;
    }

    /*** INTEGER and FLOATING ***/

    // . digits ... floating
    if (cc == '.') {
      // Look ahead for a digit:
      int nc = get();
      unget(nc);
      if (isdigit(nc))
        goto start_fraction;
      // Could go immediately to operator: goto seen_period
    }

    if (isdigit(cc)) { // binary, octal, decimal, or hexadecimal literal
      // Types of integer literals:
      // legacy octal: 0777 instead of 0o777
      enum {
        BIN, LEGACY_OCT, OCT, DEC, HEX
      } int_lit = DEC; // assume decimal number

      /* BIN: 0[bB][01](_?[01])*
         LEGACY_OCT: 0[0-7]+
         OCT: 0[oO][0-7](_?[0-7])*
         DEC: 0|[1-9](_?[0-9])*
         HEX: 0[xX][0-9a-fA-F](_?[0-9a-fA-F])*

         EXP: [eE][+-]?[0-9](_?[0-9])*

         FLOATING: .[0-9][_0-9]*EXP?
                 | DEC.([0-9][_0-9]*)?EXP?
                 | DEC EXP
       */

      if (cc == '0') {
        int nc = get();
        switch (nc) {
        case 'b': case 'B':
          token_add(cc); // the 0
          int_lit = BIN;
          break;
        case 'o': case 'O':
          token_add(cc); // the 0
          int_lit = OCT;
          break;
        case 'x': case 'X':
          token_add(cc); // the 0
          int_lit = HEX;
          break;
        default:
          if ('0' <= nc && nc <= '7') {
            token_add(cc); // the 0
            int_lit = LEGACY_OCT;
          }
          else {
            unget(nc);
            nc = cc;
          }
          break;
        }
        cc = nc;
      }
      //else: cc in [1-9]

      do {
        token_add(cc); // [0-9bBoOxX]
        cc = get();
        // FIXME: for non-DEC need at least 1 digit!
        // Allow for _ between `digits':
        if (cc == '_') {
          // Keep the _ in the token for now:
          token_add(cc);
          cc = get();
          // FIXME: this must be a digit! cannot have trailing _
        }
      } while (isdigit(cc) || int_lit == HEX && isxdigit(cc));
      // !is[x]digit(cc)

      if (int_lit == DEC) {
        int floating = 0;
        // Seen digits-sequence. Maybe followed by . or e or E?
        if (cc == '.') { // fractional part
        start_fraction:
          floating = 1;
          token_add(cc); // the .

          // digit (_? digit)*
          cc = get();
          if (isdigit(cc)) {
            do {
              token_add(cc);
              cc = get();
              if (cc == '_') {
                token_add(cc);
                cc = get();
                // FIXME: must be a digit
              }
            } while (isdigit(cc));
          }
          //else: FIXME: error
          // !isdigit(cc)
        }
        // cc != '.' || !isdigit(cc)
        if (cc == 'e' || cc == 'E') { // exponent
          // FIXME: no check for at least 1 prior digit
          floating = 1;
          token_add(cc); // the e or E
          if ((cc = get()) == '-' || cc == '+') {
            token_add(cc);
            cc = get();
          }

          // digit (_? digit)*
          if (isdigit(cc)) {
            do {
              token_add(cc);
              cc = get();
              if (cc == '_') {
                token_add(cc);
                cc = get();
                // FIXME: must be a digit
              }
            } while (isdigit(cc));
          }
          //else: FIXME: error
          // !isdigit(cc)
        }

        if (floating) {
          unget(cc);
          *type = "floating";
          break;
        }
      }

      if (cc == 'n') // BigInt
        token_add(cc);
      else
        unget(cc);

      *type = "integer";
      break;
    }

    /*** OPERATOR, PUNCTUATOR ***/

    /*
      1 definitely single char:
      ( ) [ ] { } , ; ~ :
      + - * / % & | ^ < > . = ! ?
      2 doublets, assignment
      ** ++ -- << >> && || ??
      <= >= == != += -= *= %= &= |= ^= /=
      => ?.
      3 triples
      ... === >>>
      **= <<= >>= &&= ||= ??=
      !==
      4 quadruple
      >>>=
    */

    if (strchr("()[]{},;~:", cc)) { // single char operator
      token_add(cc);
      *type = "operator";
      break;
    }

    if (strchr("+-*/%&|^<>.=!?", cc)) { // single or start of double/triple
      int c2 = get();
      token_add(cc);
      if (strchr("*+-<>&|?.=", cc) && c2 == cc) { // double or triple
        // ** ++ -- << >> && || ?? .. ==

        // special case ++ and --
        if (c2 == '+' || c2 == '-') {
            token_add(c2);
            *type = "operator";
            break;
        }

        // ** << >> && || ?? .. ==
        int c3 = get();

        // special case . and ...
        if (c2 == '.') {
          if (c3 == '.') {
            // ...
            token_add(c2);
            token_add(c3);
          }
          else {
            // ..x
            unget(c3);
            unget(c2);
          }
          // .
          *type = "operator";
          break;
        }

        // ** << >> && || ?? ==
        token_add(c2);
        if (c3 == '=') {
          // **= <<= >>= &&= ||= ??= ===
          token_add(c3);
          *type = "operator";
          break;
        }

        // ** << >> && || ?? ==

        if (c2 == '>' && c3 == c2) {
          // >>>
          int c4 = get();
          token_add(c3);
          if (c4 == '=')
            // >>>=
            token_add(c4);
          else
            unget(c4);
        }
        else
          unget(c3);

        // ** << >> && || ?? ==
        *type = "operator";
        break;
      }
      // cc !in [*+-<>&|?.=] || c2 != cc

      // also missing => ?. !== <= >= == != += -= *= %= &= |= ^= /=

      if (cc == '?' && c2 == '.' ||
          cc == '=' && c2 == '>') {
        // ?. =>
        token_add(c2);
        *type = "operator";
        break;
      }

      // still missing !== <= >= == != += -= *= %= &= |= ^= /=

      if (c2 == '=') {
        // <= >= == != += -= *= %= &= |= ^= /=
        token_add(c2);
        if (cc == '!') {
          // !=
          int c3 = get();
          if (c3 == '=')
            // !==
            token_add(c3);
          else
            unget(c3);
        }
      }
      else
        unget(c2);
      *type = "operator";
      break;
    }

    /*** ILLEGAL ***/

    if (!nowarn)
      // Mind non-printing chars!
      fprintf(stderr,
              "(W): [%s:%u] Illegal character `%s%c` (0x%02x) skipped.\n",
              filename, linenr, cc<32?"CTRL-":"", cc<32?cc+64:cc, cc);
    // Count them:
    illegals++;

  } while(1);

  // len <= MAX_TOKEN; close:
  token[len] = '\0';

  if (!strcmp(*type, "operator"))
    regex_ok = len == 1 && strchr("+-./,*", token[0])
      || strchr("!%&(:;<=>?[^{|}~", token[len-1]);

  return 1;
}

// Escape token for output as CSV string.
static void CSV_escape(FILE *out, const char *token)
{
  const char *p;
  // start CSV string:
  fputc('"', out);
  for (p = token; *p; p++) {
    if (*p == '\n') {
      fputs("\\n", out);
      continue;
    }
    if (*p == '"')
      fputc('"', out);
    fputc(*p, out);
  }
  // end CSV string:
  fputc('"', out);
}

// Escape token for output as JSON string.
static void JSON_escape(FILE *out, const char *token)
{
  // To preserve, simply escape the escape and all ":
  const char *p;
  for (p = token; *p; p++) {
    if (*p == '\n') {
      fputs("\\n", out);
      continue;
    }
    if (*p == '\\' || *p == '"')
      fputc('\\', out);
    fputc(*p, out);
  }
}

// Escape token for output as XML text.
static void XML_escape(FILE *out, const char *token)
{
#if 1
  // Alternative: escape every <, >, and &:
  const char *p;
  for (p = token; *p; p++) {
    if (*p == '<')
      fputs("&lt;", out);
    else
    if (*p == '>')
      fputs("&gt;", out);
    else
    if (*p == '&')
      fputs("&amp;", out);
    else
      fputc(*p, out);
  }
#else
  // User CDATA construct for escaping.
  // Impossible to escape ]]> occurring in token!
  // Must chop up the substring ]]> in ]] and >.
  const char *p;
  const char *q = token;
  // "abc]]>hello" => <![CDATA["abc]]]]><![CDATA[>hello"]]>
  // "]]>]]>" => <![CDATA[]]]]><!CDATA[>]]]]><![CDATA[>"]]>
  while ((p = strstr(q, "]]>"))) {
    int len = p - q; // always > 0
    fputs("<![CDATA[", out);
    fwrite(q, 1, len, out);
    fputs("]]]]>", out);
    q = p+2; // q start at >...
  }
  if (q < token+strlen(token))
    fprintf(out, "<![CDATA[%s]]>", q);
#endif
}

int main(int argc, char *argv[])
{
  extern char *optarg;
  extern int opterr;
  extern int optind;
  int option;
  char const *opt_str = "1dhm:o:svw";
  char usage_str[80];

  char token[MAX_TOKEN+1];
  const char *type;
  unsigned line;
  unsigned col;

  char *outfile = 0;
  enum { PLAIN, CSV, JSON, JSONL, XML, RAW } mode = PLAIN;
  int first_time = 1;

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
"A tokenizer for JavaScript source code with output in 6 formats.\n"
"Recognizes the following token classes: keyword, identifier, integer,\n"
"floating, string, regex, and operator.\n\n", stderr);
fprintf(stderr, usage_str, basename(argv[0]));
fputs(
"\nCommand line options are:\n"
"-d       : print debug info to stderr; implies -v.\n"
"-h       : print just this text to stderr and stop.\n"
"-m<mode> : output mode either plain (default), csv, json, jsonl, xml, or raw.\n"
"-o<file> : name for output file (instead of stdout).\n"
"-s       : enable a special start token specifying the filename.\n"
"-1       : treat all filename arguments as a continuous single input.\n"
"-v       : print action summary to stderr.\n"
"-w       : suppress all warning messages.\n",
      stderr);
      return 0;

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
    if (!freopen(filename, "r", stdin)) {
      if (!nowarn)
      fprintf(stderr, "(W): Cannot read file %s.\n", filename);
      continue;
    }

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
                "\"class\": \"filename\", \"token\": \"%s\" }",
                filename);
        first_time = 0;
      }
      break;
    case XML:
      if (!continuous_files || num_files == 1) {
        fputs("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n", stdout);
        // standalone="yes"
        fputs("<tokens>\n", stdout);
      }
      if (start_token) {
        fprintf(stdout, "<token line=\"0\" column=\"0\" class=\"filename\">");
        XML_escape(stdout, filename);
        fputs("</token>\n", stdout);
      }
      break;
    }

    while (tokenize(token, &type, &line, &col)) {
      switch (mode) {
      case RAW:
        fputs(token, stdout);
        fputc('\n', stdout);
        break;
      case PLAIN:
        fprintf(stdout, "(%4u,%3u) %s: %s\n", line, col, type, token);
        break;
      case CSV:
        // Escape , " in token
        // csvkit treats . as null fields even as ".".
        fprintf(stdout, "%u,%u,%s,", line, col, type);
        if (!strcmp(type, "string"))
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
                "\"class\": \"%s\", \"token\": \"",
                line, col, type);
        // token value is always a JSON string.
        if (!strcmp(type, "string"))
          JSON_escape(stdout, token);
        else
          fputs(token, stdout);
        fputs("\" }", stdout);
        break;
      case XML:
        fprintf(stdout, "<token line=\"%u\" column=\"%u\" class=\"%s\">",
                line, col, type);
        if (!strcmp(type, "string") || !strcmp(type, "operator"))
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
