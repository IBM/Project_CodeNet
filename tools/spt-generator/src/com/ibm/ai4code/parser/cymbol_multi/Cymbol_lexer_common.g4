lexer grammar Cymbol_lexer_common;
// PUNCUTATORS
ASSIGN: '=';
SEMICOLON: ';';
LPAREN:             '(';
RPAREN:             ')';
LBRACK:             '[';
RBRACK:             ']';
LBRACE:             '{';
RBRACE:             '}';
COMMA:				',';
BANG:               '!';
ADD:	            '+';
SUB:                '-';
MUL:                '*';
EQUAL:              '==';

// KEYWORDS:
FLOAT: 'float';  // keywords defined before ID so that it has higher priority, e.g., 'int' is labeled as INTEGER not ID
INTEGER: 'int';
VOID: 'void';
IF: 'if';
THEN:  'else';
RETURN: 'return';

// ID
ID  :   LETTER (LETTER | [0-9])* ;
fragment
LETTER : [a-zA-Z] ;

INT :   [0-9]+ ;

// WS 
WS  :   [ \t\n\r]+ -> skip ;

// COMMENT
SL_COMMENT
    :   '//' .*? '\n' -> skip
    ;
    
