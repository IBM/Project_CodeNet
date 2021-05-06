/* C code produced by gperf version 3.0.3 */
/* Command-line: gperf -LC -Nis_cpp_keyword -Hcpp_hash -c -C -I -m1 --output-file=cpp_keywords.h c++20.kw  */
/* Computed positions: -k'1,5,$' */

#if !((' ' == 32) && ('!' == 33) && ('"' == 34) && ('#' == 35) \
      && ('%' == 37) && ('&' == 38) && ('\'' == 39) && ('(' == 40) \
      && (')' == 41) && ('*' == 42) && ('+' == 43) && (',' == 44) \
      && ('-' == 45) && ('.' == 46) && ('/' == 47) && ('0' == 48) \
      && ('1' == 49) && ('2' == 50) && ('3' == 51) && ('4' == 52) \
      && ('5' == 53) && ('6' == 54) && ('7' == 55) && ('8' == 56) \
      && ('9' == 57) && (':' == 58) && (';' == 59) && ('<' == 60) \
      && ('=' == 61) && ('>' == 62) && ('?' == 63) && ('A' == 65) \
      && ('B' == 66) && ('C' == 67) && ('D' == 68) && ('E' == 69) \
      && ('F' == 70) && ('G' == 71) && ('H' == 72) && ('I' == 73) \
      && ('J' == 74) && ('K' == 75) && ('L' == 76) && ('M' == 77) \
      && ('N' == 78) && ('O' == 79) && ('P' == 80) && ('Q' == 81) \
      && ('R' == 82) && ('S' == 83) && ('T' == 84) && ('U' == 85) \
      && ('V' == 86) && ('W' == 87) && ('X' == 88) && ('Y' == 89) \
      && ('Z' == 90) && ('[' == 91) && ('\\' == 92) && (']' == 93) \
      && ('^' == 94) && ('_' == 95) && ('a' == 97) && ('b' == 98) \
      && ('c' == 99) && ('d' == 100) && ('e' == 101) && ('f' == 102) \
      && ('g' == 103) && ('h' == 104) && ('i' == 105) && ('j' == 106) \
      && ('k' == 107) && ('l' == 108) && ('m' == 109) && ('n' == 110) \
      && ('o' == 111) && ('p' == 112) && ('q' == 113) && ('r' == 114) \
      && ('s' == 115) && ('t' == 116) && ('u' == 117) && ('v' == 118) \
      && ('w' == 119) && ('x' == 120) && ('y' == 121) && ('z' == 122) \
      && ('{' == 123) && ('|' == 124) && ('}' == 125) && ('~' == 126))
/* The character set is not based on ISO-646.  */
error "gperf generated tables don't work with this execution character set. Please report a bug to <bug-gnu-gperf@gnu.org>."
#endif

#include <string.h>

#define TOTAL_KEYWORDS 95
#define MIN_WORD_LENGTH 2
#define MAX_WORD_LENGTH 16
#define MIN_HASH_VALUE 3
#define MAX_HASH_VALUE 156
/* maximum key range = 154, duplicates = 0 */

#ifdef __GNUC__
__inline
#else
#ifdef __cplusplus
inline
#endif
#endif
static unsigned int
cpp_hash (str, len)
     register const char *str;
     register unsigned int len;
{
  static const unsigned char asso_values[] =
    {
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157,  11,
      157,   6, 157, 157, 157, 157,   6, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157,   2,  39,   8,
       25,   4,  47,  20,  43,   8, 157,   0,  47,  73,
       35,  49,  64,  51,  24,  10,   0,  40,  14,  49,
       57,   0, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157, 157, 157, 157, 157,
      157, 157, 157, 157, 157, 157
    };
  register int hval = len;

  switch (hval)
    {
      default:
        hval += asso_values[(unsigned char)str[4]];
      /*FALLTHROUGH*/
      case 4:
      case 3:
      case 2:
      case 1:
        hval += asso_values[(unsigned char)str[0]];
        break;
    }
  return hval + asso_values[(unsigned char)str[len - 1]];
}

#ifdef __GNUC__
__inline
#ifdef __GNUC_STDC_INLINE__
__attribute__ ((__gnu_inline__))
#endif
#endif
const char *
is_cpp_keyword (str, len)
     register const char *str;
     register unsigned int len;
{
  static const char * const wordlist[] =
    {
      "", "", "",
      "try",
      "", "", "", "",
      "true",
      "", "",
      "int",
      "else",
      "const",
      "this",
      "short",
      "case",
      "constinit",
      "const_cast",
      "concept",
      "explicit",
      "char8_t",
      "char32_t",
      "atomic_commit",
      "struct",
      "atomic_noexcept",
      "volatile",
      "char16_t",
      "continue",
      "static_cast",
      "and",
      "static_assert",
      "static",
      "class",
      "export",
      "delete",
      "char",
      "decltype",
      "not",
      "typeid",
      "reinterpret_cast",
      "constexpr",
      "",
      "void",
      "break",
      "signed",
      "",
      "typename",
      "",
      "co_yield",
      "requires",
      "noexcept",
      "float",
      "inline",
      "alignas",
      "auto",
      "co_return",
      "if",
      "namespace",
      "template",
      "false",
      "thread_local",
      "while",
      "and_eq",
      "consteval",
      "co_await",
      "register",
      "switch",
      "",
      "extern",
      "atomic_cancel",
      "long",
      "default",
      "goto",
      "for",
      "or",
      "do",
      "private",
      "asm",
      "typedef",
      "wchar_t",
      "enum",
      "double",
      "operator",
      "xor",
      "using",
      "public",
      "new",
      "",
      "return",
      "bool",
      "alignof",
      "bitor",
      "unsigned",
      "", "",
      "not_eq",
      "", "",
      "catch",
      "", "",
      "protected",
      "throw",
      "",
      "bitand",
      "",
      "compl",
      "virtual",
      "",
      "dynamic_cast",
      "",
      "sizeof",
      "friend",
      "",
      "union",
      "", "",
      "xor_eq",
      "", "", "", "",
      "mutable",
      "", "", "", "", "", "",
      "nullptr",
      "", "", "", "", "", "", "", "", "",
      "", "", "", "", "", "", "", "", "",
      "", "", "", "", "", "", "",
      "or_eq"
    };

  if (len <= MAX_WORD_LENGTH && len >= MIN_WORD_LENGTH)
    {
      register int key = cpp_hash (str, len);

      if (key <= MAX_HASH_VALUE && key >= 0)
        {
          register const char *s = wordlist[key];

          if (*str == *s && !strncmp (str + 1, s + 1, len - 1) && s[len] == '\0')
            return s;
        }
    }
  return 0;
}
