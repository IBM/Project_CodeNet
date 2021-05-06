// Generated from Cymbol.g4 by ANTLR 4.8
package com.ibm.ai4code.parser.cymbol;
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.*;
import org.antlr.v4.runtime.tree.*;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast"})
public class CymbolParser extends Parser {
	static { RuntimeMetaData.checkVersion("4.8", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		T__0=1, ASSIGN=2, SEMICOLON=3, LPAREN=4, RPAREN=5, LBRACK=6, RBRACK=7, 
		LBRACE=8, RBRACE=9, COMMA=10, BANG=11, ADD=12, SUB=13, MUL=14, EQUAL=15, 
		FLOAT=16, INTEGER=17, VOID=18, IF=19, THEN=20, RETURN=21, ID=22, INT=23, 
		WS=24, SL_COMMENT=25;
	public static final int
		RULE_file = 0, RULE_varDecl = 1, RULE_type = 2, RULE_functionDecl = 3, 
		RULE_formalParameters = 4, RULE_formalParameter = 5, RULE_block = 6, RULE_stat = 7, 
		RULE_expr = 8, RULE_exprList = 9;
	private static String[] makeRuleNames() {
		return new String[] {
			"file", "varDecl", "type", "functionDecl", "formalParameters", "formalParameter", 
			"block", "stat", "expr", "exprList"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'then'", "'='", "';'", "'('", "')'", "'['", "']'", "'{'", "'}'", 
			"','", "'!'", "'+'", "'-'", "'*'", "'=='", "'float'", "'int'", "'void'", 
			"'if'", "'else'", "'return'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, null, "ASSIGN", "SEMICOLON", "LPAREN", "RPAREN", "LBRACK", "RBRACK", 
			"LBRACE", "RBRACE", "COMMA", "BANG", "ADD", "SUB", "MUL", "EQUAL", "FLOAT", 
			"INTEGER", "VOID", "IF", "THEN", "RETURN", "ID", "INT", "WS", "SL_COMMENT"
		};
	}
	private static final String[] _SYMBOLIC_NAMES = makeSymbolicNames();
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}

	@Override
	public String getGrammarFileName() { return "Cymbol.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public ATN getATN() { return _ATN; }

	public CymbolParser(TokenStream input) {
		super(input);
		_interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	public static class FileContext extends ParserRuleContext {
		public List<FunctionDeclContext> functionDecl() {
			return getRuleContexts(FunctionDeclContext.class);
		}
		public FunctionDeclContext functionDecl(int i) {
			return getRuleContext(FunctionDeclContext.class,i);
		}
		public List<VarDeclContext> varDecl() {
			return getRuleContexts(VarDeclContext.class);
		}
		public VarDeclContext varDecl(int i) {
			return getRuleContext(VarDeclContext.class,i);
		}
		public FileContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_file; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).enterFile(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).exitFile(this);
		}
	}

	public final FileContext file() throws RecognitionException {
		FileContext _localctx = new FileContext(_ctx, getState());
		enterRule(_localctx, 0, RULE_file);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(22); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				setState(22);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,0,_ctx) ) {
				case 1:
					{
					setState(20);
					functionDecl();
					}
					break;
				case 2:
					{
					setState(21);
					varDecl();
					}
					break;
				}
				}
				setState(24); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << FLOAT) | (1L << INTEGER) | (1L << VOID))) != 0) );
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class VarDeclContext extends ParserRuleContext {
		public TypeContext type() {
			return getRuleContext(TypeContext.class,0);
		}
		public TerminalNode ID() { return getToken(CymbolParser.ID, 0); }
		public TerminalNode SEMICOLON() { return getToken(CymbolParser.SEMICOLON, 0); }
		public TerminalNode ASSIGN() { return getToken(CymbolParser.ASSIGN, 0); }
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public VarDeclContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_varDecl; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).enterVarDecl(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).exitVarDecl(this);
		}
	}

	public final VarDeclContext varDecl() throws RecognitionException {
		VarDeclContext _localctx = new VarDeclContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_varDecl);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(26);
			type();
			setState(27);
			match(ID);
			setState(30);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ASSIGN) {
				{
				setState(28);
				match(ASSIGN);
				setState(29);
				expr(0);
				}
			}

			setState(32);
			match(SEMICOLON);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class TypeContext extends ParserRuleContext {
		public TerminalNode FLOAT() { return getToken(CymbolParser.FLOAT, 0); }
		public TerminalNode INTEGER() { return getToken(CymbolParser.INTEGER, 0); }
		public TerminalNode VOID() { return getToken(CymbolParser.VOID, 0); }
		public TypeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_type; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).enterType(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).exitType(this);
		}
	}

	public final TypeContext type() throws RecognitionException {
		TypeContext _localctx = new TypeContext(_ctx, getState());
		enterRule(_localctx, 4, RULE_type);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(34);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << FLOAT) | (1L << INTEGER) | (1L << VOID))) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class FunctionDeclContext extends ParserRuleContext {
		public TypeContext type() {
			return getRuleContext(TypeContext.class,0);
		}
		public TerminalNode ID() { return getToken(CymbolParser.ID, 0); }
		public TerminalNode LPAREN() { return getToken(CymbolParser.LPAREN, 0); }
		public TerminalNode RPAREN() { return getToken(CymbolParser.RPAREN, 0); }
		public BlockContext block() {
			return getRuleContext(BlockContext.class,0);
		}
		public FormalParametersContext formalParameters() {
			return getRuleContext(FormalParametersContext.class,0);
		}
		public FunctionDeclContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_functionDecl; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).enterFunctionDecl(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).exitFunctionDecl(this);
		}
	}

	public final FunctionDeclContext functionDecl() throws RecognitionException {
		FunctionDeclContext _localctx = new FunctionDeclContext(_ctx, getState());
		enterRule(_localctx, 6, RULE_functionDecl);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(36);
			type();
			setState(37);
			match(ID);
			setState(38);
			match(LPAREN);
			setState(40);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << FLOAT) | (1L << INTEGER) | (1L << VOID))) != 0)) {
				{
				setState(39);
				formalParameters();
				}
			}

			setState(42);
			match(RPAREN);
			setState(43);
			block();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class FormalParametersContext extends ParserRuleContext {
		public List<FormalParameterContext> formalParameter() {
			return getRuleContexts(FormalParameterContext.class);
		}
		public FormalParameterContext formalParameter(int i) {
			return getRuleContext(FormalParameterContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(CymbolParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(CymbolParser.COMMA, i);
		}
		public FormalParametersContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_formalParameters; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).enterFormalParameters(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).exitFormalParameters(this);
		}
	}

	public final FormalParametersContext formalParameters() throws RecognitionException {
		FormalParametersContext _localctx = new FormalParametersContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_formalParameters);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(45);
			formalParameter();
			setState(50);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(46);
				match(COMMA);
				setState(47);
				formalParameter();
				}
				}
				setState(52);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class FormalParameterContext extends ParserRuleContext {
		public TypeContext type() {
			return getRuleContext(TypeContext.class,0);
		}
		public TerminalNode ID() { return getToken(CymbolParser.ID, 0); }
		public FormalParameterContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_formalParameter; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).enterFormalParameter(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).exitFormalParameter(this);
		}
	}

	public final FormalParameterContext formalParameter() throws RecognitionException {
		FormalParameterContext _localctx = new FormalParameterContext(_ctx, getState());
		enterRule(_localctx, 10, RULE_formalParameter);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(53);
			type();
			setState(54);
			match(ID);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class BlockContext extends ParserRuleContext {
		public TerminalNode LBRACE() { return getToken(CymbolParser.LBRACE, 0); }
		public TerminalNode RBRACE() { return getToken(CymbolParser.RBRACE, 0); }
		public List<StatContext> stat() {
			return getRuleContexts(StatContext.class);
		}
		public StatContext stat(int i) {
			return getRuleContext(StatContext.class,i);
		}
		public BlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_block; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).enterBlock(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).exitBlock(this);
		}
	}

	public final BlockContext block() throws RecognitionException {
		BlockContext _localctx = new BlockContext(_ctx, getState());
		enterRule(_localctx, 12, RULE_block);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(56);
			match(LBRACE);
			setState(60);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << LPAREN) | (1L << LBRACE) | (1L << BANG) | (1L << SUB) | (1L << FLOAT) | (1L << INTEGER) | (1L << VOID) | (1L << IF) | (1L << RETURN) | (1L << ID) | (1L << INT))) != 0)) {
				{
				{
				setState(57);
				stat();
				}
				}
				setState(62);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(63);
			match(RBRACE);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class StatContext extends ParserRuleContext {
		public BlockContext block() {
			return getRuleContext(BlockContext.class,0);
		}
		public VarDeclContext varDecl() {
			return getRuleContext(VarDeclContext.class,0);
		}
		public TerminalNode IF() { return getToken(CymbolParser.IF, 0); }
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public List<StatContext> stat() {
			return getRuleContexts(StatContext.class);
		}
		public StatContext stat(int i) {
			return getRuleContext(StatContext.class,i);
		}
		public TerminalNode THEN() { return getToken(CymbolParser.THEN, 0); }
		public TerminalNode RETURN() { return getToken(CymbolParser.RETURN, 0); }
		public TerminalNode SEMICOLON() { return getToken(CymbolParser.SEMICOLON, 0); }
		public TerminalNode ASSIGN() { return getToken(CymbolParser.ASSIGN, 0); }
		public StatContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_stat; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).enterStat(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).exitStat(this);
		}
	}

	public final StatContext stat() throws RecognitionException {
		StatContext _localctx = new StatContext(_ctx, getState());
		enterRule(_localctx, 14, RULE_stat);
		int _la;
		try {
			setState(88);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,8,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(65);
				block();
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(66);
				varDecl();
				}
				break;
			case 3:
				enterOuterAlt(_localctx, 3);
				{
				setState(67);
				match(IF);
				setState(68);
				expr(0);
				setState(69);
				match(T__0);
				setState(70);
				stat();
				setState(73);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,6,_ctx) ) {
				case 1:
					{
					setState(71);
					match(THEN);
					setState(72);
					stat();
					}
					break;
				}
				}
				break;
			case 4:
				enterOuterAlt(_localctx, 4);
				{
				setState(75);
				match(RETURN);
				setState(77);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << LPAREN) | (1L << BANG) | (1L << SUB) | (1L << ID) | (1L << INT))) != 0)) {
					{
					setState(76);
					expr(0);
					}
				}

				setState(79);
				match(SEMICOLON);
				}
				break;
			case 5:
				enterOuterAlt(_localctx, 5);
				{
				setState(80);
				expr(0);
				setState(81);
				match(ASSIGN);
				setState(82);
				expr(0);
				setState(83);
				match(SEMICOLON);
				}
				break;
			case 6:
				enterOuterAlt(_localctx, 6);
				{
				setState(85);
				expr(0);
				setState(86);
				match(SEMICOLON);
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ExprContext extends ParserRuleContext {
		public TerminalNode ID() { return getToken(CymbolParser.ID, 0); }
		public TerminalNode LPAREN() { return getToken(CymbolParser.LPAREN, 0); }
		public TerminalNode RPAREN() { return getToken(CymbolParser.RPAREN, 0); }
		public ExprListContext exprList() {
			return getRuleContext(ExprListContext.class,0);
		}
		public TerminalNode LBRACK() { return getToken(CymbolParser.LBRACK, 0); }
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public TerminalNode RBRACK() { return getToken(CymbolParser.RBRACK, 0); }
		public TerminalNode SUB() { return getToken(CymbolParser.SUB, 0); }
		public TerminalNode BANG() { return getToken(CymbolParser.BANG, 0); }
		public TerminalNode INT() { return getToken(CymbolParser.INT, 0); }
		public TerminalNode MUL() { return getToken(CymbolParser.MUL, 0); }
		public TerminalNode ADD() { return getToken(CymbolParser.ADD, 0); }
		public TerminalNode EQUAL() { return getToken(CymbolParser.EQUAL, 0); }
		public ExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_expr; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).enterExpr(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).exitExpr(this);
		}
	}

	public final ExprContext expr() throws RecognitionException {
		return expr(0);
	}

	private ExprContext expr(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		ExprContext _localctx = new ExprContext(_ctx, _parentState);
		ExprContext _prevctx = _localctx;
		int _startState = 16;
		enterRecursionRule(_localctx, 16, RULE_expr, _p);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(112);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,10,_ctx) ) {
			case 1:
				{
				setState(91);
				match(ID);
				setState(92);
				match(LPAREN);
				setState(94);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << LPAREN) | (1L << BANG) | (1L << SUB) | (1L << ID) | (1L << INT))) != 0)) {
					{
					setState(93);
					exprList();
					}
				}

				setState(96);
				match(RPAREN);
				}
				break;
			case 2:
				{
				setState(97);
				match(ID);
				setState(98);
				match(LBRACK);
				setState(99);
				expr(0);
				setState(100);
				match(RBRACK);
				}
				break;
			case 3:
				{
				setState(102);
				match(SUB);
				setState(103);
				expr(8);
				}
				break;
			case 4:
				{
				setState(104);
				match(BANG);
				setState(105);
				expr(7);
				}
				break;
			case 5:
				{
				setState(106);
				match(ID);
				}
				break;
			case 6:
				{
				setState(107);
				match(INT);
				}
				break;
			case 7:
				{
				setState(108);
				match(LPAREN);
				setState(109);
				expr(0);
				setState(110);
				match(RPAREN);
				}
				break;
			}
			_ctx.stop = _input.LT(-1);
			setState(125);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,12,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					setState(123);
					_errHandler.sync(this);
					switch ( getInterpreter().adaptivePredict(_input,11,_ctx) ) {
					case 1:
						{
						_localctx = new ExprContext(_parentctx, _parentState);
						pushNewRecursionContext(_localctx, _startState, RULE_expr);
						setState(114);
						if (!(precpred(_ctx, 6))) throw new FailedPredicateException(this, "precpred(_ctx, 6)");
						setState(115);
						match(MUL);
						setState(116);
						expr(7);
						}
						break;
					case 2:
						{
						_localctx = new ExprContext(_parentctx, _parentState);
						pushNewRecursionContext(_localctx, _startState, RULE_expr);
						setState(117);
						if (!(precpred(_ctx, 5))) throw new FailedPredicateException(this, "precpred(_ctx, 5)");
						setState(118);
						_la = _input.LA(1);
						if ( !(_la==ADD || _la==SUB) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						setState(119);
						expr(6);
						}
						break;
					case 3:
						{
						_localctx = new ExprContext(_parentctx, _parentState);
						pushNewRecursionContext(_localctx, _startState, RULE_expr);
						setState(120);
						if (!(precpred(_ctx, 4))) throw new FailedPredicateException(this, "precpred(_ctx, 4)");
						setState(121);
						match(EQUAL);
						setState(122);
						expr(5);
						}
						break;
					}
					} 
				}
				setState(127);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,12,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	public static class ExprListContext extends ParserRuleContext {
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(CymbolParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(CymbolParser.COMMA, i);
		}
		public ExprListContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_exprList; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).enterExprList(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof CymbolListener ) ((CymbolListener)listener).exitExprList(this);
		}
	}

	public final ExprListContext exprList() throws RecognitionException {
		ExprListContext _localctx = new ExprListContext(_ctx, getState());
		enterRule(_localctx, 18, RULE_exprList);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(128);
			expr(0);
			setState(133);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(129);
				match(COMMA);
				setState(130);
				expr(0);
				}
				}
				setState(135);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public boolean sempred(RuleContext _localctx, int ruleIndex, int predIndex) {
		switch (ruleIndex) {
		case 8:
			return expr_sempred((ExprContext)_localctx, predIndex);
		}
		return true;
	}
	private boolean expr_sempred(ExprContext _localctx, int predIndex) {
		switch (predIndex) {
		case 0:
			return precpred(_ctx, 6);
		case 1:
			return precpred(_ctx, 5);
		case 2:
			return precpred(_ctx, 4);
		}
		return true;
	}

	public static final String _serializedATN =
		"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\33\u008b\4\2\t\2"+
		"\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13"+
		"\t\13\3\2\3\2\6\2\31\n\2\r\2\16\2\32\3\3\3\3\3\3\3\3\5\3!\n\3\3\3\3\3"+
		"\3\4\3\4\3\5\3\5\3\5\3\5\5\5+\n\5\3\5\3\5\3\5\3\6\3\6\3\6\7\6\63\n\6\f"+
		"\6\16\6\66\13\6\3\7\3\7\3\7\3\b\3\b\7\b=\n\b\f\b\16\b@\13\b\3\b\3\b\3"+
		"\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\5\tL\n\t\3\t\3\t\5\tP\n\t\3\t\3\t\3\t\3"+
		"\t\3\t\3\t\3\t\3\t\3\t\5\t[\n\t\3\n\3\n\3\n\3\n\5\na\n\n\3\n\3\n\3\n\3"+
		"\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\5\ns\n\n\3\n\3\n\3"+
		"\n\3\n\3\n\3\n\3\n\3\n\3\n\7\n~\n\n\f\n\16\n\u0081\13\n\3\13\3\13\3\13"+
		"\7\13\u0086\n\13\f\13\16\13\u0089\13\13\3\13\2\3\22\f\2\4\6\b\n\f\16\20"+
		"\22\24\2\4\3\2\22\24\3\2\16\17\2\u0098\2\30\3\2\2\2\4\34\3\2\2\2\6$\3"+
		"\2\2\2\b&\3\2\2\2\n/\3\2\2\2\f\67\3\2\2\2\16:\3\2\2\2\20Z\3\2\2\2\22r"+
		"\3\2\2\2\24\u0082\3\2\2\2\26\31\5\b\5\2\27\31\5\4\3\2\30\26\3\2\2\2\30"+
		"\27\3\2\2\2\31\32\3\2\2\2\32\30\3\2\2\2\32\33\3\2\2\2\33\3\3\2\2\2\34"+
		"\35\5\6\4\2\35 \7\30\2\2\36\37\7\4\2\2\37!\5\22\n\2 \36\3\2\2\2 !\3\2"+
		"\2\2!\"\3\2\2\2\"#\7\5\2\2#\5\3\2\2\2$%\t\2\2\2%\7\3\2\2\2&\'\5\6\4\2"+
		"\'(\7\30\2\2(*\7\6\2\2)+\5\n\6\2*)\3\2\2\2*+\3\2\2\2+,\3\2\2\2,-\7\7\2"+
		"\2-.\5\16\b\2.\t\3\2\2\2/\64\5\f\7\2\60\61\7\f\2\2\61\63\5\f\7\2\62\60"+
		"\3\2\2\2\63\66\3\2\2\2\64\62\3\2\2\2\64\65\3\2\2\2\65\13\3\2\2\2\66\64"+
		"\3\2\2\2\678\5\6\4\289\7\30\2\29\r\3\2\2\2:>\7\n\2\2;=\5\20\t\2<;\3\2"+
		"\2\2=@\3\2\2\2><\3\2\2\2>?\3\2\2\2?A\3\2\2\2@>\3\2\2\2AB\7\13\2\2B\17"+
		"\3\2\2\2C[\5\16\b\2D[\5\4\3\2EF\7\25\2\2FG\5\22\n\2GH\7\3\2\2HK\5\20\t"+
		"\2IJ\7\26\2\2JL\5\20\t\2KI\3\2\2\2KL\3\2\2\2L[\3\2\2\2MO\7\27\2\2NP\5"+
		"\22\n\2ON\3\2\2\2OP\3\2\2\2PQ\3\2\2\2Q[\7\5\2\2RS\5\22\n\2ST\7\4\2\2T"+
		"U\5\22\n\2UV\7\5\2\2V[\3\2\2\2WX\5\22\n\2XY\7\5\2\2Y[\3\2\2\2ZC\3\2\2"+
		"\2ZD\3\2\2\2ZE\3\2\2\2ZM\3\2\2\2ZR\3\2\2\2ZW\3\2\2\2[\21\3\2\2\2\\]\b"+
		"\n\1\2]^\7\30\2\2^`\7\6\2\2_a\5\24\13\2`_\3\2\2\2`a\3\2\2\2ab\3\2\2\2"+
		"bs\7\7\2\2cd\7\30\2\2de\7\b\2\2ef\5\22\n\2fg\7\t\2\2gs\3\2\2\2hi\7\17"+
		"\2\2is\5\22\n\njk\7\r\2\2ks\5\22\n\tls\7\30\2\2ms\7\31\2\2no\7\6\2\2o"+
		"p\5\22\n\2pq\7\7\2\2qs\3\2\2\2r\\\3\2\2\2rc\3\2\2\2rh\3\2\2\2rj\3\2\2"+
		"\2rl\3\2\2\2rm\3\2\2\2rn\3\2\2\2s\177\3\2\2\2tu\f\b\2\2uv\7\20\2\2v~\5"+
		"\22\n\twx\f\7\2\2xy\t\3\2\2y~\5\22\n\bz{\f\6\2\2{|\7\21\2\2|~\5\22\n\7"+
		"}t\3\2\2\2}w\3\2\2\2}z\3\2\2\2~\u0081\3\2\2\2\177}\3\2\2\2\177\u0080\3"+
		"\2\2\2\u0080\23\3\2\2\2\u0081\177\3\2\2\2\u0082\u0087\5\22\n\2\u0083\u0084"+
		"\7\f\2\2\u0084\u0086\5\22\n\2\u0085\u0083\3\2\2\2\u0086\u0089\3\2\2\2"+
		"\u0087\u0085\3\2\2\2\u0087\u0088\3\2\2\2\u0088\25\3\2\2\2\u0089\u0087"+
		"\3\2\2\2\20\30\32 *\64>KOZ`r}\177\u0087";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}