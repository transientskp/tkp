package org.lofar.services;

import VOTableUtil.*;
import PrimArray.*;
import com.tbf.xml.*;
import java.util.*;
import java.io.*;
import java.net.*;

/** 
 * This is a helper class that helps with parsing. Instead of dealing
 * with the factory and so on from Breeze, you just give it the filename.
 * From there, it sees if the name begins with http:// and if so opens the URL. 
 * If not, it tries to open it as a file.
 */

public class VOTableWrapper {
	Votable v;
	PrintWriter out;
	String error = null;

/** 
 * Tells you about any errors -- parsing, file opeing, etc.
 * Do not forget to check this for non-null after the parsing!
 */
	public String getLastError() {
		return error;
	}

/** 
 * This is where you get the payload -- the Breeze object representing
 * the Votable. It may be null if something went wrong in the parsing.
 */
	public Votable getVotable(){
		return v;
	}

/** 
 * The constructor that does the parsing of the XML.
 * You can give a non-null PrintWriter if you want a running commentary
 * of the parsing process.
 */
	public VOTableWrapper(String name, PrintWriter out) {
		v = null;
		this.out = out;
		InputStream input_stream = null;

		if(out != null)
			out.println("Parsing VOTable from " + name);

		if(name.startsWith("http://")){
			URL u = null;
			try {
				u = new URL(name);
			} catch(Exception e) {
				error = "Bad URL: " + name + "\n Exception is: " + e;
				return;
			}

			try {
				input_stream = u.openStream();
			} catch(Exception e) {
				error = "Cannot open URL: " + name + "\nException is: " + e;
				return;
			}
		} else {
			try {
				input_stream = new FileInputStream(name);
			} catch(Exception e) {
				error = "Cannot open file " + name + ":\n" + e;
				return;
			}
		}

		XmlParser parser = new XmlParser();
		XmlElement xml = parser.parse(input_stream);
		if (xml == null) {
			// Handle the exception here
			Exception e = parser.getLastException();
			error = "XML parse error: " + e;
			return;
		}
		
		v = new Votable(xml);

		if(v == null) {
			error = "Cannot find VOTABLE element";
			return;
		}

		if(out != null)
			out.print("Found VOTABLE:" + "\n" +
			"\tID=" + v.getId() + "\n" +
			"\tVersion=" + v.getVersion() + "\n" +
			"\tDescription=" + v.getDescription() + "\n");

// Find out if the root has an INFO element whose name is "error". If so, bail
		for(int i=0; i<v.getInfoCount(); i++){
			Info info = v.getInfoAt(i);
			if(info.getName().equals("Error")){
				this.error = info.getValue();
				v = null;
				return;
			}
		}

		if(out != null)
			out.println("Parsing successful");
	}

}

