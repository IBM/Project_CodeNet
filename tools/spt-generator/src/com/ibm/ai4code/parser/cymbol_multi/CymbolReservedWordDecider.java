package com.ibm.ai4code.parser.cymbol_multi;

import java.util.HashSet;

import com.ibm.ai4code.parser.commons.ReservedWordDeciderI;

public class CymbolReservedWordDecider implements ReservedWordDeciderI{
	public static final String [] keywords = {
			"float", 
			"int",
			"void",
			"if",
			"then",
			"else",
			"return"
	};
	
	public static final String [] ops = {
			"(",
			")",
			"[",
			"]",
			"-",
			"!",
			"*",
			"+",
			"-",
			"=="
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
	
	public CymbolReservedWordDecider() {
		buildKeyWordsHashSet();
		buildOPsHashSet();
	}

}
