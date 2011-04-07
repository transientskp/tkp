package org.lofar.data;

import java.sql.*;
import org.lofar.util.*;

public class StoreInDatabase implements StoreBehavior {
	
	private Connection con;
	private PreparedStatement pstmt;
	private int count = 0;

	// So here must be the database connections and so on
	public void store(Source src) {
		try {
			con = DatabaseManager.getConnection();
			String countSQL = "SELECT COUNT(*) FROM lofarcat;";
			pstmt = con.prepareStatement(countSQL);
			ResultSet rs = pstmt.executeQuery();
			while (rs.next()) {
				count = rs.getInt(1);
			}
			System.out.println("Source: " + src.getHtmId() + " observed at: " + src.getObsTime() + " stored in DB!");
			System.out.println("Sources stored in lofarcat: " + count);
		} catch (Exception e) {
			System.err.println("[StoreInDatabase]Exception: " + e.getMessage());
                        System.exit(1);
		}

	}
}
