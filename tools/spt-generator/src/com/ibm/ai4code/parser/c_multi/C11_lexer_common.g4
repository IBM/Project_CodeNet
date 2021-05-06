/*
 [The "BSD licence"]
 Copyright (c) 2013 Sam Harwell
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:
 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
 3. The name of the author may not be used to endorse or promote products
    derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/* Partially extracted from the original C.g4.
   - added recognition of $ as a NonDigit in Identifier
   - better line continuation handling
   - fixed bugs in pre-processor directives

   Copyright (c) 2020 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>
*/

/** C 2011 grammar built from the C11 Spec */
lexer grammar C11_lexer_common; // always imported; name does not really matter

// (GCC) Extension keywords:

Extension__ : '__extension__';
Builtin_va_arg: '__builtin_va_arg';
Builtin_offsetof: '__builtin_offsetof';
M128: '__m128';
M128d: '__m128d';
M128i: '__m128i';
Typeof__: '__typeof__';
Inline__: '__inline__';
Stdcall: '__stdcall';
Declspec: '__declspec';
Attribute__: '__attribute__';
Asm: '__asm';
Asm__: '__asm__';
Volatile__: '__volatile__';

//A.1.2 Keywords

AUTO:     'auto';
BREAK:    'break';
CASE:     'case';
CHAR:     'char';
CONST:    'const';
CONTINUE: 'continue';
DEFAULT:  'default';
DO:       'do';
DOUBLE:   'double';
ELSE:     'else';
ENUM:     'enum';
EXTERN:   'extern';
FLOAT:    'float';
FOR:      'for';
GOTO:     'goto';

IF:       'if';
INLINE:   'inline';
INT:      'int';
LONG:     'long';
REGISTER: 'register';
RESTRICT: 'restrict';
RETURN:   'return';
SHORT:    'short';
SIGNED:   'signed';
SIZEOF:   'sizeof';
STATIC:   'static';
STRUCT:   'struct';
SWITCH:   'switch';
TYPEDEF:  'typedef';
UNION:    'union';

UNSIGNED: 'unsigned';
VOID:     'void';
VOLATILE: 'volatile';
WHILE:    'while';
ALIGNAS:  '_Alignas';
ALIGNOF:  '_Alignof';
ATOMIC:   '_Atomic';
BOOL:     '_Bool';
COMPLEX:  '_Complex';
GENERIC:  '_Generic';
IMAGINARY: '_Imaginary';
NORETURN: '_Noreturn';
STATIC_ASSERT: '_Static_assert';
THREAD_LOCAL: '_Thread_local';

//A.1.3 Identifiers

Identifier
    :   IdentifierNondigit
        (   IdentifierNondigit
        |   Digit
        )*
    ;

fragment
IdentifierNondigit
    :   Nondigit
    |   UniversalCharacterName
    //|   // other implementation-defined characters...
    ;

// GJ20: extend to allow $
fragment
Nondigit
    :   [a-zA-Z_$]
    ;

fragment
Digit
    :   [0-9]
    ;

fragment
UniversalCharacterName
    :   '\\u' HexQuad
    |   '\\U' HexQuad HexQuad
    ;

fragment
HexQuad
    :   HexadecimalDigit HexadecimalDigit HexadecimalDigit HexadecimalDigit
    ;

//A.1.5 Constants

// rule for Constant moved to parser; constituents unfragmented.
/*
Constant
    :   IntegerConstant
    |   FloatingConstant
    //|   EnumerationConstant
    |   CharacterConstant
    ;
*/

IntegerConstant
    :   DecimalConstant IntegerSuffix?
    |   OctalConstant IntegerSuffix?
    |   HexadecimalConstant IntegerSuffix?
    |   BinaryConstant
    ;

fragment
BinaryConstant
    :   '0' [bB] [0-1]+
    ;

fragment
DecimalConstant
    :   NonzeroDigit Digit*
    ;

fragment
OctalConstant
    :   '0' OctalDigit*
    ;

fragment
HexadecimalConstant
    :   HexadecimalPrefix HexadecimalDigit+
    ;

fragment
HexadecimalPrefix
    :   '0' [xX]
    ;

fragment
NonzeroDigit
    :   [1-9]
    ;

fragment
OctalDigit
    :   [0-7]
    ;

fragment
HexadecimalDigit
    :   [0-9a-fA-F]
    ;

fragment
IntegerSuffix
    :   UnsignedSuffix LongSuffix?
    |   UnsignedSuffix LongLongSuffix
    |   LongSuffix UnsignedSuffix?
    |   LongLongSuffix UnsignedSuffix?
    ;

fragment
UnsignedSuffix
    :   [uU]
    ;

fragment
LongSuffix
    :   [lL]
    ;

fragment
LongLongSuffix
    :   'll' | 'LL'
    ;

FloatingConstant
    :   DecimalFloatingConstant
    |   HexadecimalFloatingConstant
    ;

fragment
DecimalFloatingConstant
    :   FractionalConstant ExponentPart? FloatingSuffix?
    |   DigitSequence ExponentPart FloatingSuffix?
    ;

fragment
HexadecimalFloatingConstant
    :   HexadecimalPrefix HexadecimalFractionalConstant BinaryExponentPart FloatingSuffix?
    |   HexadecimalPrefix HexadecimalDigitSequence BinaryExponentPart FloatingSuffix?
    ;

fragment
FractionalConstant
    :   DigitSequence? '.' DigitSequence
    |   DigitSequence '.'
    ;

fragment
ExponentPart
    :   'e' Sign? DigitSequence
    |   'E' Sign? DigitSequence
    ;

fragment
Sign
    :   '+' | '-'
    ;

DigitSequence
    :   Digit+
    ;

fragment
HexadecimalFractionalConstant
    :   HexadecimalDigitSequence? '.' HexadecimalDigitSequence
    |   HexadecimalDigitSequence '.'
    ;

fragment
BinaryExponentPart
    :   'p' Sign? DigitSequence
    |   'P' Sign? DigitSequence
    ;

fragment
HexadecimalDigitSequence
    :   HexadecimalDigit+
    ;

fragment
FloatingSuffix
    :   'f' | 'l' | 'F' | 'L'
    ;

CharacterConstant
    :   '\'' CCharSequence '\''
    |   'L\'' CCharSequence '\''
    |   'u\'' CCharSequence '\''
    |   'U\'' CCharSequence '\''
    ;

fragment
CCharSequence
    :   CChar+
    ;

fragment
CChar
    :   ~['\\\r\n] // GJ20: approximation
    |   EscapeSequence
    ;

fragment
EscapeSequence
    :   SimpleEscapeSequence
    |   OctalEscapeSequence
    |   HexadecimalEscapeSequence
    |   UniversalCharacterName
    ;

// GJ20: allow any character to be escaped
fragment
SimpleEscapeSequence
//    :   '\\' ['"?abfnrtv\\]
    :   '\\' .
    ;

fragment
OctalEscapeSequence
    :   '\\' OctalDigit
    |   '\\' OctalDigit OctalDigit
    |   '\\' OctalDigit OctalDigit OctalDigit
    ;

fragment
HexadecimalEscapeSequence
    :   '\\x' HexadecimalDigit+
    ;

//A.1.6

StringLiteral
    :   EncodingPrefix? '"' SCharSequence? '"'
    ;

fragment
EncodingPrefix
    :   'u8'
    |   'u'
    |   'U'
    |   'L'
    ;

fragment
SCharSequence
   :   SChar+
    ;

// GJ20: Handling of \ Newline is incorrect, but works somewhat.
fragment
SChar
    :   ~["\\\r\n] // GJ20: approximation
    |   EscapeSequence
    |   EscapeNewline
    ;

//A.1.7 Punctuators

// Operator and punctuation:

// Enclosing brackets:
LeftParen:    '(';
RightParen:   ')';
LeftBracket:  '[';
RightBracket: ']';
LeftBrace:    '{';
RightBrace:   '}';

// Preprocessor-related symbols:
HashMark:         '#';
HashMarkHashMark: '##';

// Alternatives:
LessColon:      '<:'; // alt [
ColonGreater:   ':>'; // alt ]
LessPercent:    '<%'; // alt {
PrecentGreater: '%>'; // alt }
PrecentColon:   '%:'; // alt #
PercentColonPercentColon: '%:%:'; // alt ##

// Punctuators:
Semi:     ';';
Colon:    ':';
Ellipsis: '...';
Comma:    ',';
Dot:      '.';

// Operators:
Question:         '?';
Plus:             '+';
Minus:            '-';
Star:             '*';
Div:              '/';
Mod:              '%';
Caret:            '^';
And:              '&';
Or:               '|';
Tilde:            '~';
Not:              '!';
Assign:           '=';
Less:             '<';
Greater:          '>';
PlusAssign:       '+=';
MinusAssign:      '-=';
StarAssign:       '*=';
DivAssign:        '/=';
ModAssign:        '%=';
XorAssign:        '^=';
AndAssign:        '&=';
OrAssign:         '|=';
LeftShift:        '<<';
RightShift:       '>>';
RightShiftAssign: '>>=';
LeftShiftAssign:  '<<=';
Equal:            '==';
NotEqual:         '!=';
LessEqual:        '<=';
GreaterEqual:     '>=';
AndAnd:           '&&';
OrOr:             '||';
PlusPlus:         '++';
MinusMinus:       '--';
Arrow:            '->';

// GJ20: completely bogus; will skip everything till next #
/*
ComplexDefine
    :   '#' Whitespace? 'define'  ~[#]*
        -> skip
    ;
*/

// GJ20: covered by Directive; see below.
/*
IncludeDirective
    :   '#' Whitespace? 'include' Whitespace? (('"' ~[\n"]+ '"') | ('<' ~[\n>]+ '>' ))
        -> skip
    ;
*/

// ignore the following asm blocks:
/*
    asm
    {
        mfspr x, 286;
    }
 */
AsmBlock
    :   'asm' ~'{'* '{' ~'}'* '}'
        -> skip
    ;

// GJ20: covered by Directive; see below.
// ignore the lines generated by c preprocessor
// sample line: '#line 1 "/home/dm/files/dk1.h" 1'
/*
LineAfterPreprocessing
    :   '#line' Whitespace* ~[\r\n]*
        -> skip
    ;  
*/

// GJ20: covered by Directive; see below.
/*
LineDirective
    :   '#' Whitespace? DecimalConstant Whitespace? StringLiteral ~[\r\n]*
        -> skip
    ;
*/

// GJ20: covered by Directive; see below.
/*
PragmaDirective
    :   '#' Whitespace? 'pragma' Whitespace ~[\r\n]*
        -> skip
    ;
*/

// GJ20: every preprocessor directive is treated a line comment.
Directive:
        '#' (~[\\\r\n]* EscapeNewline)* ~[\r\n]* -> channel(HIDDEN);

// GJ20: added vertical tab \v (^K) and formfeed \f (^L)
Whitespace
    :   [ \t\u000B\f]+
        -> skip
    ;

Newline
    :   (   '\r' '\n'?
        |   '\n'
        )
        -> skip
    ;

// GJ20: this will create logical lines.
EscapeNewline
    :   '\\' Newline
        -> skip
    ;

// GJ20: anticipate \ Newline
BlockComment
    :   '/*' .*? '*/'
        -> channel(HIDDEN)
    ;

// GJ20: anticipate \ Newline
LineComment
    :   '//' (~[\\\r\n]* EscapeNewline)* ~[\r\n]*
        -> channel(HIDDEN)
    ;
