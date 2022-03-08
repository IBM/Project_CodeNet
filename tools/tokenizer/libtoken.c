/* Copyright (c) 2021, 2022 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Code functionality shared by all tokenizers.
   This obviously avoids code duplication and associated maintenance problems.
*/

#include "libtoken.h"

// Program globals:
const char *filename = "stdin";  // current file being parsed
unsigned linenr = 1;       // physical line number counted from 1
unsigned column = 0;       // byte position in physical line, from 0
unsigned char_count = 0;   // total byte count
unsigned utf8_count = 0;   // total utf-8 encoded unicode codepoints

int buffer[MAX_BUF];       // use buffer as multi-char lookahead.
unsigned buffered = 0;     // number of buffered bytes
unsigned saved_col = 0;    // one-place buf for last column on prev line

// Program option settings:
int debug = 0;             // when 1 debug output to stderr
int verbose = 0;           // when 1 info output to stderr
int nowarn = 0;            // when 1 warnings are suppressed

unsigned illegals = 0;     // count number of illegal characters
unsigned unexpect_eof = 0; // encountered unexpected EOF
int hash_as_comment = 0;   // when 1 treat # as line comment
int newline_token = 0;     // when 1 output newline pseudo-token
int comment_token = 0;     // when 1 output comments as tokens
int whitespace_token = 0;  // when 1 output adjacent white-space as a token
int continuation_token = 0;  // when 1 output line continuation pseudo-token

static int logical_lines = 0;     // when 1 ignore line continuations in get)

// Must be synced with enum TokenClass!
const char *token_class[] = {
  /* 0*/ "identifier",
  /* 1*/ "keyword",
  /* 2*/ "string",
  /* 3*/ "character",
  /* 4*/ "integer",
  /* 5*/ "floating",
  /* 6*/ "operator",
  /* 7*/ "preprocessor",
  /* 8*/ "line_comment",
  /* 9*/ "block_comment",
  /*10*/ "whitespace",
  /*11*/ "newline",
  /*12*/ "continuation",
  /*13*/ "filename",
  /*14*/ "endoffile"
};

/* No longer using perfect hash function but simple binary search. */

/* C11 n1570.pdf 6.4.1 (44)
   C17 n2176.pdf 6.4.1 (A.1.2) (44)
*/
static const char *C_keywords[] = {
  "_Alignas",   "_Alignof",     "_Atomic",      "_Bool",        "_Complex",
  "_Generic",   "_Imaginary",   "_Noreturn",    "_Static_assert",
  "_Thread_local",

  "auto",       "break",        "case",         "char",         "const",
  "continue",   "default",      "do",           "double",       "else",
  "enum",       "extern",       "float",        "for",          "goto",
  "if",         "inline",       "int",          "long",         "register",
  "restrict",   "return",       "short",        "signed",       "sizeof",
  "static",     "struct",       "switch",       "typedef",      "union",
  "unsigned",   "void",         "volatile",     "while"
};

#if 0
/* C++ 2014 n4296.pdf 2.11 (84) */
static const char *CPP_keywords[] = {
  "alignas",       "alignof",       "and",           "and_eq",     "asm",
  "auto",          "bitand",        "bitor",         "bool",       "break",
  "case",          "catch",         "char",          "char16_t",   "char32_t",
  "class",         "compl",         "const",         "const_cast", "constexpr",
  "continue",      "decltype",      "default",       "delete",     "do",
  "double",        "dynamic_cast",  "else",          "enum",       "explicit",
  "export",        "extern",        "false",         "float",      "for",
  "friend",        "goto",          "if",            "inline",     "int",
  "long",          "mutable",       "namespace",     "new",        "noexcept",
  "not",           "not_eq",        "nullptr",       "operator",   "or",
  "or_eq",         "private",       "protected",     "public",     "register",
  "reinterpret_cast", "return",     "short",         "signed",     "sizeof",
  "static",        "static_assert", "static_cast",   "struct",     "switch",
  "template",      "this",          "thread_local",  "throw",      "true",
  "try",           "typedef",       "typeid",        "typename",   "union",
  "unsigned",      "using",         "virtual",       "void",       "volatile",
  "wchar_t",       "while",         "xor",           "xor_eq"
};
#endif

/* C++23 n4885.pdf 5.11 (92) */
static const char *CPP_keywords[] = {
  "alignas",       "alignof",       "and",           "and_eq",     "asm",
  "auto",          "bitand",        "bitor",         "bool",       "break",
  "case",          "catch",         "char",          "char16_t",   "char32_t",
  "char8_t",       "class",         "co_await",      "co_return",  "co_yield",
  "compl",         "concept",       "const",         "const_cast", "consteval",
  "constexpr",     "constinit",     "continue",      "decltype",   "default",
  "delete",        "do",            "double",        "dynamic_cast", "else",
  "enum",          "explicit",      "export",        "extern",     "false",
  "float",         "for",           "friend",        "goto",       "if",
  "inline",        "int",           "long",          "mutable",    "namespace",
  "new",           "noexcept",      "not",           "not_eq",     "nullptr",
  "operator",      "or",            "or_eq",         "private",    "protected",
  "public",        "register",      "reinterpret_cast", "requires","return",
  "short",         "signed",        "sizeof",        "static",  "static_assert",
  "static_cast",   "struct",        "switch",        "template",   "this",
  "thread_local",  "throw",         "true",          "try",        "typedef",
  "typeid",        "typename",      "union",         "unsigned",   "using",
  "virtual",       "void",          "volatile",      "wchar_t",    "while",
  "xor",           "xor_eq"
};

/* Java SE 8 (50) (false, true, null are literals) */
/* https://docs.oracle.com/javase/specs/jls/se8/html/jls-3.html#jls-3.9 */
static const char *Java_keywords[] = {
  "abstract", "assert",     "boolean", "break",     "byte",      "case",
  "catch",    "char",       "class",   "const",     "continue",  "default",
  "do",       "double",     "else",    "enum",      "extends",   "final",
  "finally",  "float",      "for",     "goto",      "if",        "implements",
  "import",   "instanceof", "int",     "interface", "long",      "native",
  "new",      "package",    "private", "protected", "public",    "return",
  "short",    "static",     "strictfp","super",     "switch", "synchronized",
  "this",     "throw",      "throws",  "transient", "try",       "void",
  "volatile", "while"
};

static const char *Python_keywords[] = {
  "False",  "None",   "True",    "and",      "as",       "assert", "async",
  "await",  "break",  "class",   "continue", "def",      "del",    "elif",
  "else",   "except", "finally", "for",      "from",     "global", "if",
  "import", "in",     "is",      "lambda",   "nonlocal", "not",    "or",
  "pass",   "raise",  "return",  "try",      "while",    "with",   "yield"
};

/* Includes future reserved keywords, strict mode reserved words and module
   code reserved words, as well as all the older standards future reserved
   words, and the literals null, false, and true.
*/
static const char *JavaScript_keywords[] = {
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

#define num_keywords(lang) sizeof(lang##_keywords)/sizeof(lang##_keywords[0]);

/* Generic binary search lookup in some keyword table.
   `word' to be searched must be NUL-terminated C string.
   `table' is array of const char * of `size' sorted alphabetically.
   Returns word found (i.e., pointer value in table) or 0.
*/
#define lang_is_keyword(lang)                                           \
  static const char *lang##_is_keyword(const char *word)                \
  {                                                                     \
    int i = 0, j = num_keywords(lang);                                  \
    while (i < j) {                                                     \
      int k = (i + j) >> 1 /* / 2 */;                                   \
      const char *kw = lang##_keywords[k];                              \
      int cmp = strcmp(word, kw);                                       \
      if (!cmp)                                                         \
        return kw;                                                      \
      if (cmp < 0) j = k; else i = k + 1;                               \
    }                                                                   \
    return 0;                                                           \
  }

/* Define individual is_keyword functions per language: */
/* C_is_keyword */
lang_is_keyword(C)
/* CPP_is_keyword */
lang_is_keyword(CPP)
/* Java_is_keyword */
lang_is_keyword(Java)
/* Python_is_keyword */
lang_is_keyword(Python)
/* JavaScript_is_keyword */
lang_is_keyword(JavaScript)

const char *(*is_keyword)(const char *) = C_is_keyword;

/* Conversion table from filename extension to language code.
   To find language code, consider all entries and check each ext
   against filename; matched language is langs[i].lang.
   Invariant: langs[X].lang == X for every Language value.
   String representation of language code is langs[X].name.

   Have certain config settings depend on the language.
   Use 2 step:
   1. determine language from name/extension
   2. look up language config
*/
static const struct {
  const char *ext;
  Language lang;
  const char *name;
}
  langs[] = {
    { ".c",    C,          "C" },
    { ".cpp",  CPP,        "C++" },
    { ".java", JAVA,       "Java" },
    { ".js",   JAVASCRIPT, "JavaScript" },
    { ".py",   PYTHON,     "Python" },

    // Alternatives:
    { ".h",    C,          "" },
    { ".C",    CPP,        "" },
    { ".cc",   CPP,        "" },
    { ".hh",   CPP,        "" },
};

const char *lang_name(Language lang)
{
  return langs[lang].name;
}

static const struct {
  //Language lang; implicit
  const char *(*is_keyword)(const char *);
}
  lang_configs[] = {
    { C_is_keyword,          },
    { CPP_is_keyword,        },
    { Java_is_keyword,       },
    { JavaScript_is_keyword, },
    { Python_is_keyword,     },
};

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
static void remove_BOM(void)
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

int open_as_stdin(const char *file)
{
  filename = file;
  if (!freopen(filename, "r", stdin)) {
    if (!nowarn)
      fprintf(stderr, "(W): Cannot read file %s.\n", filename);
    return -1;
  }
  return set_or_detect_lang(0);
}

/* Deal with DOS (\r \n) and classic Mac OS (\r) (physical) line endings.
   In case of CR LF skip (but count) the CR and return LF.
   In case of CR not followed by LF turns the CR into LF and returns that.
   All other chars are returned as is.
   Note: never returns a CR (\r). Line/column counts are not affected here.
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
      return nc; // return \n; effectively skipping the \r
    }
    // Mind nc not \n. ungetc(EOF) is Okay.
    ungetc(nc, stdin);
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

 restart:
  // Get the next character:
  if (buffered) { // chars available in lookahead buffer
    cc = buffer[--buffered]; // never EOF
    char_count++;
    // cc maybe '\r' (line continuation); act like '\n':
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

  if (cc == '\n') { // a normalized end-of-line (\r|\r?\n)
    linenr++;
    saved_col = column;
    column = 0;
    return cc; // \n here signals a logical end-of-line
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

      if (logical_lines)
        // Still need to get a character.
        // Could again start a line continuation!
        goto restart;

      // Signal that this was an escaped newline (= line continuation):
      return '\r';
    }
    // Mind nc not \n. ungetc(EOF) is Okay.
    ungetc(nc, stdin);
    // cc == '\\' a regular backslash
  }
  column++;
  return cc;
}

/* Undo action of a get() lookahead call.
   An attempt at undoing an EOF read has no effect.
   Since get() encodes logical line endings with \n and continuation
   line endings with \r, both could be subject to an unget().
*/
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
    char_count--;
    buffer[buffered++] = cc;
  }
  else {
    fprintf(stderr, "(F): Lookahead buffer overflow (MAX=%u).\n", MAX_BUF);
    exit(2);
  }
}

/* Either set this file's input language explicitly via a string or
   use the filename extension to determine the language.
   If neither works out, use the default language C.
   Uses global filename (maybe stdin).
   Once the language is known, configs for that language are applied,
   e.g. the correct keyword table to use.
*/
Language set_or_detect_lang(const char *source)
{
  int i;
  Language lang = C; // default language

  if (source) {
    /* Check if explicit language is known: */
    for (i = 0; i < sizeof(langs)/sizeof(langs[0]); i++)
      if (!strcmp(source, langs[i].name)) {
        lang = langs[i].lang;
        goto done;
      }
    fprintf(stderr, "(E): No support for language `%s'.\n", source);
  }

  char *p;
  if (p = strrchr(filename, '.')) {
    for (i = 0; i < sizeof(langs)/sizeof(langs[0]); i++)
      if (!strcmp(p, langs[i].ext)) {
        lang = langs[i].lang;
        goto done;
      }
    fprintf(stderr, "(E): Unknown filename extension `%s'.\n", p);
  }
  if (!nowarn)
    fprintf(stderr, "(W): Assuming default language C.\n");

 done:
  is_keyword = lang_configs[lang].is_keyword;
  return lang;
}

// Dynamically sized token buffer:
static char *token_buf = 0;
static unsigned token_alloc = 0;
static unsigned token_len = 0;

// Makes sure there is room in the token buffer.
static void token_buf_room(void)
{
  if (token_len == token_alloc) { // all space used up
    if (!token_alloc) { // first time allocation
      token_alloc = 65536;
      if (!(token_buf = malloc(token_alloc))) {
        fprintf(stderr, "(F): Allocation of token buffer failed.\n");
        exit(4);
      }
      token_buf[0] = '\0'; // for safety
      return;
    }

    token_alloc <<= 1;
    if (!(token_buf = realloc(token_buf, token_alloc))) {
      fprintf(stderr, "(F): Reallocation of token buffer failed.\n");
      exit(4);
    }
    //fprintf(stderr, "Realloc-ed token buf.\n");
  }
}

// Appends a character to the token buffer, always making sure there is room.
static void token_buf_push(int cc)
{
  token_buf_room();
  // There is room: token_len < token_alloc
  token_buf[token_len++] = cc;
}

// Undoes the push action but only if there is some content.
static int token_buf_pop(void)
{
  return token_len ? token_buf[--token_len] : 0;
}

// Adds a terminating NUL character which does not change the token length.
static void token_buf_close(void)
{
  token_buf_room();
  token_buf[token_len] = '\0'; // Note: no advance
}

// Resets the token buffer cursor.
static void token_buf_reset(void)
{
  token_len = 0;
}

/* Tokenization of C++ programming language source text.
   Recognizes:
   - identifier
   - reserved word/keyword
   - binary, octal, decimal, hexadecimal and floating-point numbers
   - double-quoted string literal
   - single-quoted character literal
   - all single, double, and triple operator and punctuation symbols
   - the preprocessor tokens # and ##
   Optionally:
   - filename       start_token
   - line_comment   comment_token
   - block_comment  comment_token
   - newline        newline_token
   - continuation   continuation_token
   - whitespace     whitespace_token

   Normally skips white-space and comments and flags anything
   left over as illegal characters.

   (Approximately 20 tests per single character worst-case.)

   Returns 0 upon EOF else the token length in bytes.
   (There are no 0-length tokens!)
   EOF may be interpreted as a token. The function then returns:
   token = "", type = endoffile, line and col correctly defined.

   An unexpected EOF in the middle of a token will cause an error message
   and the partial token to be output first before a next call returns 0
   (to indicate the EOF condition).
*/

unsigned C_tokenize_int(const char **token, enum TokenClass *type,
			unsigned *line, unsigned *col, unsigned *pos)
{
  int cc;
  *type = ENDOFFILE;

  do { // infinite loop; after token recognized breaks out.
    // Start collecting a token.
    token_buf_reset();
    *line = linenr;
    *col = column;
    *pos = char_count;
    // white-space tokens see continuation lines:
    logical_lines = 0;
    cc = get();

  restart:
    // cc already read; coordinates for it are correct.

    /*** WHITE-SPACE ***/

    /* In principle all consecutive white-space including \n and \r (and some
       other control chars) are collected and form a single whitespace token.
       However, when newlines are requested to be reported as separate tokens,
       they break this pattern. Note that we cannot issues multiple tokens
       in a single call to this function.

       Token buf will only hold some white-space chars when implicitly
       requested via whitespace_token; otherwise stays empty.
       Same for the \n and \r requests.
     */

    if (cc == '\n' && newline_token) { // end of a logical line
      // Here we assume the buf is empty.
      token_buf_push(cc);
      *type = NEWLINE;
      break;
    }

    if (cc == '\r' && continuation_token) { // end of a physical line
      // Here we assume the buf is empty.
      token_buf_push('\\');
      token_buf_push('\n');
      *type = CONTINUATION;
      break;
    }

    // Aggregate as much white-space as possible.
    // FIXME: officially a NUL should be considered white-space.
    while (isspace(cc)) {	// i.e., cc in [ \f\n\r\t\v]
      // Here: !newline_token (!continuation_token)
      if (whitespace_token)
        if (cc == '\r') { // line continuation
          // Convert back to original char sequence:
          token_buf_push('\\');
          token_buf_push('\n');
        }
        else
          token_buf_push(cc); // perhaps \n
      //else: white-space is discarded

      // Here: whitespace_token implies token_len > 0

      cc = get();
      if (cc == '\n' && newline_token ||
	  cc == '\r' && continuation_token) {
	// Must issue whitespace token if so requested.
	if (whitespace_token) {
	  // Undo lookahead (unget(EOF) has no effect!):
	  unget(cc); // next token will be newline/continuation
	  *type = WHITESPACE;
	  token_buf_close();
	  *token = token_buf;
	  return token_len;
	}
	// Issue newline/continuation token right away:
	goto restart;
      }
    }
    // Here: !isspace: must break or start real token.

    if (whitespace_token && token_len) {
      // Undo lookahead (unget(EOF) has no effect!):
      unget(cc);
      *type = WHITESPACE;
      break;
    }

    if (cc == EOF) {
      token_buf_reset();
      break;
    }

    // Rest of tokens treat line continuations as non-existent:
    logical_lines = 1;

    // If white-space skipped must reset coordinates:
    *line = linenr;
    *col = column-1;
    *pos = char_count-1;

    /*** OPTIONAL # LINE COMMENT (to ignore preprocessor statements) ***/
    // Java: no preprocessor directives.

    // NULs (like many other chars) in comments are silently ignored!

    if (cc == '#' && hash_as_comment) {
      if (comment_token)
        token_buf_push(cc);
      // Skip till end-of-line (\n exclusive):
      while ((cc = get()) != '\n' && cc != EOF)
        if (comment_token)
          token_buf_push(cc);
      // cc == '\n' || cc == EOF
      // Don't consider \n part of comment.
      if (comment_token) {
	// Undo lookahead (unget(EOF) has no effect!):
        unget(cc);
        *type = LINE_COMMENT;
        break;
      }
      *line = linenr-1;
      *col = saved_col;
      *pos = char_count;
      goto restart;
    }

    /*** LINE COMMENT AND BLOCK COMMENT (C/C++/Java) ***/

    if (cc == '/') {
      cc = get();
      if (cc == '/') {
        if (comment_token) {
          token_buf_push(cc);
          token_buf_push(cc);
        }
        // Skip till end-of-line (\n exclusive):
        while ((cc = get()) != '\n' && cc != EOF)
          if (comment_token)
            token_buf_push(cc);
        // cc == '\n' || cc == EOF
        // Don't consider \n part of comment.
        if (comment_token) {
	  // Undo lookahead (unget(EOF) has no effect!):
          unget(cc);
          *type = LINE_COMMENT;
          break;
        }
	*line = linenr-1;
	*col = saved_col;
	*pos = char_count;
        goto restart;
      }

      if (cc == '*') {
        if (comment_token) {
          token_buf_push('/');
          token_buf_push(cc);
        }
        // Skip till */ inclusive:
        int nc = get(); // if EOF next get will be EOF too
        if (comment_token && nc != EOF)
          token_buf_push(nc);
        do {
          cc = nc;
          nc = get();
          if (nc == EOF) { // Error!
            fprintf(stderr,
                    "(E): [%s:%u] Unexpected end-of-file in /* comment.\n",
                    filename, *line);
            unexpect_eof++;
	    if (comment_token)
	      // Better return partial comment as token and postpone EOF:
	      *type = BLOCK_COMMENT;
	    else
	      token_buf_reset();
	    token_buf_close();
	    *token = token_buf;
            return token_len;
          }
          if (comment_token)
            token_buf_push(nc);
        } while (cc != '*' || nc != '/');
        // cc == '*' && nc == '/'
        // Don't consider char right after */ as part of comment.
        if (comment_token) {
          *type = BLOCK_COMMENT;
          break;
        }
	*line = linenr;
	*col = column;
	*pos = char_count;
        cc = get();
        goto restart;
      }
      // seen / but not // or /*
      unget(cc); // char after /
      cc = '/'; // restore /
    }

    // If white-space and/or comments skipped must reset coordinates:
    *line = linenr;
    *col = column-1;
    *pos = char_count-1;

    /*** CHAR and STRING PREFIX (C/C++) ***/

    // Allow u,U,L prefix for string and char
    // FIXME: allow u8 as prefix for string
    if (cc == 'L' || cc == 'u' || cc == 'U') {
      token_buf_push(cc);
      cc = get();
      if (cc == '"')
        goto string_token;
      if (cc == '\'')
        goto char_token;
      // u,U,L will be interpreted as (start of) identifier.
      unget(cc); // char after u,U,L
      cc = token_buf_pop(); // restore original and remove from token
    }

    /*** IDENTIFIER (C/C++/Java) and KEYWORD (C/C++) ***/
    // Java: false, true, null are literals
    // FIXME: Flag to allow .letter as part of identifier?
    // (compound identifier)

    // Simplistic solution to allowing Unicode: allow any char >= 128 without
    // actual checking for UTF-8.
    if (isalpha(cc) || cc == '_' || cc == '$' || (cc & 0x80)) {
      token_buf_push(cc);
      while (isalnum(cc = get()) || cc == '_' || cc == '$' ||
             cc != EOF && (cc & 0x80))
        token_buf_push(cc);
      unget(cc);
      token_buf_close();
      *type = is_keyword(token_buf) ? KEYWORD : IDENTIFIER;
      break;
    }

    /*** INTEGER and FLOATING ***/
    // Java: uses _ in numbers as insignificant separator
    // Java: decimal suffix: [lL], float suffix: [fFdD]
    // Java: allows hex float

#if 0
    // Examples:
    int bin_num = 0B010101u;
    int oct_num = 01234567L;
    int hex_num = 0x123ABCLL;
    int dec_num = 12345678;

    float flt_num1 = 077.;
    float flt_num2 = 077.987;
    float flt_num3 = 77.;
    float flt_num4 = .77;
#endif

    // . digits ... floating
    if (cc == '.') {
      // Look ahead for a digit:
      int nc;
      if (isdigit(nc = get())) {
        unget(nc);
        goto start_fraction;
      }
      unget(nc);
      // Could go immediately to operator: goto seen_period
    }

    if (isdigit(cc)) { // binary, octal, decimal, or hexadecimal literal
      // Types of integer literals:
      enum {
        BIN, OCT, DEC, HEX
      } int_lit = cc == '0' ? OCT : DEC;

      // Lookahead:
      int nc = get();
      if (int_lit == OCT && (nc == 'x' || nc == 'X')) {
        int_lit = HEX;
        token_buf_push(cc); // the 0
        cc = nc; // the x or X
      }
      else
      if (int_lit == OCT && (nc == 'b' || nc == 'B')) {
        int_lit = BIN;
        token_buf_push(cc); // the 0
        cc = nc; // the b or B
      }
      else
        unget(nc); // isdigit(cc)

      do {
        token_buf_push(cc);
        cc = get();

        // Allow for ' between `digits':
        if (cc == '\'') {
          // Keep the ' in the token for now:
          token_buf_push(cc);
          int nc = get();
          if (isdigit(nc) || int_lit == HEX && isxdigit(nc))
            cc = nc;
          else { // Error!
            fprintf(stderr,
                    "(E): [%s:%u] C++14 only allows ' between digits.\n",
                    filename, linenr);
            // what to do?
          }
        }
      } while (isdigit(cc) || int_lit == HEX && isxdigit(cc));
      // !is[x]digit(cc)

      // FIXME: allow hex floats in C
      if (int_lit == OCT || int_lit == DEC) {
        int floating = 0;
        // Seen digits-sequence. Maybe followed by . or e or E?
        if (cc == '.') { // fractional part
        start_fraction:
          floating = 1;
          token_buf_push(cc);
          // digits? FIXME: again allow ' between digits
          while (isdigit(cc = get()))
            token_buf_push(cc);
          // !isdigit(cc)
        }
        // cc != '.' || !isdigit(cc)
        if (cc == 'e' || cc == 'E') { // exponent
          floating = 1;
          token_buf_push(cc);
          if ((cc = get()) == '-' || cc == '+') {
            token_buf_push(cc);
            cc = get();
          }
          // FIXME: no check for at least 1 digit
          // FIXME: again allow ' between digits
          while (isdigit(cc)) {
            token_buf_push(cc);
            cc = get();
          }
          // !isdigit(cc)
        }
        if (floating) {
          if (cc == 'f' || cc == 'F' || cc == 'l' || cc == 'L')
            token_buf_push(cc);
          else
            unget(cc);
          *type = FLOATING;
          break;
        }
      }

      // optional integer suffix: l, ll, lu, llu, u, ul, ull, any case
      if (cc == 'l' || cc == 'L') {
        token_buf_push(cc);
        // maybe another l
        cc = get();
        if (cc == 'l' || cc == 'L') {
          token_buf_push(cc);
          // Here: token is digits[lL][lL]
          cc = get();
        }
        // maybe a u
        if (cc == 'u' || cc == 'U')
          // Here: token is digits[lL][lL]?[u|U]
          token_buf_push(cc);
        else
          unget(cc);
      }
      else if (cc == 'u' || cc == 'U') {
        token_buf_push(cc);
        // maybe an l
        cc = get();
        if (cc == 'l' || cc == 'L') {
          token_buf_push(cc);
          // Here: token is digits[uU][lL]
          cc = get();
        }
        // maybe another l
        if (cc == 'l' || cc == 'L')
          // Here: token is digits[uU][lL]?[lL]
          token_buf_push(cc);
        else
          unget(cc);
      }
      else
        unget(cc);
      *type = INTEGER;
      break;
    }

    /*** STRING (C/C++/Java) ***/

    if (cc == '"') {
    string_token:
      token_buf_push(cc);
      // Watch out for escaped " inside string.
      cc = get();
      while (cc != '"') {
        if (cc == EOF) { // Error!
          fprintf(stderr,
                  "(E): [%s:%u] Unexpected end-of-file in string literal.\n",
                  filename, *line);
          unexpect_eof++;
	  // Better return partial string as token and postpone EOF:
	  *type = STRING;
	  token_buf_close();
	  *token = token_buf;
	  return token_len;
        }
        token_buf_push(cc);
        int nc = get();

        if (cc == '\\') {
          // FIXME: No check on valid escape char!
          // ' " ? \ a b f n r t v
          token_buf_push(nc);
          cc = get();
        }
        else
          cc = nc;
      }
      // cc == '"'
      token_buf_push(cc);
      *type = STRING;
      break;
    }

    /*** CHARACTER (C/C++/Java) ***/

    if (cc == '\'') {
    char_token:
      token_buf_push(cc);
      // Watch out for escaped ' inside char.
      cc = get();
      // Cannot have empty char!
      if (cc == '\'') {
	fprintf(stderr,
		"(E): [%s:%u] Cannot have an empty character literal.\n",
		filename, linenr);
	// Output as token anyway, but count as illegal:
	token_buf_push(cc);
	*type = CHARACTER;
	illegals++;
	break;
      }

      // FIXME: Avoid including too many chars.
      while (cc != '\'') {
        if (cc == EOF) { // Error!
          fprintf(stderr,
                  "(E): [%s:%u] Unexpected end-of-file in character literal.\n",
                  filename, linenr);
          unexpect_eof++;
	  // Better return partial character as token and postpone EOF:
	  *type = CHARACTER;
	  token_buf_close();
	  *token = token_buf;
	  return token_len;
        }
        if (cc == '\n') { // Error!
          fprintf(stderr,
                 "(E): [%s:%u] Cannot have end-of-line in character literal.\n",
                  filename, linenr);
	  illegals++;
	  // Immediately terminate character literal as if ' present.
	  // cc = '\''; make into valid literal??? No!
	  break;
        }
	token_buf_push(cc);
        int nc = get();
        if (cc == '\\') {
          token_buf_push(nc);
          cc = get();
          // FIXME: No check on valid escape char!
          // ' " ? \ a b f n r t v 0[d[d]] xh*
        }
        else {
	  cc = nc;
	  // If first char then expect no more.
	  if (token_len == 2) {
	    if (nc != '\'') {
	      fprintf(stderr,
		      "(E): [%s:%u] Cannot have multi-character literal.\n",
		      filename, linenr);
	      illegals++;
	      // Immediately terminate character literal as if ' present.
	      // cc = '\''; make into valid literal???
	      break;
	    }
	  }
	}
      }
      if (cc == '\'')
	token_buf_push(cc);
      else
	unget(cc);
      *type = CHARACTER;
      break;
    }

    /*** OPERATOR (and PUNCTUATION) (C/C++/Java) ***/

    // Operator and punctuation symbols. Longest match.

    /* Operator or punctuator   Alternative representation
       {        <%
       }        %>
       [        <:
       ]        :>
       #        %:      (not supported here)
       ##       %:%:    (not supported here)
    */

    // Single char operator or punctuator (C/C++/Java)
    // { } [ ] ( ) ; : ? . ~ ! + - * / % ^ = & | < > ,
    // Double char operator or punctuator (C/C++)
    // <: :> <% %>
    // Double char operator or punctuator (C/C++/Java)
    // += -= *= /= %= ^= &= |= == != <= >= && || << >> ++ -- ->
    // Double char operator or punctuator (C++/Java)
    // ::
    // Double char operator or punctuator (C++)
    // .*
    // Triple char operator or punctuator (C/C++/Java)
    // ... <<= >>=
    // Triple char operator or punctuator (C++)
    // ->* <=>
    // Java: @ >>> >>>=

    //seen_period:

    token_buf_push(cc);
    token_buf_close();
    //token=[cc,0];len=1

    if (strstr("{}[]();?~,@", token_buf)) { // allow @ for Java
      // Single char operator/punctuator.
      *type = OPERATOR;
      break;
    }

    if (strstr("<:.-+*/%^&|=!>", token_buf)) { // single or start of double/triple
      // Check second char:
      int c2 = get();
      if (c2 != EOF) {
        token_buf_push(c2);
        //token=[cc,c2];len=2

        // Check third char:
        int c3 = get();
        if (c3 != EOF) {
          token_buf_push(c3);
          token_buf_close();
          //token=[cc,c2,c3,0];len=3
          if (!strcmp(">>>", token_buf)) { // allow >>> for Java
            //token=[>,>,>,0];len=3
            // Look-ahead for =:
            int c4 = get();
            if (c4 == '=') // >>>= for Java
              token_buf_push(c4);
              //token=[>,>,>,=];len=4
            else
              unget(c4);
              //token=[>,>,>,0];len=3
            *type = OPERATOR;
            break;
          }
          //token=[cc,c2,c3,0];len=3

          if (!strcmp("...", token_buf) ||
              !strcmp("<=>", token_buf) ||
              !strcmp("->*", token_buf) ||
              !strcmp("<<=", token_buf) ||
              !strcmp(">>=", token_buf)) {
            // Triple char operator/punctuator.
            *type = OPERATOR;
            break;
          }

          // Maybe double char. Undo the c3 token extension:
          token_buf_pop();
          token_buf_close();
          //token=[cc,c2,0];len=2
        }
        else
          token_buf_close();
          //token=[cc,c2,0];len=2
        unget(c3);

        // Maybe double char.
        static const char * const ops2[] = {
          "<:", "<%", "<=", "<<", ":>",
          "::", ".*", "->", "-=", "--",
          "+=", "++", "*=", "/=", "%>",
          "%=", "^=", "&=", "&&", "|=",
          "||", "==", "!=", ">=", ">>"
        };
        unsigned size = sizeof(ops2) / sizeof(ops2[0]);
        unsigned i;
        for (i = 0; i < size; i++)
          if (!strcmp(ops2[i], token_buf))
            break;
        if (i < size) {
          *type = OPERATOR;
          break;
        }
        //token=[cc,c2,0];len=2

        // Must be single char. Undo the c2 token extension:
        token_buf_pop();
        token_buf_close();
        //token=[cc,0];len=1
      }
      //else token=[cc,0];len=1

      // Must be single char.
      unget(c2);
      *type = OPERATOR;
      break;
    }
    //token=[cc,0];len=1

    /*** PREPROCESSOR (C/C++) ***/

    if (cc == '#') {
      int nc = get();
      if (nc != '#')
        unget(nc);
      else
        token_buf_push(nc);
      *type = PREPROCESSOR;
      break;
    }

    // What is left here? Illegal chars!
    if (!nowarn)
      // Mind non-printing chars!
      fprintf(stderr,
              "(W): [%s:%u] Illegal character `%s%c` (0x%02x) skipped.\n",
              filename, linenr, cc<32?"CTRL-":"", cc<32?cc+64:cc, cc);
    // Count them:
    illegals++;

  } while (1);
  token_buf_close();
  *token = token_buf;
  return token_len;
}

unsigned C_tokenize(const char **token, const char **type,
                    unsigned *line, unsigned *col, unsigned *pos)
{
  enum TokenClass typeid;
  unsigned result = C_tokenize_int(token, &typeid, line, col, pos);
  *type = token_class[typeid];
  return result;
}

// Escape hard newlines in a string.
void RAW_escape(FILE *out, const char *token)
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
void CSV_escape(FILE *out, const char *token)
{
  const char *p;
  // start CSV string:
  fputc('"', out);
  for (p = token; *p; p++) {
    if (*p == '\n') { // escape embedded real new lines
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
void JSON_escape(FILE *out, const char *token)
{
  // C/C++ has escapes: \' \" \? \a \b \f \n \r \t \v \x \0.
  // To preserve, simply escape the backslash and all ":
  const char *p;
  for (p = token; *p; p++) {
    if (*p == '\n') { // escape embedded real new lines
      fputs("\\n", out);
      continue;
    }
    if (*p == '\t') { // escape embedded real TABs
      fputs("\\t", out);
      continue;
    }
    // FIXME: control characters from U+0000 through U+001F must be escaped
    if (*p == '\\' || *p == '"')
      fputc('\\', out);
    fputc(*p, out);
  }
}

// Escape token for output as XML text.
void XML_escape(FILE *out, const char *token)
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
