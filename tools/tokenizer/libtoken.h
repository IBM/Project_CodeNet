/* Copyright (c) 2021, 2022 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Code functionality shared by all tokenizers.
*/

#ifndef LIBTOKEN_H
#define LIBTOKEN_H

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

#define MAX_BUF       8  // maximum lookahead in chars

/* Let's assume UTF-8 encoding.
   https://www.cprogramming.com/tutorial/unicode.html
   https://opensource.apple.com/source/tidy/tidy-2.2/tidy/src/utf8.c.auto.html
*/

// Test for start of UTF-8 sequence.
#define utf8_start(cc)  (((cc)&0xC0)!=0x80)
#define utf8_follow(cc) (((cc)&0xC0)==0x80)

#define utf8_len(cc) \
  (((cc)&0xF8)==0xF0 ? 4 : ((cc)&0xF0)==0xE0 ? 3 : ((cc)&0xE0)==0xC0 ? 2 : 1)

typedef enum { C, CPP, JAVA, JAVASCRIPT, PYTHON } Language;

// Program globals:
extern const char *filename/*= "stdin"*/;  // current file being parsed
extern unsigned linenr/*= 1*/;       // physical line number counted from 1
extern unsigned column/*= 0*/;       // char position in physical line, from 0
extern unsigned saved_col/*= 0*/;    // 1-place buf for last column on prev line
extern unsigned char_count/*= 0*/;   // total char/byte count
extern unsigned utf8_count/*= 0*/;   // total utf-8 char count
extern unsigned buffered/*= 0*/;     // number of buffered chars
extern int buffer[MAX_BUF];          // use buffer as multi-char lookahead.

// Program option settings:
extern int debug/*= 0*/;             // when 1 debug output to stderr
extern int verbose/*= 0*/;           // when 1 info output to stderr
extern int nowarn/*= 0*/;            // when 1 warnings are suppressed

extern unsigned illegals/*= 0*/;     // count number of illegal characters
extern unsigned unexpect_eof/*= 0*/; // encountered unexpected EOF
extern int hash_as_comment/*= 0*/;   // when 1 treat # as line comment
extern int newline_token/*= 0*/;     // when 1 output newline pseudo-token
extern int comment_token/*= 0*/;     // when 1 output comments as tokens
extern int whitespace_token/*= 0*/;  // when 1 output adjacent white-space as a token
extern int continuation_token/*= 0*/; // when 1 output line continuation pseudo-token

enum TokenClass {
  /* 0*/ IDENTIFIER,
  /* 1*/ KEYWORD,
  /* 2*/ STRING,
  /* 3*/ CHARACTER,
  /* 4*/ INTEGER,
  /* 5*/ FLOATING,
  /* 6*/ OPERATOR,
  /* 7*/ PREPROCESSOR,
  /* 8*/ LINE_COMMENT,
  /* 9*/ BLOCK_COMMENT,
  /*10*/ WHITESPACE,
  /*11*/ NEWLINE,
  /*12*/ CONTINUATION,
  /*13*/ FILENAME,
  /*14*/ ENDOFFILE
};

extern const char *token_class[];

// keyword lookup function (pointer variable):
// (initialized by set_or_detect_lang())
extern const char *(*is_keyword)(const char *);

extern int get(void);
extern void unget(int cc);
extern Language set_or_detect_lang(const char *source);
extern const char *lang_name(Language lang);
extern int open_as_stdin(const char *file);

extern unsigned C_tokenize_int(const char **token, enum TokenClass *type,
			       unsigned *line, unsigned *col, unsigned *pos);
extern unsigned C_tokenize(const char **token, const char **type,
			   unsigned *line, unsigned *col, unsigned *pos);

extern void  RAW_escape(FILE *out, const char *token);
extern void  CSV_escape(FILE *out, const char *token);
extern void JSON_escape(FILE *out, const char *token);
extern void  XML_escape(FILE *out, const char *token);

#ifdef __cplusplus
}
#endif

#endif /* LIBTOKEN_H */
