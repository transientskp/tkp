package org.lofar.data.pipeline;

public class IntegrationTimes {
	private int integrId;
	private int fileId;
	private short logseries;
	private long timeStart;

	public int getIntegrId() {
		return integrId;
	}

	public int getFileId() {
		return fileId;
	}

	public short getLogseries() {
		return logseries;
	}

	public long getTimeStart() {
		return timeStart;
	}

	public void setIntegrId(int integrId) {
		this.integrId = integrId;
	}

	public void setFileId(int fileId) {
		this.fileId = fileId;
	}

	public void setLogseries(short logseries) {
		this.logseries = logseries;
	}

	public void setTimeStart(long timeStart) {
		this.timeStart = timeStart;
	}

}
