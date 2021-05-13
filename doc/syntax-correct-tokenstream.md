# A Syntactically Correct Token Stream

## Introduction

With some ingenuity in terms of defining token classes and the symbols that
represent them, it is possible to tokenize source code input of certain
programming languages such that the token stream itself is a syntactically
correct program. By the latter we mean that the token stream can be correctly
parsed as a sentence of the language grammar. Of course, all semantic aspects
such as use of identifiers (uniquely declared within a scope), application of
operators to the correctly typed values, etc. are no longer valid.

Apart from being an interesting curiosity,
being syntactically correct makes it possible to read the program as a
template: the complete grammatical structure is still clearly present,
especially if we present the tokenized program text in a pretty-printed form.

The following sections will show the details of the tokenization process as
applied to the programming language C. It should be obvious how a similar
approach can be developed for most imperative programming languages such as
C++, Java, and Python (pretty-printing Python might be a bit of a challenge).

## Approach

So how can we tokenize C source code in such a way that the result is still
syntactically correct?

The trick to achieve this is to choose the right representative for each
token class, i.e., the symbol used to designate a certain token class is a
correct literal that belongs to that token class, a representative.
Instead of the usual class names like number, operator, punctuator,
we choose representative literals for those classes.

Another subtle detail is to choose the least number of representatives of
operators to ensure that expressions and other constructs involving operators
will remain syntactically correct after the transformation. To represent any
operator we therefore choose the asterisk symbol (`*`) which can either be
used as a unary or an infix operator and moreover allows pointers to be
correctly declared. Unfortunately, replacing all minus signs (`-`) with `*`
might lead to errors in case of negative numbers, hence we make an exception
of it and will add the minus sign as an additional explicit operator token.
All other operators are not further distinguished (they all appear as `*`).

For strings and character literals we make sure that their representatives do
not contain a space character. As is commonly the case, we reserve the space
character as the separator between tokens. That way simply splitting the input
at white-space can fully reconstruct the individual tokens when needed.

Putting all tokens on a single line might cause problems for certain tools
that have some input line length limit. Moreover, the C pre-processor
directives are not free-format and require to be put on a single (logical)
line. To overcome this problem one could simply discard all pre-processor
directives or have the tokenizer respect newlines. It depends on the back-end
processing which solution is to be desired.

## Token class definitions

Here we define the various token classes and suggest a representative for
each. On the outset we require that the vocabulary of all tokens is closed,
i.e., we prefer a fixed set of token instances. For that reason we let every
keyword represent itself since their class is closed. We will distinguish
between user identifiers and standard identifiers. The former will
collectively be represented by a single class element, say `id`. The latter
must be one of a large set of over 300 names of functions and standard
variables defined by a typical collection of C header files residing in
`/usr/include` and also includes C pre-processor names like `include`,
`define`, `ifdef`, etc. We assume that programmers will not use any of the
standard identifiers for purposes other than their intended meaning,
although this is not in any way required by the language.

The following table summarizes the set of token representatives.

|Representative:           | Represents:
|--------------------------|-----------
| `strcpy`, `malloc`, etc. | the standard identifiers (over 300)
| `id`                     | any identifier
| `[ ] ( ) { } < >`        | any of these punctuators
| `; ? : :: , . ...`       | any of these punctuators (`::` only for C++)
| `=`                      | any assignment operator (`+=`, `*=`, etc.)
| `++ --`                  | auto-increment, auto-decrement
| `-`                      | exception to better handle negative numbers
| `*`                      | any other operator (`*` covers more cases than `+`)
| `0`                      | the number `0`
| `1`                      | the number `1`
| `123`                    | any integer number except `0` and `1`
| `3.14`                   | any floating-point number
| `""`                     | any string literal
| `'A`'                    | any character literal
| `#`                      | the preprocessor symbol `#`
| `##`                     | the preprocessor symbol `##` (very rare)

## Example

We will now demonstrate the tokenization of a small C program using the above
suggested scheme. As an example we use the following complete and compilable C
program (`test1.c`) that exhibits many of the different token types.

```C
#include <stdio.h>

#define N 10

/* Compute factorial recursively. */
static int factorial(int i)
{
  if (i == 0)
    return 1;
  else
    return i * factorial(i - 1);
}

int main(int argc, char *argv[])
{
  fprintf(stdout, "fac(%d) = %d\n", N, factorial(N));
  return 0;
}
```

We tokenize this to CSV format. To save space we only show the first 20 lines
of output: from `tokenize -m csv test1.c`:

```CSV
line,column,class,token
1,0,preprocessor,#
1,1,identifier,include
1,9,operator,<
1,10,identifier,stdio
1,15,operator,.
1,16,identifier,h
1,17,operator,>
3,0,preprocessor,#
3,1,identifier,define
3,8,identifier,N
3,10,integer,10
6,0,keyword,static
6,7,keyword,int
6,11,identifier,factorial
6,20,operator,(
6,21,keyword,int
6,25,identifier,i
6,26,operator,)
7,0,operator,{
8,2,keyword,if
```

This output is then filtered by a simple AWK script (`filter5.awk`) to turn it
into a stream of the above defined token classes. Here we will use `\` to
indicate line continuations; these are not present in the actual output though.

```console
# include < id . id > # define id 123 static int id ( int id ) { if \
( id * 0 ) return 1 ; else return id * id ( id - 1 ) ; } int main ( \
int argc , char * argv [ ] ) { fprintf ( stdout , "" , id , id ( id \
) ) ; return 0 ; } 
```

Unfortunately, the C pretty-printer that we use, is not able to correctly
handle the token stream on a single line because of the pre-processor
directives. Our tokenizer however is able to preserve newlines. So using that
option we get the following filtered token stream (`test1.toks`):

```console
$ tokenize -n -m csv test1.c | ./filter5.awk -v ORS=" "
# include < id . id > 

# define id 123 


static int id ( int id ) 
{ 
if ( id * 0 ) 
return 1 ; 
else 
return id * id ( id - 1 ) ; 
} 

int main ( int argc , char * argv [ ] ) 
{ 
fprintf ( stdout , "" , id , id ( id ) ) ; 
return 0 ; 
} 
```

Now this output can easily be pretty-printed to this:

```C
# include < id . id > 

# define id 123 

static int id (int id)
{
    if (id * 0)
        return 1;
    else
        return id * id (id - 1);
}

int main (int argc, char *argv [])
{
    fprintf (stdout, "", id, id (id));
    return 0;
}
```

# Conclusion

A tokenizer followed by a simple AWK filter can render a token stream that
when pretty-printed resembles a template for the original source code.
