package org.lofar.services;

import java.io.*;
import java.util.*;

import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;

import org.lofar.data.*;

import org.w3c.dom.Document;
import org.w3c.dom.*;

import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;


public class SExtractorService {
	private Source source;
	private Source[] sources;
	private List sourceList;

	public List getSourceListFromFile(String fileName) {
		readSourceFile(fileName);
		return getSourceList();
	}

	private void setSourceList(List sourceList) {
		this.sourceList = sourceList;
	}

	private List getSourceList() {
		return sourceList;
	}

	private void setSource(Source source) {
		this.source = source;
	}

	private Source getSource() {
		return source;
	}

	public Source[] getSourcesFromFile(String fileName) {
		readSourceFile(fileName);
		sources = new Source[getSourceList().size()];
		int i = 0;
		for (Iterator iter = sourceList.iterator(); iter.hasNext();) {
                        sources[i++] = (Source) iter.next();
		}
		return sources;
	}

	private void readSourceFile(String fileName) {
		try {
                        DocumentBuilderFactory docBuilderFactory = DocumentBuilderFactory.newInstance();
                        DocumentBuilder docBuilder = docBuilderFactory.newDocumentBuilder();
                        Document doc = docBuilder.parse (new File(fileName));
                        doc.getDocumentElement().normalize();

                        NodeList timeObsList = doc.getElementsByTagName("tijd");
                        Element timeObsElement = (Element) timeObsList.item(0);
                        String obsTime = ((Node)timeObsElement.getChildNodes().item(0)).getNodeValue().trim();

                        NodeList listOfSources = doc.getElementsByTagName("source");
                        int totalSources = listOfSources.getLength();

			sourceList = new ArrayList();

			for (int s = 0; s < listOfSources.getLength(); s++) {

                                Node sourceNode = listOfSources.item(s);
                                Element sourceElement = (Element) sourceNode;

                                NodeList fluxautoList = sourceElement.getElementsByTagName("flux_auto");
                                Element fluxautoElement = (Element) fluxautoList.item(0);
                                double flux = Double.parseDouble(((Node)fluxautoElement.getChildNodes().item(0)).getNodeValue().trim());

                                NodeList raList = sourceElement.getElementsByTagName("ra");
                                Element raElement = (Element) raList.item(0);
                                double ra = Double.parseDouble(((Node)raElement.getChildNodes().item(0)).getNodeValue().trim());

                                NodeList draList = sourceElement.getElementsByTagName("dra");
                                Element draElement = (Element) draList.item(0);
                                double dra = Double.parseDouble(((Node)draElement.getChildNodes().item(0)).getNodeValue().trim());

                                NodeList decList = sourceElement.getElementsByTagName("dec");
                                Element decElement = (Element) decList.item(0);
                                double dec = Double.parseDouble(((Node)decElement.getChildNodes().item(0)).getNodeValue().trim());

                                NodeList ddecList = sourceElement.getElementsByTagName("ddec");
                                Element ddecElement = (Element) ddecList.item(0);
                                double ddec = Double.parseDouble(((Node)ddecElement.getChildNodes().item(0)).getNodeValue().trim());

                                // Be aware! The level of the HTMid can be different from the level of the HTMrange
                                Source src = new Source();
				src.setHtmIdLevel(19);
				src.setHtmId(HtmServices.getHtmId(src.getHtmIdLevel(), ra, dec));
				src.setObsTime(obsTime);
				src.setRA(ra);
				src.setDRA(dra);
				src.setDec(dec);
				src.setDDec(ddec);
				src.setFlux(flux);
				src.setHtmRangeLevel(21);
				src.setHtmRange(HtmServices.getHtmCover(src.getHtmRangeLevel(), ra-dra/2, dec + ddec/2, ra + dra/2, dec-ddec/2));
				sourceList.add(src);
				//System.out.println("Source in list; Source[" + s + "]: obsTime = " + src.getObsTime() + 
				//			"; htmid = " + src.getHtmId());
			}
			setSourceList(sourceList);
			System.out.println("Sources extracted: " + getSourceList().size() + "::.."); 
                } catch (FileNotFoundException e) {
                        System.out.println("FileNotFoundException: " + fileName);
                } catch (SAXParseException err) {
                        System.out.println ("** Parsing error" + ", line " + err.getLineNumber () + ", uri " + err.getSystemId ());
                        System.out.println(" " + err.getMessage ());
                } catch (SAXException e) {
                        Exception x = e.getException ();
                        ((x == null) ? e : x).printStackTrace ();
                } catch (Throwable t) {
                        t.printStackTrace();
                }
	}
}
