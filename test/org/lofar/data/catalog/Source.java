package org.lofar.data.catalog;

import edu.jhu.htm.core.HTMrange;

public class Source {
	private int srcId;
	private int obsId;
	private int classId;
	private long htmId;
	private double ra;
	private double dec;
	private double raErr;
	private double decErr;
	private double spectralIndex;

    /**
     * Holds value of property comment.
     */
    private String comment;

	public int getSrcId() {
		return srcId;
	}

	public int getObsId() {
		return obsId;
	}

	public int getClassId() {
		return classId;
	}

	public long getHtmId() {
		return htmId;
	}

	public double getRA() {
		return ra;
	}

	public double getRAErr() {
		return raErr;
	}

	public double getDec() {
		return dec;
	}

	public double getDecErr() {
		return decErr;
	}

	public double getSpectralIndex() {
		return spectralIndex;
	}

	public void setSrcId(int srcId) {
		this.srcId = srcId;
	}

	public void setObsId(int obsId) {
		this.obsId = obsId;
	}

	public void setClassId(int classId) {
		this.classId = classId;
	}

	public void setHtmId(long htmId) {
		this.htmId = htmId;
	}

	public void setRA(double ra) {
		this.ra = ra;
	}

	public void setRAErr(double raErr) {
		this.raErr = raErr;
	}

	public void setDec(double dec) {
		this.dec = dec;
	}

	public void setDecErr(double decErr) {
		this.decErr = decErr;
	}

	public void setSpectralIndex(double spectralIndex) {
		this.spectralIndex = spectralIndex;
	}

    /**
     * Getter for property comment.
     * @return Value of property comment.
     */
    public String getComment() {

        return this.comment;
    }

    /**
     * Setter for property comment.
     * @param comment New value of property comment.
     */
    public void setComment(String comment) {

        this.comment = comment;
    }

}
