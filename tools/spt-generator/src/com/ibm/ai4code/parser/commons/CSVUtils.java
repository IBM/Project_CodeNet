package com.ibm.ai4code.parser.commons;
import java.io.FileWriter;
import java.io.IOException;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
public class CSVUtils {
	
	private static CSVPrinter printer = null;
	
	public static void openFile(String fileName, String ... header) throws IOException {
		if(fileName == null) {
			printer = new CSVPrinter(System.out, CSVFormat.RFC4180.withHeader(header).withRecordSeparator("\n")); // weiz 2020-12-13, support output to stdout for csv file
		}else {
			printer = new CSVPrinter(new FileWriter(fileName), CSVFormat.RFC4180.withHeader(header).withRecordSeparator("\n")); // use \n instead of \r\n (DOS) as line seperator 
		}
	
	}
	
	public static void writeRecord(Object... arg0 ) throws IOException {
		printer.printRecord(arg0);
	}
	
	public static void closeFile() throws IOException {
		assert(printer != null);
		printer.close();
	}

	
}
