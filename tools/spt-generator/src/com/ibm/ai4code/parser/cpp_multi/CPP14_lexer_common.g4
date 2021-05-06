lexer grammar CPP14_lexer_common;

/* GJ20: covered by new Directive; see below.
MultiLineMacro:
        '#' (~[\n]*? '\\' '\r'? '\n')+ ~ [\n]+ -> channel (HIDDEN);
*/

/* GJ20: covered by new Directive; see below.
Directive: '#' ~ [\n]* -> channel (HIDDEN);
*/

// GJ20: every preprocessor directive is treated a line comment.
Directive:
        '#' (~[\\\r\n]* EscapeNewline)* ~[\r\n]* -> channel(HIDDEN);

/*Keywords*/

ALIGNAS:        'alignas';
ALIGNOF:        'alignof';
ASM:            'asm';
ASSERT:         'assert';
AUTO:           'auto';
BOOL:           'bool';
BREAK:          'break';
CASE:           'case';
CATCH:          'catch';
CHAR:           'char';
CHAR16_T:       'char16_t';
CHAR32_T:       'char32_t';
CLASS:          'class';
CONST:          'const';
CONSTEXPR:      'constexpr';
CONST_CAST:     'const_cast';
CONTINUE:       'continue';
DECLTYPE:       'decltype';
DEFAULT:        'default';
DELETE:         'delete';
DO:             'do';
DOUBLE:         'double';
DYNAMIC_CAST:   'dynamic_cast';
ELSE:           'else';
ENUM:           'enum';
EXPLICIT:       'explicit';
EXPORT:         'export';
EXTERN:         'extern';
FALSE:          'false';
FLOAT:          'float';
FOR:            'for';
FRIEND:         'friend';
GOTO:           'goto';
IF:             'if';
INLINE:         'inline';
INT:            'int';
LONG:           'long';
MUTABLE:        'mutable';
NAMESPACE:      'namespace';
NEW:            'new';
NOEXCEPT:       'noexcept';
NULLPTR:        'nullptr';
OPERATOR:       'operator';
PRIVATE:        'private';
PROTECTED:      'protected';
PUBLIC:         'public';
REGISTER:       'register';
REINTERPRET_CAST: 'reinterpret_cast';
RETURN:         'return';
SHORT:          'short';
SIGNED:         'signed';
SIZEOF:         'sizeof';
STATIC:         'static';
STATIC_ASSERT:  'static_assert';
STATIC_CAST:    'static_cast';
STRUCT:         'struct';
SWITCH:         'switch';
TEMPLATE:       'template';
THIS:           'this';
THREAD_LOCAL:   'thread_local';
THROW:          'throw';
TRUE:           'true';
TRY:            'try';
TYPEDEF:        'typedef';
TYPEID:         'typeid';
TYPENAME:       'typename';
UNION:          'union';
UNSIGNED:       'unsigned';
USING:          'using';
VIRTUAL:        'virtual';
VOID:           'void';
VOLATILE:       'volatile';
WCHAR_T:        'wchar_t';
WHILE:          'while';

// GJ20: ?
FINAL:          'final';
OVERRIDE:       'override';

// Operator and punctuation:

// Enclosing brackets:
LeftParen:	'(';
RightParen:  	')';
LeftBracket: 	'[' | LessColon      { setText("["); };
RightBracket:	']' | ColonGreater   { setText("]"); };
LeftBrace:	'{' | LessPercent    { setText("{"); };
RightBrace:	'}' | PercentGreater { setText("}"); };

// Preprocessor-related symbols:
HashMark:	'#'  | PercentColon       { setText("#"); };
DoubleHashMark: '##' | DoublePercentColon { setText("##"); };

// Alternatives:
LessColon:      '<:'; // alt [
ColonGreater:   ':>'; // alt ]
LessPercent:    '<%'; // alt {
PercentGreater: '%>'; // alt }
PercentColon:   '%:'; // alt #
DoublePercentColon: '%:%:'; // alt ##

// Punctuators:
Semi:		';';
Colon:		':';
DoubleColon:	'::';
Ellipsis:	'...';
Comma:		',';
Dot:		'.';

// Operators:

// GJ20: alt are mapped to preferred symbol

Question:	'?';
Plus:		'+';
Minus:		'-';
Star:		'*';
Div:		'/';
Mod:		'%';
Caret:		'^' | XOR    { setText("^"); };
And:	        '&' | BITAND { setText("&"); };
Or:		'|' | BITOR  { setText("|"); };
Tilde:		'~' | COMPL  { setText("~"); };
Not:		'!' | NOT    { setText("!"); };
Assign:		'=';
Less:		'<';
Greater:	'>';
PlusAssign:	'+=';
MinusAssign:	'-=';
StarAssign:	'*=';
DivAssign:	'/=';
ModAssign:	'%=';
XorAssign:	'^=' | XOR_EQ { setText("^="); };
AndAssign:	'&=' | AND_EQ { setText("&="); };
OrAssign:	'|=' | OR_EQ  { setText("|="); };
//LeftShift:	'<<'; // GJ20: problem with template <<
//RightShift:	'>>'; // GJ20: problem with template << ... >>
LeftShiftAssign:'<<=';
RightShiftAssign:'>>=';
Equal:		'==';
NotEqual:	'!=' | NOT_EQ  { setText("!="); };
LessEqual:	'<=';
GreaterEqual:	'>=';
AndAnd:		'&&' | AND     { setText("&&"); };
OrOr:		'||' | OR      { setText("||"); };
PlusPlus:	'++';
MinusMinus:	'--';
Arrow:		'->';
ArrowStar:	'->*';
DotStar:	'.*';

// 2.11 Table 4 Alternative representations (also 2.5 Table 1)

// GJ20: treat as operators; not keywords
AND:	        'and';    // alt &&
AND_EQ:	        'and_eq'; // alt &=
BITAND:	        'bitand'; // alt &
BITOR:	        'bitor';  // alt |
COMPL:	        'compl';  // alt ~
NOT:	        'not';    // alt !
NOT_EQ:	        'not_eq'; // alt !=
OR:	        'or';     // alt ||
OR_EQ:	        'or_eq';  // alt |=
XOR:	        'xor';    // alt ^
XOR_EQ:	        'xor_eq'; // alt ^=

fragment Hexquad:
        HEXADECIMALDIGIT HEXADECIMALDIGIT HEXADECIMALDIGIT HEXADECIMALDIGIT;

fragment Universalcharactername:
        '\\u' Hexquad
        | '\\U' Hexquad Hexquad;

Identifier:
        /*
         Identifiernondigit | Identifier Identifiernondigit | Identifier DIGIT
         */
        Identifiernondigit (Identifiernondigit | DIGIT)*;

fragment Identifiernondigit: NONDIGIT | Universalcharactername;

fragment NONDIGIT: [a-zA-Z_];

fragment DIGIT: [0-9];

IntegerLiteral:
        DecimalLiteral Integersuffix?
        | OctalLiteral Integersuffix?
        | HexadecimalLiteral Integersuffix?
        | BinaryLiteral Integersuffix?;

fragment DecimalLiteral: NONZERODIGIT ('\''? DIGIT)*;

OctalLiteral: '0' ('\''? OCTALDIGIT)*;

fragment HexadecimalLiteral: ('0x' | '0X') HEXADECIMALDIGIT (
                '\''? HEXADECIMALDIGIT
        )*;

fragment BinaryLiteral: ('0b' | '0B') BINARYDIGIT ('\''? BINARYDIGIT)*;

fragment NONZERODIGIT: [1-9];

fragment OCTALDIGIT: [0-7];

fragment HEXADECIMALDIGIT: [0-9a-fA-F];

fragment BINARYDIGIT: [01];

fragment Integersuffix:
        Unsignedsuffix Longsuffix?
        | Unsignedsuffix Longlongsuffix?
        | Longsuffix Unsignedsuffix?
        | Longlongsuffix Unsignedsuffix?;

fragment Unsignedsuffix: [uU];

fragment Longsuffix: [lL];

fragment Longlongsuffix: 'll' | 'LL';

CharacterLiteral:
        '\'' Cchar+ '\''
        | 'u' '\'' Cchar+ '\''
        | 'U' '\'' Cchar+ '\''
        | 'L' '\'' Cchar+ '\'';

fragment Cchar:
        ~ ['\\\r\n]
        | Escapesequence
        | Universalcharactername;

fragment Escapesequence:
        Simpleescapesequence
        | Octalescapesequence
        | Hexadecimalescapesequence;

fragment Simpleescapesequence:
        '\\\''
        | '\\"'
        | '\\?'
        | '\\\\'
        | '\\a'
        | '\\b'
        | '\\f'
        | '\\n'
        | '\\r'
        | '\\t'
        | '\\v';

fragment Octalescapesequence:
        '\\' OCTALDIGIT
        | '\\' OCTALDIGIT OCTALDIGIT
        | '\\' OCTALDIGIT OCTALDIGIT OCTALDIGIT;

fragment Hexadecimalescapesequence: '\\x' HEXADECIMALDIGIT+;

FloatingLiteral:
        Fractionalconstant Exponentpart? Floatingsuffix?
        | Digitsequence Exponentpart Floatingsuffix?;

fragment Fractionalconstant:
        Digitsequence? '.' Digitsequence
        | Digitsequence '.';

fragment Exponentpart:
        'e' SIGN? Digitsequence
        | 'E' SIGN? Digitsequence;

fragment SIGN: [+-];

fragment Digitsequence: DIGIT ('\''? DIGIT)*;

fragment Floatingsuffix: [flFL];

StringLiteral:
        Encodingprefix? '"' Schar* '"'
        | Encodingprefix? 'R' Rawstring;

fragment Encodingprefix: 'u8' | 'u' | 'U' | 'L';

// GJ20: Handling of \ Newline is incorrect, but works somewhat.
fragment Schar:
        ~ ["\\\r\n]
        | Escapesequence
        | EscapeNewline
        | Universalcharactername;

//fragment Rawstring: '"' .*? '(' .*? ')' .*? '"';
// GJ20:
fragment Rawstring: '"' DChars '(' RChars ')' DChars '"';
// GJ20: Must be max 16 chars and front and back must be the same!
fragment DChars: ~[ ()\\\t\u000B\f\r\n]*;
// GJ20: approximation
fragment RChars: ~[)]*;

BooleanLiteral: FALSE | TRUE;

PointerLiteral: NULLPTR;

UserDefinedLiteral:
        UserDefinedIntegerLiteral
        | UserDefinedFloatingLiteral
        | UserDefinedStringLiteral
        | UserDefinedCharacterLiteral;

fragment UserDefinedIntegerLiteral:
        DecimalLiteral Udsuffix
        | OctalLiteral Udsuffix
        | HexadecimalLiteral Udsuffix
        | BinaryLiteral Udsuffix;

fragment UserDefinedFloatingLiteral:
        Fractionalconstant Exponentpart? Udsuffix
        | Digitsequence Exponentpart Udsuffix;

UserDefinedStringLiteral: StringLiteral Udsuffix;

fragment UserDefinedCharacterLiteral: CharacterLiteral Udsuffix;

fragment Udsuffix: Identifier;

// GJ20: added vertical tab \v (^K) and formfeed \f (^L)
Whitespace: [ \t\u000B\f]+ -> skip;

// GJ20: this will create logical lines.
EscapeNewline: '\\' Newline -> skip;

Newline: ('\r' '\n'? | '\n') -> skip;

BlockComment: '/*' .*? '*/' -> skip;

//LineComment: '//' ~ [\r\n]* -> skip;

// GJ20: anticipate \ Newline
LineComment:   '//' (~[\\\r\n]* EscapeNewline)* ~[\r\n]* -> skip;
