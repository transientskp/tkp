package org.lofar.pipeline;

import java.sql.*;
import java.util.*;

import org.lofar.util.DatabaseManager;

public class OpenConnection {
	
        public static void main(String[] args) {
	        Connection con = DatabaseManager.getConnection();
	}

}
