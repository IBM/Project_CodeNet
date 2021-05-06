package com.ibm.ai4code.parser.java_multi;

import java.util.HashSet;

import com.ibm.ai4code.parser.commons.ReservedWordDeciderI;

public class JavaReservedWordDecider implements ReservedWordDeciderI{
	//cat *kws_orig.txt | grep ":" | cut -d':' -f2 | sed "s/'/\"/g" | sed "s/;/,/g"
	public static final String [] keywords= {
		    "abstract",
            "assert",
           "boolean",
             "break",
              "byte",
              "case",
             "catch",
              "char",
             "class",
             "const",
          "continue",
           "default",
                "do",
            "double",
              "else",
              "enum",
           "extends",
             "final",
           "finally",
             "float",
               "for",
                "if",
              "goto",
        "implements",
            "import",
        "instanceof",
               "int",
         "interface",
              "long",
            "native",
               "new",
           "package",
           "private",
         "protected",
            "public",
            "return",
             "short",
            "static",
          "strictfp",
             "super",
            "switch",
      "synchronized",
              "this",
             "throw",
            "throws",
         "transient",
               "try",
              "void",
          "volatile",
             "while"
	};
	//cat *ops_orig.txt | grep ":" | cut -d':' -f2 | sed "s/'/\"/g" | sed "s/;/,/g"
	public static final String [] ops = {
			  "(",
	             ")",
	             "{",
	             "}",
	             "[",
	             "]",
	               ";", // weiz 2020-1029
	              ",",
	                ".",
	             "=",
	                 ">",
	                 "<",
	               "!",
	              "~",
	           "?",
	              ":", // weiz  2020-10-29
	              "==",
	                 "<=",
	                 ">=",
	           "!=",
	                "&&",
	                 "||",
	                "++",
	                "--",
	                "+",
	                "-",
	                "*",
	                "/",
	             "&",
	              "|",
	              "^",
	                "%",
	         "+=",
	         "-=",
	         "*=",
	         "/=",
	         "&=",
	          "|=",
	         "^=",
	         "%=",
	      "<<=",
	      ">>=",
	     ">>>=",
	              "->",
	         "::" // weiz 2020-10-29

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
	public  JavaReservedWordDecider() {
		buildKeyWordsHashSet();
		buildOPsHashSet();
	}
	
	@Override
	public boolean isReserved(String word) {
		return (keywordsHashSet.contains(word) || opsHashSet.contains(word));
	}

}
