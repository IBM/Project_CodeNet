/* Copyright (c) 2020, 2021 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Simple C/C++ (and Java) Tokenizer.
   For the most part assumes that the input source text is grammatically
   correct C or C++ code.
   (Since Java at the lexical level is very close, could in principle
   also be used as Java tokenizer, albeit that not all of its keywords
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
   without any interpretation of escaped characters etc.

   Moreover, skips white-space, control characters and comments and
   flags anything left over as illegal characters.

   See these refs for details on the lexical definitions:
   C++14 Final Working Draft: n4140.pdf
   https://www.ibm.com/support/knowledgecenter/en/SSGH3R_13.1.3/com.ibm.xlcpp1313.aix.doc/language_ref/lexcvn.html

   Shortcomings:
   Column position gets confused when TABs and CRs are present in the input.
   (A TAB is counted as a single character position. A CR causes a transition
   to a new line.)
   No trigraph sequences (??x) are recognized.
   No alternative tokens except keyword ones for certain operators.
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

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <unistd.h>		/* getopt() */
#include <libgen.h>		/* basename() */

/* Let's introduce more parameters so that it becomes easier to
   configure the state-machines for the various tokens.
   Use a NUL character to disable the parameter, i.e., a NUL value
   means "this char is not in effect; a test for it fails".

   FIXME: not yet used!
*/
// Character that may be used to group digits in a number:
#define CFG_DIGITS_SEP		'\''
// Extra character that may start an identifier:
#define CFG_ID_START_EXTRA	'_'
// Extra character that may continue an identifier:
// Maybe allows a set of characters, like also $?
#define CFG_ID_CONT_EXTRA	'_'
// May a floating-point number start with a decimal point:
//#define CFG_FLOAT_DOT

// FIXME: make token size dynamic.
#define MAX_TOKEN 65535         // maximum token length in chars (\0 exclusive)
#define MAX_BUF 8               // maximum buffer size in chars

// Program globals:
static char *filename = "stdin";// current file being parsed
static unsigned linenr = 1;     // line number counted from 1
static unsigned column = 0;     // char position in line, counted from 0
static unsigned char_count = 0; // total char/byte count
static unsigned utf8_count = 0; // total utf-8 char count
static char buffer[MAX_BUF];    // use buffer as multi-char lookahead.
static unsigned buffered = 0;   // number of buffered chars
static unsigned saved_col = 0;  // one-place buf for last column on prev line
static unsigned illegals = 0;	// count number of illegal characters
static unsigned unexpect_eof = 0; // encountered unexpected EOF
static unsigned num_files = 0;	// number of files read
// keyword lookup function:
static const char *(*is_keyword)(const char *, unsigned);

// Program option settings:
static int debug = 0;		// when 1 debug output to stderr
static int verbose = 0;         // when 1 info output to stderr
static int nowarn = 0;		// when 1 warnings are suppressed
static int hash_as_comment = 0;	// when 1 treat # as line comment
static int start_token = 0;	// when 1 start filename pseudo-token
static int newline_token = 0;	// when 1 output newline pseudo-token
static int continuous_files = 0;// when 1 do not reset after each file
static enum { C, CPP, JAVA, PYTHON } source = CPP;

// Use perfect hash function.
#include "cpp_keywords.h"	// is_cpp_keyword()
#include "java_keywords.h"	// is_java_keyword()

// Append char cc to token; discard when no more room:
#define token_add(cc) \
  do { if (len < MAX_TOKEN) token[len++] = (cc); } while(0)

#define utf8_start(cc)	(((cc)&0xC0)!=0x80)
#define utf8_follow(cc) (((cc)&0xC0)==0x80)

#define utf8_len(cc) \
  (((cc)&0xF8)==0xF0 ? 4 : ((cc)&0xF0)==0xE0 ? 3 : ((cc)&0xE0)==0xC0 ? 2 : 1)

/* Let's assume UTF-8 encoding.
   https://www.cprogramming.com/tutorial/unicode.html
   https://opensource.apple.com/source/tidy/tidy-2.2/tidy/src/utf8.c.auto.html
*/

void unget(int cc)
{
  if (cc == EOF) return;
  if (buffered < MAX_BUF) {
    if (cc == '\n') {
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

// Act like getchar().
// Mind linenr,column apply to physical lines not logical ones.
int get(void)
{
  int cc;

 restart:
  // Get the next character:
  if (buffered) // chars available in lookahead buffer
    cc = buffer[--buffered]; // never EOF
    // cc might be \ and followed by fresh \n
    // Note: never can have buffered line continuation, i.e., \ \n.
  else { // must read fresh char
    cc = getchar();
    if (cc == EOF) return EOF;
    // Count all chars, even the \ of a line continuation:
    char_count++;
    if (utf8_start(cc)) utf8_count++;
  }

  // Treat Mac line endings ('\r') as regular newlines:
  if (cc == '\n' || cc == '\r') {
    linenr++;
    saved_col = column;
    column = 0;
    return '\n';
  }

  // Deal with \ line continuations! Must look ahead.
  if (cc == '\\') {
    // Must look ahead; mind next char might be buffered!
    if (buffered)
      // Never can have \n for next char:
      assert(buffer[buffered-1] != '\n');
    else {
      // Must get fresh character:
      int nc = getchar(); // do not count yet; maybe must unget

      // Maybe \r \n combination?
      if (nc == '\r') {
	// Look ahead for \n:
	int c2 = getchar(); // do not count yet; maybe must unget
	if (c2 == '\n') {
	  // Skip \r but count it:
	  char_count++;
	  utf8_count++;
	  nc = '\n';
	}
	else {
	  unget(c2);
	  // nc == '\r'
	}
      }

      if (nc == '\n') { // 1 logical line: discard \\n combo:
	char_count++; // counts the newline
	linenr++;     // on next physical line
	// never unget a continuation
	//saved_col = column;
	column = 0;

	// Still need to get a character.
	// Could again start a line continuation!
	goto restart;
      }
      // Mind nc not \n but maybe \ or \r, then goes to buffer.
      unget(nc);
    }
    // cc == '\\' a regular backslash
  }
  column++;
  return cc;
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
   Skips white-space, control characters and comments and flags anything
   left over as illegal characters.

   (In the order of 20 tests per single character worst-case.)

   Returns 0 upon EOF or error.
*/
int tokenize(char *token, const char **type, unsigned *line, unsigned *col)
{
  unsigned len;
  int cc;
  *type = "";

  do { // infinite loop; after token recognized breaks out.
    len = 0;
    cc = get();

  restart:
    // cc already read.

    /*** WHITE-SPACE ***/

    // Skip (abutted) space and control chars and comments:
    // [ \t\f\v\n]
    //    while (cc <= ' ' && cc != EOF)
    while (isspace(cc) && cc != EOF && cc != '\n')
      cc = get();
    if (cc == EOF)
      return 0;
    if (cc == '\n') {
      if (newline_token) {
	// token is empty.
	*line = linenr-1;
	*col  = saved_col;
	*type = "newline";
	break;
      }
      cc = get();
      goto restart;
    }
    // !isspace(cc) && cc != EOF

    /*** OPTIONAL # LINE COMMENT (to ignore preprocessor statements) ***/
    // Java: no preprocessor directives.

    if (cc == '#' && hash_as_comment) {
      // Skip till end-of-line (\n exclusive):
      while ((cc = get()) != '\n' && cc != EOF)
	;
      // cc == '\n' || cc == EOF
      goto restart;
    }

    /*** LINE COMMENT AND BLOCK COMMENT (C/C++/Java) ***/

    if (cc == '/') {
      cc = get();
      if (cc == '/') {
        // Skip till end-of-line (\n exclusive):
        while ((cc = get()) != '\n' && cc != EOF)
          ;
        // cc == '\n' || cc == EOF
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

    // Start collecting a token.
    // Token should finish with cc being last char of token!
    *line = linenr;
    *col = column-1; // 1 char lookahead

    /*** CHAR and STRING PREFIX (C/C++) ***/

    // Allow u,U,L prefix for string and char
    // FIXME: allow u8 as prefix for string
    if (cc == 'L' || cc == 'u' || cc == 'U') {
      token[len++] = cc;
      cc = get();
      if (cc == '"')
        goto string_token;
      if (cc == '\'')
        goto char_token;
      // u,U,L will be interpreted as (start of) identifier.
      unget(cc); // char after u,U,L
      cc = token[--len]; // restore original and remove from token
    }

    /*** IDENTIFIER (C/C++/Java) and KEYWORD (C/C++) ***/
    // Java: false, true, null are literals
    // FIXME: Flag to allow .letter as part of identifier?
    // (compound identifier)

    // Simplistic solution to allowing Unicode: allow any char >= 128 without
    // actual checking for UTF-8.
    if (isalpha(cc) || cc == '_' || cc == '$' || cc & 0x80) {
      // First char always fits.
      token[len++] = cc;
      while (isalnum(cc = get()) || cc == '_' || cc == '$' || cc & 0x80)
        token_add(cc);
      unget(cc);
      *type = is_keyword(token, len) ? "keyword" : "identifier";
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
	token_add(cc); // the 0
	cc = nc; // the x or X
      }
      else
      if (int_lit == OCT && (nc == 'b' || nc == 'B')) {
	int_lit = BIN;
	token_add(cc); // the 0
	cc = nc; // the b or B
      }
      else
	unget(nc); // isdigit(cc)

      do {
        token_add(cc);
        cc = get();

	// Allow for ' between `digits':
        if (cc == '\'') {
          // Keep the ' in the token for now:
          token_add(cc);
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
	  token_add(cc);
	  // digits? FIXME: again allow ' between digits
	  while (isdigit(cc = get()))
	    token_add(cc);
	  // !isdigit(cc)
	}
	// cc != '.' || !isdigit(cc)
	if (cc == 'e' || cc == 'E') { // exponent
	  floating = 1;
	  token_add(cc);
	  if ((cc = get()) == '-' || cc == '+') {
	    token_add(cc);
	    cc = get();
	  }
	  // FIXME: no check for at least 1 digit
	  // FIXME: again allow ' between digits
	  while (isdigit(cc)) {
	    token_add(cc);
	    cc = get();
	  }
	  // !isdigit(cc)
	}
	if (floating) {
	  if (cc == 'f' || cc == 'F' || cc == 'l' || cc == 'L')
	    token_add(cc);
	  else
	    unget(cc);
	  *type = "floating";
	  break;
	}
      }

      // optional integer suffix: l, ll, lu, llu, u, ul, ull, any case
      if (cc == 'l' || cc == 'L') {
        token_add(cc);
        // maybe another l
        cc = get();
        if (cc == 'l' || cc == 'L') {
          token_add(cc);
          // Here: token is digits[lL][lL]
          cc = get();
        }
        // maybe a u
        if (cc == 'u' || cc == 'U')
          // Here: token is digits[lL][lL]?[u|U]
          token_add(cc);
        else
          unget(cc);
      }
      else if (cc == 'u' || cc == 'U') {
        token_add(cc);
        // maybe an l
        cc = get();
        if (cc == 'l' || cc == 'L') {
          token_add(cc);
          // Here: token is digits[uU][lL]
          cc = get();
        }
        // maybe another l
        if (cc == 'l' || cc == 'L')
          // Here: token is digits[uU][lL]?[lL]
          token_add(cc);
        else
          unget(cc);
      }
      else
        unget(cc);
      *type = "integer";
      break;
    }

    /*** STRING (C/C++/Java) ***/

    if (cc == '"') {
    string_token:
      // First char always fits.
      token[len++] = cc;
      // Remember start position:
      unsigned lin = linenr;
      // Watch out for escaped " inside string.
      cc = get();
      while (cc != '"') {
        if (cc == EOF) { // Error!
          fprintf(stderr,
		  "(E): [%s:%u] Unexpected end-of-file in string literal.\n",
		  filename, lin);
	  unexpect_eof++;
          return 0;
        }
        token_add(cc);
        int nc = get();

        if (cc == '\\') {
	  // FIXME: No check on valid escape char!
	  // ' " ? \ a b f n r t v
	  token_add(nc);
          cc = get();
        }
        else
          cc = nc;
      }
      // cc == '"'
      token_add(cc);
      *type = "string";
      break;
    }

    /*** CHARACTER (C/C++/Java) ***/

    if (cc == '\'') {
    char_token:
      // First char always fits.
      token[len++] = cc;
      // Watch out for escaped ' inside char.
      cc = get();
      // FIXME: Cannot have empty char!
      while (cc != '\'') {
        if (cc == EOF) { // Error!
          fprintf(stderr,
		  "(E): [%s:%u] Unexpected end-of-file in char literal.\n",
		  filename, linenr);
	  unexpect_eof++;
          return 0;
        }
        token_add(cc);
        int nc = get();
        if (cc == '\\') {
          token_add(nc);
          cc = get();
          // FIXME: No check on valid escape char!
          // ' " ? \ a b f n r t v 0[d[d]] xh*
        }
        else
          cc = nc;
      }
      // cc == '\''
      token_add(cc);
      *type = "character";
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

    // First char always fits.
    token[len++] = cc;
    token[len] = '\0';
    //token=[cc,0];len=1

    if (strstr("{}[]();?~,@", token)) { // allow @ for Java
      // Single char operator/punctuator.
      *type = "operator";
      break;
    }

    if (strstr("<:.-+*/%^&|=!>", token)) { // single or start of double/triple
      // Check second char:
      int c2 = get();
      if (c2 != EOF) {
        token[len++] = c2;
	//token=[cc,c2];len=2

        // Check third char:
        int c3 = get();
        if (c3 != EOF) {
          token[len++] = c3;
          token[len] = '\0';
	  //token=[cc,c2,c3,0];len=3
	  if (!strcmp(">>>", token)) { // allow >>> for Java
	    //token=[>,>,>,0];len=3
	    // Look-ahead for =:
	    int c4 = get();
	    if (c4 == '=') // >>>= for Java
	      token[len++] = c4;
	      //token=[>,>,>,=];len=4
	    else
	      unget(c4);
  	      //token=[>,>,>,0];len=3
            *type = "operator";
            break;
	  }
	  //token=[cc,c2,c3,0];len=3

          if (!strcmp("...", token) ||
              !strcmp("<=>", token) ||
              !strcmp("->*", token) ||
              !strcmp("<<=", token)) {
            // Triple char operator/punctuator.
            *type = "operator";
            break;
          }

          // Maybe double char. Undo the c3 token extension:
          token[--len] = '\0';
	  //token=[cc,c2,0];len=2
        }
	else
	  token[len] = '\0';
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
          if (!strcmp(ops2[i], token))
            break;
        if (i < size) {
          *type = "operator";
          break;
        }
	//token=[cc,c2,0];len=2

        // Must be single char. Undo the c2 token extension:
        token[--len] = '\0';
	//token=[cc,0];len=1
      }
      //else token=[cc,0];len=1

      // Must be single char.
      unget(c2);
      *type = "operator";
      break;
    }
    //token=[cc,0];len=1

    /*** PREPROCESSOR (C/C++) ***/

    if (cc == '#') {
      int nc = get();
      if (nc != '#')
        unget(nc);
      else
        token[len++] = nc;
      *type = "preprocessor";
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
  // len <= MAX_TOKEN
  token[len] = '\0';
  return 1;
}

// Escape token for output as CSV string.
void CSV_escape(FILE *out, const char *token)
{
  const char *p;
  // start CSV string:
  fputc('"', out);
  for (p = token; *p; p++) {
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
  // To preserve, simply escape the escape and all ":
  const char *p;
  for (p = token; *p; p++) {
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

int main(int argc, char *argv[])
{
  extern char *optarg;
  extern int opterr;
  extern int optind;
  int option;
  char const *opt_str = "1cdhjl:m:no:rsvw";
  char usage_str[80];

  char token[MAX_TOKEN+1];
  const char *type;
  unsigned line;
  unsigned col;

  char *outfile = 0;
  enum { PLAIN, CSV, JSON, JSONL, XML, RAW } mode = PLAIN;
  int first_time = 1;
  int explicit_source = 0;

  sprintf(usage_str, "usage: %%s [ -%s ] [ FILES ]\n", opt_str);

  /* Process arguments: */
  while ((option = getopt(argc, argv, opt_str)) != EOF) {
    switch (option) {

    case '1':
      continuous_files = 1;
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
"floating, string, character, operator, and preprocessor.\n\n", stdout);
fprintf(stderr, usage_str, basename(argv[0]));
fputs(
"\nCommand line options are:\n"
"-c       : treat a # character as the start of a line comment.\n"
"-d       : print debug info to stderr; implies -v.\n"
"-h       : print just this text to stderr and stop.\n"
"-j       : assume input is Java (deprecated: use -l Java or .java).\n"
"-l       : specify language explicitly (C, C++, Java).\n"
"-m<mode> : output mode either plain (default), csv, json, jsonl, xml, or raw.\n"
"-n       : output newlines as a special pseudo token.\n"
"-o<file> : name for output file (instead of stdout).\n"
"-s       : enable a special start token specifying the filename.\n"
"-1       : treat all filename arguments as a continuous single input.\n"
"-v       : print action summary to stderr.\n"
"-w       : suppress all warning messages.\n",
      stderr);
      return 0;

    case 'j':
      source = JAVA;
      explicit_source = 1;
      break;

    case 'l':
      if (!strcmp(optarg, "C"))
	source = C;
      else if (!strcmp(optarg, "C++"))
	source = CPP;
      else if (!strcmp(optarg, "Java"))
	source = JAVA;
      else {
	if (!nowarn)
        fprintf(stderr, "(W): Unknown source %s (using C).\n", optarg);
      }
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
    if (!explicit_source) {
      // Determine language from extension:
      int len = strlen(filename);
      if (len > 2 && !strcmp(filename+len-2, ".c"))
	source = C;
      else if (len > 4 && !strcmp(filename+len-4, ".cpp"))
	source = CPP;
      else if (len > 5 && !strcmp(filename+len-5, ".java"))
	source = JAVA;
    }

  doit:
    if (verbose) fprintf(stderr, "(I): Processing file %s...\n", filename);
    num_files++;

    // Determine which keyword lookup function to use:
    is_keyword = source == JAVA ? is_java_keyword : is_cpp_keyword;

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
        if (!strcmp(type, "string") ||
            // Do we need this too? Yes!
            !strcmp(type, "character") && strchr(token, '"') ||
            !strcmp(type, "character") && strchr(token, ','))
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
        if (!strcmp(type, "string") || !strcmp(type, "character"))
          JSON_escape(stdout, token);
        else
          fputs(token, stdout);
        fputs("\" }", stdout);
        break;
      case XML:
        fprintf(stdout, "<token line=\"%u\" column=\"%u\" class=\"%s\">",
                line, col, type);
        if (!strcmp(type, "string")
            || !strcmp(type, "character")
            || !strcmp(type, "operator"))
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
