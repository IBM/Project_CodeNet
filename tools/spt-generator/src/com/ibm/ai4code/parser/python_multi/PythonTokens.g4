lexer grammar PythonTokens;
import PythonLexer;
options { superClass=PythonTokensLexerBase; }
tokens { INDENT, DEDENT, LINE_BREAK }



// keywords
KEYWORDS:
DEF                |
RETURN             |
RAISE              |
FROM               |
IMPORT             |
NONLOCAL           |
AS                 |
GLOBAL             |
ASSERT             |
IF                 |
ELIF               |
ELSE               |
WHILE              |
FOR                |
IN                 |
TRY                |
NONE               |
FINALLY            |
WITH               |
EXCEPT             |
LAMBDA             |
OR                 |
AND                |
NOT                |
IS                 |
CLASS              |
YIELD              |
DEL                |
PASS               |
CONTINUE           |
BREAK              |
ASYNC              |
AWAIT              |
PRINT              |
EXEC               |
TRUE               |
FALSE              ;

// Operators
OPERATORS:
DOT                | 
ELLIPSIS           | 
REVERSE_QUOTE      | 
STAR               | 
COMMA              | 
COLON              | 
SEMI_COLON         | 
POWER              | 
ASSIGN             | 
OR_OP              | 
XOR                | 
AND_OP             | 
LEFT_SHIFT         | 
RIGHT_SHIFT        | 
ADD                | 
MINUS              | 
DIV                | 
MOD                | 
IDIV               | 
NOT_OP             | 
LESS_THAN          | 
GREATER_THAN       | 
EQUALS             | 
GT_EQ              | 
LT_EQ              | 
NOT_EQ_1           | 
NOT_EQ_2           | 
AT                 | 
ARROW              | 
ADD_ASSIGN         | 
SUB_ASSIGN         | 
MULT_ASSIGN        | 
AT_ASSIGN          | 
DIV_ASSIGN         | 
MOD_ASSIGN         | 
AND_ASSIGN         | 
OR_ASSIGN          | 
XOR_ASSIGN         | 
LEFT_SHIFT_ASSIGN  | 
RIGHT_SHIFT_ASSIGN | 
POWER_ASSIGN       | 
IDIV_ASSIGN        ; 

//  Numbers
NUMBER:
DECIMAL_INTEGER    | 
OCT_INTEGER        | 
HEX_INTEGER        | 
BIN_INTEGER        | 
IMAG_NUMBER        | 
FLOAT_NUMBER       ;




// Punctuation
PUNCTUATOR:
OPEN_BRACKET       | 
CLOSE_BRACKET      |
OPEN_PAREN         |
CLOSE_PAREN         | 
OPEN_BRACE        | 
CLOSE_BRACE        ; 









