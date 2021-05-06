package com.ibm.ai4code.parser.commons;
import org.apache.commons.cli.*;
public class Args {
	public static boolean MULTI = false; // use "single" g4 file, or use "multi" g4 file, where we have different toke types
 	public static void parse(CommandLine cmd) {
		if(cmd.hasOption("multi")) {
			MULTI = true;
		}
	}

}
