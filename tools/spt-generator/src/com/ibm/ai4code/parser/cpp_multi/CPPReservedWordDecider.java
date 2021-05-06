package com.ibm.ai4code.parser.cpp_multi;

import java.util.HashSet;

import com.ibm.ai4code.parser.commons.ReservedWordDeciderI;

public class CPPReservedWordDecider implements ReservedWordDeciderI{
	// cat cpp14kws_orig.txt | grep ":" | cut -d':' -f2 | sed "s/'/\"/g" | sed "s/;/,/g"
	public static final String [] keywords= 
		{
				"alignas",
				 "alignof",
				 "asm",
				 "auto",
				 "bool",
				 "break",
				 "case",
				 "catch",
				 "char",
				 "char16_t",
				 "char32_t",
				 "class",
				 "const",
				 "constexpr",
				 "const_cast",
				 "continue",
				 "decltype",
				 "default",
				 "delete",
				 "do",
				 "double",
				 "dynamic_cast",
				 "else",
				 "enum",
				 "explicit",
				 "export",
				 "extern",
				 "false",
				 "final",
				 "float",
				 "for",
				 "friend",
				 "goto",
				 "if",
				 "inline",
				 "int",
				 "long",
				 "mutable",
				 "namespace",
				 "new",
				 "noexcept",
				 "nullptr",
				 "operator",
				 "override",
				 "private",
				 "protected",
				 "public",
				 "register",
				 "reinterpret_cast",
				 "return",
				 "short",
				 "signed",
				 "sizeof",
				 "static",
				 "static_assert",
				 "static_cast",
				 "struct",
				 "switch",
				 "template",
				 "this",
				 "thread_local",
				 "throw",
				 "true",
				 "try",
				 "typedef",
				 "typeid",
				 "typename",
				 "union",
				 "unsigned",
				 "using",
				 "virtual",
				 "void",
				 "volatile",
				 "wchar_t",
				 "while"				
		};
	// cat cpp14ops_orig.txt | grep ":" | cut -d':' -f2 | sed "s/'/\"/g" | sed "s/;/,/g"
	public static final String[] ops = {
			"(",
			 ")",
			 "[",
			 "]",
			 "{",
			 "}",
			 "+",
			 "-",
			 "*",
			 "/",
			 "%",
			 "^",
			 "&",
			 "|",
			 "~",
			 "!" ,
			 "not",
			 "=",
			 "<",
			 ">",
			 "+=",
			 "-=",
			 "*=",
			 "/=",
			 "%=",
			 "^=",
			 "&=",
			 "|=",
			 "<<",
			 ">>",
			 "<<=",
			 ">>=",
			 "==",
			 "!=",
			 "<=",
			 ">=",
			 "&&",
			 "and",
			 "||" ,
			 "or",
			 "++",
			 "--",
			 ",",
			 "->*",
			 "->",
			 "?",
			 ":", // weiz 2020-10-29, this is a tricky one, as my grep cut is based on ':'
			 "::", // weiz 2020-10-29, this is a tricky one, as my grep cut is based on ':'
			 ";", //weiz 2020-10-29, because in my shell script, i did s/;/,/g" to make java happy with its array declaration thus, i need to put ; back
			 ".",
			 ".*",
			 "..."
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
	@Override
	public boolean isReserved(String word) {
		return (keywordsHashSet.contains(word) || opsHashSet.contains(word));
	}
	
	public CPPReservedWordDecider() {
		buildKeyWordsHashSet();
		buildOPsHashSet();
	}
	
	
}
