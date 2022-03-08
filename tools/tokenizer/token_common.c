/* Copyright (c) 2021 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Code functionality shared by all tokenizers.
   This obviously avoids code duplication and associated maintenance problems.
*/

#include "token_common.h"

// Program globals:
char *filename = "stdin";  // current file being parsed
unsigned linenr = 1;       // physical line number counted from 1
unsigned column = 0;       // byte position in physical line, from 0
unsigned char_count = 0;   // total byte count
unsigned utf8_count = 0;   // total utf-8 encoded unicode codepoints

int buffer[MAX_BUF];       // use buffer as multi-char lookahead.
unsigned buffered = 0;     // number of buffered bytes
unsigned saved_col = 0;    // one-place buf for last column on prev line
unsigned illegals = 0;     // count number of illegal characters
unsigned unexpect_eof = 0; // encountered unexpected EOF
unsigned num_files = 0;    // number of files read

// Program option settings:
int debug = 0;             // when 1 debug output to stderr
int verbose = 0;           // when 1 info output to stderr
int nowarn = 0;            // when 1 warnings are suppressed
Language source = C;       // language mode

/* Conversion table from filename extension to language code.
   To find language code, consider all entries and check each ext
   against filename; matched language is langs[i].lang.
   Invariant: langs[X].lang == X for every Language value.
   String representation of language code is langs[X].name.
*/
static const struct { const char *ext; Language lang; const char *name; }
  langs[] = {
    { ".c",    C,          "C" },
    { ".cc",   CPP,        "C++" },
    { ".java", JAVA,       "Java" },
    { ".js",   JAVASCRIPT, "JavaScript" },
    { ".py",   PYTHON,     "Python" },

    // Alternatives:
    { ".C",    CPP, 0 },
    { ".cpp",  CPP, 0 }
};

/* Generic binary search lookup in some keyword table.
   `word' to be searched must be NUL-terminated C string.
   `table' is array of const char * of `size' sorted alphabetically.
   Returns word found (i.e., pointer value in table) or 0.
*/
const char *is_keyword(const char *word,
                       const char *table[], unsigned size)
{
  int i = 0, j = size;
  while (i < j) {
    int k = (i + j) >> 1 /* / 2 */;
    int cmp = strcmp(word, table[k]);
    if (!cmp)
      return table[k];
    if (cmp < 0) j = k; else i = k + 1;
  }
  return 0;
}

/* Must be called right after a file is opened as stdin.
   Will attempt to remove any UTF-8 unicode signature (byte-order mark, BOM)
   at the beginning of the file.
   Unicode: U+FEFF
   UTF-8: EF BB BF

   First bytes Encoding              Must remove?
   00 00 FE FF UTF-32 big endian     Yes
   FF FE 00 00 UTF-32 little endian  Yes
   FE FF       UTF-16 big endian     Yes
   FF FE       UTF-16 little endian  Yes
   00 00 00 xx UTF-32 big endian     No
   xx 00 00 00 UTF-32 little endian  No
   00 xx       UTF-16 big endian     No
   xx 00       UTF-16 little endian  No
   otherwise   UTF-8                 No
*/
void remove_BOM(void)
{
  int c1 = getchar();
  if (c1 == 0xEF) {
    int c2 = getchar();
    if (c2 == 0xBB) {
      int c3 = getchar();
      if (c3 == 0xBF) {
        return;
      }
      if (c3 != EOF) buffer[buffered++] = c3;
    }
    if (c2 != EOF) buffer[buffered++] = c2;
  }
  if (c1 != EOF) buffer[buffered++] = c1;
}

/* Deal with DOS (\r \n) and classic Mac OS (\r) (physical) line endings.
   In case of CR LF skip (but count) the CR and return LF.
   In case of CR not followed by LF turns the CR into LF and returns that.
   All other chars are returned as is.
   Note: never returns a CR (\r).
*/
static int normalize_newline(void)
{
  /* No need to recognize Unicode code points here. */
  int cc = getchar();

  if (cc == '\r') {
    // Maybe \r \n (CR NL) combination?
    int nc = getchar();
    if (nc == '\n') {
      char_count++; // counts the carriage return
      utf8_count++;
      // No use incrementing column.
      return nc; // effectively skip the \r
    }
    // Mind nc not \n.
    if (nc != EOF) ungetc(nc, stdin);
    // cc == '\r'; consider a newline as well, so turn into \n:
    cc = '\n';
  }
  return cc;
}

/* Detects escaped newlines (line continuations) and signals them with the
   special '\r' character (that otherwise is not used).
   Keeps track of physical coordinates and absolute location for each character.
*/
int get(void)
{
  int cc;

  // Get the next character:
  if (buffered) { // chars available in lookahead buffer
    cc = buffer[--buffered]; // never EOF
    // cc maybe '\r'; act like '\n':
    if (cc == '\n' || cc == '\r') {
      linenr++;
      saved_col = column;
      column = 0;
      return cc;
    }
    column++;
    return cc;
  }

  // Read a fresh char:
  cc = normalize_newline(); // cc != '\r'
  if (cc == EOF) return EOF;
  char_count++;
  if (utf8_start(cc)) utf8_count++;

  if (cc == '\n') { // a normalized (physical) end-of-line
    linenr++;
    saved_col = column;
    column = 0;
    return cc;
  }

  // Deal with explicit \ line continuations!
  if (cc == '\\') {
    // Must look ahead (never maintained across get calls!):
    int nc = normalize_newline(); // cc != '\r'
    if (nc == '\n') {
      char_count++; // counts the newline
      utf8_count++;
      linenr++;     // on next physical line
      saved_col = column+1; // +1 for backslash
      column = 0;
      // Signal that this was an escaped newline:
      return '\r';
    }
    // Mind nc not \n.
    if (nc != EOF) ungetc(nc, stdin);
    // cc == '\\' a regular backslash
  }
  column++;
  return cc;
}

void unget(int cc)
{
  if (cc == EOF) return;
  if (buffered < MAX_BUF) {
    if (cc == '\n' || cc == '\r') {
      linenr--;
      // column was 0 right after getting the \n
      // hopefully there are no multiple ungets of \n
      column = saved_col;
    }
    else
      column--;
    buffer[buffered++] = cc;
  }
  else {
    fprintf(stderr, "(F): Lookahead buffer overflow (MAX=%u).\n", MAX_BUF);
    exit(2);
  }
}

/* Determine programming language from filename extension:
   .c             | C
   .cc, .C, .cpp  | C++
   .java          | Java

   Uses global filename (maybe stdin).
*/
Language detect_lang(void)
{
  char *p;
  if (p = strrchr(filename, '.')) {
    int i;
    for (i = 0; i < sizeof(langs)/sizeof(langs[0]); i++)
      if (!strcmp(p, langs[i].ext))
        return langs[i].lang;
  }
  return C;
}
