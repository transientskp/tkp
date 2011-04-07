package org.lofar.data;

public class FitsFile {
	private int id;
	private int type;
	private String in;
	private String out;

	public int getId() {
		return id;
	}

	public int getType() {
		return type;
	}

	public String getIn() {
		return in;
	}

	public String getOut() {
		return out;
	}

	public void setId(int id) {
		this.id = id;
	}

	public void setType(int type) {
		this.type = type;
	}

	public void setIn(String in) {
		this.in = in;
	}

	public void setOut(String out) {
		this.out = out;
	}

}
