/** Simple statically-typed programming language with functions and variables
 *  taken from "Language Implementation Patterns" book.
 */
grammar Cymbol;

file:   (functionDecl | varDecl)+ ;

varDecl
    :   type ID ('=' expr)? ';'
    ;
type:   'float' | 'int' | 'void' ; // user-defined types



functionDecl
    :   type ID '(' formalParameters? ')' block // "void f(int x) {...}"
    ;
formalParameters
    :   formalParameter (',' formalParameter)*
    ;
formalParameter
    :   type ID
    ;

block:  '{' stat* '}' ;   // possibly empty statement block
stat:   block
    |   varDecl
    |   'if' expr 'then' stat ('else' stat)?
    |   'return' expr? ';' 
    |   expr '=' expr ';' // assignment
    |   expr ';'          // func call
    ;

expr:   ID '(' exprList? ')'    // func call like f(), f(x), f(1,2)
    |   ID '[' expr ']'         // array index like a[i], a[i][j]
    |   '-' expr                // unary minus
    |   '!' expr                // boolean not
    |   expr '*' expr
    |   expr ('+'|'-') expr
    |   expr '==' expr          // equality comparison (lowest priority op)
    |   ID                      // variable reference
    |   INT
    |   '(' expr ')'
    ;
exprList : expr (',' expr)* ;   // arg list

/*KEYWORDS:
FLOAT |
INTEGER |
VOID |
IF | 
THEN  |
RETURN; */

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



ID  :   LETTER (LETTER | [0-9])* ;
fragment
LETTER : [a-zA-Z] ;

INT :   [0-9]+ ;

WS  :   [ \t\n\r]+ -> skip ;

SL_COMMENT
    :   '//' .*? '\n' -> skip
    ;
    

