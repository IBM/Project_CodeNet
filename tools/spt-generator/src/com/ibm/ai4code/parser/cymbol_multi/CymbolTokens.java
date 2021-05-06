// Generated from CymbolTokens.g4 by ANTLR 4.8
package com.ibm.ai4code.parser.cymbol_multi;
import org.antlr.v4.runtime.Lexer;
import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.TokenStream;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.misc.*;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast"})
public class CymbolTokens extends Lexer {
	static { RuntimeMetaData.checkVersion("4.8", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		KEYWORDS=1, PUNCTUATORS=2, ASSIGN=3, SEMICOLON=4, LPAREN=5, RPAREN=6, 
		LBRACK=7, RBRACK=8, LBRACE=9, RBRACE=10, COMMA=11, BANG=12, ADD=13, SUB=14, 
		MUL=15, EQUAL=16, FLOAT=17, INTEGER=18, VOID=19, IF=20, THEN=21, RETURN=22, 
		ID=23, INT=24, WS=25, SL_COMMENT=26;
	public static String[] channelNames = {
		"DEFAULT_TOKEN_CHANNEL", "HIDDEN"
	};

	public static String[] modeNames = {
		"DEFAULT_MODE"
	};

	private static String[] makeRuleNames() {
		return new String[] {
			"KEYWORDS", "PUNCTUATORS", "ASSIGN", "SEMICOLON", "LPAREN", "RPAREN", 
			"LBRACK", "RBRACK", "LBRACE", "RBRACE", "COMMA", "BANG", "ADD", "SUB", 
			"MUL", "EQUAL", "FLOAT", "INTEGER", "VOID", "IF", "THEN", "RETURN", "ID", 
			"LETTER", "INT", "WS", "SL_COMMENT"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, null, null, "'='", "';'", "'('", "')'", "'['", "']'", "'{'", "'}'", 
			"','", "'!'", "'+'", "'-'", "'*'", "'=='", "'float'", "'int'", "'void'", 
			"'if'", "'else'", "'return'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, "KEYWORDS", "PUNCTUATORS", "ASSIGN", "SEMICOLON", "LPAREN", "RPAREN", 
			"LBRACK", "RBRACK", "LBRACE", "RBRACE", "COMMA", "BANG", "ADD", "SUB", 
			"MUL", "EQUAL", "FLOAT", "INTEGER", "VOID", "IF", "THEN", "RETURN", "ID", 
			"INT", "WS", "SL_COMMENT"
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


	public CymbolTokens(CharStream input) {
		super(input);
		_interp = new LexerATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	@Override
	public String getGrammarFileName() { return "CymbolTokens.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public String[] getChannelNames() { return channelNames; }

	@Override
	public String[] getModeNames() { return modeNames; }

	@Override
	public ATN getATN() { return _ATN; }

	public static final String _serializedATN =
		"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\34\u00af\b\1\4\2"+
		"\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4"+
		"\13\t\13\4\f\t\f\4\r\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22"+
		"\t\22\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30\4\31"+
		"\t\31\4\32\t\32\4\33\t\33\4\34\t\34\3\2\3\2\3\2\3\2\3\2\3\2\5\2@\n\2\3"+
		"\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\5\3P\n\3\3\4\3"+
		"\4\3\5\3\5\3\6\3\6\3\7\3\7\3\b\3\b\3\t\3\t\3\n\3\n\3\13\3\13\3\f\3\f\3"+
		"\r\3\r\3\16\3\16\3\17\3\17\3\20\3\20\3\21\3\21\3\21\3\22\3\22\3\22\3\22"+
		"\3\22\3\22\3\23\3\23\3\23\3\23\3\24\3\24\3\24\3\24\3\24\3\25\3\25\3\25"+
		"\3\26\3\26\3\26\3\26\3\26\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\30\3\30"+
		"\3\30\7\30\u0090\n\30\f\30\16\30\u0093\13\30\3\31\3\31\3\32\6\32\u0098"+
		"\n\32\r\32\16\32\u0099\3\33\6\33\u009d\n\33\r\33\16\33\u009e\3\33\3\33"+
		"\3\34\3\34\3\34\3\34\7\34\u00a7\n\34\f\34\16\34\u00aa\13\34\3\34\3\34"+
		"\3\34\3\34\3\u00a8\2\35\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\23\13\25\f"+
		"\27\r\31\16\33\17\35\20\37\21!\22#\23%\24\'\25)\26+\27-\30/\31\61\2\63"+
		"\32\65\33\67\34\3\2\5\3\2\62;\4\2C\\c|\5\2\13\f\17\17\"\"\2\u00c4\2\3"+
		"\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2"+
		"\2\17\3\2\2\2\2\21\3\2\2\2\2\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2\31"+
		"\3\2\2\2\2\33\3\2\2\2\2\35\3\2\2\2\2\37\3\2\2\2\2!\3\2\2\2\2#\3\2\2\2"+
		"\2%\3\2\2\2\2\'\3\2\2\2\2)\3\2\2\2\2+\3\2\2\2\2-\3\2\2\2\2/\3\2\2\2\2"+
		"\63\3\2\2\2\2\65\3\2\2\2\2\67\3\2\2\2\3?\3\2\2\2\5O\3\2\2\2\7Q\3\2\2\2"+
		"\tS\3\2\2\2\13U\3\2\2\2\rW\3\2\2\2\17Y\3\2\2\2\21[\3\2\2\2\23]\3\2\2\2"+
		"\25_\3\2\2\2\27a\3\2\2\2\31c\3\2\2\2\33e\3\2\2\2\35g\3\2\2\2\37i\3\2\2"+
		"\2!k\3\2\2\2#n\3\2\2\2%t\3\2\2\2\'x\3\2\2\2)}\3\2\2\2+\u0080\3\2\2\2-"+
		"\u0085\3\2\2\2/\u008c\3\2\2\2\61\u0094\3\2\2\2\63\u0097\3\2\2\2\65\u009c"+
		"\3\2\2\2\67\u00a2\3\2\2\29@\5#\22\2:@\5%\23\2;@\5\'\24\2<@\5)\25\2=@\5"+
		"+\26\2>@\5-\27\2?9\3\2\2\2?:\3\2\2\2?;\3\2\2\2?<\3\2\2\2?=\3\2\2\2?>\3"+
		"\2\2\2@\4\3\2\2\2AP\5\7\4\2BP\5\t\5\2CP\5\13\6\2DP\5\r\7\2EP\5\17\b\2"+
		"FP\5\21\t\2GP\5\23\n\2HP\5\25\13\2IP\5\27\f\2JP\5\31\r\2KP\5\33\16\2L"+
		"P\5\35\17\2MP\5\37\20\2NP\5!\21\2OA\3\2\2\2OB\3\2\2\2OC\3\2\2\2OD\3\2"+
		"\2\2OE\3\2\2\2OF\3\2\2\2OG\3\2\2\2OH\3\2\2\2OI\3\2\2\2OJ\3\2\2\2OK\3\2"+
		"\2\2OL\3\2\2\2OM\3\2\2\2ON\3\2\2\2P\6\3\2\2\2QR\7?\2\2R\b\3\2\2\2ST\7"+
		"=\2\2T\n\3\2\2\2UV\7*\2\2V\f\3\2\2\2WX\7+\2\2X\16\3\2\2\2YZ\7]\2\2Z\20"+
		"\3\2\2\2[\\\7_\2\2\\\22\3\2\2\2]^\7}\2\2^\24\3\2\2\2_`\7\177\2\2`\26\3"+
		"\2\2\2ab\7.\2\2b\30\3\2\2\2cd\7#\2\2d\32\3\2\2\2ef\7-\2\2f\34\3\2\2\2"+
		"gh\7/\2\2h\36\3\2\2\2ij\7,\2\2j \3\2\2\2kl\7?\2\2lm\7?\2\2m\"\3\2\2\2"+
		"no\7h\2\2op\7n\2\2pq\7q\2\2qr\7c\2\2rs\7v\2\2s$\3\2\2\2tu\7k\2\2uv\7p"+
		"\2\2vw\7v\2\2w&\3\2\2\2xy\7x\2\2yz\7q\2\2z{\7k\2\2{|\7f\2\2|(\3\2\2\2"+
		"}~\7k\2\2~\177\7h\2\2\177*\3\2\2\2\u0080\u0081\7g\2\2\u0081\u0082\7n\2"+
		"\2\u0082\u0083\7u\2\2\u0083\u0084\7g\2\2\u0084,\3\2\2\2\u0085\u0086\7"+
		"t\2\2\u0086\u0087\7g\2\2\u0087\u0088\7v\2\2\u0088\u0089\7w\2\2\u0089\u008a"+
		"\7t\2\2\u008a\u008b\7p\2\2\u008b.\3\2\2\2\u008c\u0091\5\61\31\2\u008d"+
		"\u0090\5\61\31\2\u008e\u0090\t\2\2\2\u008f\u008d\3\2\2\2\u008f\u008e\3"+
		"\2\2\2\u0090\u0093\3\2\2\2\u0091\u008f\3\2\2\2\u0091\u0092\3\2\2\2\u0092"+
		"\60\3\2\2\2\u0093\u0091\3\2\2\2\u0094\u0095\t\3\2\2\u0095\62\3\2\2\2\u0096"+
		"\u0098\t\2\2\2\u0097\u0096\3\2\2\2\u0098\u0099\3\2\2\2\u0099\u0097\3\2"+
		"\2\2\u0099\u009a\3\2\2\2\u009a\64\3\2\2\2\u009b\u009d\t\4\2\2\u009c\u009b"+
		"\3\2\2\2\u009d\u009e\3\2\2\2\u009e\u009c\3\2\2\2\u009e\u009f\3\2\2\2\u009f"+
		"\u00a0\3\2\2\2\u00a0\u00a1\b\33\2\2\u00a1\66\3\2\2\2\u00a2\u00a3\7\61"+
		"\2\2\u00a3\u00a4\7\61\2\2\u00a4\u00a8\3\2\2\2\u00a5\u00a7\13\2\2\2\u00a6"+
		"\u00a5\3\2\2\2\u00a7\u00aa\3\2\2\2\u00a8\u00a9\3\2\2\2\u00a8\u00a6\3\2"+
		"\2\2\u00a9\u00ab\3\2\2\2\u00aa\u00a8\3\2\2\2\u00ab\u00ac\7\f\2\2\u00ac"+
		"\u00ad\3\2\2\2\u00ad\u00ae\b\34\2\2\u00ae8\3\2\2\2\n\2?O\u008f\u0091\u0099"+
		"\u009e\u00a8\3\b\2\2";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}