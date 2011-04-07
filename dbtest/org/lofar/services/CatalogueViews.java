package org.lofar.services;

import java.sql.*;

/**
 * This class creates view on all the catalogues in the lofar database.
 */
public class CatalogueViews {
	
	/**
	 * Array of catalogues in use
	 */
	private static final String[] catalogues = {"wenss", "nvss", "vlss", "lofar"};
 
	public static void createViews(double raMin, double raMax, double decMin, double decMax) {
		for (int i = 0; i < getCatalogues().length; i++) {
			createView(getCatalogueTables()[i], getCatalogueViews()[i], raMin, raMax, decMin, decMax);
		}
	}
	
	public static void dropViews() {
                for (int i = 0; i < getCatalogues().length; i++) {
                        dropView(getCatalogueViews()[i]);
                }
	}

	private static String[] getCatalogues() {
		return catalogues;
	}

	public static String[] getCatalogueTables() {
		String[] catalogueTables = new String[catalogues.length];
		for (int i = 0; i < catalogues.length; i++) {
			catalogueTables[i] = catalogues[i] + "cat";
		}
		return catalogueTables;
	}

	public static String[] getCatalogueViews() {
		String[] catalogueViews = new String[catalogues.length];
		for (int i = 0; i < catalogues.length; i++) {
			catalogueViews[i] = catalogues[i] + "catview";
		}
		return catalogueViews;
	}

	private static void createView(String table, String view
					, double raMin, double raMax, double decMin, double decMax) {

		StringBuffer createNewView = new StringBuffer();
		try {
			Class.forName("com.mysql.jdbc.Driver");
	                Connection con = DriverManager.getConnection("jdbc:mysql://acamar.science.uva.nl:3306/lofar?user=lofar&password=cs1");
        	        Statement st = con.createStatement();
			createNewView.append(	"CREATE VIEW " + view + 
						" AS SELECT * FROM " + table + 
						" WHERE RA BETWEEN " + raMin + " AND " + raMax +
						"   AND DECL BETWEEN " + decMin + " AND " + decMax + ";");
			st.executeUpdate(createNewView.toString());
		} catch (SQLException e) {
			System.err.println(e.getMessage());
			System.exit(1);
		} catch (ClassNotFoundException e) {
			System.err.println(e.getMessage());
			System.exit(1);
		} finally {
			System.out.println("View: " + view + " created succesfully.");
		}
        }

	private static void dropView(String view) {

                StringBuffer dropView = new StringBuffer();
                try {
                	Class.forName("com.mysql.jdbc.Driver");
	                Connection con = DriverManager.getConnection("jdbc:mysql://acamar.science.uva.nl:3306/lofar?user=lofar&password=cs1");
        	        Statement st = con.createStatement();
                        dropView.append("DROP VIEW " + view + ";");
                        st.executeUpdate(dropView.toString());
                } catch (SQLException e) {
                        System.err.println(e.getMessage());
                        System.exit(1);
                } catch (ClassNotFoundException e) {
                        System.err.println(e.getMessage());
                        System.exit(1);
                } finally {
			System.out.println("View: " + view + " dropped succesfully.");
		}
        }

}
