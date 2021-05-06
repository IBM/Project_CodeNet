// Generated from Cymbol_lexer_common.g4 by ANTLR 4.8
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
public class Cymbol_lexer_common extends Lexer {
	static { RuntimeMetaData.checkVersion("4.8", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		ASSIGN=1, SEMICOLON=2, LPAREN=3, RPAREN=4, LBRACK=5, RBRACK=6, LBRACE=7, 
		RBRACE=8, COMMA=9, BANG=10, ADD=11, SUB=12, MUL=13, EQUAL=14, FLOAT=15, 
		INTEGER=16, VOID=17, IF=18, THEN=19, RETURN=20, ID=21, INT=22, WS=23, 
		SL_COMMENT=24;
	public static String[] channelNames = {
		"DEFAULT_TOKEN_CHANNEL", "HIDDEN"
	};

	public static String[] modeNames = {
		"DEFAULT_MODE"
	};

	private static String[] makeRuleNames() {
		return new String[] {
			"ASSIGN", "SEMICOLON", "LPAREN", "RPAREN", "LBRACK", "RBRACK", "LBRACE", 
			"RBRACE", "COMMA", "BANG", "ADD", "SUB", "MUL", "EQUAL", "FLOAT", "INTEGER", 
			"VOID", "IF", "THEN", "RETURN", "ID", "LETTER", "INT", "WS", "SL_COMMENT"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'='", "';'", "'('", "')'", "'['", "']'", "'{'", "'}'", "','", 
			"'!'", "'+'", "'-'", "'*'", "'=='", "'float'", "'int'", "'void'", "'if'", 
			"'else'", "'return'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, "ASSIGN", "SEMICOLON", "LPAREN", "RPAREN", "LBRACK", "RBRACK", 
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


	public Cymbol_lexer_common(CharStream input) {
		super(input);
		_interp = new LexerATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	@Override
	public String getGrammarFileName() { return "Cymbol_lexer_common.g4"; }

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
		"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\32\u0093\b\1\4\2"+
		"\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4"+
		"\13\t\13\4\f\t\f\4\r\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22"+
		"\t\22\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30\4\31"+
		"\t\31\4\32\t\32\3\2\3\2\3\3\3\3\3\4\3\4\3\5\3\5\3\6\3\6\3\7\3\7\3\b\3"+
		"\b\3\t\3\t\3\n\3\n\3\13\3\13\3\f\3\f\3\r\3\r\3\16\3\16\3\17\3\17\3\17"+
		"\3\20\3\20\3\20\3\20\3\20\3\20\3\21\3\21\3\21\3\21\3\22\3\22\3\22\3\22"+
		"\3\22\3\23\3\23\3\23\3\24\3\24\3\24\3\24\3\24\3\25\3\25\3\25\3\25\3\25"+
		"\3\25\3\25\3\26\3\26\3\26\7\26t\n\26\f\26\16\26w\13\26\3\27\3\27\3\30"+
		"\6\30|\n\30\r\30\16\30}\3\31\6\31\u0081\n\31\r\31\16\31\u0082\3\31\3\31"+
		"\3\32\3\32\3\32\3\32\7\32\u008b\n\32\f\32\16\32\u008e\13\32\3\32\3\32"+
		"\3\32\3\32\3\u008c\2\33\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\23\13\25\f"+
		"\27\r\31\16\33\17\35\20\37\21!\22#\23%\24\'\25)\26+\27-\2/\30\61\31\63"+
		"\32\3\2\5\3\2\62;\4\2C\\c|\5\2\13\f\17\17\"\"\2\u0096\2\3\3\2\2\2\2\5"+
		"\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2"+
		"\2\21\3\2\2\2\2\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2\31\3\2\2\2\2\33"+
		"\3\2\2\2\2\35\3\2\2\2\2\37\3\2\2\2\2!\3\2\2\2\2#\3\2\2\2\2%\3\2\2\2\2"+
		"\'\3\2\2\2\2)\3\2\2\2\2+\3\2\2\2\2/\3\2\2\2\2\61\3\2\2\2\2\63\3\2\2\2"+
		"\3\65\3\2\2\2\5\67\3\2\2\2\79\3\2\2\2\t;\3\2\2\2\13=\3\2\2\2\r?\3\2\2"+
		"\2\17A\3\2\2\2\21C\3\2\2\2\23E\3\2\2\2\25G\3\2\2\2\27I\3\2\2\2\31K\3\2"+
		"\2\2\33M\3\2\2\2\35O\3\2\2\2\37R\3\2\2\2!X\3\2\2\2#\\\3\2\2\2%a\3\2\2"+
		"\2\'d\3\2\2\2)i\3\2\2\2+p\3\2\2\2-x\3\2\2\2/{\3\2\2\2\61\u0080\3\2\2\2"+
		"\63\u0086\3\2\2\2\65\66\7?\2\2\66\4\3\2\2\2\678\7=\2\28\6\3\2\2\29:\7"+
		"*\2\2:\b\3\2\2\2;<\7+\2\2<\n\3\2\2\2=>\7]\2\2>\f\3\2\2\2?@\7_\2\2@\16"+
		"\3\2\2\2AB\7}\2\2B\20\3\2\2\2CD\7\177\2\2D\22\3\2\2\2EF\7.\2\2F\24\3\2"+
		"\2\2GH\7#\2\2H\26\3\2\2\2IJ\7-\2\2J\30\3\2\2\2KL\7/\2\2L\32\3\2\2\2MN"+
		"\7,\2\2N\34\3\2\2\2OP\7?\2\2PQ\7?\2\2Q\36\3\2\2\2RS\7h\2\2ST\7n\2\2TU"+
		"\7q\2\2UV\7c\2\2VW\7v\2\2W \3\2\2\2XY\7k\2\2YZ\7p\2\2Z[\7v\2\2[\"\3\2"+
		"\2\2\\]\7x\2\2]^\7q\2\2^_\7k\2\2_`\7f\2\2`$\3\2\2\2ab\7k\2\2bc\7h\2\2"+
		"c&\3\2\2\2de\7g\2\2ef\7n\2\2fg\7u\2\2gh\7g\2\2h(\3\2\2\2ij\7t\2\2jk\7"+
		"g\2\2kl\7v\2\2lm\7w\2\2mn\7t\2\2no\7p\2\2o*\3\2\2\2pu\5-\27\2qt\5-\27"+
		"\2rt\t\2\2\2sq\3\2\2\2sr\3\2\2\2tw\3\2\2\2us\3\2\2\2uv\3\2\2\2v,\3\2\2"+
		"\2wu\3\2\2\2xy\t\3\2\2y.\3\2\2\2z|\t\2\2\2{z\3\2\2\2|}\3\2\2\2}{\3\2\2"+
		"\2}~\3\2\2\2~\60\3\2\2\2\177\u0081\t\4\2\2\u0080\177\3\2\2\2\u0081\u0082"+
		"\3\2\2\2\u0082\u0080\3\2\2\2\u0082\u0083\3\2\2\2\u0083\u0084\3\2\2\2\u0084"+
		"\u0085\b\31\2\2\u0085\62\3\2\2\2\u0086\u0087\7\61\2\2\u0087\u0088\7\61"+
		"\2\2\u0088\u008c\3\2\2\2\u0089\u008b\13\2\2\2\u008a\u0089\3\2\2\2\u008b"+
		"\u008e\3\2\2\2\u008c\u008d\3\2\2\2\u008c\u008a\3\2\2\2\u008d\u008f\3\2"+
		"\2\2\u008e\u008c\3\2\2\2\u008f\u0090\7\f\2\2\u0090\u0091\3\2\2\2\u0091"+
		"\u0092\b\32\2\2\u0092\64\3\2\2\2\b\2su}\u0082\u008c\3\b\2\2";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}