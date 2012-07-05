/*
 * Created on 2-feb-04
 *
 */
package nl.rabobank.cdw.util;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.NamingException;
import javax.servlet.ServletContext;
import javax.sql.DataSource;

import nl.rabobank.cdw.appdomain.PlatFormContext;
import nl.rabobank.cdw.dao.DAOFactory;
import nl.rabobank.cdw.dao.SQLManager;
import nl.rabobank.cdw.dao.db2.IBMDAOFactory;
import nl.rabobank.cdw.dao.oracle.OracleDAOFactory;
import nl.rabobank.cdw.exception.CloseSQLResourcesException;
import nl.rabobank.cdw.exception.DatabaseDisabledException;
import nl.rabobank.cdw.exception.RaboDistributedException;
import nl.rabobank.cdw.log.RaboLogManager;

import org.apache.commons.logging.Log;

/**
 * Utility class for DB connection creation and destroys<BR>
 * Applicationkey used for property file(<i>key</i>.properties)
 * @author TermaatWA
 *
 */
public class DBManager {

        /** extension of filename for configuration (.properties) **/
        private final static String EXT_PROPERTIES_FILE = ".properties";

        /** Application key for configuration file */
        public final static String MAIN_APP_KEY = "bms";

        /** Database enabled key for configuration file */
        public final static String DB_ENABLED_KEY = "init_databaseenabled";

        /** Db2 specific enabled key for configuration file */
        public final static String DB2_ENABLED_KEY = "init_db2enabled";

        /** Oracle specific enabled key for configuration file */
        public final static String ORACLE_ENABLED_KEY = "init_oracleenabled";

        private final static String logString = "[CDW][DBManager]";
        private static Log log = null; //HIER NIET ZETTEN, DIT MOET IN DE METHODE
INITIALIZE !!

        /** caches to prevent repetitive and expensive lookups **/
        private static Map cachedPropertiesByKey = null;
        private static Map cachedDSByKey = null;
        private static ServletContext lookupContext = null;

        /**
         * Close the given Statement and Connection.<BR>
         * @param statement the Statement to be closed.
         * @param connection the Connection to be closed.
         * @throws RaboDistributedException for every SQL Exception.
         */
        public static void closeConnection(ResultSet rs, Statement statement,
Connection connection)
                throws RaboDistributedException {
                SQLException sqle = null;
                try {
                        if (rs != null) {
                                rs.close();
                        }
                }
                catch (SQLException e) {
                        sqle = e;
                }
                try {
                        if (statement != null) {
                                statement.close();
                        }
                }
                catch (SQLException e) {
                        sqle = e;
                }
                try {
                        if (connection != null) {
                                connection.commit();
                                connection.close();
                        }
                }
                catch (SQLException e) {
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
        public static void closeConnection(Statement statement, Connection
connection) throws RaboDistributedException {
                SQLException sqle = null;
                try {
                        if (statement != null) {
                                statement.close();
                        }
                }
                catch (SQLException e) {
                        sqle = e;
                }
                try {
                        if (connection != null) {
                                connection.commit();
                                connection.close();
                        }
                }
                catch (SQLException e) {
                        sqle = e;
                }
                if (sqle != null) {
                        throw new RaboDistributedException(sqle);
                }
        }
        public static void closeConnection(Connection con) throws SQLException {
                if (con != null) {
                        con.commit();
                        con.close();
                }
        }
        public static void closeStatement(Statement stmt) throws SQLException {
                if (stmt != null) {
                        stmt.close();
                }
        }
        public static void closeResultSet(ResultSet rs) throws SQLException {
                if (rs != null) {
                        rs.close();
                }
        }
        /**
         * Close the given ResultSet, its Statement and its Connection.<BR>
         * @param resultset the ResultSet to be closed.
         * @throws RaboDistributedException for every SQL Exception.
         */
        public static void close(ResultSet rs) throws CloseSQLResourcesException {
                Statement stmt;
                Connection con;
                if (rs != null) {
                        try {
                                stmt = rs.getStatement();
                                con = stmt.getConnection();
                                closeResultSet(rs);
                                closeStatement(stmt);
                                closeConnection(con);
                        }
                        catch (SQLException sqle) {
                                CloseSQLResourcesException csqlre = new
CloseSQLResourcesException("Failed to close SQLResource", sqle);
                                throw csqlre;
                        }
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
        public static Connection getConnection(String argApplicationKey) throws
RaboDistributedException {
                Properties props = getProperties(argApplicationKey);
                String datasourceName = props.getProperty("datasourcename");
                String user = props.getProperty("user");
                String password = props.getProperty("password");
                //String webapp = props.getProperty("webapp");
                if (datasourceName == null) {
                        System.out.println(
                                new java.util.Date().toString()
                                        + " [CDW][DBManager] Cannot find property: datasourcename for: "
                                        + argApplicationKey);
                        throw new RaboDistributedException("[CDW][DBManager] Error while
getting a connection to the database 1");
                }
                try {
                        DataSource cachedDS = (DataSource) cachedDSByKey.get(argApplicationKey);
                        if (cachedDS == null) {
                                javax.naming.Context ctx = getInitialContext();
                                System.out.println(
                                        new java.util.Date().toString() + " [CDW][DBManager] trying to
lookup: '" + datasourceName + "'");
                                DataSource ds = (DataSource) ctx.lookup(datasourceName);
                                cachedDS = ds;
                                cachedDSByKey.put(argApplicationKey, cachedDS);
                        }
                        if (user != null) {
                                /*
                                raboLogger.error(new java.util.Date().toString()  + " [CDW][DBManager]
we gaan naar " + argApplicationKey  + " manier1 " + user + " " +
password);
                                */
                                return cachedDS.getConnection(user, password);
                        }
                        else {
                                return cachedDS.getConnection();
                        }
                }
                catch (NamingException ne) {
                        ne.printStackTrace();
                        System.out.println(
                                new java.util.Date().toString()
                                        + " [CDW][DBManager] NamingException while getting a connection to
the database for: "
                                        + argApplicationKey);
                        throw new RaboDistributedException("error while getting a connection to
the database 2", ne);
                }
                catch (SQLException sqle) {
                        System.out.println(
                                new java.util.Date().toString()
                                        + " [CDW][DBManager] SQLException while getting a connection to the
database for: "
                                        + argApplicationKey);
                        throw new RaboDistributedException(
                                new java.util.Date().toString()
                                        + " [CDW][DBManager] Error while getting a connection to the database
3",
                                sqle);
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
                }
                catch (NamingException nam) {
                        System.out.println("[CDW][DBManager] Unable to create Initial context");
                        throw new RaboDistributedException("[CDW][DBManager] Unable to create
Initial context", nam);
                }
        }
        /**
         * returns properties object containing all<br>
         * properties from configuration file.
         *
         * @param argApplicationKey  application name
         * @return properties for application
         */
        public static Properties getProperties(String argApplicationKey) throws
RaboDistributedException {
                Properties cachedProps = (Properties)
cachedPropertiesByKey.get(argApplicationKey);
                if (cachedProps == null) {
                        Properties props = new Properties();
                        String filename = argApplicationKey + EXT_PROPERTIES_FILE;
                        InputStream is = lookupContext.getResourceAsStream("WEB-INF/" + filename);
                        System.out.println("[CDW][DBManager] Lookup file: " + filename + " for:
" + argApplicationKey);
                        if (is == null) {
                                System.out.println(
                                        "[CDW][DBManager] " + " Unable to lookup file: " + filename + " for:
" + argApplicationKey);
                                throw new RaboDistributedException("[CDW][DBManager] Cannot find file:
" + filename);
                        }
                        else {
                                System.out.println("[CDW][DBManager] Found file " + filename + " for:
" + argApplicationKey);
                        }
                        try {
                                //System.out.println("DBManager-tijdelijk voor put props=" +
props.size()) ;
                                props.load(is);
                                //System.out.println("DBManager-tijdelijk voor put argApplicationKey="
+ argApplicationKey);
                                cachedPropertiesByKey.put(argApplicationKey, props);
                                //System.out.println("DBManager-tijdelijk na put argApplicationKey=" +
argApplicationKey) ;
                                //System.out.println("DBManager-tijdelijk na put props=" +
props.size()) ;
                                cachedProps = props;
                        }
                        catch (FileNotFoundException e) {
                                System.out.println("[CDW][DBManager] Cannot find file: " + filename +
" " + e.getMessage());
                                throw new RaboDistributedException("[CDW][DBManager] Cannot find file:
" + filename, e);
                        }
                        catch (IOException e) {
                                System.out.println("[CDW][DBManager] Cannot read file: " + filename +
" " + e.getMessage());
                                throw new RaboDistributedException("[CDW][DBManager] Cannot read file:
" + filename, e);
                        }
                        finally {
                                try {
                                        is.close();
                                }
                                catch (IOException e) {
                                        System.out.println(
                                                "[CDW][DBManager] Failed to close file: " + filename + " for: " +
argApplicationKey);
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
                //System.out.println(" Tijdelijk1-- argApplicationKey=" +
argApplicationKey + " key=" + key);
                Properties p = getProperties(argApplicationKey);
                //System.out.println(" Tijdelijk2-- argApplicationKey=" +
argApplicationKey + " key=" + key);
                //System.out.println(" Tijdelijk3-- p.getProperty(key)=" +
p.getProperty(key));
                return p.getProperty(key);
        }
        /**
         * Initialize the context for properties path
         * @param arg_lookupContext
         * @return
         */
        public static boolean initialize(ServletContext arg_lookupContext) {
                cachedPropertiesByKey = Collections.synchronizedMap(new HashMap());
                cachedDSByKey = Collections.synchronizedMap(new HashMap());
                lookupContext = arg_lookupContext;
                log = RaboLogManager.getLogger(DBManager.class);
                return true;
        }
        /**
         * Return Object as String. Used for logging purposes.
         * @return java.lang.String
         */
        public static String staticToString() {
                return "[CDW][DBManager]";
        }
        /**
         * @return
         */
        public static ServletContext getLookupContext() {
                return lookupContext;
        }
        /** Voert een query uit op het gegeven platform en retourneert de resultset.
         *  Na gebruik dient deze resultset gesloten te worden, met methode
closeConnection(resultset).
         *
         *  @return ResultSet met de resultaten
         *
         *  @param platform is ZOS of AIX - anders
java.lang.IllegalArgumentException
         *  @param queryID is een unieke identifier voor de uit te voeren query,
die in queries.xml voorkomt.
         *                  Mag niet null zijn (IllegalArgumentException).
         *  @param parameters zijn de in te vullen parameters voor de query. Mag
null zijn.
         *
         *  @throws java.lang.IllegalArgumentException als platform is niet ZOS
of AIX
         *  @throws java.lang.IllegalArgumentException als queryID leeg is of null
         *  @throws nl.rabobank.cdw.exception.DatabaseDisabledException
         *                       als de gevraagde database volgens properties niet gebruikt dient
te worden.
         */
        public static ResultSet query(String platform, String queryID, Object[]
parameters)
                        throws java.lang.IllegalArgumentException, DatabaseDisabledException,
SQLException {

                String query = null;
                Connection con;
                PreparedStatement stmt;
                ResultSet rs = null;
                String database = mapPlatformToDatabase(platform);

                //vind de query en zet een connection op
                query = SQLManager.getQueryByID(database, queryID);

                try {
                        con = DBManager.getConnection(database);
                }
                catch (Exception e) {
                        if (log.isErrorEnabled()) {
                                log.error(staticToString() + StringUtilities.getTrace(e));
                        }
                        throw new SQLException("Could not get connection to database: " +
platform + ":" + database);
                }

                try {
                        stmt = con.prepareStatement(query);
                }
                catch (Exception e) {
                        if (log.isErrorEnabled()) {
                                log.error(staticToString() + StringUtilities.getTrace(e));
                        }
                        throw new SQLException("Could not create preparedStatement for query: "
+ platform + ":" + query);
                }

                if (log.isDebugEnabled()) {
                        log.debug("==========================================================");
                        log.debug(DBManager.logString + " - query()");
                        log.debug("Query = " + query);
                }

                //vul het prepared statement met alle parameters:
                for (int i = 0; i < parameters.length; i++) {

                        Object param = parameters[i];

                        if (param instanceof String) {
                                stmt.setString(i + 1, (String) param);
                        }

                        if (param instanceof Short) {
                                stmt.setShort(i + 1, ((Short)param).shortValue());
                        }

                        if (param instanceof Integer) {
                                stmt.setInt(i + 1, ((Integer) param).intValue());
                        }

                        if (param instanceof Long) {
                                stmt.setLong(i + 1, ((Long) param).longValue());
                        }

                        if (param instanceof Date) {
                                stmt.setTimestamp(i + 1, new java.sql.Timestamp(((Date)
param).getTime()));
                        }

                        if (log.isDebugEnabled()) {
                                log.debug(DBManager.logString + " Param " + i + " = " +
param.toString());
                        }
                }

                if (log.isDebugEnabled()) {
                        log.debug("==========================================================");
                }

                //voer uit en retourneer het resultaat
                try {
                        rs = stmt.executeQuery();
                }
                catch (Exception e) {
                        if (log.isErrorEnabled()) {
                                log.error(staticToString() + StringUtilities.getTrace(e));
                        }
                        throw new SQLException("Error while executing preparedStatement for
query: " + platform + ":" + query);
                }

                return rs;
        }

        /** Voert een update uit op het gegeven platform.
         *  @return int het aantal gewijzigde records
         *
         *  @param platform is ZOS of AIX - anders
java.lang.IllegalArgumentException
         *  @param updateID is een unieke identifier voor de uit te voeren
update, die in queries.xml voorkomt.
         *                  Mag niet null zijn (IllegalArgumentException).
         *  @param parameters zijn de in te vullen parameters voor de update. Mag
null zijn.
         *
         *  @throws java.lang.IllegalArgumentException als platform is niet ZOS
of AIX
         *  @throws java.lang.IllegalArgumentException als queryID leeg is of null
         *  @throws nl.rabobank.cdw.exception.DatabaseDisabledException
         *                       als de gevraagde database volgens properties niet gebruikt dient
te worden.
         *  @throws SQLException bij andere database-problemen.
         */
        public static int update(String platform, String updateID, Object[]
parameters)
                        throws java.lang.IllegalArgumentException, DatabaseDisabledException,
                                SQLException, RaboDistributedException {

                String update = null;
                Connection con = null;
                PreparedStatement stmt = null;
                String database = mapPlatformToDatabase(platform);

                int recordCount;
                int i=0;

                //vind de query en zet een connection op
                update = SQLManager.getQueryByID(database, updateID);

                try {
                        con = DBManager.getConnection(database);
                }
                catch (Exception e) {
                        if (log.isErrorEnabled()) {
                                log.error(staticToString() + StringUtilities.getTrace(e));
                        }
                        throw new SQLException("Could not get connection to database: " +
platform + ":" + database);
                }

                try {
                        stmt = con.prepareStatement(update);
                }
                catch (Exception e) {
                        if (log.isErrorEnabled()) {
                                log.error(staticToString() + StringUtilities.getTrace(e));
                        }
                        throw new SQLException("Could not create preparedStatement for query: "
+ platform + ":" + update);
                }

                if (log.isDebugEnabled()) {
                        log.debug("==========================================================");
                        log.debug(DBManager.logString + " - query()");
                        log.debug("Query = " + update);
                }

                //vul het prepared statement met alle parameters:
                for (i = 0; i < parameters.length; i++) {

                        Object param = parameters[i];

                        if (param instanceof String) {
                                stmt.setString(i + 1, (String) param);
                        }

                        if (param instanceof Short) {
                                stmt.setShort(i + 1, ((Short)param).shortValue());
                        }

                        if (param instanceof Integer) {
                                stmt.setInt(i + 1, ((Integer) param).intValue());
                        }

                        if (param instanceof Long) {
                                stmt.setLong(i + 1, ((Long) param).longValue());
                        }

                        if (param instanceof Date) {
                                stmt.setTimestamp(i + 1, new java.sql.Timestamp(((Date)
param).getTime()));
                        }

                        if (log.isDebugEnabled()) {
                                log.debug(DBManager.logString + " Param " + i + " = " +
param.toString());
                        }
                }


                if (log.isDebugEnabled()) {
                        log.debug("==========================================================");
                }

                //voer uit en retourneer het resultaat
                try {
                        recordCount = stmt.executeUpdate();
                }
                catch (Exception e) {
                        if (log.isErrorEnabled()) {
                                log.error(staticToString() + StringUtilities.getTrace(e));
                        }
                        throw new SQLException("Error while executing preparedStatement for
query: " + platform + ":" + update);
                }
                finally {
                        try {
                                closeConnection(stmt, con);
                        }
                        catch (Exception e) {
                                if (log.isErrorEnabled()) {
                                        log.error(staticToString() + StringUtilities.getTrace(e));
                                }
                        }
                }

                return recordCount;
        }

        /** @return String een indicatie van welke database gebruikt wordt bij
gegeven platform.
         *   Dit is OF de waarde van OracleDAOFactory.DAO_APP_KEY, DANWEL de
waarde van IBMDAOFactory.DAO_APP_KEY.
         * @throws nl.rabobank.cdw.exception.DatabaseDisabledException
         *                       als de gevraagde database volgens properties niet gebruikt dient
te worden.
         *  @throws IllegalArgumentException als platform is niet ZOS of AIX
         */
        private static String mapPlatformToDatabase(String platform)
                throws DatabaseDisabledException, IllegalArgumentException {
                boolean dbEnabledDB2 = false;
                boolean dbEnabledOracle = false;
                String database = null;
                //mogen we databases gebruiken?
                try {
                        String dbEnabled = getProperty(MAIN_APP_KEY, DB_ENABLED_KEY);
                        dbEnabledDB2 = "true".equals(dbEnabled) &&
"true".equals(getProperty(MAIN_APP_KEY, DB2_ENABLED_KEY));
                        dbEnabledOracle = "true".equals(dbEnabled) &&
"true".equals(getProperty(MAIN_APP_KEY, ORACLE_ENABLED_KEY));
                }
                catch (RaboDistributedException e) {
                        log.error(DAOFactory.toTextString() + " error resolving database keys,
using default stub implementation");
                        throw new DatabaseDisabledException("error resolving database keys,
using default stub implementation");
                }
                //bepaal welke database je wilt gebruiken, en of dat mag volgens de
settings:
                //AIX
                if (PlatFormContext.AIX.equals(platform)) { // AIX, dus Oracle !
                        if (dbEnabledOracle) {
                                database = OracleDAOFactory.DAO_APP_KEY;
                        }
                        else { // settings willen dat je geen database gebruikt, meldt dit terug:
                                throw new DatabaseDisabledException("Oracle wordt niet gebruikt
volgens settings");
                        }
                        //ZOS
                }
                else
                        if (PlatFormContext.ZOS.equals(platform)) { //ZOS, dus DB2 !
                                if (dbEnabledDB2) {
                                        database = IBMDAOFactory.DAO_APP_KEY;
                                }
                                else { // settings willen dat je geen database gebruikt, meldt dit terug:
                                        throw new DatabaseDisabledException("DB2 wordt niet gebruikt volgens
settings");
                                }
                        }
                        else { //onbekend platform !!
                                throw new java.lang.IllegalArgumentException("parameter platform
should be ZOS of AIX");
                        }
                return database;
        }
}

