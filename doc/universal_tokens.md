# Proposal, considerations and rationale for a "Universal tokenizer output stream specification"

## What is a tokenizer?

A tokenizer is a procedure usually implemented as a computer program that
splits an input text in smaller pieces that have a certain significance. One
typical application is to split a sentence in its constituting words and
punctuation symbols. In the realm of programming languages a tokenizer is used
by almost every compiler and interpreter to split the input program text in
chunks that make up the atomic terminal symbols of the language grammar.
These chunks are called tokens.
There are 2 broad classes of tokens

1. tokens with a fixed prescribed representation
2. tokens that are defined by rules (e.g. by a regular expression)

The former class typically consists of operator symbols and reserved words;
the latter class allows for user-defined identifiers and the notation of
specific numeric constants and string literals.

## Purpose of tokens

The main purpose of tokens depends on the application. A compiler or
interpreter typically would be happy with a stream of tokens that ignores all
white-space and comments in the input text. Other uses might prefer to keep
the comments. For instance a syntax highlighting program would use a
particular font and color to render comments.

So the first question is: do we discard white-space and comments or not?
A troubling aspect of comments is that it includes block comments that can
stretch over several physical input lines. A token output format (to be
discussed in more detail below) can thus not be simply line based in that case.

A nice and preferred aspect of the definition of a token would be that its
literal text string fits on a single line of output irrespective of the actual
output format chosen. For instance XML has no problem with multi-line text;
in contrast JSON strings must fit on a single line but allow for embedded
escaped newlines.

So an important second question is: do we enforce that tokens are output 1 per
line?

This is convenient for many Unix text utilities that process their input line
by line.

## Aspects of tokens

One way of proceeding is to look at how each supported programming language
defines its tokens and try to find a common intersection of token classes.
Here we work from the other end, and first look at some general aspects that
we might like to know about the tokens.

What are aspects of a token (assume we already have precise definitions) that
could be of general interest:

1. Obviously we want to know the literal token text itself.
2. Although maybe redundant, the length in bytes of the token text could be
   useful.
3. Some indication of the location of the token in the text is deemed useful.
   These coordinates could be an absolute position, or a (line,column)
   combination, or both.
4. A classification of the token in a category (token class).

Additionally some more context could be of use, like

5. What is the name of the source file, and 
6. explicit token stream begin and end indicators when multiple files are
   processed.
7. We may even go beyond the lexical level: the same token literal
   may be used in different contexts, with different meanings. Think of
   `*` as the multiplication operator and `*` as the _pointer-to_
   symbol in a type definition. Should the token class convey these
   distinctions? Are we willing to fully parse the source input to
   derive these semantic annotations?

### token classes

Here we assume that a token class is defined at the lexical level;
there is no need to know the grammar of the language and do a parse to
derive this classification.
Some reasonable token class names, used and applicable across many languages
are:

- identifier
- reserved word/keyword (does not include standard functions etc.)
- number (lump all numbers together?), or split up like:
  * integer number (no fraction; make distinction on notation?)
  * floating-point number
- single quoted (character) literal (at least 1 character?)
- double quoted (string) literal
- operator
  * punctuation (hard to distinguish from operator sometimes)
- language-specific special tokens like # and ## for CPP in C/C++

Suggestion for generic token class names:

| Class:       | Description:
|--------------|------------
| identifier   | any identifier
| keyword      | a reserved word
| integer      | integer number irrespective of notation
| floating     | a floating-point number
| string       | a double-quoted string (maybe empty)
| character    | a single-quoted character (or string)
| operator     | any symbol used to operate on values
| punctuator   | any  symbol used for punctuation
| preprocessor | either # or ##
| filename     | pseudo token: start of a new file
| newline      | pseudo token: end of logical line

Quite often, too much specialization will be hard to undo;
additional specialization will be easy to implement by some post-processing
filter program using sed or awk.
For instance,
identifiers can be checked against a list of standard function names and
hence separated in these and user identifiers.
Operator symbols are easily grouped in various sub-classes like arithmetic,
logical, relational, etc. or just unary and binary. But the roles of
some symbols cannot be correctly distinguished without proper semantic
annotation, e.g.. the symbol `<` could be part of a template
definition in C++ or merely the less-than operator.

Suggestion for a set of punctuator symbols:
```console
[ ] ( ) { } . , ? : :: ; ... @
```

Suggestion for a set of operator symbols:
```console
-> ->* .* ++ -- * / % + - << >>
== != < > <= >= <=>
~ ! | || & && ^
=  *= /= %= += -= <<= >>= >>>= &= ^==
```

## Output formats

An important guideline for the choice of an output format is its flexibility
of use. The output should be easy to post-process preferable by standard
open-source tools. We identify 3 formats that come to mind and fit the bill:

1. **CSV**: simple line-based format that is easily parsed by many available
utilities like `csvkit`. Requires that we have the same number of fields per
token of course. Mind that we need to observe the definition of quoted text in
CSV and encode tokens accordingly. This is something we need to do for most
other formats too.
2. **JSON**: very popular and not line-based.
3. **XML**: diminishing popularity but a solid and standardized format.

Both JSON and XML are very flexible and also offer the possibility of
validating the format against a schema. Both are of course much more verbose
than simple CSV.

Many tools use a proprietary format that is tailored to their needs.
Examples are Python's syntax highlighter
[pygmentize](https://pygments.org/docs/tokens/#module-pygments.token)
and the [ANTLR4](https://www.antlr.org/api/Java/org/antlr/v4/runtime/Token.html) lexer tokens output format.

## Proposal for CSV

Every token will occupy one CSV record, i.e., one physical line.
The various fields are separated by commas. Care has to be taken to
escape special characters: a comma itself has to be enclosed in double
quotes; double quoted strings must have their double quotes doubled.

Header: `line,column,class,token`

## Proposal for JSON

If we choose to represent each token on a single line, it is best to adopt the
JSON Lines specification, i.e., have a single JSON object per line. Officially
such a file is not valid JSON, but each line is.

Object keys: `line`, `column`, `class`, `token`

A more compact but less descriptive alternative is to simply use an
array per token with a fixed number of assigned elements. For instance
the first element would be the line number, the second the column
number, the third the token class and the fourth the token string.

## Proposal for XML

In XML we have the option of storing data in either attributes of elements or
as the text contents of the element. Simple-typed data is best stored as
attributes. Free text and longer strings should become the text node of an
element. It makes sense to have an element per token and collect all token
elements under some root element.

Elements: `<tokens>`, `<token>`

Attributes: `line`, `column` `class`

## Question summary

- output white-space and comments or not?
- continue in case of errors or not?
- what format to use? all on single line?
- what character encoding to use?
- distinguish operator and punctuation symbols?
- several (a hierarchy of) operator classes?
- annotate with semantic information gleaned from parse tree?
- distinguish integer and floating-point numbers?
- even further distinction in octal, decimal, hexadecimal?
- absolute position, line/column, or both?
- apart from token literal, class, and coordinates anything else?

## References

> <a id="1">[1]</a>
[Tokenizers: How machines read](https://blog.floydhub.com/tokenization-nlp/)

> <a id="2">[2]</a>
Daniel P Delorey, Charles Knutson, Mark Davies,
[Mining Programming Language Vocabularies from Source Code](https://www.researchgate.net/publication/228825985_Mining_Programming_Language_Vocabularies_from_Source_Code),
December 2008
