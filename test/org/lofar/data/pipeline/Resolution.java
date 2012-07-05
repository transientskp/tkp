package org.lofar.data.pipeline;

public class Resolution {
	private int resId;
	private double major;
	private double minor;
	private double pa;

	public int getResId() {
		return resId;
	}

	public double getMajor() {
		return major;
	}

	public double getMinor() {
		return minor;
	}

	public double getPA() {
		return pa;
	}

	public void setResId(int resId) {
		this.resId = resId;
	}

	public void setMajor(double major) {
		this.major = major;
	}

	public void setMinor(double minor) {
		this.minor = minor;
	}

	public void setPA(double pa) {
		this.pa = pa;
	}

}
