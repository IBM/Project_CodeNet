package com.ibm.ai4code.parser;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.util.BitSet;
import java.util.List;

import javax.management.RuntimeErrorException;

import org.antlr.v4.runtime.BaseErrorListener;
import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.DefaultErrorStrategy;
import org.antlr.v4.runtime.Lexer;
import org.antlr.v4.runtime.Parser;
import org.antlr.v4.runtime.RecognitionException;
import org.antlr.v4.runtime.Recognizer;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.Vocabulary;
import org.antlr.v4.runtime.atn.ATNConfigSet;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.tree.ParseTree;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import com.ibm.ai4code.parser.c.*;
import com.ibm.ai4code.parser.c_multi.C11Lexer;
import com.ibm.ai4code.parser.c_multi.C11Parser;
import com.ibm.ai4code.parser.c_multi.C11ReservedWordDecider;
import com.ibm.ai4code.parser.c_multi.C11Tokens;
import com.ibm.ai4code.parser.cpp_multi.*;
import com.ibm.ai4code.parser.cymbol.CymbolLexer;
import com.ibm.ai4code.parser.cymbol.CymbolParser;
import com.ibm.ai4code.parser.cymbol.CymbolReservedWordDecider;
import com.ibm.ai4code.parser.java_multi.*;
import com.ibm.ai4code.parser.commons.Args;
import com.ibm.ai4code.parser.commons.JsonUtils;
import com.ibm.ai4code.parser.commons.ReservedWordDeciderI;
import com.ibm.ai4code.parser.commons.SPT;
import com.ibm.ai4code.parser.cpp.CPP14Lexer;
import com.ibm.ai4code.parser.cpp.CPP14Parser;
import com.ibm.ai4code.parser.cpp.CPPReservedWordDecider;
import com.ibm.ai4code.parser.java.JavaLexer;
import com.ibm.ai4code.parser.java.JavaParser;
import com.ibm.ai4code.parser.java.JavaReservedWordDecider;
import com.ibm.ai4code.parser.python.PythonLexer;
import com.ibm.ai4code.parser.python.PythonParser;
import com.ibm.ai4code.parser.python.PythonReservedWordDecider;

import com.ibm.ai4code.parser.cobol.*;

public class SPTGenerator {
	/**
	 * 
	 * @param srcFileName
	 * @param dstFileName
	 * @return True, when successfully processed an SPT
	 * @throws IOException
	 */
	public static boolean generate(String srcFileName, String dstFileName) throws IOException {
		String[] fileInfo = Utils.getFileInfo(srcFileName);
		String fileType = fileInfo[1];
		InputStream is = new FileInputStream(srcFileName);
		CharStream input = CharStreams.fromStream(is);
		ParseTree tree = null;
		CommonTokenStream tokenStream = null;
		ReservedWordDeciderI rwdi = null;
		Lexer lexer = null;
		String[] ruleNames = null;
		Vocabulary vocabulary = null;
		//System.err.println("[SPT Info] " + srcFileName + " started");
		try {
			if (fileType.equals("c")) {
				/*lexer = new CLexer(input);
				tokenStream = new CommonTokenStream(lexer);
				CParser parser = new CParser(tokenStream);
				parser.removeErrorListeners();
				parser.addErrorListener(new SPTBaseErrorListener(srcFileName));
				ruleNames = parser.getRuleNames();
				tree = parser.compilationUnit();
				rwdi = new CReservedWordDecider();*/
				
				if(!Args.MULTI) {
					lexer = new com.ibm.ai4code.parser.c_multi.C11Lexer(input);
					lexer.removeErrorListeners(); // weiz 2021-03-07
					lexer.addErrorListener(new SPTLexerBaseErrorListener(srcFileName)); // weiz 2021-03-07
					tokenStream = new CommonTokenStream(lexer);
					C11Parser parser = new com.ibm.ai4code.parser.c_multi.C11Parser(tokenStream);
					parser.removeErrorListeners();
					parser.addErrorListener(new SPTParserBaseErrorListener(srcFileName));
					ruleNames = parser.getRuleNames();
					tree = parser.compilationUnit();
					rwdi = new com.ibm.ai4code.parser.c_multi.C11ReservedWordDecider();
				}else {
					lexer = new com.ibm.ai4code.parser.c.CLexer(input);
					lexer.removeErrorListeners(); // weiz 2021-03-07
					lexer.addErrorListener(new SPTLexerBaseErrorListener(srcFileName)); // weiz 2021-03-07
					tokenStream = new CommonTokenStream(lexer);
					com.ibm.ai4code.parser.c.CParser parser = new com.ibm.ai4code.parser.c.CParser(tokenStream);
					parser.removeErrorListeners();
					parser.addErrorListener(new SPTParserBaseErrorListener(srcFileName));
					ruleNames = parser.getRuleNames();
					tree = parser.compilationUnit();
					rwdi = new com.ibm.ai4code.parser.c.CReservedWordDecider();
				}
				
			} else if (fileType.equals("cpp")) {
				if(!Args.MULTI) {
					lexer = new com.ibm.ai4code.parser.cpp.CPP14Lexer(input);
					lexer.removeErrorListeners(); // weiz 2021-03-07
					lexer.addErrorListener(new SPTLexerBaseErrorListener(srcFileName)); // weiz 2021-03-07
					tokenStream = new CommonTokenStream(lexer);
					CPP14Parser parser = new com.ibm.ai4code.parser.cpp.CPP14Parser(tokenStream);
					parser.removeErrorListeners();
					parser.addErrorListener(new SPTParserBaseErrorListener(srcFileName));
					ruleNames = parser.getRuleNames();
					tree = parser.translationUnit();
					rwdi = new com.ibm.ai4code.parser.cpp.CPPReservedWordDecider();
				}else {
					lexer = new com.ibm.ai4code.parser.cpp_multi.CPP14Lexer(input);
					lexer.removeErrorListeners(); // weiz 2021-03-07
					lexer.addErrorListener(new SPTLexerBaseErrorListener(srcFileName)); // weiz 2021-03-07
					tokenStream = new CommonTokenStream(lexer);
					com.ibm.ai4code.parser.cpp_multi.CPP14Parser parser = new com.ibm.ai4code.parser.cpp_multi.CPP14Parser(tokenStream);
					parser.removeErrorListeners();
					parser.addErrorListener(new SPTParserBaseErrorListener(srcFileName));
					ruleNames = parser.getRuleNames();
					tree = parser.translationUnit();
					rwdi = new com.ibm.ai4code.parser.cpp_multi.CPPReservedWordDecider();
				}
			} else if (fileType.equals("java")) {
				if(!Args.MULTI) {
					lexer = new com.ibm.ai4code.parser.java.JavaLexer(input);
					lexer.removeErrorListeners(); // weiz 2021-03-07
					lexer.addErrorListener(new SPTLexerBaseErrorListener(srcFileName)); // weiz 2021-03-07
					tokenStream = new CommonTokenStream(lexer);
					com.ibm.ai4code.parser.java.JavaParser parser = new com.ibm.ai4code.parser.java.JavaParser(tokenStream);
					parser.removeErrorListeners();
					parser.addErrorListener(new SPTParserBaseErrorListener(srcFileName));
					ruleNames = parser.getRuleNames();
					tree = parser.compilationUnit();
					rwdi = new com.ibm.ai4code.parser.java.JavaReservedWordDecider();
				}else {
					lexer = new com.ibm.ai4code.parser.java_multi.JavaLexer(input);
					lexer.removeErrorListeners(); // weiz 2021-03-07
					lexer.addErrorListener(new SPTLexerBaseErrorListener(srcFileName)); // weiz 2021-03-07
					tokenStream = new CommonTokenStream(lexer);
					com.ibm.ai4code.parser.java_multi.JavaParser parser = new com.ibm.ai4code.parser.java_multi.JavaParser(tokenStream);
					parser.removeErrorListeners();
					parser.addErrorListener(new SPTParserBaseErrorListener(srcFileName));
					ruleNames = parser.getRuleNames();
					tree = parser.compilationUnit();
					rwdi = new com.ibm.ai4code.parser.java_multi.JavaReservedWordDecider();
				}
			} else if (fileType.equals("py")) {
				if(!Args.MULTI) {
					lexer = new PythonLexer(input);
					lexer.removeErrorListeners(); // weiz 2021-03-07
					lexer.addErrorListener(new SPTLexerBaseErrorListener(srcFileName)); // weiz 2021-03-07
					tokenStream = new CommonTokenStream(lexer);
					PythonParser parser = new PythonParser(tokenStream);
					parser.removeErrorListeners();
					parser.addErrorListener(new SPTParserBaseErrorListener(srcFileName));
					ruleNames = parser.getRuleNames();
					tree = parser.root();
					rwdi = new PythonReservedWordDecider();
				}else {
					lexer = new com.ibm.ai4code.parser.python_multi.PythonLexer(input);
					lexer.removeErrorListeners(); // weiz 2021-03-07
					lexer.addErrorListener(new SPTLexerBaseErrorListener(srcFileName)); // weiz 2021-03-07
					tokenStream = new CommonTokenStream(lexer);
					com.ibm.ai4code.parser.python_multi.PythonParser parser = new com.ibm.ai4code.parser.python_multi.PythonParser(tokenStream);
					parser.removeErrorListeners();
					parser.addErrorListener(new SPTParserBaseErrorListener(srcFileName));
					ruleNames = parser.getRuleNames();
					tree = parser.root();
					rwdi = new PythonReservedWordDecider();
					
				}
			} else if (fileType.equals("cbl")) {
				lexer = new Cobol85Lexer(input);
				lexer.removeErrorListeners(); // weiz 2021-03-07
				lexer.addErrorListener(new SPTLexerBaseErrorListener(srcFileName)); // weiz 2021-03-07
				tokenStream = new CommonTokenStream(lexer);
				Cobol85Parser parser = new Cobol85Parser(tokenStream);
				parser.removeErrorListeners();
				parser.addErrorListener(new SPTParserBaseErrorListener(srcFileName));
				ruleNames = parser.getRuleNames();
				tree = parser.compilationUnit();
				rwdi = new CobolReservedWordDecider();

			} else if(fileType.equals("c11")) {
				lexer = new C11Lexer(input);
				//lexer = new C11Tokens(input);
				lexer.removeErrorListeners(); // weiz 2021-03-07
				lexer.addErrorListener(new SPTLexerBaseErrorListener(srcFileName)); // weiz 2021-03-07
				tokenStream = new CommonTokenStream(lexer);
				C11Parser parser = new C11Parser(tokenStream);
				parser.removeErrorListeners();
				parser.addErrorListener(new SPTParserBaseErrorListener(srcFileName));
				ruleNames = parser.getRuleNames();
				tree = parser.compilationUnit();
				rwdi = new C11ReservedWordDecider();
				
			} else if(fileType.equals("cymbol")) {
				if(!Args.MULTI) {
					lexer = new CymbolLexer(input);
					lexer.removeErrorListeners(); // weiz 2021-03-07
					lexer.addErrorListener(new SPTLexerBaseErrorListener(srcFileName)); // weiz 2021-03-07
					tokenStream = new CommonTokenStream(lexer);
					CymbolParser parser = new CymbolParser(tokenStream);
					//parser.removeErrorListeners();
					//parser.addErrorListener(new SPTBaseErrorListener(srcFileName));
					ruleNames = parser.getRuleNames();
					tree = parser.file();
					rwdi = new CymbolReservedWordDecider();
				}else {
					lexer = new com.ibm.ai4code.parser.cymbol_multi.CymbolLexer(input);
					lexer.removeErrorListeners(); // weiz 2021-03-07
					lexer.addErrorListener(new SPTLexerBaseErrorListener(srcFileName)); // weiz 2021-03-07
					tokenStream = new CommonTokenStream(lexer);
					com.ibm.ai4code.parser.cymbol_multi.CymbolParser parser = new com.ibm.ai4code.parser.cymbol_multi.CymbolParser(tokenStream);
					//parser.removeErrorListeners();
					//parser.addErrorListener(new SPTBaseErrorListener(srcFileName));
					ruleNames = parser.getRuleNames();
					tree = parser.file();
					rwdi = new com.ibm.ai4code.parser.cymbol_multi.CymbolReservedWordDecider();
				}
			}
			else {
				throw new RuntimeErrorException(new Error("Unknow file type " + fileType));
			}
			// step 3 build PT and SPT
			vocabulary = lexer.getVocabulary();
			SPT spt = new SPT(tree, ruleNames, vocabulary);
			spt.setSrcFileName(srcFileName); //weiz 2021-03-06
			spt.simplify();
			spt.indexing();
			if (rwdi != null) {
				spt.labeling(rwdi); // weiz 2020-10-29, labeling
			}

			JsonUtils.serializeSPT(spt, dstFileName);
			System.out.println(dstFileName + " is generated!");
			//System.err.println("[SPT Info] " + srcFileName + " finished");
			return true;
		} catch (RuntimeException re) {
			System.err.println("[SPT Warning] " + srcFileName + " cannot be processed.");
			return false;
		}
		
	}
	
	static  class SPTParserBaseErrorListener extends BaseErrorListener{
		String srcFileName;
		public SPTParserBaseErrorListener(String srcFileName) {
			this.srcFileName = srcFileName;
		}
		@Override
		public void syntaxError(Recognizer<?, ?> recognizer,
								Object offendingSymbol,
								int line,
								int charPositionInLine,
								String msg,
								RecognitionException e)
		{
			String errMsg = "[SPT Error] " + srcFileName + " parser syntax error!";
		    System.err.println(errMsg);
			throw new RuntimeException(errMsg);
			
		}

	}
	
	static  class SPTLexerBaseErrorListener extends BaseErrorListener{
		String srcFileName;
		public SPTLexerBaseErrorListener(String srcFileName) {
			this.srcFileName = srcFileName;
		}
		@Override
		public void syntaxError(Recognizer<?, ?> recognizer,
								Object offendingSymbol,
								int line,
								int charPositionInLine,
								String msg,
								RecognitionException e)
		{
			String errMsg = "[SPT Error] " + srcFileName + " lexer syntax error!";
		    System.err.println(errMsg);
			throw new RuntimeException(errMsg);
			
		}

	}
	
	class BailErrorStrategy extends DefaultErrorStrategy{
		String srcFileName;
		public BailErrorStrategy(String srcFileName) {
			this.srcFileName = srcFileName;
		}
		@Override
		public void recover(Parser recognizer, RecognitionException e) {
			throw new RuntimeException("recover exception");
		}
		@Override
		public Token recoverInline(Parser recognizer) throws RecognitionException {
			throw new RuntimeException("recoverInline exception");
		}
		/** Make sure we don't attempt to recover from problems in subrules. */
		@Override
		public void sync(Parser recognizer) throws RecognitionException {
			// TODO Auto-generated method stub
			//super.sync(recognizer);
		}
	}
	
	
	
	
	
	public static void handleSingle(String srcFileName, String dstDir) throws IOException {
		// always first spt-ize 
		String [] info = Utils.getFileInfo(srcFileName);
		String dstFileName = dstDir  + "/" + info[0] + ".json";
		boolean sptSuccess = SPTGenerator.generate(srcFileName, dstFileName);
		if(!sptSuccess) { // if spt not successful, then forgo the tokenize part
			return;
		}


		// tokenize
		dstFileName = dstDir  + "/" +info[0] +".csv"; // weiz 2020-11-20, use csv file to represent tokens 
		Tokenizer.tokenize(srcFileName, dstFileName);


	}
	
	public static void handleBatch(String srcBatchFileName) throws IOException{
		try (BufferedReader br = new BufferedReader(new FileReader(srcBatchFileName))) {
		    String line;
		    while ((line = br.readLine()) != null) {
		       String [] lines = line.split(" |\t");
		       assert(lines.length == 2);
		       String srcFileName = lines[0];
		       String dstDir = lines[1];
		       handleSingle(srcFileName, dstDir);
		    }
		}
	}
	
	public static void handleArgs(String[] args) throws ParseException, IOException {
		CommandLineParser parser = new DefaultParser();
		Options options = new Options();
		Option helpOpt = Option.builder("h").longOpt("help").desc("Usage").build();
		Option multiOpt = Option.builder("multi").longOpt("multi").desc("Use multiple g4 files to have less fine grained toke type").build();
		Option dstOpt = Option.builder("d").longOpt("dest").desc("Destination directory ").hasArg().build();
		Option batchOpt = Option.builder("b").longOpt("batch").desc("Batch processing").build();
		options.addOption(helpOpt);
		options.addOption(multiOpt);
		options.addOption(dstOpt);
		options.addOption(batchOpt);
		CommandLine cli = parser.parse(options, args);
		Args.parse(cli); // weiz 2021-02-15, add options so it takes the multi option
		if(cli.hasOption("h")) {
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp( "SPTGenerator input_file(either source code or batch processing input)", options );
			return;
		}
		
		List<String> leftoverArgs = cli.getArgList();
		assert(leftoverArgs.size() == 1); // We should always get one input file (either it is src code or the batch input file)
		String srcFileName = leftoverArgs.get(0);
		if(cli.hasOption("b")) { // batch procesing
			String srcBatchFileName = srcFileName;
			handleBatch(srcBatchFileName);
		}else { // single file processing
			String dstDir  = null;
			String src = srcFileName;
			if(cli.hasOption("d")) {
				dstDir = cli.getOptionValue("d");
			}
			handleSingle(src, dstDir);
		}
		
		
		
	}

	public static void main(String[] args) throws IOException, ParseException {
		handleArgs(args);
	}

}
