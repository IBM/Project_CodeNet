package com.ibm.ai4code.parser;

import javax.management.RuntimeErrorException;

public class Utils {
	/**
	 * Assuming there is at least one period which seperates the real name and the file extension
	 * return file_name and file_type
	 * @param fileName
	 * @return results[] results[0]: basename (base name without file extension) results[1]: file_type (file extension) 
	 */
	public static String [] getFileInfo(String fileName) throws RuntimeException{
		int len = fileName.length();
		int periodIdx = -1;
		int fwdSlashIdx = -1; // really only work for linux
		int i = 0;
		for(i = len -1; i >= 0; i--) {
			if(fileName.charAt(i) == '.') {
				periodIdx = i;
				break;
			}
		}
		if(periodIdx == -1) {
			throw new RuntimeException(fileName+ " periodIdx == -1");
		}
		for(; i>=0; i--) {
			if(fileName.charAt(i) == '/') {
				fwdSlashIdx = i;
				break;
			}
		}
		fwdSlashIdx++;
		String baseName = fileName.substring(fwdSlashIdx, periodIdx);
		String fileNameType = fileName.substring(periodIdx+1);
		String results[] = {baseName, fileNameType};
		return results;
	}
	
	public static void showHierarchy(Class<?> c) {
		if (c.getSuperclass() == null) {
            System.out.println(c.getName());
            return;
        }
        showHierarchy(c.getSuperclass());
        System.out.println(c.getName());
	}
	
	public static void main(String[] args) {
		//String fileName = "./examples/c/helloworld.c";
		String fileName = "helloworld.c";
		String [] results = getFileInfo(fileName); 
		System.out.println(results[0]);
		System.out.println(results[1]);
	}

}
