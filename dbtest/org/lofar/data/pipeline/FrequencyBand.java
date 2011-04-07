package org.lofar.data.pipeline;

public class FrequencyBand {
	private int freqId;
	private double freqStart;
	private double freqEnd;
	private Double freqEff;

	public int getFreqId() {
		return freqId;
	}

	public double getFreqStart() {
		return freqStart;
	}

	public double getFreqEnd() {
		return freqEnd;
	}

	public Double getFreqEff() {
		return freqEff;
	}

	public void setFreqId(int freqId) {
		this.freqId = freqId;
	}

	public void setFreqStart(double freqStart) {
		this.freqStart = freqStart;
	}

	public void setFreqEnd(double freqEnd) {
		this.freqEnd = freqEnd;
	}

	public void setFreqEff(Double freqEff) {
		this.freqEff = freqEff;
	}

}
