/* For list of changes made to the original C.g4 see C11Parser.g4.

   Copyright (c) 2020 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>
*/

lexer grammar JavaTokens;
import Java_lexer_common;

// Note: treating false, true, and null as keywords!
Keyword:

  ABSTRACT     | ASSERT       | BOOLEAN      | BREAK        | BYTE         
| CASE         | CATCH        | CHAR         | CLASS        | CONST        
| CONTINUE     | DEFAULT      | DO           | DOUBLE       | ELSE         
| ENUM         | EXTENDS      | FINAL        | FINALLY      | FLOAT        
| FOR          | IF           | GOTO         | IMPLEMENTS   | IMPORT       
| INSTANCEOF   | INT          | INTERFACE    | LONG         | NATIVE       
| NEW          | PACKAGE      | PRIVATE      | PROTECTED    | PUBLIC       
| RETURN       | SHORT        | STATIC       | STRICTFP     | SUPER        
| SWITCH       | SYNCHRONIZED | THIS         | THROW        | THROWS       
| TRANSIENT    | TRY          | VOID         | VOLATILE     | WHILE        
| BOOL_LITERAL
| NULL_LITERAL
;

// Literals

Integer:

  DECIMAL_LITERAL
| HEX_LITERAL
| OCT_LITERAL
| BINARY_LITERAL
;

Floating:

  FLOAT_LITERAL
| HEX_FLOAT_LITERAL
;

Character: CHAR_LITERAL;

String: STRING_LITERAL;

Operator:

// Separators

  LPAREN
| RPAREN
| LBRACE
| RBRACE
| LBRACK
| RBRACK
| SEMI
| COMMA
| DOT

// Operators

| ASSIGN
| GT
| LT
| BANG
| TILDE
| QUESTION
| COLON
| EQUAL
| LE
| GE
| NOTEQUAL
| AND
| OR
| INC
| DEC
| ADD
| SUB
| MUL
| DIV
| BITAND
| BITOR
| CARET
| MOD
| ADD_ASSIGN
| SUB_ASSIGN
| MUL_ASSIGN
| DIV_ASSIGN
| AND_ASSIGN
| OR_ASSIGN
| XOR_ASSIGN
| MOD_ASSIGN
| LSHIFT_ASSIGN
| RSHIFT_ASSIGN
| URSHIFT_ASSIGN

// Java 8 tokens

| ARROW
| COLONCOLON

// Additional symbols not defined in the lexical specification

| AT
| ELLIPSIS
;

Identifier: IDENTIFIER;
