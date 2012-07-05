package org.lofar.data;

public class Source {
	private long htmId;
	private double ra;
	private double dec;
	private double flux;

	public long getHtmId() {
		return htmId;
	}

	public double getRA() {
		return ra;
	}

	public double getDec() {
		return dec;
	}

	public double getFlux() {
		return flux;
	}

	public void setHtmId(long htmId) {
		this.htmId = htmId;
	}

	public void setRA(double ra) {
		this.ra = ra;
	}

	public void setDec(double dec) {
		this.dec = dec;
	}

	public void setFlux(double flux) {
		this.flux = flux;
	}
}
