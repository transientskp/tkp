package org.lofar.pipeline;

import java.sql.*;
import java.util.*;

import org.lofar.util.DatabaseManager;

public class TestOpenConnection {
	
        public static void main(String[] args) {
		Connection con;
	        con = DatabaseManager.getConnection();
	        con = DatabaseManager.getConnection();
	        con = DatabaseManager.getConnection();
	}

}
