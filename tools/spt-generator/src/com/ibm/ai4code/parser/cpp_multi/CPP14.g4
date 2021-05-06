/*******************************************************************************
 * The MIT License (MIT)
 *
 * Copyright (c) 2015 Camilo Sanchez (Camiloasc1) 2020 Martin Mirchev (Marti2203)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
 * associated documentation files (the "Software"), to deal in the Software without restriction,
 * including without limitation the rights to use, copy, modify, merge, publish, distribute,
 * sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or
 * substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
 * NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 * DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * ****************************************************************************
 */

/* Changes made to the original CPP14Parser.g4:
   - renamed this file to CPP14.g4
   - imports common lexer rules CPP14_lexer_common.g4
   - made all keywords upper case
   - fixed operator <<() and operator >>()

   Copyright (c) 2020 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>
*/

/** Based on n4296 draft C++ 2014 */
grammar CPP14;
import CPP14_lexer_common;

/*Basic concepts*/

translationUnit: declarationseq? EOF;
/*Expressions*/

primaryExpression:
	literal+
	| THIS
	| LeftParen expression RightParen
	| idExpression
	| lambdaExpression;

idExpression: unqualifiedId | qualifiedId;

unqualifiedId:
	Identifier
	| operatorFunctionId
	| conversionFunctionId
	| literalOperatorId
	| Tilde (className | decltypeSpecifier)
	| templateId;

qualifiedId: nestedNameSpecifier TEMPLATE? unqualifiedId;

nestedNameSpecifier:
	(theTypeName | namespaceName | decltypeSpecifier)? DoubleColon
	| nestedNameSpecifier (
		Identifier
		| TEMPLATE? simpleTemplateId
	) DoubleColon;
lambdaExpression:
	lambdaIntroducer lambdaDeclarator? compoundStatement;

lambdaIntroducer: LeftBracket lambdaCapture? RightBracket;

lambdaCapture:
	captureList
	| captureDefault (Comma captureList)?;

captureDefault: And | Assign;

captureList: capture (Comma capture)* Ellipsis?;

capture: simpleCapture | initcapture;

simpleCapture: And? Identifier | THIS;

initcapture: And? Identifier initializer;

lambdaDeclarator:
	LeftParen parameterDeclarationClause? RightParen MUTABLE? exceptionSpecification?
		attributeSpecifierSeq? trailingReturnType?;

postfixExpression:
	primaryExpression
	| postfixExpression LeftBracket (expression | bracedInitList) RightBracket
	| postfixExpression LeftParen expressionList? RightParen
	| (simpleTypeSpecifier | typeNameSpecifier) (
		LeftParen expressionList? RightParen
		| bracedInitList
	)
	| postfixExpression (Dot | Arrow) (
		TEMPLATE? idExpression
		| pseudoDestructorName
	)
	| postfixExpression (PlusPlus | MinusMinus)
	| (
		DYNAMIC_CAST
		| STATIC_CAST
		| REINTERPRET_CAST
		| CONST_CAST
	) Less theTypeId Greater LeftParen expression RightParen
	| typeIdOfTheTypeId LeftParen (expression | theTypeId) RightParen;
/*
 add a middle layer to eliminate duplicated function declarations
 */

typeIdOfTheTypeId: TYPEID;

expressionList: initializerList;

pseudoDestructorName:
	nestedNameSpecifier? (theTypeName DoubleColon)? Tilde theTypeName
	| nestedNameSpecifier TEMPLATE simpleTemplateId DoubleColon Tilde theTypeName
	| Tilde decltypeSpecifier;

unaryExpression:
	postfixExpression
	| (PlusPlus | MinusMinus | unaryOperator | SIZEOF) unaryExpression
	| SIZEOF (
		LeftParen theTypeId RightParen
		| Ellipsis LeftParen Identifier RightParen
	)
	| ALIGNOF LeftParen theTypeId RightParen
	| noExceptExpression
	| newExpression
	| deleteExpression;

unaryOperator: Or | Star | And | Plus | Tilde | Minus | Not;

newExpression:
	DoubleColon? NEW newPlacement? (
		newTypeId
		| (LeftParen theTypeId RightParen)
	) newInitializer?;

newPlacement: LeftParen expressionList RightParen;

newTypeId: typeSpecifierSeq newDeclarator?;

newDeclarator:
	pointerOperator newDeclarator?
	| noPointerNewDeclarator;

noPointerNewDeclarator:
	LeftBracket expression RightBracket attributeSpecifierSeq?
	| noPointerNewDeclarator LeftBracket constantExpression RightBracket attributeSpecifierSeq?;

newInitializer:
	LeftParen expressionList? RightParen
	| bracedInitList;

deleteExpression:
	DoubleColon? DELETE (LeftBracket RightBracket)? castExpression;

noExceptExpression: NOEXCEPT LeftParen expression RightParen;

castExpression:
	unaryExpression
	| LeftParen theTypeId RightParen castExpression;

pointerMemberExpression:
	castExpression ((DotStar | ArrowStar) castExpression)*;

multiplicativeExpression:
	pointerMemberExpression (
		(Star | Div | Mod) pointerMemberExpression
	)*;

additiveExpression:
	multiplicativeExpression (
		(Plus | Minus) multiplicativeExpression
	)*;

shiftExpression:
	additiveExpression (shiftOperator additiveExpression)*;

shiftOperator: Greater Greater | Less Less;

relationalExpression:
	shiftExpression (
		(Less | Greater | LessEqual | GreaterEqual) shiftExpression
	)*;

equalityExpression:
	relationalExpression (
		(Equal | NotEqual) relationalExpression
	)*;

andExpression: equalityExpression (And equalityExpression)*;

exclusiveOrExpression: andExpression (Caret andExpression)*;

inclusiveOrExpression:
	exclusiveOrExpression (Or exclusiveOrExpression)*;

logicalAndExpression:
	inclusiveOrExpression (AndAnd inclusiveOrExpression)*;

logicalOrExpression:
	logicalAndExpression (OrOr logicalAndExpression)*;

conditionalExpression:
	logicalOrExpression (
		Question expression Colon assignmentExpression
	)?;

assignmentExpression:
	conditionalExpression
	| logicalOrExpression assignmentOperator initializerClause
	| throwExpression;

assignmentOperator:
	Assign
	| StarAssign
	| DivAssign
	| ModAssign
	| PlusAssign
	| MinusAssign
	| RightShiftAssign
	| LeftShiftAssign
	| AndAssign
	| XorAssign
	| OrAssign;

expression: assignmentExpression (Comma assignmentExpression)*;

constantExpression: conditionalExpression;
/*Statements*/

statement:
	labeledStatement
	| attributeSpecifierSeq? (
		expressionStatement
		| compoundStatement
		| selectionStatement
		| iterationStatement
		| jumpStatement
		| tryBlock
	)
	| declarationStatement;

labeledStatement:
	attributeSpecifierSeq? (
		Identifier
		| CASE constantExpression
		| DEFAULT
	) Colon statement;

expressionStatement: expression? Semi;

compoundStatement: LeftBrace statementSeq? RightBrace;

statementSeq: statement+;

selectionStatement:
	IF LeftParen condition RightParen statement (ELSE statement)?
	| SWITCH LeftParen condition RightParen statement;

condition:
	expression
	| attributeSpecifierSeq? declSpecifierSeq declarator (
		Assign initializerClause
		| bracedInitList
	);

iterationStatement:
	WHILE LeftParen condition RightParen statement
	| DO statement WHILE LeftParen expression RightParen Semi
	| FOR LeftParen (
		forInitStatement condition? Semi expression?
		| forRangeDeclaration Colon forRangeInitializer
	) RightParen statement;

forInitStatement: expressionStatement | simpleDeclaration;

forRangeDeclaration:
	attributeSpecifierSeq? declSpecifierSeq declarator;

forRangeInitializer: expression | bracedInitList;

jumpStatement:
	(
		BREAK
		| CONTINUE
		| RETURN (expression | bracedInitList)?
		| GOTO Identifier
	) Semi;

declarationStatement: blockDeclaration;
/*Declarations*/

declarationseq: declaration+;

declaration:
	blockDeclaration
	| functionDefinition
	| templateDeclaration
	| explicitInstantiation
	| explicitSpecialization
	| linkageSpecification
	| namespaceDefinition
	| emptyDeclaration
	| attributeDeclaration;

blockDeclaration:
	simpleDeclaration
	| asmDefinition
	| namespaceAliasDefinition
	| usingDeclaration
	| usingDirective
	| staticAssertDeclaration
	| aliasDeclaration
	| opaqueEnumDeclaration;

aliasDeclaration:
	USING Identifier attributeSpecifierSeq? Assign theTypeId Semi;

simpleDeclaration:
	declSpecifierSeq? initDeclaratorList? Semi
	| attributeSpecifierSeq declSpecifierSeq? initDeclaratorList Semi;

staticAssertDeclaration:
	STATIC_ASSERT LeftParen constantExpression Comma StringLiteral RightParen Semi;

emptyDeclaration: Semi;

attributeDeclaration: attributeSpecifierSeq Semi;

declSpecifier:
	storageClassSpecifier
	| typeSpecifier
	| functionSpecifier
	| FRIEND
	| TYPEDEF
	| CONSTEXPR;

declSpecifierSeq: declSpecifier+ attributeSpecifierSeq?;

storageClassSpecifier:
	REGISTER
	| STATIC
	| THREAD_LOCAL
	| EXTERN
	| MUTABLE;

functionSpecifier: INLINE | VIRTUAL | EXPLICIT;

typedefName: Identifier;

typeSpecifier:
	trailingTypeSpecifier
	| classSpecifier
	| enumSpecifier;

trailingTypeSpecifier:
	simpleTypeSpecifier
	| elaboratedTypeSpecifier
	| typeNameSpecifier
	| cvQualifier;

typeSpecifierSeq: typeSpecifier+ attributeSpecifierSeq?;

trailingTypeSpecifierSeq:
	trailingTypeSpecifier+ attributeSpecifierSeq?;

simpleTypeSpecifier:
	nestedNameSpecifier? theTypeName
	| nestedNameSpecifier TEMPLATE simpleTemplateId
	| CHAR
	| CHAR16_T
	| CHAR32_T
	| WCHAR_T
	| BOOL
	| SHORT
	| INT
	| LONG
	| SIGNED
	| UNSIGNED
	| FLOAT
	| DOUBLE
	| VOID
	| AUTO
	| decltypeSpecifier;

theTypeName:
	className
	| enumName
	| typedefName
	| simpleTemplateId;

decltypeSpecifier:
	DECLTYPE LeftParen (expression | AUTO) RightParen;

elaboratedTypeSpecifier:
	classKey (
		attributeSpecifierSeq? nestedNameSpecifier? Identifier
		| simpleTemplateId
		| nestedNameSpecifier TEMPLATE? simpleTemplateId
	)
	| ENUM nestedNameSpecifier? Identifier;

enumName: Identifier;

enumSpecifier:
	enumHead LeftBrace (enumeratorList Comma?)? RightBrace;

enumHead:
	enumkey attributeSpecifierSeq? (
		nestedNameSpecifier? Identifier
	)? enumbase?;

opaqueEnumDeclaration:
	enumkey attributeSpecifierSeq? Identifier enumbase? Semi;

enumkey: ENUM (CLASS | STRUCT)?;

enumbase: Colon typeSpecifierSeq;

enumeratorList:
	enumeratorDefinition (Comma enumeratorDefinition)*;

enumeratorDefinition: enumerator (Assign constantExpression)?;

enumerator: Identifier;

namespaceName: originalNamespaceName | namespaceAlias;

originalNamespaceName: Identifier;

namespaceDefinition:
	INLINE? NAMESPACE (Identifier | originalNamespaceName)? LeftBrace namespaceBody = declarationseq
		? RightBrace;

namespaceAlias: Identifier;

namespaceAliasDefinition:
	NAMESPACE Identifier Assign qualifiednamespacespecifier Semi;

qualifiednamespacespecifier: nestedNameSpecifier? namespaceName;

usingDeclaration:
	USING ((TYPENAME? nestedNameSpecifier) | DoubleColon) unqualifiedId Semi;

usingDirective:
	attributeSpecifierSeq? USING NAMESPACE nestedNameSpecifier? namespaceName Semi;

asmDefinition: ASM LeftParen StringLiteral RightParen Semi;

linkageSpecification:
	EXTERN StringLiteral (
		LeftBrace declarationseq? RightBrace
		| declaration
	);

attributeSpecifierSeq: attributeSpecifier+;

attributeSpecifier:
	LeftBracket LeftBracket attributeList? RightBracket RightBracket
	| alignmentspecifier;

alignmentspecifier:
	ALIGNAS LeftParen (theTypeId | constantExpression) Ellipsis? RightParen;

attributeList: attribute (Comma attribute)* Ellipsis?;

attribute: (attributeNamespace DoubleColon)? Identifier attributeArgumentClause?;

attributeNamespace: Identifier;

attributeArgumentClause: LeftParen balancedTokenSeq? RightParen;

balancedTokenSeq: balancedtoken+;

balancedtoken:
	LeftParen balancedTokenSeq RightParen
	| LeftBracket balancedTokenSeq RightBracket
	| LeftBrace balancedTokenSeq RightBrace
	| ~(
		LeftParen
		| RightParen
		| LeftBrace
		| RightBrace
		| LeftBracket
		| RightBracket
	)+;
/*Declarators*/

initDeclaratorList: initDeclarator (Comma initDeclarator)*;

initDeclarator: declarator initializer?;

declarator:
	pointerDeclarator
	| noPointerDeclarator parametersAndQualifiers trailingReturnType;

pointerDeclarator: (pointerOperator CONST?)* noPointerDeclarator;

noPointerDeclarator:
	declaratorid attributeSpecifierSeq?
	| noPointerDeclarator (
		parametersAndQualifiers
		| LeftBracket constantExpression? RightBracket attributeSpecifierSeq?
	)
	| LeftParen pointerDeclarator RightParen;

parametersAndQualifiers:
	LeftParen parameterDeclarationClause? RightParen cvqualifierseq? refqualifier?
		exceptionSpecification? attributeSpecifierSeq?;

trailingReturnType:
	Arrow trailingTypeSpecifierSeq abstractDeclarator?;

pointerOperator:
	(And | AndAnd) attributeSpecifierSeq?
	| nestedNameSpecifier? Star attributeSpecifierSeq? cvqualifierseq?;

cvqualifierseq: cvQualifier+;

cvQualifier: CONST | VOLATILE;

refqualifier: And | AndAnd;

declaratorid: Ellipsis? idExpression;

theTypeId: typeSpecifierSeq abstractDeclarator?;

abstractDeclarator:
	pointerAbstractDeclarator
	| noPointerAbstractDeclarator? parametersAndQualifiers trailingReturnType
	| abstractPackDeclarator;

pointerAbstractDeclarator:
	noPointerAbstractDeclarator
	| pointerOperator+ noPointerAbstractDeclarator?;

noPointerAbstractDeclarator:
	noPointerAbstractDeclarator (
		parametersAndQualifiers
		| noPointerAbstractDeclarator LeftBracket constantExpression? RightBracket
			attributeSpecifierSeq?
	)
	| parametersAndQualifiers
	| LeftBracket constantExpression? RightBracket attributeSpecifierSeq?
	| LeftParen pointerAbstractDeclarator RightParen;

abstractPackDeclarator:
	pointerOperator* noPointerAbstractPackDeclarator;

noPointerAbstractPackDeclarator:
	noPointerAbstractPackDeclarator (
		parametersAndQualifiers
		| LeftBracket constantExpression? RightBracket attributeSpecifierSeq?
	)
	| Ellipsis;

parameterDeclarationClause:
	parameterDeclarationList (Comma? Ellipsis)?;

parameterDeclarationList:
	parameterDeclaration (Comma parameterDeclaration)*;

parameterDeclaration:
	attributeSpecifierSeq? declSpecifierSeq (
		(declarator | abstractDeclarator?) (
			Assign initializerClause
		)?
	);

functionDefinition:
	attributeSpecifierSeq? declSpecifierSeq? declarator virtualSpecifierSeq? functionBody;

functionBody:
	constructorInitializer? compoundStatement
	| functionTryBlock
	| Assign (DEFAULT | DELETE) Semi;

initializer:
	braceOrEqualInitializer
	| LeftParen expressionList RightParen;

braceOrEqualInitializer:
	Assign initializerClause
	| bracedInitList;

initializerClause: assignmentExpression | bracedInitList;

initializerList:
	initializerClause Ellipsis? (
		Comma initializerClause Ellipsis?
	)*;

bracedInitList: LeftBrace (initializerList Comma?)? RightBrace;
/*Classes*/

className: Identifier | simpleTemplateId;

classSpecifier:
	classHead LeftBrace memberSpecification? RightBrace;

classHead:
	classKey attributeSpecifierSeq? (
		classHeadName classVirtSpecifier?
	)? baseClause?
	| UNION attributeSpecifierSeq? (
		classHeadName classVirtSpecifier?
	)?;

classHeadName: nestedNameSpecifier? className;

classVirtSpecifier: FINAL;

classKey: CLASS | STRUCT;

memberSpecification:
	(memberdeclaration | accessSpecifier Colon)+;

memberdeclaration:
	attributeSpecifierSeq? declSpecifierSeq? memberDeclaratorList? Semi
	| functionDefinition
	| usingDeclaration
	| staticAssertDeclaration
	| templateDeclaration
	| aliasDeclaration
	| emptyDeclaration;

memberDeclaratorList:
	memberDeclarator (Comma memberDeclarator)*;

memberDeclarator:
	declarator (
		virtualSpecifierSeq? pureSpecifier?
		| braceOrEqualInitializer?
	)
	| Identifier? attributeSpecifierSeq? Colon constantExpression;

virtualSpecifierSeq: virtualSpecifier+;

virtualSpecifier: OVERRIDE | FINAL;
/*
 purespecifier: Assign '0'//Conflicts with the lexer ;
 */

pureSpecifier:
	Assign val = OctalLiteral {if($val.text.compareTo("0")!=0) throw new InputMismatchException(this);
		};
/*Derived classes*/

baseClause: Colon baseSpecifierList;

baseSpecifierList:
	baseSpecifier Ellipsis? (Comma baseSpecifier Ellipsis?)*;

baseSpecifier:
	attributeSpecifierSeq? (
		baseTypeSpecifier
		| VIRTUAL accessSpecifier? baseTypeSpecifier
		| accessSpecifier VIRTUAL? baseTypeSpecifier
	);

classOrDeclType:
	nestedNameSpecifier? className
	| decltypeSpecifier;

baseTypeSpecifier: classOrDeclType;

accessSpecifier: PRIVATE | PROTECTED | PUBLIC;
/*Special member functions*/

conversionFunctionId: OPERATOR conversionTypeId;

conversionTypeId: typeSpecifierSeq conversionDeclarator?;

conversionDeclarator: pointerOperator conversionDeclarator?;

constructorInitializer: Colon memInitializerList;

memInitializerList:
	memInitializer Ellipsis? (Comma memInitializer Ellipsis?)*;

memInitializer:
	meminitializerid (
		LeftParen expressionList? RightParen
		| bracedInitList
	);

meminitializerid: classOrDeclType | Identifier;
/*Overloading*/

operatorFunctionId: OPERATOR theOperator;

literalOperatorId:
	OPERATOR (
		StringLiteral Identifier
		| UserDefinedStringLiteral
	);
/*Templates*/

templateDeclaration:
	TEMPLATE Less templateparameterList Greater declaration;

templateparameterList:
	templateParameter (Comma templateParameter)*;

templateParameter: typeParameter | parameterDeclaration;

typeParameter:
	(
		(TEMPLATE Less templateparameterList Greater)? CLASS
		| TYPENAME
	) ((Ellipsis? Identifier?) | (Identifier? Assign theTypeId));

simpleTemplateId:
	templateName Less templateArgumentList? Greater;

templateId:
	simpleTemplateId
	| (operatorFunctionId | literalOperatorId) Less templateArgumentList? Greater;

templateName: Identifier;

templateArgumentList:
	templateArgument Ellipsis? (Comma templateArgument Ellipsis?)*;

templateArgument: theTypeId | constantExpression | idExpression;

typeNameSpecifier:
	TYPENAME nestedNameSpecifier (
		Identifier
		| TEMPLATE? simpleTemplateId
	);

explicitInstantiation: EXTERN? TEMPLATE declaration;

explicitSpecialization: TEMPLATE Less Greater declaration;
/*Exception handling*/

tryBlock: TRY compoundStatement handlerSeq;

functionTryBlock:
	TRY constructorInitializer? compoundStatement handlerSeq;

handlerSeq: handler+;

handler:
	CATCH LeftParen exceptionDeclaration RightParen compoundStatement;

exceptionDeclaration:
	attributeSpecifierSeq? typeSpecifierSeq (
		declarator
		| abstractDeclarator
	)?
	| Ellipsis;

throwExpression: THROW assignmentExpression?;

exceptionSpecification:
	dynamicExceptionSpecification
	| noeExceptSpecification;

dynamicExceptionSpecification:
	THROW LeftParen typeIdList? RightParen;

typeIdList: theTypeId Ellipsis? (Comma theTypeId Ellipsis?)*;

noeExceptSpecification:
	NOEXCEPT LeftParen constantExpression RightParen
	| NOEXCEPT;
/*Preprocessing directives*/

/*Lexer*/

theOperator:
	NEW (LeftBracket RightBracket)?
	| DELETE (LeftBracket RightBracket)?
	| Plus
	| Minus
	| Star
	| Div
	| Mod
	| Caret
	| And
	| Or
	| Tilde
	| Not
	| Assign
	| shiftOperator // GJ20: allow shift operators
	| Greater
	| Less
	| GreaterEqual
	| PlusAssign
	| MinusAssign
	| StarAssign
	| Assign
	| ModAssign
	| XorAssign
	| AndAssign
	| OrAssign
	| Less Less
	| Greater Greater
	| RightShiftAssign
	| LeftShiftAssign
	| Equal
	| NotEqual
	| LessEqual
	| GreaterEqual
	| AndAnd
	| OrOr
	| PlusPlus
	| MinusMinus
	| Comma
	| ArrowStar
	| Arrow
	| LeftParen RightParen
	| LeftBracket RightBracket;

literal:
	IntegerLiteral
	| CharacterLiteral
	| FloatingLiteral
	| StringLiteral
	| TRUE // weiz 2021-02-24 Previously it was BooleanLiteral, which caused ambiguity for parser   GJ21
	| FALSE // weiz 2021-02-24 Previously it was BooleanLiteral, which caused ambiguity for parser  GJ21
	| PointerLiteral
	| UserDefinedLiteral;
