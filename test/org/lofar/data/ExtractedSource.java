package org.lofar.data;

import edu.jhu.htm.core.HTMrange;

public class ExtractedSource {
	private int xtrSrcId;
	private int beamId;
	private int freqId;
	private int integrId;
	private byte logId;
	private long htmId;
	private double ra;
	private double dec;
	private double raErr;
	private double decErr;
	private double stokesI;
	private double stokesQ;
	private double stokesU;
	private double stokesV;
	private double stokesIErr;
	private double stokesQErr;
	private double stokesUErr;
	private double stokesVErr;
	private String props;

	public int getXtrSrcId() {
		return xtrSrcId;
	}

	public int getBeamId() {
		return beamId;
	}

	public int getFreqId() {
		return freqId;
	}

	public int getIntegrId() {
		return integrId;
	}

	public byte getLogId() {
		return logId;
	}

	public long getHtmId() {
		return htmId;
	}

	public double getRA() {
		return ra;
	}

	public double getRaErr() {
		return raErr;
	}

	public double getDec() {
		return dec;
	}

	public double getDecErr() {
		return decErr;
	}

	public double getStokesI() {
		return stokesI;
	}

	public double getStokesQ() {
		return stokesQ;
	}

	public double getStokesU() {
		return stokesU;
	}

	public double getStokesV() {
		return stokesV;
	}

	public double getStokesIErr() {
		return stokesIErr;
	}

	public double getStokesQErr() {
		return stokesQErr;
	}

	public double getStokesUErr() {
		return stokesUErr;
	}

	public double getStokesVErr() {
		return stokesVErr;
	}

	public String getProps() {
		StringBuffer props = new StringBuffer();
		props.append(getXtrSrcId() + ";");
		props.append(getBeamId() + ";");
		props.append(getIntegrId() + ";");
		props.append(getHtmId() + ";");
		props.append(getRA() + ";");
		props.append(getRaErr() + ";");
		props.append(getDec() + ";");
		props.append(getDecErr() + ";");
		props.append(getStokesI() + ";");
		props.append(getStokesQ() + ";");
		props.append(getStokesU() + ";");
		props.append(getStokesV() + ";");
		props.append(getStokesIErr() + ";");
		props.append(getStokesQErr() + ";");
		props.append(getStokesUErr() + ";");
		props.append(getStokesVErr() + ";");
		return props.toString();
	}

	public void setXtrSrcId(int xtrSrcId) {
		this.xtrSrcId = xtrSrcId;
	}

	public void setBeamId(int beamId) {
		this.beamId = beamId;
	}

	public void setFreqId(int freqId) {
		this.freqId = freqId;
	}

	public void setIntegrId(int integrId) {
		this.integrId = integrId;
	}

	public void setLogId(byte logId) {
		this.logId = logId;
	}

	public void setHtmId(long htmId) {
		this.htmId = htmId;
	}

	public void setRA(double ra) {
		this.ra = ra;
	}

	public void setRaErr(double raErr) {
		this.raErr = raErr;
	}

	public void setDec(double dec) {
		this.dec = dec;
	}

	public void setDecErr(double decErr) {
		this.decErr = decErr;
	}

	public void setStokesI(double stokesI) {
		this.stokesI = stokesI;
	}

	public void setStokesQ(double stokesQ) {
		this.stokesQ = stokesQ;
	}

	public void setStokesU(double stokesU) {
		this.stokesU = stokesU;
	}

	public void setStokesV(double stokesV) {
		this.stokesV = stokesV;
	}

	public void setStokesIErr(double stokesIErr) {
		this.stokesIErr = stokesIErr;
	}

	public void setStokesQErr(double stokesQErr) {
		this.stokesQErr = stokesQErr;
	}

	public void setStokesUErr(double stokesUErr) {
		this.stokesUErr = stokesUErr;
	}

	public void setStokesVErr(double stokesVErr) {
		this.stokesVErr = stokesVErr;
	}

}
