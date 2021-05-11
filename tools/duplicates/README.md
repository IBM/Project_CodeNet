# Find near-duplicates among source code files

## Introduction

This program finds clusters of near-duplicate files of source code.
The input is a single file with a sample per line. A sample consists
of a unique (within the input) identifier for the source code, e.g.
its file name or its file name path, and a list of tokens.

To be precise, the identifier and list of tokens are separated by a single TAB
character. This choice precludes allowing TAB characters in the identifier.
For the tokens themselves there are 2 options: either SPACE
separated or TAB separated; which one is used is autodetected by the program.
Using TABs facilitates string and character literals that
contain spaces; typically programming languages do not allow unescaped TAB
characters within a string or character literal. Even if that happens, such a
literal will then merely be treated as multiple tokens. For our purpose of
duplication detection, breaking up string literals at white-space does not do
much harm to
the outcome. Other applications may decide to use the same input format but
might insist on correctly handling the original tokens.

The list of tokens is never empty. The token list can thus easily be split using the separator character
as delimiter. (Note that all comments are assumed to have been removed.)

In the subsequent examples the Project CodeNet dataset is
under the /Volume1/AI4CODE directory, which will be different for another user.
As an example, here are the first 3 samples of tokenized C/C++ source code files:

```console
/Volume1/AI4CODE/Project_CodeNet/data/p00000/C/s423724218.c	using namespace std ; int main ( ) { int a , b , c , d ; a = 1 ; b = 1 ; d = 1 ; do { c = a * b ; cout << a << << b << << c << ; b ++ ; if ( b == 11 ) { b = 1 ; a ++ ; } d ++ ; } while ( d <= 100 ) ; } 
/Volume1/AI4CODE/Project_CodeNet/data/p00000/C/s920742007.c	using namespace std ; int main ( ) { int a , b , c , d ; a = 1 ; b = 1 ; d = 1 ; do { c = a * b ; cout << a << << b << << c << ; b ++ ; if ( b == 11 ) { b = 1 ; a ++ ; } d ++ ; } while ( d <= 100 ) ; } 
/Volume1/AI4CODE/Project_CodeNet/data/p00000/C/s425941185.c	int main ( ) { for ( int i = 1 ; i < 10 ; i ++ ) { for ( int j = 1 ; j < 10 ; j ++ ) { if ( i == 9 && j == 9 ) { printf ( , i , j , i * j ) ; } else { printf ( , i , j , i * j ) ; } } } return 0 ; } 
```

Preparing this input format can be accomplished with a few bash commands.
Assume the existence of a tokenizer that outputs a single token per line then
the following will produce a sample for the source file `$1` to standard output:

```bash
echo -e -n "$1\t"
tokenize "$1" | sed "/^[\"']/d" | tr -s '\n' ' '
echo
```

Including strings and making sure tokens are separated by a TAB can be
accomplished with:

```bash
echo -e -n "$1\t"
tokenize "$1" | tr -s '\n' '\t' | sed '$ s/.$//'
echo
```

It should be noted that samples with less than 20 token instances are
discarded. This can be changed with the `-M` option.

The output echoes the identifiers clustered 1 per line and separated by a
blank line. Here is an example of 3 output clusters in Jaccard mode:

```console
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s693224029.c:
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s667072386.c:  0.97, 0.96

/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s269264590.c:
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s562267449.c:  0.94, 0.95
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s222863615.c:  1.00, 0.98

/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s613594379.c:
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s546115621.c:  0.98, 0.98
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s920361752.c:  0.95, 0.98
```

Here is an example of some clusters in LCS mode:

```console
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s441758757.c:     (161)
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s199394875.c: 159 (160)

/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s269264590.c:     (130)
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s562267449.c: 124 (133)
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s284444458.c: 122 (136)
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s222863615.c: 129 (130)

/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s613594379.c:     (249)
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s546115621.c: 247 (249)
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s920361752.c: 246 (249)
```

The output in COSINE mode looks like this:

```console
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s839759041.c:
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s502803295.c:  0.91
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s279938930.c:  0.92

/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s269264590.c:
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s562267449.c:  0.99
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s284444458.c:  0.96
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s222863615.c:  1.00
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s291709227.c:  0.91

/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s613594379.c:
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s546115621.c:  1.00
/Volume1/AI4CODE/Project_CodeNet/data/p00009/C/s920361752.c:  1.00
```

Of course there is no reason why even with the same input different modes with
their own thresholds should result in the same clusters. Typically there will
be some overlap though.

The meaning of the numbers after the identifiers are explained below.

## Algorithm

In principle each sample is compared with all others pairwise.
The input is preprocessed to derive both an encoded token list representation
and a bag of tokens as a multiset. For the bag of tokens, 2 Jaccard similarity
values are calculated: one considering the bag as a set (ignoring the
multiplicity of token occurrences, i.e., act as if they are all 1) and the other considering the bag as a
multiset. Each value has its own threshold and both must be met to declare the
sample pair part of a cluster. Once clustered, a sample is removed from
subsequent consideration (based on the assumption that similarity is an
equivalence relation, in particular it is assumed transitive).

As an alternative one can also compute the longest common subsequence (LCS) of
the token lists or the cosine similarity of the multiset of tokens seen as
sparse feature vectors. Check the `-h` help option of the program.

## Metrics

In general Jaccard similarity is defined as the quotient of the cardinalities
of the intersection and union of the two sets under consideration. By this
definition the value lies in the closed interval [0,1] with 0 meaning
completely dissimilar and 1 meaning identical. Of course, in our application
where we have sets of tokens that have already been somewhat filtered, even a
1 score between a pair of samples does not necessarily mean that the source
codes are semantically equivalent (first because we do not consider order and
second because we might have dropped all strings and characters).

The LCS (longest common subsequence) computes an integer value that represents
the length of the longest, not-necessarily consecutive, sequence of tokens
that appear identically and in the same order in both samples.

To speed up the clustering process we only compute similarity for pairs whose
token list lengths are within 5% (relative to the length of the first sample
in a pair).

The meaning of the numbers output after each cluster element depends on the
mode of operation:

1. in Jaccard mode, the cluster representative (first line of a cluster) has
   no additional information; all other cluster elements are followed by 2
   numbers, the first the set similarity score and the second the multiset
   score (as compared to the cluster representative). The default thresholds
   to be considered near-duplicates are 0.9 and 0.8 respectively.

2. in LCS mode, the cluster representative (first line of a cluster) is
   followed by its length in tokens in parentheses; the other cluster elements
   are followed by 2 numbers, the first is the length of the longest common
   subsequence (as compared with the cluster representative) and the second
   its own token length in parentheses (within 5% of the representative's
   length). To be considered near-duplicates the LCS should be at least 0.9 of
   the length of the representative.

3. in COSINE mode, the cluster representative (first line of a cluster) has
   no additional information; the other cluster elements are followed by
   the value of their cosine similarity with respect to the cluster
   representative. To qualify as part of a cluster, the cosine must be at
   least 0.9.

## Results of experiments

As datasets we chose all Accepted C++ files from Project CodeNet, all POJ-104 C and
C++ files, and the Python files of py150. Note that during tokenization all
comments are removed. We report on cases with and without the removal of all
string (enclosed in double quotes) and character (enclosed in
single quotes) literals. If less than 20 tokens remain the sample
is discarded but still counted under the _Size_ column in the table below.
_Clusters_ shows the number of groups of files deemed similar to each other.
Mind that files that form a singleton cluster, i.e., they are found not to be
similar to any other file, are not included in the _Clusters_ count.
_Duplicates_ gives the total count of all files in the clusters. The
_Duplication Factor_ is the ratio of _Duplicates_ minus _Clusters_ over _Size_ minus _<20_.

|  Dataset  | Size (files) |   <20 | Clusters | Duplicates | Dupl. Factor |
|-----------|-------------:|------:|---------:|-----------:|-------------:|
| Project CodeNet ² |   4,353,049  |   115 |  336,617 | 1,374,575  |        23.8% |
| POJ-104 ¹ |      52,000  |     0 |    1,301 |     2,826  |         2.9% |
| POJ-104 ² |      52,000  |     0 |    1,147 |     2,454  |         2.5% |
| py150   ¹ |     150,000  | 7,350 |    5,288 |    22,194  |        11.9% |
| py150   ² |     150,000  | 7,124 |    4,253 |    13,791  |         6.7% |

Table: Duplication results for 3 datasets; with (²) and without (¹) strings.

These outcomes cannot directly be compared with table 1 in Allamanis [[1]](#1).
In the paper the tokenization only seems to keep identifiers (and strings for
Python). It is also not clear how many files are discarded because of
inability of a correct parse or because of too few tokens (20 identifiers).

### Extracting problem similarity

The generated clusters can be further analyzed and from them we can extract
relationships between the problems. This is detailed [here](./Clusters.md).

## References

> <a id="1">[1]</a>
Miltiadis Allamanis,
["The Adverse Effects of Code Duplication in Machine Learning Models of Code,"](https://arxiv.org/abs/1812.06469)
Onward! 2019: Proceedings of the 2019 ACM SIGPLAN International Symposium on
New Ideas, New Paradigms, and Reflections on Programming and Software, October
2019, pp. 143–153, doi: 10.1145/3359591.3359735.

> <a id="2">[2]</a>
H. Sajnani, V. Saini, J. Svajlenko, C. K. Roy and C. V. Lopes, ["SourcererCC: Scaling Code Clone Detection to Big-Code,"](https://arxiv.org/pdf/1512.06448.pdf) 2016 IEEE/ACM 38th International Conference on Software Engineering (ICSE), Austin, TX, 2016, pp. 1157-1168, doi: 10.1145/2884781.2884877.
