# Tokenizer for C/C++ and Java Source

## Introduction

This is a simple C/C++ and Java tokenizer program written in C.
This same repository also offers separate programs for a Python tokenizer
(`pytokenize`) and a JavaScript tokenizer (`jstokenize`). They all share most
of the command-line options and have the same output formats.

Here we focus on the C/C++/Java tokenizer (`tokenize`), but most of this
documentation equally applies to the other tokenizer program.
The `Makefile` builds them all.

The following lexeme classes are recognized:

- identifier
- reserved word/keyword of the language of the input source
- binary, octal, decimal, hexadecimal and floating-point numbers
- double-quoted string literal
- single-quoted character literal
- all single, double, and triple operator and punctuation symbols
- the preprocessor tokens # and ##
- a number of pseudo tokens depending on selected options

For each correctly recognized token, the program determines its class/type and
the exact coordinates (line number and column) in the input text of
its starting character. All token literals are output exactly as they appear in
the source text, without any interpretation of possibly escaped characters.

A newline is defined as a single linefeed character `\n`, a carriage return
`\r`, or the combination carriage return `\r` followed by linefeed `\n`.
Line continuations, i.e., a backslash immediately followed by a newline, are handled
at the character input level, so the token recognizers will only see logical
lines. Line and column coordinates however reflect positions in the physical line
structure, not the logical one. When so requested, logical line endings are
output as `newline` pseudo tokens and will be represented by a linefeed
character. Similarly, when requested, continuations are output as
`continuation` pseudo tokens and will be represented by a backslash-escaped
linefeed `\\n`.

For instance the appearance of a line continuation inside a string literal:

```C
	"A long string literal that is broken here \
to stretch over two lines."
```

upon output as a token becomes:

```C
	"A long string literal that is broken here to stretch over two lines."
```

White-space (SPACE and TAB characters), certain control characters, and comments are
normally skipped and anything left over is flagged as illegal characters.

Since Java at the lexical level is very close to C and C++, this tokenizer
can also be used for Java, albeit that some literal pecularities are not
recognized. The program looks at the file name extension to determine the
language. This can be overridden (and must be specified in case of using
standard input) by the `-l` option.
Depending on the language setting, the proper set of keywords will be
recognized.

## Program options

The program options can be listed with the `-h` option:

```console
$ tokenize -h
A tokenizer for C/C++ (and Java) source code with output in 6 formats.
Recognizes the following token classes: keyword, identifier, integer,
floating, string, character, operator, and preprocessor.

usage: tokenize [ -1acdhjkl:m:nNo:rsvwW ] [ FILES ]

Command line options are:
-a       : append to output file instead of create or overwrite.
-c       : treat a # character as the start of a line comment.
-d       : print debug info to stderr; implies -v.
-h       : print just this text to stderr and stop.
-k       : output line and block comments as tokens.
-l<lang> : specify language explicitly (C, C++, Java).
-m<mode> : output mode either plain (default), csv, json, jsonl, xml, or raw.
-n       : output newlines as a special pseudo token.
-N       : output line continuations as a special pseudo token.
-o<file> : write output to this file (instead of stdout).
-s       : enable a special start token specifying the filename.
-1       : treat all filename arguments as a continuous single input.
-v       : print action summary to stderr.
-w       : suppress all warning messages.
-W       : output adjacent white-space as a token.
```

The program reads multiple files. Depending on the `-1` option, the files
are either treated as a single input, or processed separately. When processed
separately (no -1 option) the output is as if each file is processed
individually, emitting start and end symbols where appropriate depending on
the mode setting.

## Multiple output modes

The tokenizer has multiple output modes. They are plain text, CSV, JSON, JSONL
XML, and RAW mode. A sample of plain text output looks like this:

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

| Class:        | Description:
|---------------|------------
| identifier    | any identifier
| keyword       | a reserved word
| integer       | integer number irrespective of notation
| floating      | a floating-point number
| string        | a double-quoted string (maybe empty)
| character     | a single-quoted character
| operator      | any operator or punctuator symbol
| preprocessor  | either `#` or `##`

The following classes are only recognized when the appropriate switch has been set:

| Class:        | Description:                           | Switch:
|---------------|----------------------------------------|---------
| line_comment  | treat `#` till end of line as comment  | -c -k
| line_comment  | a comment that starts with `//`        | -k
| block_comment | a comment enclosed in `/*` and `*/`    | -k
| filename      | pseudo token: start of a new file      | -s
| newline       | pseudo token `\n`: end of logical line | -n
| continuation  | pseudo token `\\n`: line continuation  | -N
| whitespace    | adjacent white-space                   | -W

The `filename` token is optional. It will be included when the `-s` option is
provided. It is a pseudo token that provides the filename of the input as the
first token. Similarly, the `newline` is a pseudo token and appears only with
the `-n` option. It signals the end of a logical line. Mind that multiple
newlines occurring in sequence are not suppressed nor aggregated but appear as
separate newline tokens (the same holds for continuations).
The `newline` token will
be represented by a linefeed character (LF). Depending on the output mode this
will be escaped appropriately. The `-W` would normally also collect any
newlines except when `-n` is a also set and continuations except when `-N` is
set in which case they are treated as separate tokens. To summarize, the valid
combinations of these options and their effect are:

| Switches: | Effect on output:
|-----------|------------------
|           | all white-space, line endings inclusive, discarded
| -n        | newline tokens for logical lines
| -N        | continuation tokens
| -W        | whitespace tokens inclusive all physical line endings
| -n -N     | newline and continuation tokens
| -W -n     | whitespace tokens and newline tokens separately
| -W -N     | whitespace tokens and continuation tokens separately
| -W -n -N  | whitespace, newline, and continuation all separately

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
String tokens are always escaped and any original double quote is doubled.
A newline on its own or as part of whitespace will appear escaped as `\n`.
A whitespace token text will appear inside double quotes. A continuation token
will appear as `"\\n"`.

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

## tokML

Recently a new program has been added: `tokml`. As the name suggests the
output is in XML format but unlike the `-mxml` option to `tokenize`, `tokml`
outputs the original source code annotated with XML elements that supply the
token information. This is an approach identical to what `srcML` does for a
parse tree. The precise XML syntax used is defined by the RelaxNG schema in
the file `tokml-schema.rnc`.

The XML annotation makes it very convenient to apply XPath and XQuery queries
to the token stream, e.g. by using tools like `xidel` and `xmlstarlet`.

## References

> <a id="1">[1]</a>
[C++14 Final Working Draft n4140](https://github.com/cplusplus/draft/blob/master/papers/n4140.pdf)

> <a id="2">[2]</a>
<https://www.ibm.com/support/knowledgecenter/en/SSGH3R_13.1.3/com.ibm.xlcpp1313.aix.doc/language_ref/lexcvn.html>
