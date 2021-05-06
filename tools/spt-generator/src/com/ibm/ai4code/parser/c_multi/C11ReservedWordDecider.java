package com.ibm.ai4code.parser.c_multi;

import java.util.HashSet;

import com.ibm.ai4code.parser.commons.ReservedWordDeciderI;

public class C11ReservedWordDecider implements ReservedWordDeciderI{
	// cat ckws_orig.txt | grep ":" | cut -d':' -f2 | sed "s/'/\"/g" | sed "s/;/,/g"
	public static final String [] keywords = {
			"auto",
			 "break",
			 "case",
			 "char",
			 "const",
			 "continue",
			 "default",
			 "do",
			 "double",
			 "else",
			 "enum",
			 "extern",
			 "float",
			 "for",
			 "goto",
			 "if",
			 "inline",
			 "int",
			 "long",
			 "register",
			 "restrict",
			 "return",
			 "short",
			 "signed",
			 "sizeof",
			 "static",
			 "struct",
			 "switch",
			 "typedef",
			 "union",
			 "unsigned",
			 "void",
			 "volatile",
			 "while",
			 "_Alignas",
			 "_Alignof",
			 "_Atomic",
			 "_Bool",
			 "_Complex",
			 "_Generic",
			 "_Imaginary",
			 "_Noreturn",
			 "_Static_assert",
			 "_Thread_local"
	};
	// cat cops_orig.txt | grep ":" | cut -d':' -f2 | sed "s/'/\"/g" | sed "s/;/,/g"
	public static final String [] ops = {
			"(",
			 ")",
			 "[",
			 "]",
			 "{",
			 "}",
			 "<",
			 "<=",
			 ">",
			 ">=",
			 "<<",
			 ">>",
			 "+",
			 "++",
			 "-",
			 "--",
			 "*",
			 "/",
			 "%",
			 "&",
			 "|",
			 "&&",
			 "||",
			 "^",
			 "!",
			 "~",
			 "?",
			 ":", // weiz 2020-10-29
			 ";", // weiz 2020-10-29
			 ",",
			 "=",
			 "*=",
			 "/=",
			 "%=",
			 "+=",
			 "-=",
			 "<<=",
			 ">>=",
			 "&=",
			 "^=",
			 "|=",
			 "==",
			 "!=",
			 "->",
			 ".",
			 "..."
	};

	@Override
	public boolean isReserved(String word) {
		return (keywordsHashSet.contains(word) || opsHashSet.contains(word));
	}
	
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
	
	public C11ReservedWordDecider() {
		buildKeyWordsHashSet();
		buildOPsHashSet();
	}
	
	

}
