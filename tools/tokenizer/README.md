# Tokenizer for C/C++ and Java Source

## Introduction

This is a simple C/C++ and Java tokenizer program written in C.
This same repository also offers separate programs for a Python tokenizer
(`pytokenize`) and a JavaScript tokenizer (`jstokenize`). They all share most
of the command-line options and have the same output formats.

Here we focus on the C/C++/Java tokenizer (`tokenize`), but most of this
documentation equally applies to the other tokenizer program. The `Makefile`
builds them all.

The following lexeme classes are recognized:

- identifier
- reserved word/keyword
- binary, octal, decimal, hexadecimal and floating-point numbers
- double-quoted string literal
- single-quoted character literal
- all single, double, and triple operator and punctuation symbols
- the preprocessor tokens # and ##

For each correctly recognized token, the program determines its class/type and
the exact coordinates (line number and column) in the input text of
its starting character. All token literals are output exactly as they appear in
the source text, without any interpretation of escaped characters.

A newline is defined as a single linefeed character `\n` or the combination
carriage return `\r` followed by linefeed `\n`.
Line continuations (a backslash immediately followed by a newline) are handled
at the character input level, so the token recognizers will only see logical
lines. Line and column reflect positions in the physical line structure, not the logical one.

For instance the appearance of a line continuation inside a string literal:

```C
	"A long string literal that is broken here \
to stretch over two lines."
```

upon output as a token becomes:

```C
	"A long string literal that is broken here to stretch over two lines."
```

Moreover, white-space, control characters and comments are skipped and
anything left over is flagged as illegal characters.

Since Java at the lexical level is very close to C and C++, this tokenizer
can also be used for Java, albeit that some literal pecularities are not
recognized. The program looks at the file name extension to determine the
language. This can be overridden (and must be specified in case of using
standard input) by the `-l` option.
Depending on the language setting, the proper set of keywords will be
recognized. For C and C++ their
combined set of (95) keywords is recognized, assuming that a C program will not
inadvertently use C++ keywords as regular identifiers.

## Program options

The program options can be listed with the `-h` option:

```console
$ tokenize -h
A tokenizer for C/C++ (and Java) source code with output in 6 formats.
Recognizes the following token classes: keyword, identifier, integer,
floating, string, character, operator, and preprocessor.

usage: tokenize [ -1cdhjl:m:no:rsvw ] [ FILES ]

Command line options are:
-c       : treat a # character as the start of a line comment.
-d       : print debug info to stderr; implies -v.
-h       : print just this text to stderr and stop.
-j       : assume input is Java (deprecated: use -l Java or .java).
-l<lang> : specify language explicitly (C, C++, Java).
-m<mode> : output mode either plain (default), csv, json, jsonl, xml, or raw.
-n       : output newlines as a special pseudo token.
-o<file> : name for output file (instead of stdout).
-s       : enable a special start token specifying the filename.
-1       : treat all filename arguments as a continuous single input.
-v       : print action summary to stderr.
-w       : suppress all warning messages.
```

The program reads multiple files. Depending on the `-1` option, the files
are either treated as a single input, or processed separately. When processed
separately (no -1 option) the output is as if each file is processed
individually, emitting start and end symbols where appropriate depending on
the mode setting.

## Multiple output modes

The tokenizer has multiple output modes. They are plain text, CSV, JSON, JSONL
and XML. A sample of plain text output looks like this:

```text
(  62,  0) preprocessor: #
(  62,  1) identifier: include
(  62,  9) string: "perfect_hash.h"
(  64,  0) preprocessor: #
(  64,  1) identifier: define
(  64,  8) identifier: token_add
(  64, 17) operator: (
(  64, 18) identifier: cc
(  64, 20) operator: )
(  65,  2) keyword: do
(  65,  5) operator: {
(  65,  7) keyword: if
(  65, 10) operator: (
(  65, 11) identifier: len
(  65, 15) operator: <
(  65, 17) identifier: MAX_TOKEN
(  65, 26) operator: )
(  65, 28) identifier: token
(  65, 33) operator: [
(  65, 34) identifier: len
(  65, 37) operator: ++
(  65, 39) operator: ]
(  65, 41) operator: =
(  65, 43) operator: (
(  65, 44) identifier: cc
(  65, 46) operator: )
(  65, 47) operator: ;
(  65, 49) operator: }
(  65, 51) keyword: while
(  65, 56) operator: (
(  65, 57) integer: 0
(  65, 58) operator: )
(  68,  0) keyword: int
(  68,  4) identifier: get
(  68,  7) operator: (
(  68,  8) operator: )
```

Line numbers are 1 based, columns start at 0 (Emacs-style).
The token classes are:

| Class:       | Description:
|--------------|------------
| identifier   | any identifier
| keyword      | a reserved word
| integer      | integer number irrespective of notation
| floating     | a floating-point number
| string       | a double-quoted string (maybe empty)
| character    | a single-quoted character
| operator     | any operator or punctuator symbol
| preprocessor | either # or ##
| filename     | pseudo token: start of a new file
| newline      | pseudo token: end of logical line

The `filename` token is optional. It will be included when the `-s` option is
provided. It is a pseudo token that provides the filename of the input as the
first token. Similarly, the `newline` is a pseudo token and appears only with
the `-n` option. It signals the end of a logical line. Mind that multiple
newlines occurring in sequence are not suppressed. The `newline` token has no
textual representation, e.g. in XML mode output it will appear as an empty
text element.

### CSV output

CSV output has this header and a few lines of sample rows:

```text
line,column,class,token
...
624,12,operator,:
625,6,identifier,fprintf
625,13,operator,(
625,14,identifier,stdout
625,20,operator,","
625,22,string,"""</tokens>\n"""
...
```

The operator token `,` is escaped with double quotes, like so `","`.
String tokens are escaped as well and any original double quote is doubled.

### JSON output

In JSON output all token values are represented as strings. String class
tokens themselves are properly escaped, especially backslash escape characters
are doubled.

```json
[
...
{ "line": 624, "column": 12, "class": "operator", "token": ":" },
{ "line": 625, "column": 6, "class": "identifier", "token": "fprintf" },
{ "line": 625, "column": 13, "class": "operator", "token": "(" },
{ "line": 625, "column": 14, "class": "identifier", "token": "stdout" },
{ "line": 625, "column": 20, "class": "operator", "token": "," },
{ "line": 625, "column": 22, "class": "string", "token": "\"</tokens>\\n\"" },
...
]
```

There is also a related JSONL mode that outputs one token object per line, but
does not collect them as a JSON array.

### XML output

For XML output, the 3 characters `<`, `>`, and `&` are escaped by replacing
them with the corresponding entities in the character and string class
tokens. (An alternative would be to use the CDATA construct.)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<tokens>
...
<token line="624" column="12" class="operator">:</token>
<token line="625" column="6" class="identifier">fprintf</token>
<token line="625" column="13" class="operator">(</token>
<token line="625" column="14" class="identifier">stdout</token>
<token line="625" column="20" class="operator">,</token>
<token line="625" column="22" class="string">"&lt;/tokens&gt;\n"></token>
...
</tokens>

```

## References

> <a id="1">[1]</a>
[C++14 Final Working Draft n4140](https://github.com/cplusplus/draft/blob/master/papers/n4140.pdf)

> <a id="2">[2]</a>
<https://www.ibm.com/support/knowledgecenter/en/SSGH3R_13.1.3/com.ibm.xlcpp1313.aix.doc/language_ref/lexcvn.html>
