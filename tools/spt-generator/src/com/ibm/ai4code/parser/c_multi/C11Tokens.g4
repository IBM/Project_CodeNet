/* For list of changes made to the original C.g4 see C11Parser.g4.

   Copyright (c) 2020 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>
*/

lexer grammar C11Tokens;
import C11_lexer_common;

//A.1.2 Keywords

Keyword
    : AUTO       | IF          | UNSIGNED
    | BREAK      | INLINE      | VOID
    | CASE       | INT         | VOLATILE
    | CHAR       | LONG        | WHILE
    | CONST      | REGISTER    | ALIGNAS
    | CONTINUE   | RESTRICT    | ALIGNOF
    | DEFAULT    | RETURN      | ATOMIC
    | DO         | SHORT       | BOOL
    | DOUBLE     | SIGNED      | COMPLEX
    | ELSE       | SIZEOF      | GENERIC
    | ENUM       | STATIC      | IMAGINARY
    | EXTERN     | STRUCT      | NORETURN
    | FLOAT      | SWITCH      | STATIC_ASSERT
    | FOR        | TYPEDEF     | THREAD_LOCAL
    | GOTO       | UNION
    ;

//A.1.3 Identifiers

//A.1.5 Constants

/*
IntegerConstant
FloatingConstant
CharacterConstant
*/

//A.1.6 StringLiteral

//A.1.7

Punctuator
    : LeftBracket | RightBracket | LeftParen | RightParen | LeftBrace
    | RightBrace  | Dot | Arrow | PlusPlus | MinusMinus | And | Star
    | Plus | Minus | Tilde | Not | Div | Mod | LeftShift | RightShift
    | Less | Greater | LessEqual | GreaterEqual | Equal | NotEqual | Caret
    | Or | AndAnd | OrOr | Question | Colon | Semi | Ellipsis | Assign
    | StarAssign | DivAssign | ModAssign | PlusAssign | MinusAssign
    | LeftShiftAssign | RightShiftAssign | AndAssign | XorAssign
    | OrAssign | Comma | HashMark | HashMarkHashMark | LessColon
    | ColonGreater | LessPercent | PrecentGreater | PrecentColon
    | PercentColonPercentColon
    ;
