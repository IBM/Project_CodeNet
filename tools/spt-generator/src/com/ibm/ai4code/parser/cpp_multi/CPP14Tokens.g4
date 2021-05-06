/* Copyright (c) 2020 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   Draft standard document n4296.
*/

lexer grammar CPP14Tokens;
import CPP14_lexer_common;

Keyword:

// 2.11 Table 3

  ALIGNAS     | CONTINUE      | FRIEND     | REGISTER          | TRUE
| ALIGNOF     | DECLTYPE      | GOTO       | REINTERPRET_CAST  | TRY
| ASM         | DEFAULT       | IF         | RETURN            | TYPEDEF
| AUTO        | DELETE        | INLINE     | SHORT             | TYPEID
| BOOL        | DO            | INT        | SIGNED            | TYPENAME
| BREAK       | DOUBLE        | LONG       | SIZEOF            | UNION
| CASE        | DYNAMIC_CAST  | MUTABLE    | STATIC            | UNSIGNED
| CATCH       | ELSE          | NAMESPACE  | STATIC_ASSERT     | USING
| CHAR        | ENUM          | NEW        | STATIC_CAST       | VIRTUAL
| CHAR16_T    | EXPLICIT      | NOEXCEPT   | STRUCT            | VOID
| CHAR32_T    | EXPORT        | NULLPTR    | SWITCH            | VOLATILE
| CLASS       | EXTERN        | OPERATOR   | TEMPLATE          | WCHAR_T
| CONST       | FALSE         | PRIVATE    | THIS              | WHILE
| CONSTEXPR   | FLOAT         | PROTECTED  | THREAD_LOCAL
| CONST_CAST  | FOR           | PUBLIC     | THROW

// GJ20: ?
| FINAL
| OVERRIDE
;

//Identifier: Identifier;

Integer: IntegerLiteral;

Floating: FloatingLiteral;

String: StringLiteral;

Character: CharacterLiteral;

// GJ20: exclude shift operators!
// GJ20: make all alternates show as the usual symbols
Operator:

  LeftParen
| RightParen
| LeftBracket  { setText("["); }
| RightBracket { setText("]"); }
| LeftBrace    { setText("{"); }
| RightBrace   { setText("}"); }
| Dot | Arrow | PlusPlus | MinusMinus
| And          { setText("&"); }
| Star | Plus | Minus
| Tilde        { setText("~"); }
| Not          { setText("!"); }
| Div | Mod //| LeftShift | RightShift
| Less | Greater | LessEqual | GreaterEqual | Equal
| NotEqual     { setText("!="); }
| Caret        { setText("^"); }
| Or           { setText("|"); }
| AndAnd       { setText("&&"); }
| OrOr         { setText("||"); }
| Question | Colon | Semi | Ellipsis | Assign
| StarAssign | DivAssign | ModAssign | PlusAssign | MinusAssign
| LeftShiftAssign | RightShiftAssign
| AndAssign    { setText("&="); }
| XorAssign    { setText("^="); }
| OrAssign     { setText("|="); }
| Comma
| HashMark     { setText("#"); }
| DoubleHashMark { setText("##"); }
| ArrowStar | DoubleColon | DotStar
;
