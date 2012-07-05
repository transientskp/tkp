package org.lofar.data;

import edu.jhu.htm.core.HTMrange;

/**
 * @deprecated Use org.lofar.data.catalog.Source
 */
public class Source {
	private long htmId;
	private double ra;
	private double dec;
	private double dRa;
	private double dDec;
	private double flux;
	private double dFlux;
	private double fluxMax;
	private double dFluxMax;
	private double fluxIso;
	private double dFluxIso;
	private double fluxIsocor;
	private double dFluxIsocor;
	private double fluxAper;
	private double dFluxAper;
	private double fluxAuto;
	private double dFluxAuto;
	private double isoAreafImage;
	private double runid;
	private int dist;
	private int ddist;
	private String major;
	private String minor;
	private double dmajor;
	private double dminor;
	private double PA;
	private double dPA;
	private String res;
	private int dres;
	/*
	 * The range of HTMids corresponding to the corners of the rectangular:
	 * (ra-dra/2, dec + ddec/2, ra + dra/2, dec-ddec/2) and with a HTMlevel 
	 * given by htmRangeLevel
	 */
	private HTMrange htmRange;
	/*
	 * The level by which the HTMid is calculated
	 */
	private int htmIdLevel;
	private int htmRangeLevel;
	private String obsTime;
	private String comment;

	public long getHtmId() {
		return htmId;
	}

	public double getRA() {
		return ra;
	}

	public double getDRA() {
		return dRa;
	}

	public double getDec() {
		return dec;
	}

	public double getDDec() {
		return dDec;
	}

	public double getFlux() {
		return flux;
	}

	public double getDFlux() {
		return dFlux;
	}

	public double getFluxMax() {
		return fluxMax;
	}

	public double getDFluxMax() {
		return dFluxMax;
	}

	public double getFluxIso() {
		return fluxIso;
	}

	public double getDFluxIso() {
		return dFluxIso;
	}

	public double getFluxIsocor() {
		return fluxIsocor;
	}

	public double getDFluxIsocor() {
		return dFluxIsocor;
	}

	public double getFluxAper() {
		return fluxAper;
	}

	public double getDFluxAper() {
		return dFluxAper;
	}

	public double getFluxAuto() {
		return fluxAuto;
	}

	public double getDFluxAuto() {
		return dFluxAuto;
	}

	public double getIsoAreafImage() {
		return isoAreafImage;
	}

	public double getRunid() {
		return runid;
	}

	public HTMrange getHtmRange() {
		return htmRange;
	}

	public int getHtmIdLevel() {
		return htmIdLevel;
	}

	public int getHtmRangeLevel() {
		return htmRangeLevel;
	}

	public String getObsTime() {
		return obsTime;
	}

	public String getComment() {
		return comment;
	}

	public void setHtmId(long htmId) {
		this.htmId = htmId;
	}

	public void setRA(double ra) {
		this.ra = ra;
	}

	public void setDRA(double dRa) {
		this.dRa = dRa;
	}

	public void setDec(double dec) {
		this.dec = dec;
	}

	public void setDDec(double dDec) {
		this.dDec = dDec;
	}

	public void setFlux(double flux) {
		this.flux = flux;
	}

	public void setDFlux(double dFlux) {
		this.dFlux = dFlux;
	}

	public void setFluxMax(double fluxMax) {
		this.fluxMax = fluxMax;
	}

	public void setDFluxMax(double dFluxMax) {
		this.dFluxMax = dFluxMax;
	}

	public void setFluxIso(double fluxIso) {
		this.fluxIso = fluxIso;
	}

	public void setDFluxIso(double dFluxIso) {
		this.dFluxIso = dFluxIso;
	}

	public void setFluxIsocor(double fluxIsocor) {
		this.fluxIsocor = fluxIsocor;
	}

	public void setDFluxIsocor(double dFluxIsocor) {
		this.dFluxIsocor = dFluxIsocor;
	}

	public void setFluxAper(double fluxAper) {
		this.fluxAper = fluxAper;
	}

	public void setDFluxAper(double dFluxAper) {
		this.dFluxAper = dFluxAper;
	}

	public void setFluxAuto(double fluxAuto) {
		this.fluxAuto = fluxAuto;
	}

	public void setDFluxAuto(double dFluxAuto) {
		this.dFluxAuto = dFluxAuto;
	}

	public void setIsoAreafImage(double isoAreafImage) {
		this.isoAreafImage = isoAreafImage;
	}

	public void setRunid(double runid) {
		this.runid = runid;
	}

	public void setHtmRange(HTMrange htmRange) {
		this.htmRange = htmRange;
	}

	public void setHtmIdLevel(int htmIdLevel) {
		this.htmIdLevel = htmIdLevel;
	}

	public void setHtmRangeLevel(int htmRangeLevel) {
		this.htmRangeLevel = htmRangeLevel;
	}

	public void setObsTime(String obsTime) {
		this.obsTime = obsTime;
	}

	public void setComment(String comment) {
		this.comment = comment;
	}

	public void setDist(int dist) {
		this.dist = dist;
	}

	public int getDist() {
		return dist; 
	}

	public void setDDist(int ddist) {
		this.ddist = ddist;
	}

	public int getDDist() {
		return ddist; 
	}

	public void setMajor(String major) {
		this.major = major;
	}

	public String getMajor() {
		return major;
	}

	public void setMinor(String minor) {
		this.minor = minor;
	}

	public String getMinor() {
		return minor;
	}

	public void setDMajor(double dmajor) {
		this.dmajor = dmajor;
	}

	public double getDMajor() {
		return dmajor;
	}

	public void setDMinor(double dminor) {
		this.dminor = dminor;
	}

	public double getDMinor() {
		return dminor;
	}

	public void setPA(double PA) {
		this.PA = PA;
	}

	public double getPA() {
		return PA;
	}

	public void setDPA(double dPA) {
		this.dPA = dPA;
	}

	public double getDPA() {
		return dPA;
	}

	public void setRes(String res) {
		this.res = res;
	}

	public String getRes() {
		return res;
	}

	public void setDRes(int dres) {
		this.dres = dres;
	}

	public int getDRes() {
		return dres;
	}

}
