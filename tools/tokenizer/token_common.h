/* Copyright (c) 2021 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Code functionality shared by all tokenizers.
*/

#ifndef TOKEN_COMMON_H
#define TOKEN_COMMON_H

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

// FIXME: make token size dynamic.
#define MAX_TOKEN 65535  // maximum token length in chars (\0 exclusive)
#define MAX_BUF       8  // maximum lookahead in chars

// Test for start of UTF-8 sequence.
#define utf8_start(cc)          (((cc)&0xC0)!=0x80)

// Append char cc to token; discard when no more room:
#define token_add(cc) \
  do { if (len < MAX_TOKEN) token[len++] = (cc); } while(0)

typedef enum { C, CPP, JAVA, JAVASCRIPT, PYTHON } Language;

// Program globals:
extern char *filename/*= "stdin"*/;  // current file being parsed
extern unsigned linenr/*= 1*/;       // physical line number counted from 1
extern unsigned column/*= 0*/;       // char position in physical line, from 0
extern unsigned char_count/*= 0*/;   // total char/byte count
extern unsigned utf8_count/*= 0*/;   // total utf-8 char count

extern int buffer[MAX_BUF];          // use buffer as multi-char lookahead.
extern unsigned buffered/*= 0*/;     // number of buffered chars
extern unsigned saved_col/*= 0*/;    // 1-place buf for last column on prev line
extern unsigned illegals/*= 0*/;     // count number of illegal characters
extern unsigned unexpect_eof/*= 0*/; // encountered unexpected EOF
extern unsigned num_files/*= 0*/;    // number of files read

// Program option settings:
extern int debug/*= 0*/;             // when 1 debug output to stderr
extern int verbose/*= 0*/;           // when 1 info output to stderr
extern int nowarn/*= 0*/;            // when 1 warnings are suppressed
extern Language source/*= C*/;       // language mode

extern const char *is_keyword(const char *word,
                              const char *table[], unsigned size);

extern int get(void);
extern void unget(int cc);
extern Language detect_lang(void);

#endif /* TOKEN_COMMON_H */
