/* Copyright (c) 2020 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Simple Regular Expression (RE) based tokenizer for C/C++.
   Processes character input in a number of phases:
   1. Read character by character and compose logical lines by recognizing
      backslash-newline line continuations and removing them.
      In this phase we keep track of the physical line number and column
      position.
   2. Treating the input logical line per logical line and detecting line
      and block comments and considering them as white-space, and together
      with any other adjacent white-space will be compacted into a single space
      character. Newlines are not considered white-space and simply signal
      the end of a logical line (unless inside of a block comment and then
      they will disappear).
   3. The compaction of white-space of phase 2 has to be inhibited from
      taking place inside double-quote delimited string literals.
   4. A non-comment, white-space compacted logical line ultimately is buffered
      and becomes the subject of possibly multiple token RE matching calls.

   Note that use of logical lines and white-space compaction makes tracing
   the original line and column position for a token rather tricky.
   This is solved by explicitly keeping the coordinates of all characters
   in a logical line.
*/

#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <regex.h>

// POSIX Extended Regular Expressions for all parts of token output.

/* Can we use non-capturing groups? No!
   Define REs here with the least grouping, i.e., avoid ()
   Many RE chars lose special meaning inside char class []
   Postpone the necessity of () as long as possible.
*/

/* Escape sequences:
   \a ^G  7 0x07 alarm/bell
   \b ^H  8 0x08 backspace
   \t ^I  9 0x09 horizontal tab
   \n ^J 10 0x0A newline
   \v ^K 11 0x0B vertical tab
   \f ^L 12 0x0C formfeed
   \r ^M 13 0x0D carriage return
   \"    34 0x22 double quote
   \'    39 0x27 single quote
   \?    63 0x3F question mark
   \\    92 0x5C backslash
*/

// Any amount of white-space:
#define ws_RE           "[ \t\v\f\n]*"

// 96 chars (omitted are e.g.: @ $ `)
//                                     33 56 67         8         9       9
//                        1234 5 6 7 8 34 90 9012345678901234567890123 4 56
#define basic_char0_RE  "[][ \t\v\f\na-zA-Z0-9_{}#()<>%:;.?*+/^&|~!=,\\\"'-]"

// all basic chars except \n and >
#define h_chars_RE      "[][ \t\v\fa-zA-Z0-9_{}#()<%:;.?*+/^&|~!=,\\\"'-]+"
// all basic chars except \n and \"
#define q_chars_RE      "[][ \t\v\fa-zA-Z0-9_{}#()<>%:;.?*+/^&|~!=,\\'-]+"
#define header_RE       "<"h_chars_RE">|\""q_chars_RE"\""
#define pp_number_RE    "\\.?[0-9]('?[a-zA-Z_0-9]|[eE][+-]|\\.)*"

#define unichar_RE      "\\\\u[0-9a-fA-F]{4}|\\\\U[0-9a-fA-F]{8}"

//#define identifier_RE "[_a-zA-Z][_a-zA-Z0-9]*"
#define identifier_RE   "([_a-zA-Z]|"unichar_RE")([_a-zA-Z0-9]|"unichar_RE")*"

#define suffix_RE       "([uU]ll?|[uU]LL?|ll?[uU]?|LL?[uU]?)?"
#define binary_RE       "0[bB][01]('?[01])*"suffix_RE
#define octal_RE        "0('?[0-7])*"suffix_RE
#define decimal_RE      "[1-9]('?[0-9])*"suffix_RE
#define hexadecimal_RE  "0[xX][0-9a-fA-F]('?[0-9a-fA-F])*"suffix_RE
#define integer_RE      binary_RE"|"octal_RE"|"decimal_RE"|"hexadecimal_RE

#define dec_part_RE     "[0-9]('?[0-9])*"
#define exponent_RE     "[eE][-+]?[0-9]('?[0-9])*"
#define floating_RE     "(\\."dec_part_RE"("exponent_RE")?|"\
                        dec_part_RE"\\.("dec_part_RE")?("exponent_RE")?|"\
                        dec_part_RE exponent_RE")[fFlL]?"

#define oct_char_RE     "\\\\[0-7]{1,3}"
#define hex_char_RE     "\\\\x[0-9a-fA-F]+"
#define escape_RE       "\\\\['\"?abfnrtv\\]|"oct_char_RE"|"hex_char_RE
#define character_RE    "[uUL]?'([^'\\\n]|"escape_RE"|"unichar_RE")'"
#define string_RE       "[uUL]?\"([^\"\\\n]|"escape_RE"|"unichar_RE")*\""

// should really be: any basic source char except ) followed by delimiter
#define r_chars_RE      "[^)]*"
// delimiter; first and second occurrence in rawstring must be the same
// use back reference \3:
#define d_chars_RE      "([^ ()\\\t\v\f\n]{0,16})"
#define rawstring_RE    "[uUL]?R\""d_chars_RE"\\("r_chars_RE"\\)\\3\""

#define operator_RE     "[][{}();?~,]|<=>|<<=|\\.\\.\\.|->\\*|>>=|"\
                        "[*/!=^]=?|<[:%=<]?|:[:>]?|\\.[*]?|-[->=]?|\\+[=+]?|"\
                        "%[>=]?|&[=&]?|>[>=]?|\\|[|=]?"

#define preprocessor_RE "##?"

#define token_RE        "^"ws_RE"(("rawstring_RE")|("identifier_RE")|("\
                        integer_RE")|("floating_RE")|("string_RE")|("\
                        character_RE")|("operator_RE")|("preprocessor_RE"))"

#define NMATCH 34

// Guarded against overflow but not full-proof!
#define MAX_LINE 4096   // maximum logical line length in chars (\0 exclusive)

#define utf8_start(cc)          (((cc)&0xC0)!=0x80)

// Append char cc to buffer and record coordinates; discard when no more room:
#define buffer_add(cc) \
  do { \
    if (buffered < MAX_LINE) { \
      linenrs[buffered] = linenr; \
      columns[buffered] = column-1; \
      buffer[buffered++] = (cc); \
    } \
  } while(0)

#define buffer_close()          buffer[buffered] = '\0'

// Program globals:
static char *filename = "stdin";// current file being parsed
static regex_t *compiled_token_RE; // the compiled token RE
static unsigned linenr = 1;     // line number counted from 1
static unsigned column = 0;     // char position in line, counted from 0
static unsigned char_count = 0; // total char/byte count
static unsigned utf8_count = 0; // total utf-8 char count

static char buffer[MAX_LINE+1]; // use buffer as multi-char lookahead.
static unsigned buffered = 0;   // number of buffered chars
static unsigned linenrs[MAX_LINE]; // original line's line number
static unsigned columns[MAX_LINE]; // original line's column positions
static unsigned illegals = 0;   // count number of illegal characters
static unsigned unexpect_eof=0; // encountered unexpected EOF

// Program option settings:
static int debug = 0;           // when 1 debug output to stderr
static int verbose = 0;         // when 1 info output to stderr
static int nowarn = 0;          // when 1 warnings are suppressed
static int hash_as_comment = 0; // when 1 treat # as line comment

// Counting the number of opening parenthesis ( from 0:
static const char *classes[] = {
  /*  0 */ 0, // complete match leading white-space inclusive
  /*  1 */ 0, // complete token text white-space exclusive
  /*  2 */ "string", // raw string
  /*  3 */ 0, // delimiter part of raw string
  /*  4 */ "identifier",
  /*  5 */ 0,
  /*  6 */ 0,
  /*  7 */ "integer",
  /*  8 */ 0, // last of ('[01])
  /*  9 */ 0,
  /* 10 */ 0, // last of ('[0-7])
  /* 11 */ 0,
  /* 12 */ 0, // last of ('[0-9)]
  /* 13 */ 0,
  /* 14 */ 0, // last of ('[0-9a-fA-F)]
  /* 15 */ 0,
  /* 16 */ "floating",
  /* 17 */ 0, // floating without [fFlL]
  /* 18-27 */ 0,0,0,0,0,0,0,0,0,0, // variants of floating
  /* 28 */ "string", // " inclusive
  /* 29 */ 0, // last char in string
  /* 30 */ "character", // ' inclusive
  /* 31 */ 0, // last char in character
  /* 32 */ "operator",
  /* 33 */ "preprocessor"
};

// Pre-compile the token_RE regular expression.
regex_t *precompile(void)
{
  regex_t *re = malloc(sizeof(regex_t));
  int errcode = regcomp(re, token_RE, REG_EXTENDED);
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

// Returns length of matched token (ws inclusive) or 0 when in error.
unsigned get_token(char const *text, unsigned start)
{
  if (!*text) return 0;
  regex_t *re = compiled_token_RE;
  size_t nmatch = NMATCH;
  regmatch_t pmatch[NMATCH];

  if (regexec(re, text, nmatch, pmatch, REG_NOTEOL) == REG_NOMATCH) {
    // Warn about the failed match:
    fprintf(stderr, "(W) [%u:%u] not a valid token; skipped.\n",
            linenrs[start],columns[start]);
    // Cannot recover; no more input.
    return 0;
  }
  // Here: a valid token recognized.

  // Total length matched (leading white-space inclusive):
  assert(pmatch[0].rm_so == 0);
  unsigned skiplen = pmatch[0].rm_eo;

  unsigned i;
  for (i = 0; i < NMATCH; i++) {
    const char *key = classes[i];
    if (!key) continue;
    int offset = pmatch[i].rm_so;
    unsigned len = pmatch[i].rm_eo - offset;
    char const *p = text + offset;
    if (!len) continue;

    // Only CSV-style output for now; no escaping of " yet.
    // FIXME: Must check identifier for reserved words.
    fprintf(stdout, "%u,%u,%s,", linenrs[start+offset],columns[start+offset],key);
    //fprintf(stdout, "%2d: ", i);
    fwrite(p, 1, len, stdout);
    fputc('\n', stdout);
  }
  return skiplen;
}

/* Deal with DOS (\r \n) and classic Mac OS (\r) line endings.
   Keeps track of physical coordinates and absolute location for each character.
*/
int normalize_newline(void)
{
  int cc = getchar();

  if (cc == '\r') {
    // Maybe \r \n (CR NL) combination?
    int nc = getchar();
    if (nc == '\n') {
      char_count++; // counts the carriage return
      utf8_count++;
      // No use incrementing column.
      return nc; // return \n; effectively skipping the \r
    }
    // Mind nc not \n. ungetc(EOF) is Okay.
    ungetc(nc, stdin);
    // cc == '\r'; consider a newline as well, so turn into \n:
    cc = '\n';
  }
  return cc;
}

/* Phase 1.
   Forms logical lines by resolving escaped newlines (line continuations).
*/
int get(void)
{
  int cc;
 restart:
  // Read a fresh char:
  cc = normalize_newline(); // cc != '\r'
  if (cc == EOF) return EOF;
  char_count++;
  if (utf8_start(cc)) utf8_count++;

  if (cc == '\n') { // a normalized end-of-line (\r|\r?\n)
    linenr++;
    column = 0;
    return cc; // \n here signals a logical end-of-line
  }

  // Deal with \ line continuations!
  if (cc == '\\') {
    // Must look ahead (never maintained across get calls!):
    int nc = normalize_newline();
    if (nc == '\n') { // 1 logical line: discard \\n combo:
      char_count++; // counts the newline
      utf8_count++;
      linenr++;     // on next physical line
      column = 0;

      // Still need to get a character.
      // Could again start a line continuation!
      goto restart;
    }
    // Mind nc not \n. ungetc(EOF) is Okay.
    ungetc(nc, stdin);
    // cc == '\\' a regular backslash
  }
  column++;
  return cc;
}

/* Phase 2.
   Removes line and block comments and condenses white-space up to a newline.
   Signals presence of any leading white-space by setting ws to 1.
   Must not be active inside strings literals!
*/
int filter(int *ws)
{
  int cc = get();
  *ws = 0;

 restart:
  // cc already read.

  /*** WHITE-SPACE ***/

  // Skip (abutted) space and control chars and comments:
  //while (cc != EOF && strchr(" \f\n\r\t\v", cc))
  while (cc != EOF && cc != '\n' && isspace(cc)) {
    *ws = 1;
    cc = get();
  }
  if (cc == EOF || cc == '\n')
    return cc;
  // cc != EOF && !isspace(cc)

  /*** OPTIONAL # LINE COMMENT (to ignore preprocessor statements) ***/
  // Java: no preprocessor directives.

  if (cc == '#' && hash_as_comment) {
    // Skip till end-of-line (\n exclusive):
    while ((cc = get()) != EOF && cc != '\n')
      ;
    // cc == '\n' || cc == EOF
    *ws = 1;
    return cc;
  }

  /*** LINE COMMENT AND BLOCK COMMENT (C/C++/Java) ***/

  if (cc == '/') {
    cc = get();
    if (cc == '/') {
      // Skip till end-of-line (\n exclusive):
      while (cc != EOF && (cc = get()) != '\n')
        ;
      // cc == '\n' || cc == EOF
      *ws = 1;
      return cc;
    }

    if (cc == '*') {
      // Skip till */ inclusive:
      int nc = get();
      if (nc == EOF) { // Error!
        fputs("(E): Unexpected end-of-file in /* comment.\n", stderr);
        unexpect_eof++;
        return EOF;
      }
      do {
        cc = nc;
        nc = get();
        if (nc == EOF) { // Error!
          fputs("(E): Unexpected end-of-file in /* comment.\n", stderr);
          unexpect_eof++;
          return EOF;
        }
      } while (cc != '*' || nc != '/');
      // cc == '*' && nc == '/'
      cc = get();
      *ws = 1;
      goto restart;
    }
    // seen / but not // or /*
    ungetc(cc, stdin); // char after /
    cc = '/'; // restore /
  }
  return cc;
}

/* Phase 3.
   Buffers up enough characters to encompass any possible token length.
   Assumes buffer contents is white-space followed by at least 1 token
   and contains 1 logical line.
   Tokens (but not comments) are assumed to fit on a logical line.
*/
int buffer_fill(void)
{
  int cc;
  int ws;
  int start_linenr = linenr;
  buffered = 0;
  while ((cc = filter(&ws)) != EOF && cc != '\n') {
    if (ws) buffer_add(' ');
    buffer_add(cc);
    // special action for ": (cannot have this situation for ')
    if (cc == '"') {
      // Switch to unfiltered input till unescaped closing ":
      if ((cc = get()) == '"') {
        buffer_add(cc);
        // An empty string literal.
        continue;
      }
      if (cc == EOF || cc == '\n')
        // unexpected EOF or newline in string
        break;
      buffer_add(cc);
      int pc;
      do {
        pc = cc;
        cc = get();
        if (cc == EOF || cc == '\n')
          // unexpected EOF or newline in string
          goto break_outer;
        buffer_add(cc);
      } while (pc == '\\' || cc != '"');
      // pc != '\\' && cc == '"'
    }
  }
 break_outer:
  // cc == EOF || cc == '\n'
  // Note: line of only white-space will have nothing in buffer.

  // Only deal with non-empty lines:
  if (buffered) {
    buffer_close();
    // All white-space in buffer compressed to single ' '
    // (except of course in string literal).

    // Match tokens in buffer:
    const char *p = buffer;
    unsigned len;
    while ((len = get_token(p, p-buffer)))
      p += len;
  }
  return cc;
}

int main(int argc, char *argv[])
{
  compiled_token_RE = precompile();

  if (argc > 1 && argv[1]) {
    filename = argv[1];
    if (!freopen(filename, "r", stdin)) {
      fprintf(stderr, "(E) unable to open `%s' for reading.\n", filename);
      return 1;
    }
  }

  while (buffer_fill() != EOF)
    ;
  return 0;
}
