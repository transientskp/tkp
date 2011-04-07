package org.lofar.test;

import java.io.*;
import java.nio.*;
import java.util.*;

public class TestInputStream {

    public static void main(String[] args) throws IOException {

	BufferedReader stdIn = new BufferedReader(new InputStreamReader(System.in));
	String userInput = "";
	StringBuffer votfile = new StringBuffer("");

	while (userInput != null) {
	    	//System.out.println("echo: " + userInput);
		votfile.append(userInput + "\n");
	    	//System.out.println(userInput);
		userInput = stdIn.readLine();
		//votfile.append(stdIn.readLine() + "\n");
	}

	stdIn.close();
	System.out.println("Klaar\n" + votfile.toString());
    }
}
