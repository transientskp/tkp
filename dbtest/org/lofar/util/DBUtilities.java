package org.lofar.util;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.NamingException;
import javax.servlet.ServletContext;
import javax.sql.DataSource;


/**
 * Utility class for DB connection creation and destroys<BR>
 * Applicationkey used for property file(<i>key</i>.properties)
 */
public class DBUtilies {

        /** extension of filename for configuration (.properties) **/
        private final static String EXT_PROPERTIES_FILE = ".properties";

        /** Singleton factory **/
        private static DBUtilies aFactorySingleton;

        /** caches to prevent repetitive and expensive lookups **/
        private static Map cachedPropertiesByKey = null;
        private static Map cachedDSByKey = null;

        private static ServletContext lookupContext = null;

        /**
         * DBUtilies private constructor.
         */
        private DBUtilies() {
                super();
                DBUtilies.cachedPropertiesByKey = Collections.synchronizedMap(new HashMap());
                DBUtilies.cachedDSByKey = Collections.synchronizedMap(new HashMap());
        }
        /**
         * Close the given Statement and Connection.<BR>
         * @param statement the Statement to be closed.
         * @param connection the Connection to be closed.
         * @throws RaboDistributedException for every SQL Exception.
         */
        public static void closeConnection(ResultSet rs, Statement statement, Connection connection)
        throws RaboDistributedException {

                SQLException sqle = null;
                try {
                        if (rs != null) rs.close();
                } catch (SQLException e) {
                        sqle = e;
                }
                try {
                        if (statement != null) {
                                statement.close();
                        }
                } catch (SQLException e) {
                        sqle = e;
                }
                try {
                        if (connection != null) {
                                connection.commit();
                                connection.close();
                        }
                } catch (SQLException e) {
                        sqle = e;
                }
                if (sqle != null) {
                        throw new RaboDistributedException(sqle);
                }
        }

        /**
         * Close the given Statement and Connection.<BR>
         * @param statement the Statement to be closed.
         * @param connection the Connection to be closed.
         * @throws RaboDistributedException for every SQL Exception.
         */
        public static void closeConnection(
                Statement statement,
                Connection connection)
                throws RaboDistributedException {

                SQLException sqle = null;
                try {
                        if (statement != null) {
                                statement.close();
                        }
                } catch (SQLException e) {
                        sqle = e;
                }
                try {
                        if (connection != null) {
                                connection.commit();
                                connection.close();
                        }
                } catch (SQLException e) {
                        sqle = e;
                }
                if (sqle != null) {
                        throw new RaboDistributedException(sqle);
                }
        }

        /**
         * Get a connection to the configured database.<BR>
         * Uses hard coded 'datasourcename' property name
         *
         * @param argApplicationKey application name
         * @return an open connection Connection.
         * @throws RaboDistributedException for every Naming and SQL Exception.
         */
        public static Connection getConnection(String argApplicationKey) throws Exception {
                Properties props = getProperties(argApplicationKey);
                String datasourceName = props.getProperty("datasourcename");
                String user = props.getProperty("user");
                String password = props.getProperty("password");
                String webapp = props.getProperty("webapp");

                if (datasourceName == null) {
                        System.out.println("[DBUtilities] Cannot find property: dsname for: " + argApplicationKey);
                        throw new Exception("[DBUtilies] Error while getting a connection to the database 1");
                }
                try {
                        DataSource cachedDS = (DataSource) cachedDSByKey.get(argApplicationKey);
                        if (cachedDS == null) {
                                javax.naming.Context ctx = getInitialContext();
                                System.out.println("[DBUtilies] trying to lookup: '" + datasourceName + "'");
                                DataSource ds = (DataSource) ctx.lookup(datasourceName);
                                cachedDS = ds;
                                cachedDSByKey.put(argApplicationKey, cachedDS);
                        }
                        if (user != null) {
                                return cachedDS.getConnection(user, password);
                        } else {
                                return cachedDS.getConnection();
                        }
                } catch (NamingException ne) {
                        ne.printStackTrace();
                        System.out.println("[DBUtilies] NamingException" +
				"while getting a connection to the database for: " + argApplicationKey);
                        throw new Exception("error while getting a connection to the database 2", ne);
                } catch (SQLException sqle) {
                        System.out.println("[DBUtilies] SQLException " +
				"while getting a connection to the database for: " + argApplicationKey);
                        throw new Exception( "[DBUtilies] Error while getting a connection to the database3", sqle);
                }
        }
        /**
         * Create and return a context.<BR>
         * @return the Context create for the used configuration set.
         * @throws RaboDistributedException for every Naming Exception.
         */
        public static Context getInitialContext() throws RaboDistributedException {
                try {
                        return new InitialContext();
                } catch (NamingException nam) {
                        System.out.println("[CDW][DBUtilies] Unable to create Initial context");
                        throw new RaboDistributedException(
                                "[CDW][DBUtilies] Unable to create Initial context",
                                nam);
                }
        }

        /**
         * returns properties object containing all<br>
         * properties from configuration file.
         *
         * @param argApplicationKey  application name
         * @return properties for application
         */
        public static Properties getProperties(String argApplicationKey)
                throws RaboDistributedException {

                DBUtilies util = DBUtilies.getInstance();
                Properties cachedProps =
                        (Properties) util.cachedPropertiesByKey.get(argApplicationKey);
                if (cachedProps == null) {
                        Properties props = new Properties();
                        String filename = argApplicationKey + EXT_PROPERTIES_FILE;
                        InputStream is =
                                lookupContext.getResourceAsStream("WEB-INF/" + filename);
                        System.out.println(
                                "[CDW][DBUtilies] Lookup file: "
                                        + filename
                                        + " for: "
                                        + argApplicationKey);

                        if (is == null) {
                                System.out.println(
                                        "[CDW][DBUtilies] "
                                                + " Unable to lookup file: "
                                                + filename
                                                + " for: "
                                                + argApplicationKey);

                                throw new RaboDistributedException(
                                        "[CDW][DBUtilies] Cannot find file: " + filename);
                        } else {
                                System.out.println(
                                        "[CDW][DBUtilies] Found file "
                                                + filename
                                                + " for: "
                                                + argApplicationKey);

                        }

                        try {
                                props.load(is);
                                util.cachedPropertiesByKey.put(argApplicationKey, props);
                                cachedProps = props;
                        } catch (FileNotFoundException e) {
                                System.out.println("[CDW][DBUtilies] Cannot find file: "
                                        + filename
                                        + " "
                                        + e.getMessage());
                                throw new RaboDistributedException(
                                        "[CDW][DBUtilies] Cannot find file: " + filename,
                                        e);
                        } catch (IOException e) {
                                System.out.println("[CDW][DBUtilies] Cannot read file: "
                                        + filename
                                        + " "
                                        + e.getMessage());
                                throw new RaboDistributedException(
                                        "[CDW][DBUtilies] Cannot read file: " + filename,
                                        e);
                        } finally {
                                try {
                                        is.close();
                                } catch (IOException e) {
                                        System.out.println(
                                                "[CDW][DBUtilies] Failed to close file: "
                                                        + filename
                                                        + " for: "
                                                        + argApplicationKey);

                                }
                        }
                }
                return cachedProps;
        }

        /**
         * returns value for key
         *
         * @param argApplicationKey  java.lang.String
         * @param property key java.lang.String
         * @return property value java.lang.String
         */
        public static String getProperty(String argApplicationKey, String key)
                throws RaboDistributedException {
                Properties p = getProperties(argApplicationKey);
                return p.getProperty(key);
        }

        /**
         * Returns the singleton instance of the DBUtilies
         * The sychronized keyword is intentionally left out the
         * as I don't think the potential to intialize the singleton
         * twice at startup time (which is not a destructive event)
         * is worth creating a sychronization bottleneck on this
         * VERY frequently used class, for the lifetime of the
         * client application.
         *
         * @return singleton DBUtilies
         */
        private static DBUtilies getInstance() {
                if (DBUtilies.aFactorySingleton == null) {
                        DBUtilies.aFactorySingleton = new DBUtilies();
                }
                return DBUtilies.aFactorySingleton;
        }

        /**
         * Initialize the context for properties path
         * @param arg_lookupContext
         * @return
         */
        public static boolean initialize(ServletContext arg_lookupContext) {
                try {
                        DBUtilies util = getInstance();
                        util.lookupContext = arg_lookupContext;
                } catch (Exception e) {
                        System.out.println("[CDW][DBUtilies] " + e.getMessage());
                        return false;
                }
                return true;
        }

        /**
         * Return Object as String. Used for logging purposes.
         * @return java.lang.String
         */
        public String toString() {
                return "[CDW][DBUtilies]";
        }
        /**
         * @return
         */
        public static ServletContext getLookupContext() {
                return lookupContext;
        }

}

