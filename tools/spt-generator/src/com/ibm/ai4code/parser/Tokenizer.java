package com.ibm.ai4code.parser;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.List;

import javax.management.RuntimeErrorException;


import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.Lexer;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.Vocabulary;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import com.ibm.ai4code.parser.c.*;
import com.ibm.ai4code.parser.c_multi.C11Tokens;
import com.ibm.ai4code.parser.cobol.Cobol85Lexer;
import com.ibm.ai4code.parser.commons.CSVUtils;
import com.ibm.ai4code.parser.cpp.CPP14Lexer;
import com.ibm.ai4code.parser.cymbol.CymbolLexer;
import com.ibm.ai4code.parser.java.JavaLexer;
import com.ibm.ai4code.parser.python.PythonLexer;

import com.ibm.ai4code.parser.commons.Args;
public class Tokenizer {
	
	
	
	public static void tokenize(String srcFileName, String dstFileName) throws IOException {
		String[] fileInfo = Utils.getFileInfo(srcFileName);
		String fileType = fileInfo[1];
		InputStream is = new FileInputStream(srcFileName);
		CharStream input = CharStreams.fromStream(is);
		Lexer lexer = null;
		CommonTokenStream tokenStream = null;
		if (fileType.equals("c")) {
			/*lexer = new CLexer(input);
			tokenStream = new CommonTokenStream(lexer);*/
			if(!Args.MULTI) {
				lexer = new com.ibm.ai4code.parser.c.CLexer(input);
			}else {
				lexer = new com.ibm.ai4code.parser.c_multi.C11Tokens(input);
			}
			tokenStream = new CommonTokenStream(lexer);
		} else if (fileType.equals("cpp")) {
			if(!Args.MULTI) {
				lexer = new com.ibm.ai4code.parser.cpp.CPP14Lexer(input);
			}else {
				lexer = new com.ibm.ai4code.parser.cpp_multi.CPP14Tokens(input);
			}
			tokenStream = new CommonTokenStream(lexer);

		} else if (fileType.equals("java")) {
			if(!Args.MULTI){
				lexer = new com.ibm.ai4code.parser.java.JavaLexer(input);
			}else {
				lexer = new com.ibm.ai4code.parser.java_multi.JavaTokens(input);
			}
			tokenStream = new CommonTokenStream(lexer);

		} else if (fileType.equals("py")) {
			if(!Args.MULTI) {
				lexer = new PythonLexer(input);
				tokenStream = new CommonTokenStream(lexer);
			}else {
				lexer = new com.ibm.ai4code.parser.python_multi.PythonTokens(input);
				tokenStream = new CommonTokenStream(lexer);
			}
			
		}else if (fileType.equals("cbl")) {
			lexer = new Cobol85Lexer(input);
			tokenStream = new CommonTokenStream(lexer);
		}else if (fileType.equals("c11")) { // weiz 2020-12-08, Geert's split c grammar
			lexer = new C11Tokens(input);
			tokenStream = new CommonTokenStream(lexer);
		} else if (fileType.equals("cymbol")) {
			if(!Args.MULTI) {
				lexer = new CymbolLexer(input);
				tokenStream = new CommonTokenStream(lexer);
			}else {
				lexer = new com.ibm.ai4code.parser.cymbol_multi.CymbolTokens(input);
				tokenStream = new CommonTokenStream(lexer);
			}
		}
		else {
			throw new RuntimeErrorException(new Error("Unknow file type " + fileType));
			
		}
		
		
		tokenStream.fill(); // weiz 2020-11-16, we need to fill the tokenStream so that token index can be generated. 
		List<Token> tokens = tokenStream.getTokens();
		Vocabulary vocabulary = lexer.getVocabulary();
		// “CSV header: seqnr, start, stop, text, class, channel, line, column”
		CSVUtils.openFile(dstFileName, "seqnr", "start", "stop", 
				"text", "class", "channel", "line", "column");
		for(Token token:tokens) {
			//Utils.showHierarchy(token.getClass());
			int tokenIdx=token.getTokenIndex();
			int startIdx = token.getStartIndex();
			int stopIdx = token.getStopIndex();
			String txt = token.getText();
			if ( txt!=null ) { // weiz 2020-11-17, this logic is copied from CommonToken.toString() method 
				txt = txt.replace("\n","\\n");
				txt = txt.replace("\r","\\r");
				txt = txt.replace("\t","\\t");
			}
			else {
				txt = "<no text>";
			}
			String tokenSymbolicName = vocabulary.getSymbolicName(token.getType());	
			String displayName = vocabulary.getDisplayName(token.getType()).toLowerCase();
			//System.out.println(tokenSymbolicName+"-----"+displayName);
			int line = token.getLine();
			int channel = token.getChannel(); // weiz 2020-12-10
			int positionInLine = token.getCharPositionInLine();
			
			//CSVUtils.writeRecord("@"+tokenIdx, ""+startIdx+":"+stopIdx, txt, tokenSymbolicName, ""+line+":"+positionInLine);
			// “CSV header: seqnr, start, stop, text, class, channel, line, column”
			CSVUtils.writeRecord(tokenIdx, 
					startIdx, stopIdx, txt, displayName, channel, line, positionInLine);
		}
		if(dstFileName != null) {
			System.out.println(dstFileName + " is generated.");
		}
		CSVUtils.closeFile();
				
	}
	
	public static void handleSingle(String srcFileName, String dstDir) throws IOException {
		String [] info = Utils.getFileInfo(srcFileName);
		String dstFileName = (dstDir == null) ? null:(dstDir+ "/"+ info[0] + ".csv");
		Tokenizer.tokenize(srcFileName, dstFileName);
	}
	
	public static void handleBatch(String srcBatchFileName) throws IOException{
		try (BufferedReader br = new BufferedReader(new FileReader(srcBatchFileName))) {
		    String line;
		    while ((line = br.readLine()) != null) {
		       String [] lines = line.split(" ");
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
			formatter.printHelp( "Tokenize input_file(either source code or batch processing input)", options );
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
