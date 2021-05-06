package com.ibm.ai4code.parser.python;

import java.util.HashSet;

import com.ibm.ai4code.parser.commons.ReservedWordDeciderI;

public class PythonReservedWordDecider implements ReservedWordDeciderI{
	// cat *kws_orig.txt | grep ":" | cut -d':' -f2 | sed "s/'/\"/g" | sed "s/;/,/g"
	public static final String [] keywords = {
			"def",
			 "return",
			 "raise",
			 "from",
			 "import",
			 "nonlocal",
			 "as",
			 "global",
			 "assert",
			 "if",
			 "elif",
			 "else",
			 "while",
			 "for",
			 "in",
			 "try",
			 "None",
			 "finally",
			 "with",
			 "except",
			 "lambda",
			 "or",
			 "and",
			 "not",
			 "is",
			 "class",
			 "yield",
			 "del",
			 "pass",
			 "continue",
			 "break",
			 "async",
			 "await",
			 "print",
			 "exec",
			 "True",
			 "False"
	};
	
	// cat *ops_orig.txt | grep ":" | cut -d':' -f2 | sed "s/'/\"/g" | sed "s/;/,/g"
	public static final String [] ops = {
			".",
			 "...",
			 "`",
			 "*",
			 ",",
			 ":", // weiz 2020-10-29
			 ";", // weiz 2020-10-29
			 "**",
			 "=",
			 "|",
			 "^",
			 "&",
			 "<<",
			 ">>",
			 "+",
			 "-",
			 "/",
			 "%",
			 "//",
			 "~",
			 "<",
			 ">",
			 "==",
			 ">=",
			 "<=",
			 "<>",
			 "!=",
			 "@",
			 "->",
			 "+=",
			 "-=",
			 "*=",
			 "@=",
			 "/=",
			 "%=",
			 "&=",
			 "|=",
			 "^=",
			 "<<=",
			 ">>=",
			 "**=",
			 "//=",
			 "(", // weiz 2020-10-29 {IncIndentLevel(),},
			 ")", // weiz 2020-10-29 {DecIndentLevel(),},
			 "{", // weiz 2020-10-29 {IncIndentLevel(),},
			 "}", // weiz 2020-10-29 {DecIndentLevel(),},
			 "[", // weiz 2020-10-29 {IncIndentLevel(),},
			 "]" // weiz 2020-10-29 {DecIndentLevel(),},
	};
	
	HashSet<String> keywordsHashSet=new HashSet<String>();
	HashSet<String> opsHashSet = new HashSet<String>();
	public void buildKeyWordsHashSet() {
		for(String keyword: keywords) {
			keywordsHashSet.add(keyword);
		}
	}
	public void buildOPsHashSet() {
		for(String op: ops) {
			opsHashSet.add(op);
		}
	}
	public PythonReservedWordDecider() {
	
		buildKeyWordsHashSet();
		buildOPsHashSet();
	}
	
	@Override
	public boolean isReserved(String word) {
		return (keywordsHashSet.contains(word) || opsHashSet.contains(word));
	}

}
