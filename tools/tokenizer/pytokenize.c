/* Copyright (c) 2021 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Tokenizer for Python 3.x

   Token classes:
   - identifier
   - keyword
   - string
   - integer
   - floating
   - imaginary
   - operator
   - filename pseudo token only when so requested
   - layout pseudo tokens (NEWLINE, INDENT, DEDENT) only when so requested

   Restrictions:
   - rudimentatry support for Unicode; input encoding assumed to be UTF-8
     identifiers may contain Unicode but exact ranges are not checked
   - no interpretation of string prefixes and escaped characters
     except for raw mode
   - bytes and string literals treated equally

   See also:
   https://github.com/antlr/grammars-v4/blob/master/python/python/PythonLexer.g4
   https://docs.python.org/3/reference/lexical_analysis.html
*/

#include <unistd.h>             /* getopt() */
#include <libgen.h>             /* basename() */
#include "token_common.h"

// Program globals:
static unsigned brackets_opened = 0; // unpaired nested ( [ { seen
static int prev_was_newline = 1;     // no previous token or was newline
static int first_time = 1;	     // control add , for JSON and JSONL

// Program option settings:
static int start_token = 0;       // when 1 start filename pseudo-token
static int continuous_files = 0;  // when 1 do not reset after each file
static enum { PLAIN, CSV, JSON, JSONL, XML, RAW } mode = PLAIN;
static int output_layout = 0;     // when 1 output layout pseudo tokens

static const char *keywords[] = {
  "False",  "None",   "True",    "and",      "as",       "assert", "async",
  "await",  "break",  "class",   "continue", "def",      "del",    "elif",
  "else",   "except", "finally", "for",      "from",     "global", "if",
  "import", "in",     "is",      "lambda",   "nonlocal", "not",    "or",
  "pass",   "raise",  "return",  "try",      "while",    "with",   "yield"
};

static const unsigned num_keywords = sizeof(keywords)/sizeof(keywords[0]);

static void emit(const char *s, unsigned line, unsigned col)
{
  if (output_layout) {
    switch (mode) {
    case RAW:
      fprintf(stdout, "#%s#\n", s);
      break;
    case PLAIN:
      fprintf(stdout, "(%4u,%3u) layout: %s\n", line, col, s);
      break;
    case CSV:
      fprintf(stdout, "%u,%u,layout,%s\n", line, col, s);
      break;
    case JSON:
    case JSONL:
      if (first_time)
        first_time = 0;
      else {
        if (mode == JSON) fputc(',', stdout);
        fputc('\n', stdout);
      }
      fprintf(stdout, "{ \"line\": %u, \"column\": %u, "
              "\"class\": \"layout\", \"token\": \"%s\" }", line, col, s);
      break;
    case XML:
      fprintf(stdout,
              "<token line=\"%u\" column=\"%u\" class=\"layout\">%s</token>\n",
              line, col, s);
      break;
    }
  }
}

// Fixed size stack of indentations; hard check for overflow!
#define MAX_INDENTS 128
static unsigned indents[MAX_INDENTS];
static unsigned *sp = indents;
#define indents_reset() do { sp = indents; } while(0)
#define indents_empty() (sp == indents)
#define indents_full()  (sp == indents+MAX_INDENTS)
#define indents_top()   (indents_empty() ? 0 : *(sp-1))
#define indents_push(i) do { assert(!indents_full()); *sp++ = (i); } while(0)
#define indents_pop()   do { assert(!indents_empty()); sp--; } while(0)

// emit NEWLINE and deal with indentation
static void process_newline(unsigned indent)
{
  emit("NEWLINE", linenr-1, saved_col);

  unsigned last_indent = indents_top(); // maybe 0

  if (indent > last_indent) {
    indents_push(indent);
    emit("INDENT", linenr, column-1);
    // Here: !empty() && top() == indent
  }
  else
  if (indent < last_indent) {
    // Here: indent < last_indent => !empty() && indent < top()
    do {
      emit("DEDENT", linenr, column ? column-1 : 0);
      indents_pop();
    } while (indent < indents_top());
    // Here: empty() || indent >= top()
    if (indent > indents_top() && !nowarn)
      fprintf(stderr, "(W): Incorrect indentation.\n");
  }
  // else: indent == last_indent: no action
}

// cc in [ \t\f]
static int process_ws(int cc)
{
  // Collect white-space and compute possible indentation:
  unsigned indent = 0;
  do {
    if (cc != '\f') // \f not considered part of indentation
      indent += cc == '\t' ? 8 - (indent & 0x07) : 1;
    cc = get();
  } while (strchr(" \t\f", cc));

  // Test whether indentation is significant:
  if (prev_was_newline && !brackets_opened && !strchr("\n#\r", cc))
    process_newline(indent);

  return cc;
}

/* Assume input is UTF-8 encoded Unicode code points.
   Will read 1 code point and return that as int.
   The number of bytes read is len and they are put in the bytes buffer.
   EOF is never counted as such and will not appear in bytes.
   Returns EOF upon end-of-file otherwise the Unicode code point.
*/
static int utf8_codepoint(int cc, int *len, int bytes[4])
{
  *len = 0;
  if (cc == EOF)
    return EOF;
  /* cc must be single byte: */
  assert((cc & 0xFFFFFF00) == 0);
  bytes[(*len)++] = cc;
  if (cc < 0x80) /* ASCII */
    return cc;
  /* cc = 0b1xxxxxxx */
  int cp, n;
  if ((cc & 0xE0) == 0xC0) { /* cc = 0b110xxxxx */
    n = 2;
    cp = cc & 0x1F; /* 5 bits */
  }
  else if ((cc & 0xF0) == 0xE0) { /* cc = 0b1110xxxx */
    n = 3;
    cp = cc & 0x0F; /* 4 bits */
  }
  else if ((cc & 0xF8) == 0xF0) { /* cc = 0b11110xxx */
    n = 4;
    cp = cc & 0x07; /* 3 bits */
  } 
  else { /* invalid utf-8 start byte */
    if (!nowarn)
      fprintf(stderr, "(W): [%s:%u] Invalid UTF-8 start byte 0x%02x.\n",
              filename, linenr, cc);
    return cc;
  }
  /* collect all follow bytes: */
  while (--n) { /* at most 3 iterations */
    cc = get();
    if (cc == EOF) { /* unexpected EOF in utf-8 sequence */
      if (!nowarn)
        fprintf(stderr, "(W): [%s:%u] Unexpected EOF in UTF-8 sequence.\n",
                filename, linenr);
      return EOF;
    }
    bytes[(*len)++] = cc;
    if ((cc & 0xC0) != 0x80) { /* invalid utf-8 follow byte */
      if (!nowarn)
        fprintf(stderr, "(W): [%s:%u] Invalid UTF-8 follow byte 0x%02x.\n",
                filename, linenr, cc);
      return cc;
    }
    cp <<= 6;
    cp |= (cc & 0x3F); /* 6 bits */
  }
  /* check for validness; not in surrogate range, etc. */
  if (cp >= 0xD800 && cp <= 0xDFFF ||
      cp > 0x10FFFF || cp == 0xFFFE || cp == 0xFFFF) {
    /* invalid Unicode code point. */
    if (!nowarn)
      fprintf(stderr, "(W): [%s:%u] Invalid Unicode code point 0x%04x.\n",
              filename, linenr, cp);
  }
  return cp;
}

static int is_id_start(int cp, int utf8_len)
{
  if (utf8_len == 1 && isalpha(cp) || cp == '_' || utf8_len > 1)
    return 1;
  return 0;
}

static int is_id_follow(int cp, int utf8_len)
{
  if (utf8_len == 1 && isalnum(cp) || cp == '_' || utf8_len > 1)
    return 1;
  return 0;
}

/* Tokenization of Python programming language source text.
   Returns 1 when a next valid token is recognized.
   Then the token is made avaliable in the NUL-terminated string `token`,
   and its token class is indicated via `type` and its location in the
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

    /* Can have [ \t\f]* inbetween tokens.
       May have indentation \f?[ \t]* at beginning of logical line.
       Tokens (except strings) cannot extend beyond a physical line
       and may not be interrupted by a line continuation.

       \n signals completion of a logical line
       \r signals a line joiner and generally will be ignored
       blank lines do not generate NEWLINE tokens
    */

    if (strchr(" \t\f", cc)) {
      cc = process_ws(cc);
      goto restart;
    }

    if (cc == '\n') {
      prev_was_newline = 1;
      cc = get();
      // Maybe EOF!
      if (!brackets_opened && !strchr(" \t\n#\r\f", cc))
        process_newline(0);
      goto restart;
    }

    if (cc == '\r') {
      cc = get();
      goto restart;
    }

    // cc !in [ \t\n\r\f], maybe EOF
    if (cc == EOF) {
      // Undo any outstanding indents:
      while (!indents_empty()) {
        emit("DEDENT", linenr, column);
        indents_pop();
      }
      return 0;
    }

    /*** LINE COMMENT ***/

    if (cc == '#') {
      // Skip till end-of-line (\n exclusive):
      while ((cc = get()) != EOF && cc != '\n' && cc != '\r')
        ;
      // cc == '\n' || cc == '\r' || cc == EOF
      if (cc == '\r') {
	// presumably a \ may occur in a comment as last char before \n
        /*
	  if (!nowarn)
	  fprintf(stderr, "(W): Comment may not be continued with \\.\n");
	*/
        // Effectively ignore any \ and terminate logical line:
        cc == '\n';
      }
      goto restart;
    }

    // Start collecting a token.
    // Token should finish with cc being last char of token!
    *line = linenr;
    *col  = column-1; // 1 char lookahead

#if 0
    /*** ANY (test only) ***/
    while (!strchr(" \t\n\r\f#", cc)) {
      token_add(cc);
      cc = get();
    }
    *type = "any";
    break;
#endif

    /*** STRING PREFIX ***/
    // No distinction between bytes and string literals!

    int raw = 0;
    int lc = tolower(cc);
    if (strchr("bufr", lc)) { // [bBuUfFrR]
      token_add(cc);
      raw = lc == 'r';
      cc = get();
      if (cc == '\'' || cc == '"') // [bBuUrRfF]['"]
        goto string_token;

      if (lc == 'b' || lc == 'f') { // [bBfF]
        if (cc == 'r' || cc == 'R') { // [bBfF][rR]
          token_add(cc);
          cc = get();
          if (cc == '\'' || cc == '"') // [bBfF][rR]['"]
            goto string_token;
          // [bBfF][rR] first 2 chars of identifier
        }
        //else: [bBfF] first char of identifier
      }
      else
      if (lc == 'r') {
        if (cc == 'b' || cc == 'B' || cc == 'f' || cc == 'F') { // [rR][bBfF]
          token_add(cc);
          cc = get();
          if (cc == '\'' || cc == '"') // [rR][bBfF]['"]
            goto string_token;
          // [rR][bBfF] first 2 chars of identifier
        }
        //else: [rR] first char of identifier
      }
      //else: [uU] first char of identifier
      unget(cc);
      goto ident_token;
    }

    /*** STRING and BYTES LITERAL ***/

    // Backticks are a deprecated alias for repr(); removed in 3.0

    if (cc == '\'' || cc == '"' || cc == '`') { // a first, starting quote
      int qc;
    string_token:
      token_add(cc);
      // Check for 3 in a row:
      qc = cc;
      if ((cc = get()) == qc) { // a second qc
        int q3 = get();
        token_add(cc);
        if (q3 == qc) { // and a third one
          token_add(q3);
          // start long string contents
          do {
            int pc = cc;
            cc = get();

            while (cc == '\r') { // explicit line continuation
              if (raw) {
                token_add('\\'); token_add('\n');
              }
              //else discard
              cc = get();
            }
            if (cc == EOF) {
              if (!nowarn)
              fprintf(stderr, "(W): Unexpected EOF in long string.\n");
              unexpect_eof++;
              break;
            }

            token_add(cc);
            // Assume \ is not escaped itself. Happens though!
            if (pc == '\\') // escape next char; no check
              cc = '\0';
            else
            if (cc == qc) { // a first unescaped quote
              int q2 = get();
              token_add(q2);
              if (q2 == qc) { // a second quote
                int q3 = get();
                token_add(q3);
                if (q3 == qc) { // a third one
                  *type = "string";
                  break;
                }
                // qc qc but not a third one
                cc = q3;
              }
              else // qc but not a second one
                cc = q2;
            }
          } while (1);
          break;
        }
        // qc qc: empty short string
        *type = "string";
        // undo lookahead of q3:
        unget(q3);
        break;
      }
      // short string, cc != qc
      // start short string contents
      int pc = '\0';
      do {
        token_add(cc);
        if (pc == '\\') // escape next char; no check
          cc = '\0';
        else
        if (cc == qc) { // unescaped quote
          *type = "string";
          break;
        }
        pc = cc;
        cc = get();

        while (cc == '\r') { // explicit line continuation
          if (raw) {
            token_add('\\'); token_add('\n');
          }
          //else discard
          cc = get();
        }
        if (cc == EOF) {
          if (!nowarn)
          fprintf(stderr,
          "(W): Unexpected EOF or unescaped newline in short string.\n");
          unexpect_eof++;
          break;
        }
      } while (1);
      break;
    }

    /*** IDENTIFIER and KEYWORD ***/
    int utf8_len;
    int utf8_bytes[4];
    int all_ascii = 1;

    int cp = utf8_codepoint(cc, &utf8_len, utf8_bytes);
    if (cp == EOF) // bad code point; already reported.
      break;
    // 1 <= utf8_len <= 4
    all_ascii = utf8_len == 1;
    if (is_id_start(cp, utf8_len)) {
      int i;
      for (i = 0; i < utf8_len; i++)
        token_add(utf8_bytes[i]);
    ident_token:
      cc = get();
      cp = utf8_codepoint(cc, &utf8_len, utf8_bytes);
      if (cp == EOF) // bad code point; already reported.
        break;
      all_ascii &= utf8_len == 1;
      while (is_id_follow(cp, utf8_len)) {
        int i;
        for (i = 0; i < utf8_len; i++)
          token_add(utf8_bytes[i]);
        cc = get();
        cp = utf8_codepoint(cc, &utf8_len, utf8_bytes);
        if (cp == EOF) // bad code point; already reported.
          break;
        all_ascii &= utf8_len == 1;
      }
      // Undo look ahead:
      while (utf8_len)
        unget(utf8_bytes[--utf8_len]);
      token[len] = '\0';
      *type = all_ascii && is_keyword(token, keywords, num_keywords)
        ? "keyword" : "identifier";
      break;
    }

    /*** INTEGER and FLOATING and IMAGINARY ***/

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
      enum {
        BIN, OCT, DEC, HEX
      } int_lit = DEC; // assume decimal number

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
          unget(nc);
          nc = cc;
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

        if (cc == 'j' || cc == 'J') { // imaginary number
          token_add(cc);
          *type = "imaginary";
          break;
        }

        if (floating) {
          unget(cc);
          *type = "floating";
          break;
        }
      }
      unget(cc);
      *type = "integer";
      break;
    }

    /*** OPERATOR ***/

    if (strchr("([{", cc)) { // opening brackets
      // Keep track of nesting bracket levels:
      brackets_opened++;
      token_add(cc);
      *type = "operator";
      break;
    }

    if (strchr(")]}", cc)) { // closing brackets
      // Keep track of nesting bracket levels:
      if (brackets_opened) brackets_opened--;
      token_add(cc);
      *type = "operator";
      break;
    }

    if (strchr(",;~", cc)) { // single char operator/delimiter
      token_add(cc);
      *type = "operator";
      break;
    }

    if (strchr("+-*/%@&|^<>:.=!", cc)) { // single or start of double/triple
      int c2 = get();
      token_add(cc);
      if (strchr("/*<>.", cc) && c2 == cc) { // double or triple
        // // ** << >> ..
        int c3 = get();
        if (c2 == '.') {
          if (c3 == '.') {
            // ...
            token_add(c2);
            token_add(c3);
            *type = "operator";
            break;
          }
          // ..x
          unget(c3);
          unget(c2);
          // .
          *type = "operator";
          break;
        }
        // c2 in [/*<>]
        token_add(c2);
        if (c3 == '=') {
          // //= **= <<= >>=
          token_add(c3);
          *type = "operator";
          break;
        }
        // // ** << >>
        unget(c3);
        *type = "operator";
        break;
      }
      // cc !in [/*<>.] || c2 != cc

      // all triples dealt with; these doubles // ** << >> and .

      if (cc == '-' && c2 == '>') {
        // ->
        token_add(c2);
        *type = "operator";
        break;
      }

      if (c2 == '=') {
        // += -= *= /= %= @= &= |= ^= <= >= := == !=
        token_add(c2);
        *type = "operator";
        break;
      }

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
  prev_was_newline = 0;
  return 1;
}

// Escape hard newlines in a string.
static void RAW_escape(FILE *out, const char *token)
{
  const char *p;
  for (p = token; *p; p++) {
    if (*p == '\n') {
      fputs("\\n", out);
      continue;
    }
    fputc(*p, out);
  }
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
  char const *opt_str = "1dhlm:o:svw";
  char usage_str[80];

  char token[MAX_TOKEN+1];
  const char *type;
  unsigned line;
  unsigned col;

  char *outfile = 0;

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
"A tokenizer for Python (3) source code with output in 6 formats.\n"
"Recognizes the following token classes: keyword, identifier, integer,\n"
"floating, imaginary, string, and operator.\n\n", stderr);
fprintf(stderr, usage_str, basename(argv[0]));
fputs(
"\nCommand line options are:\n"
"-d       : print debug info to stderr; implies -v.\n"
"-h       : print just this text to stderr and stop.\n"
"-l       : output layout pseudo tokens (default don't).\n"
"-m<mode> : output mode either plain (default), csv, json, jsonl, xml, or raw.\n"
"-o<file> : name for output file (instead of stdout).\n"
"-s       : enable a special start token specifying the filename.\n"
"-1       : treat all filename arguments as a continuous single input.\n"
"-v       : print action summary to stderr.\n"
"-w       : suppress all warning messages.\n",
      stderr);
      return 0;

    case 'l':
      output_layout = 1;
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
      fputs("(F): Unknown option. Stop.\n", stderr);
      fprintf(stderr, usage_str, argv[0]);
      return 1;
    }
  }

  if (outfile && outfile[0]) {
    if (!freopen(outfile, "w", stdout)) {
      fprintf(stderr, "(F): Cannot open %s for writing.\n", outfile);
      exit(3);
    }
  }

  if (optind == argc)
    goto doit;

  do {
    filename = argv[optind];
    if (!freopen(filename, "r", stdin)) {
      if (!nowarn)
      fprintf(stderr, "(W): Cannot read file %s; skipped.\n", filename);
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
        // Watch out for multi-line strings
        if (!strcmp(type, "string"))
          RAW_escape(stdout, token);
        else
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
      brackets_opened = 0;
      prev_was_newline = 1;
      indents_reset();
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
