package org.lofar.data.catalog;

public class Measurement {
	private long msId;
	private int srcId;
	private int freqEffId;
	private int integrTimeStartId;
	private int fileId;
	private int swVrsId;
	private Double[] stokesI;
	private Double[] stokesQ;
	private Double[] stokesU;
	private Double[] stokesV;
	private Double[] stokesIErr;
	private Double[] stokesQErr;
	private Double[] stokesUErr;
	private Double[] stokesVErr;
	private String[] props;

	public long getMsId() {
		return msId;
	}

	public int getSrcId() {
		return srcId;
	}

	public int getFreqEffId() {
		return freqEffId;
	}

	public int getIntegrTimeStartId() {
		return integrTimeStartId;
	}

	public int getFileId() {
		return fileId;
	}

	public int getSwVrsId() {
		return swVrsId;
	}

	public Double[] getStokesI() {
		return stokesI;
	}

	public Double[] getStokesQ() {
		return stokesQ;
	}

	public Double[] getStokesU() {
		return stokesU;
	}

	public Double[] getStokesV() {
		return stokesV;
	}

	public Double[] getStokesIErr() {
		return stokesIErr;
	}

	public Double[] getStokesQErr() {
		return stokesQErr;
	}

	public Double[] getStokesUErr() {
		return stokesUErr;
	}

	public Double[] getStokesVErr() {
		return stokesVErr;
	}

	public String[] getProps() {
		String[] props = new String[13];
		props[0] = "srcid = " + getSrcId();
		props[1] = "freqeffid = " + getFreqEffId();
		props[2] = "integrtime_sid = " + getIntegrTimeStartId(); 
		props[3] = "fileid = " + getFileId();
		props[4] = "swvrsid = " + getSwVrsId();
		Double[] stokesI = getStokesI();
		Double[] stokesQ = getStokesQ();
		Double[] stokesU = getStokesU();
		Double[] stokesV = getStokesV();
		Double[] stokesIErr = getStokesIErr();
		Double[] stokesQErr = getStokesQErr();
		Double[] stokesUErr = getStokesUErr();
		Double[] stokesVErr = getStokesVErr();
		StringBuffer sb = new StringBuffer();
		for (int i = 0; i < stokesI.length; i++) {
			sb.append("I" + (i + 1) + " = " + stokesI[i].doubleValue() + "; ");
		}
		props[5] = "stokesI: " + sb.toString();
		sb = new StringBuffer();
		if (stokesQ != null) {
			for (int i = 0; i < stokesQ.length; i++) {
				if (stokesQ[i] != null) {
					sb.append("Q" + (i + 1) + " = " + stokesQ[i].doubleValue() + "; ");
				} else {
					sb.append("Q" + (i + 1) + " = null; ");
				}
			}
		} else {
			sb.append("Q1-12: null");
		}
		props[6] = "stokesQ: " + sb.toString();
		sb = new StringBuffer();
		if (stokesU != null) {
			for (int i = 0; i < stokesU.length; i++) {
				if (stokesU[i] != null) {
					sb.append("U" + (i + 1) + " = " + stokesU[i].doubleValue() + "; ");
				} else {
					sb.append("U" + (i + 1) + " = null; ");
				}
			}
		} else {
			sb.append("U1-12: null");
		}
		props[7] = "stokesU: " + sb.toString();
		sb = new StringBuffer();
		if (stokesV != null) {
			for (int i = 0; i < stokesV.length; i++) {
				if (stokesV[i] != null) {
					sb.append("V" + (i + 1) + " = " + stokesV[i].doubleValue() + "; ");
				} else {
					sb.append("V" + (i + 1) + " = null; ");
				}
			}
		} else {
			sb.append("V1-12: null");
		}
		props[8] = "stokesV: " + sb.toString();
		sb = new StringBuffer();
		for (int i = 0; i < stokesIErr.length; i++) {
			sb.append("IErr" + (i + 1) + " = " + stokesIErr[i].doubleValue() + "; ");
		}
		props[9] = "stokesIErr: " + sb.toString();
		sb = new StringBuffer();
		if (stokesQErr != null) {
			for (int i = 0; i < stokesQErr.length; i++) {
				if (stokesQErr[i] != null) {
					sb.append("QErr" + (i + 1) + " = " + stokesQErr[i].doubleValue() + "; ");
				} else {
					sb.append("QErr" + (i + 1) + " = null; ");
				}
			}
		} else {
			sb.append("QErr1-12: null");
		}
		props[10] = "stokesQErr: " + sb.toString();
		sb = new StringBuffer();
		if (stokesUErr!= null) {
			for (int i = 0; i < stokesUErr.length; i++) {
				if (stokesUErr[i] != null) {
					sb.append("UErr" + (i + 1) + " = " + stokesUErr[i].doubleValue() + "; ");
				} else {
					sb.append("UErr" + (i + 1) + " = null; ");
				}
			}
		} else {
			sb.append("UErr1-12: null");
		}
		props[11] = "stokesUErr: " + sb.toString();
		sb = new StringBuffer();
		if (stokesVErr != null) {
			for (int i = 0; i < stokesVErr.length; i++) {
				if (stokesVErr[i] != null) {
					sb.append("VErr" + (i + 1) + " = " + stokesVErr[i].doubleValue() + "; ");
				} else {
					sb.append("VErr" + (i + 1) + " = null; ");
				}
			}
		} else {
			sb.append("VErr1-12: null");
		}
		props[12] = "stokesVErr: " + sb.toString();
		return props;
	}

	public void setMsId(long msId) {
		this.msId = msId;
	}

	public void setSrcId(int srcId) {
		this.srcId = srcId;
	}

	public void setFreqEffId(int freqEffId) {
		this.freqEffId = freqEffId;
	}

	public void setIntegrTimeStartId(int integrTimeStartId) {
		this.integrTimeStartId = integrTimeStartId;
	}

	public void setFileId(int fileId) {
		this.fileId = fileId;
	}

	public void setSwVrsId(int swVrsId) {
		this.swVrsId = swVrsId;
	}

	public void setStokesI(Double[] stokesI) {
		this.stokesI = stokesI;
	}

	public void setStokesQ(Double[] stokesQ) {
		this.stokesQ = stokesQ;
	}

	public void setStokesU(Double[] stokesU) {
		this.stokesU = stokesU;
	}

	public void setStokesV(Double[] stokesV) {
		this.stokesV = stokesV;
	}

	public void setStokesIErr(Double[] stokesIErr) {
		this.stokesIErr = stokesIErr;
	}

	public void setStokesQErr(Double[] stokesQErr) {
		this.stokesQErr = stokesQErr;
	}

	public void setStokesUErr(Double[] stokesUErr) {
		this.stokesUErr = stokesUErr;
	}

	public void setStokesVErr(Double[] stokesVErr) {
		this.stokesVErr = stokesVErr;
	}

}
