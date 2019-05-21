import java.io.*;
import java.util.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.*;
import javax.swing.*;


class FieldReader {
  // next_field Returns:
  //   Non-Empty String: trimmed next field string if it exists in this line
  //   Empty String: "" is returned for each end of line
  //   null: end of file or error
  
  BufferedReader r = null;
  String line = null;
  
  FieldReader ( BufferedReader f ) {
    r = f;
  }

	String next_field () {
	  String field = null;
	  if (line == null) {
	    // The line buffer needs to be refreshed
	    try {
	    	// Read in a line and replace tabs with spaces and trim spaces afterward
  	    line = r.readLine().replace('\t',' ').trim();
	    } catch ( Exception e ) {
	      return ( null );
	    }
	  }
	  if (line.equals("")) {
	    // The trim function returned an empty string so report this as an end of line
	    line = null;
	    return ( "" );
	  }
	  
	  // The String is not null so separate off the first non-blank field
	  // Check for a blank or tab
	  int blank = line.indexOf ( ' ' );
	    
	  if (blank >= 0) {
	    // Found a blank (or tab converted to blank)
	    field = line.substring(0,blank).trim();
	    line = line.substring(blank).trim();
	  } else {
	    // No blank found at all
	    field = line.trim();
	    line = "";
	  }
	  return ( field );
	}	
}



abstract class data_file {

	public abstract double f ( double x );
	public abstract void find_x_range();
	public abstract void find_y_range();
	
	public boolean valid_data = false;

	String name = "Identity";
	Color color = Color.red;
	boolean continuous = true;
	int num_samples = -1;     // Use -1 to indicate that there are no samples
	double samples[] = null;

  public double min_x = Double.NaN;
  public double max_x = Double.NaN;

  public double min_y = Double.NaN;
  public double max_y = Double.NaN;

	public void setName(String s) {
		name = s;
	}
	public String getName() {
		return name;
	}
	public void setColor ( Color c ) {
		color = c;
	}

  public int buffer_size = 2000000000;

	public BufferedReader get_reader ( String file_name ) {
    BufferedReader br = null;
    try {
      if (buffer_size > 0) {
        try {
          br = new BufferedReader(new InputStreamReader(new FileInputStream(file_name)),buffer_size);
        } catch ( Error er ) {
          System.out.println ( "Unable to allocate " + buffer_size + " bytes of memory, attempting smaller allocation" );
    		  br = new BufferedReader(new InputStreamReader(new FileInputStream(file_name)));
        } catch ( Exception e ) {
          System.out.println ( "Unable to allocate " + buffer_size + " bytes of memory, attempting smaller allocation" );
    		  br = new BufferedReader(new InputStreamReader(new FileInputStream(file_name)));
        }
		  } else {
		    br = new BufferedReader(new InputStreamReader(new FileInputStream(file_name)));
		  }
		} catch ( Exception e ) {
		}
		return ( br );
	}

  static int next_color = 0;
  static int color_list[][] = {
    { 255,   0,   0 },
    {   0, 255,   0 },
    {   0,   0, 255 },
    { 255, 255,   0 },
    { 255,   0, 255 },
    {   0, 255, 255 },
    { 255, 255, 255 },
    { 150,   0,   0 },
    {   0, 150,   0 },
    {   0,   0, 150 },
    { 150, 150,   0 },
    { 150,   0, 150 },
    {   0, 150, 150 },
    { 150, 150, 150 }
  };

  public static Color get_next_color() {
		if (next_color >= color_list.length) {
		  next_color = 0;
		}
		int r = color_list[next_color][0];
		int g = color_list[next_color][1];
		int b = color_list[next_color][2];
		next_color += 1;
		return ( new Color(r,g,b) );
  }

  public static Color get_next_computed_color() {
  	do {
    	next_color += 1;
   	} while ( (next_color % 8) == 0 );
		int r = 255 * ((next_color >> 0) % 2);
		int g = 255 * ((next_color >> 1) % 2);
		int b = 255 * ((next_color >> 2) % 2);
		return ( new Color(r,g,b) );
  }

}


class file_x extends data_file {
  // This is a series of impulses or event times
  double eps = 0.1;
  double x_values[] = null;
  public file_x ( String file_name, double epsilon ) {
    eps = epsilon;
    // Read the values
    name = "File=\"" + file_name + "\"";
    int num_values = 0;
    for (int pass=0; pass<=1; pass++) {
      num_values = 0;
		  try {
		    BufferedReader br = get_reader ( file_name );
			  FieldReader fr = new FieldReader ( br );
			  String xfield = null;
			  do {
				  xfield = fr.next_field();
  				if ( (xfield != null) && (xfield.length() > 0) ) {
  				  double x_val = new Double(xfield);
  				  if (pass > 0) {
  				    x_values[num_values] = x_val;
  				  }
  				  num_values += 1;
				  }
			  } while ( xfield != null );
		  } catch (Exception e) {
		  }
		  if ( (pass == 0) && (num_values > 0) ) {
		    x_values = new double[num_values];
		  }
		}
		// Print the values (debugging)
		for (int i=0; i<x_values.length; i++) {
		  System.out.println ( "x[" + i + "] = " + x_values[i] );
		}
  }
	public void find_x_range() {
	}
	public void find_y_range() {
	}
	public double f ( double x ) {
	  return Double.NaN;
	}
}


class file_y extends data_file {
  // This is an evenly sampled function
  double x0 = 0;
  double dx = 1;
  double y_values[] = null;
  public file_y ( String file_name, double start_x, double delta_x ) {
    x0 = start_x;
    dx = delta_x;
    // Read the values
    name = "File=\"" + file_name + "\"";
    int num_values = 0;
    for (int pass=0; pass<=1; pass++) {
      num_values = 0;
		  try {
		    BufferedReader br = get_reader ( file_name );
			  FieldReader fr = new FieldReader ( br );
			  String yfield = null;
			  do {
				  yfield = fr.next_field();
  				if ( (yfield != null) && (yfield.length() > 0) ) {
  				  double y_val = new Double(yfield);
  				  if (pass > 0) {
  				    y_values[num_values] = y_val;
  				  }
  				  num_values += 1;
				  }
			  } while ( yfield != null );
		  } catch (Exception e) {
		  }
		  if ( (pass == 0) && (num_values > 0) ) {
		    y_values = new double[num_values];
		  }
		}
		// Print the values (debugging)
		for (int i=0; i<y_values.length; i++) {
		  //System.out.println ( "x=" + (x0+(i*dx)) + ", y=" + y_values[i] );
		}
		// Test the interpolation (debugging)
		for (int i=0; i<(3*y_values.length); i++) {
		  double test_x = (x0+(i*dx/3));
		  //System.out.println ( "x=" + test_x + ", y=" + f(test_x) + " ... should be close to " + y_values[i/3] );
		}
  }
	public void find_x_range() {
	}
	public void find_y_range() {
	}
	public double f ( double x ) {
	  if (y_values == null) {
	    return Double.NaN;
	  } else {
	    if (x < x0) {
	      // Requested x value is below the low end of the values
	      return ( Double.NaN );
	    } else if (x > x0+(dx * (y_values.length-1))) {
	      // Requested x value is beyond the high end of the values
	      return ( Double.NaN );
	    } else {
	      // Calculate the pair of values for interpolation
	      int lower_index = (int)((x-x0)/dx);
	      double remainder = ((x-x0)/dx) - lower_index;
	      // Interpolate between lower_index and lower_index+1
	      // System.out.println ( "  lower_index = " + lower_index + ", remainder = " + remainder + ", dx = " + dx );
	      return ( y_values[lower_index] + ( remainder * ( (y_values[lower_index+1]-y_values[lower_index]) /* / dx */ ) ) );
	    }
	  }
	}
}


class file_xy extends data_file {
  // This is a set of arbitrary (x,y) pairs
  double x_values[] = null;
  double y_values[] = null;
  double average_delta = Double.NaN;
  
  public file_xy ( String data_name, double x[], double y[] ) {
    name = "Data=\"" + data_name + "\"";
    int num_values = x.length;
    if (y.length < num_values) num_values = y.length;
	  x_values = new double[num_values];
	  y_values = new double[num_values];
    for (int i=0; i<num_values; i++) {
		  x_values[i] = x[i];
		  y_values[i] = y[i];
    }
  }

  /*
  public double[][] append_block ( double[][] blocks, double[] block, int num_blocks ) {
    double[][] new_blocks = new double[num_blocks+1][];
    for (int b=0; b<num_blocks; b++) {
      System.out.println ( "Copying block " + b );
      new_blocks[b] = blocks[b];
    }
    new_blocks[num_blocks] = block;
    return new_blocks;
  }
  */

  public double[][] append_block ( double[][] blocks, double[] block ) {
    int base_len = 0;
    if (blocks == null) {
      base_len = 0;
    } else {
      base_len = blocks.length;
    }
    double[][] new_blocks = new double[base_len+1][];
    if (blocks != null) {
      for (int b=0; b<base_len; b++) {
        // System.out.println ( "Copying block " + b );
        new_blocks[b] = blocks[b];
      }
    }
    new_blocks[base_len] = block;
    return new_blocks;
  }



  public file_xy ( String file_name ) {

    double[][] blocks = null;
    int blocksize = 100000*2; // Must be an EVEN number to save on checking!!!
    double[] block = null;
    int num_blocks = 0;
    int blockindex = 0;
    int total_values = 0;
    int num_values = 0;

    name = "File=\"" + file_name + "\"";

    try {
      BufferedReader in = new BufferedReader(new FileReader(file_name));
      String s;
      while ( (s = in.readLine()) != null ) {
        String ss[] = s.split(" ");
        for (int i=0; i<ss.length; i++) {
          if (block == null) {
            block = new double[blocksize];
            blockindex = 0;
          }
          block[blockindex] = Double.parseDouble(ss[i]);
          blockindex += 1;
          if (blockindex >= blocksize) {
            blocks = append_block ( blocks, block );
            num_blocks += 1;
            block = new double[blocksize];
            blockindex = 0;
          }
          total_values += 1;
        }
      }

      if (blockindex != 0) {
        // This indicates that there's a partially filled block that needs to be added to the blocks array
        blocks = append_block ( blocks, block );
        num_blocks += 1;
      }

      System.out.println ( "Read " + total_values + " values into " + num_blocks + " blocks" );

      // Allocate and copy from the blocks into the arrays

      num_values = total_values / 2;

      x_values = new double[num_values];
      y_values = new double[num_values];

      int blocknum = 0;
      blockindex = 0;
      for (int i=0; i<num_values; i++) {
        x_values[i] = blocks[blocknum][blockindex++];
        y_values[i] = blocks[blocknum][blockindex++];
        // System.out.println ( "Assigned " + x_values[i] + ", " + y_values[i] );
        if (blockindex >= blocksize) {
          blocknum += 1;
          blockindex = 0;
        }
	    }


	  } catch ( IOException ie ) {
	    System.out.println ( "Error reading file " + file_name );
	    ie.printStackTrace();
	  } catch ( Exception e ) {
	    System.out.println ( "Exception reading file " + file_name + ": " + e );
	    e.printStackTrace();
    }


    /* Uncomment for debugging
    try {
      PrintStream dumpfile = new PrintStream ( file_name + ".dump.txt" );
      for (int i=0; i<num_values; i++) {
        dumpfile.println ( x_values[i] + " " + y_values[i] );
      }
      dumpfile.flush();
      dumpfile.close();
    } catch ( Exception xx ) {
    }
    */


    /* Old Vector code ... was slooooow

    Vector blocks = new Vector();
    int blocksize = 200*200; // Must be an EVEN number to save on checking!!!
    double block[] = null;
    int blockindex = 0;
    int total_values = 0;
    try {
      BufferedReader in = new BufferedReader(new FileReader(file_name));
      String s;
      while ( (s = in.readLine()) != null ) {
        String ss[] = s.split(" ");
        for (int i=0; i<ss.length; i++) {
          if (block == null) {
            block = new double[blocksize];
            blockindex = 0;
          }
          block[blockindex++] = Double.parseDouble(ss[i]);
          if (blockindex >= blocksize) {
            blocks.addElement ( block );
            block = new double[blocksize];
          }
          total_values += 1;
        }
      }
      System.out.println ( "Read " + total_values + " values" );

      // Allocate and copy from the blocks into the arrays

      int num_values = total_values / 2;

      x_values = new double[num_values];
      y_values = new double[num_values];

      int blocknum = 0;
      blockindex = 0;
      try {
        System.out.println ( "Try reading from the blocks vector" );
        block = (double[])blocks.elementAt(blockindex);
      } catch ( Exception eee ) {
        System.out.println ( "Error reading block from Vector: " + eee );
      }
      for (int i=0; i<num_values; i++) {
        x_values[i] = (double)(i);
        y_values[i] = (double)(i*i);
	    }
	  } catch ( IOException e ) {
	    System.out.println ( "Error reading file " + file_name );
    }


    // New one pass code uses a Vector:
    Vector values = new Vector();
    // Read the values
    name = "File=\"" + file_name + "\"";
    int num_values = 0;
	  try {
	    BufferedReader br = get_reader ( file_name );
		  FieldReader fr = new FieldReader ( br );
		  String xfield = null;
		  String yfield = null;
		  do {
			  xfield = fr.next_field();
			  if ( (xfield != null) && (xfield.length() > 0) ) {
  				yfield = fr.next_field();
  				if ( (yfield != null) && (yfield.length() > 0) ) {
  				  values.addElement ( new Double(xfield) );
  				  values.addElement ( new Double(yfield) );
  				  num_values += 1;
  				}
			  }
		  } while ( (xfield != null) && (yfield != null) );
	  } catch (Exception e) {
	    System.out.println ( "Error reading from file: " + file_name );
	    valid_data = false;
	    return;
	  }

    // Allocate and copy from the vector into the array
    x_values = new double[num_values];
    y_values = new double[num_values];
    for (int i=0; i<num_values; i++) {
      x_values[i] = (Double)(values.elementAt(2*i));
      y_values[i] = (Double)(values.elementAt((2*i)+1));
	  }
    */

    /* Old two pass code reads twice to use an array:
    // Read the values
    name = "File=\"" + file_name + "\"";
    int num_values = 0;
    for (int pass=0; pass<=1; pass++) {
      num_values = 0;
		  try {
		    BufferedReader br = get_reader ( file_name );
			  FieldReader fr = new FieldReader ( br );
			  String xfield = null;
			  String yfield = null;
			  do {
				  xfield = fr.next_field();
				  if ( (xfield != null) && (xfield.length() > 0) ) {
    				yfield = fr.next_field();
    				if ( (yfield != null) && (yfield.length() > 0) ) {
    				  double x_val = new Double(xfield);
    				  double y_val = new Double(yfield);
    				  // System.out.println ( "Read " + x_val + "," + y_val );
    				  if (pass > 0) {
    				    x_values[num_values] = x_val;
    				    y_values[num_values] = y_val;
    				  }
    				  num_values += 1;
    				}
				  }
			  } while ( (xfield != null) && (yfield != null) );
		  } catch (Exception e) {
		    System.out.println ( "Error reading from file: " + file_name );
		    valid_data = false;
		    return;
		  }
		  if ( (pass == 0) && (num_values > 0) ) {
		    x_values = new double[num_values];
		    y_values = new double[num_values];
		  }
		}
		*/


    // Check to see if the file is already sorted to save time
		boolean sorted = true;
		for (int i=1; i<x_values.length; i++) {
		  if (x_values[i-1] > x_values[i]) {
		    sorted = false;
		    break;
		  }
		}

		if (!sorted) {
		  // Sort the values by x for faster searching and interpolation later
		  // Should use a faster sorting algorithm, but this works for now
		  System.out.println ( "Sorting values ..." );
		  for (int i=0; i<x_values.length; i++) {
		    double temp;
		    for (int j=i; j<x_values.length; j++) {
		      if (x_values[i] > x_values[j]) {
		        // Swap them
		        temp = x_values[i];
		        x_values[i] = x_values[j];
		        x_values[j] = temp;
		        temp = y_values[i];
		        y_values[i] = y_values[j];
		        y_values[j] = temp;
		      }
		    }
		  }
		}
    // Check for duplicate x values
    boolean has_unique_x_values = true;
		for (int i=1; i<x_values.length; i++) {
		  if (x_values[i-1] == x_values[i]) {
		    has_unique_x_values = false;
		    break;
		  }
		}
		if (!has_unique_x_values) {
		  // Average duplicate points
		  // Start by counting the number of unique x samples
		  double last_unique = x_values[0];
		  int num_unique = 1;
		  for (int i=1; i<x_values.length; i++) {
		    if (x_values[i] != last_unique) {
		      num_unique += 1;
		      last_unique = x_values[i];
		    }
		  }
		  // Allocate a new array of unique values
		  double unique_x_values[] = new double[num_unique];
		  double unique_y_values[] = new double[num_unique];
		  
		  // Eliminate the duplicate values
		  System.out.println ( "Array has " + x_values.length + " x values, but only " + num_unique + " are unique. Eliminating duplicate values ..." );
		  int unique_index = 0;
		  unique_x_values[unique_index] = x_values[0];
		  unique_y_values[unique_index] = y_values[0];
		  int num_summed = 1;
		  for (int i=1; i<x_values.length; i++) {
		    if (x_values[i] == unique_x_values[unique_index]) {
		      unique_y_values[unique_index] += y_values[i];
		      num_summed += 1;
		    } else {
		      unique_y_values[unique_index] = unique_y_values[unique_index] / num_summed;
		      unique_index += 1;
		      unique_x_values[unique_index] = x_values[i];
		      unique_y_values[unique_index] = y_values[i];
		      num_summed = 1;
		    }
		  }
		  if (num_summed != 1) {
        unique_y_values[num_unique-1] = unique_y_values[num_unique-1] / num_summed;
      }
      x_values = unique_x_values;
      y_values = unique_y_values;
		}

		// Check to see if the file is evenly sampled to save time
    
    double sum_of_deltas = 0;
    double max_delta = 0;
    double min_delta = 0;
    int num_to_check = x_values.length;
    /* TODO */ if (num_to_check > 100) num_to_check = 100;  // This is to avoid changes in delta due to precision problems in MCell output
		for (int i=1; i<num_to_check; i++) {
		  double delta = x_values[i] - x_values[i-1];
		  if ( (i==1) || (delta > max_delta) ) {
		    max_delta = delta;
		  }
		  if ( (i==1) || (delta < min_delta) ) {
		    min_delta = delta;
		  }
		  sum_of_deltas += delta;
		}
		if ( ( (max_delta-min_delta) / ((max_delta+min_delta)/2) ) < 0.001 ) {  // TODO This is an arbitrary value of 0.001
		  average_delta = sum_of_deltas / num_to_check;
		}
    System.out.println ( "   " + min_delta + " < delta < " + max_delta + ",  Average delta for first " + num_to_check + " = " + average_delta );

		// Print the values (debugging)
		//for (int i=0; i<x_values.length; i++) {
		//  System.out.println ( "x=" + x_values[i] + ", y=" + y_values[i] );
		//}
    valid_data = true;

	}

	public void find_x_range() {
		int num_values = x_values.length;
	  if (num_values > 0) {
	  	min_x = max_x = x_values[0];
	  }
    for (int i=0; i<num_values; i++) {
		  if (x_values[i] < min_x) min_x = x_values[i];
		  if (x_values[i] > max_x) max_x = x_values[i];
		}
	}
	public void find_y_range() {
		int num_values = y_values.length;
	  if (num_values > 0) {
	  	min_y = max_y = y_values[0];
	  }
    for (int i=0; i<num_values; i++) {
		  if (y_values[i] < min_y) min_y = y_values[i];
		  if (y_values[i] > max_y) max_y = y_values[i];
		}
	}
	public double f ( double x ) {
	  // Assume x values are sorted
	  if (x_values == null) {
	    return Double.NaN;
	  } else {
	    if (x < x_values[0]) {
	      return ( Double.NaN );
	      // return ( y_values[0] );
	    } else if (x > x_values[x_values.length-1]) {
	      return ( Double.NaN );
	      // return ( y_values[y_values.length-1] );
	    } else {
	      // Find and interpolate a data point
				if (Double.isNaN(average_delta)) {	      
	        // Perform a linear search from the beginning
	        for (int i=1; i<x_values.length; i++) {
	          if (x < x_values[i]) {
	            // Interpolate between i-1 and i
	            return ( y_values[i-1] + ( (x-x_values[i-1]) * ( (y_values[i]-y_values[i-1]) / (x_values[i]-x_values[i-1]) )  ) );
	          }
	        }
  	      return ( y_values[y_values.length-1] );
	      } else {
  	      // Perform a linear search from the estimated location
	        int guess_i = (int)((x - x_values[0]) / average_delta);
	        if (guess_i < 0) guess_i = 0;
	        if (guess_i >= x_values.length) guess_i = x_values.length-1;
//System.out.println ( "Searching from " + guess_i );
	        if (x == x_values[guess_i]) {
	          // Exact match ... not too likely unless x values are integer or power of 2
	          return ( y_values[guess_i] );
	        } else if (x > x_values[guess_i]) {
	          // x is greater than the guess so search up from guess
	          for (int i=guess_i+1; i<x_values.length; i++) {
	            if (x < x_values[i]) {
	              // Interpolate between i-1 and i
	              return ( y_values[i-1] + ( (x-x_values[i-1]) * ( (y_values[i]-y_values[i-1]) / (x_values[i]-x_values[i-1]) )  ) );
	            }
	          }
    	      return ( y_values[y_values.length-1] );
	        } else {
	          // x is less than the guess so search down from guess
	          for (int i=guess_i-1; i>=0; i--) {
	            if (x > x_values[i]) {
	              // Interpolate between i and i+1
	              return ( y_values[i] + ( (x-x_values[i]) * ( (y_values[i+1]-y_values[i]) / (x_values[i+1]-x_values[i]) )  ) );
	            }
	          }
    	      return ( y_values[0] );
	        }
	      }
	    }
	  }
	}

}


class data_file_set {
	//public abstract data_file_set();
	public data_file flist[] = new data_file[0];
  public double min_x = Double.NaN;
  public double max_x = Double.NaN;
  public double min_y = Double.NaN;
  public double max_y = Double.NaN;
	data_file add ( data_file f ) {
		// Add the data_file to the data_file list
		data_file fl[] = new data_file[flist.length+1];
		for (int i=0; i<flist.length; i++) {
			fl[i] = flist[i];
		}
		fl[flist.length] = f;
		flist = fl;
		return f;
	}
	public void find_x_range() {
		int num_files = flist.length;
		for (int i=0; i<num_files; i++) {
			flist[i].find_x_range();
		}
	  if (num_files > 0) {
	  	min_x = flist[0].min_x;
	  	max_x = flist[0].max_x;
	  }
    for (int i=0; i<num_files; i++) {
		  if (flist[i].min_x < min_x) min_x = flist[i].min_x;
		  if (flist[i].max_x > max_x) max_x = flist[i].max_x;
		}
	}
	public void find_y_range() {
		int num_files = flist.length;
		for (int i=0; i<num_files; i++) {
			flist[i].find_y_range();
		}
	  if (num_files > 0) {
	  	min_y = flist[0].min_y;
	  	max_y = flist[0].max_y;
	  }
    for (int i=0; i<num_files; i++) {
		  if (flist[i].min_y < min_y) min_y = flist[i].min_y;
		  if (flist[i].max_y > max_y) max_y = flist[i].max_y;
		}
	}
}



class DisplayPanel extends JPanel implements ActionListener,MouseListener,MouseWheelListener,MouseMotionListener,KeyListener, FilenameFilter {

	static final String S = File.separator;
	
	public boolean loading = false;

	String settings_file_name = "PlotData_settings.txt";
	String input_dir = "input";
	String output_dir = "output2";

	String base_path = ".";

  double x0 = 0;
  double x_scale = 1;
  
  String current_base_path = "";
  String current_file_name = "";

	JFrame frame=null;
	data_file_set func_set = null;

	public DisplayPanel() {
		setBorder(BorderFactory.createLineBorder(Color.black));
		setBackground ( new Color ( 0, 0, 0 ) );
		current_base_path = base_path;
		load_settings();
	}

	public void set_frame ( JFrame f ) {
		frame = f;
	}
	
	public void add_file ( data_file df ) {
	  boolean old_loading = loading;
	  loading = true;
	  repaint();
	  if (func_set == null) {
	    func_set = new data_file_set();
	  }
	  func_set.add ( df );
	  loading = old_loading;
	  repaint();
	}

	public void set_files ( String file_names[] ) {
		func_set = new data_file_set();
		if ( file_names != null ) {
			data_file fd;
			for (int i=0; i<file_names.length; i++) {
				fd = func_set.add ( new file_xy ( file_names[i] ) );
				int r = 255 * (((i+1) >> 0) % 2);
				int g = 255 * (((i+1) >> 1) % 2);
				int b = 255 * (((i+1) >> 2) % 2);
				fd.setColor ( new Color(r,g,b) );
			}
		}
	}
	
	public void save_and_exit() {
		save_settings();
		System.exit(0);
	}

	public void load_settings() {
		try {
			FieldReader fr = new FieldReader ( new BufferedReader(new InputStreamReader(new FileInputStream(settings_file_name))) );
			String field = null;
			do {
				field = fr.next_field();
				if ( (field != null) && (field.length() > 0) ) {
					// System.out.println ( "Field: " + field );
					if (field.equals("CurrentBasePath:")) {
						field = fr.next_field();
						if ( (field != null) && (field.length() > 0) ) {
							current_base_path = field;
							System.out.println ( "Setting base path to : " + current_base_path );
						}
					} else if (field.equals("InputFile:")) {
						field = fr.next_field();
						if ( (field != null) && (field.length() > 0) ) {
						  current_file_name = field;
							System.out.println ( "Setting input file to : " + field );
						}
					} else if (field.equals("InputDirName:")) {
						field = fr.next_field();
						if ( (field != null) && (field.length() > 0) ) {
							input_dir = field;
							System.out.println ( "Setting Input Directory to : " + input_dir );
						}
					} else if (field.equals("OutputDirName:")) {
						field = fr.next_field();
						if ( (field != null) && (field.length() > 0) ) {
							output_dir = field;
							System.out.println ( "Setting Output Directory to : " + output_dir );
						}
					} else if (field.equals("Scale:")) {
						field = fr.next_field();
						if ( (field != null) && (field.length() > 0) ) {
							x_scale = new Double(field);
							System.out.println ( "Setting Scale to : " + x_scale );
						}
					} else if (field.equals("Offset:")) {
						field = fr.next_field();
						if ( (field != null) && (field.length() > 0) ) {
							x0 = new Double(field);
							System.out.println ( "Setting Offset to : " + x0 );
						}
					} else if (field.equals("Annotation:")) {
						field = fr.next_field();
						if ( (field != null) && (field.length() > 0) ) {
							double annotation_level = new Double(field);
							System.out.println ( "Setting Annotation level to : " + annotation_level );
							if (annotation_level < 0.5) {
								annotation = false;
							} else {
								annotation = true;
							}
						}
					} else if (field.equals("Combined:")) {
						field = fr.next_field();
						if ( (field != null) && (field.length() > 0) ) {
							double combined_level = new Double(field);
							System.out.println ( "Setting Combined to : " + combined_level );
							if (combined_level < 0.5) {
								combined = false;
							} else {
								combined = true;
							}
						}
					} else if (field.equals("Variable_Y:")) {
						field = fr.next_field();
						if ( (field != null) && (field.length() > 0) ) {
							double var_level = new Double(field);
							System.out.println ( "Setting Variable Y to : " + var_level );
							if (var_level < 0.5) {
								var_y = false;
							} else {
								var_y = true;
							}
						}
					} else if (field.equals("WindowWidth:")) {
						field = fr.next_field();
						if ( (field != null) && (field.length() > 0) ) {
							int w = new Integer(field);
							System.out.println ( "Setting width to : " + w );
							pref_w = w;
						}
					} else if (field.equals("WindowHeight:")) {
						field = fr.next_field();
						if ( (field != null) && (field.length() > 0) ) {
							int h = new Integer(field);
							System.out.println ( "Setting height to : " + h );
							pref_h = h;
						}
					}
				}
			} while (field != null);

		} catch (FileNotFoundException fnfe) {
			// Could not read the settings file so create one with current program defaults
			save_settings();
		}
	}

	public void save_settings() {
		System.out.println ( "Saving persistent settings to: \"" + settings_file_name + "\"" );
		try {
			OutputStreamWriter o = new OutputStreamWriter ( new FileOutputStream ( settings_file_name ) );
			o.write ( "CurrentBasePath: " + current_base_path + "\n" );
			o.write ( "InputFile: " + current_file_name + "\n" );
			o.write ( "Scale: " + x_scale + "\n" );
			o.write ( "Offset: " + x0 + "\n" );
			if (annotation) {
				o.write ( "Annotation: 1.0\n" );
			} else {
				o.write ( "Annotation: 0.0\n" );
			}
			if (combined) {
				o.write ( "Combined: 1.0\n" );
			} else {
				o.write ( "Combined: 0.0\n" );
			}
			if (var_y) {
				o.write ( "Variable_Y: 1.0\n" );
			} else {
				o.write ( "Variable_Y: 0.0\n" );
			}
			Rectangle r = getBounds();
			o.write ( "WindowWidth: " + r.width + "\n" );
			o.write ( "WindowHeight: " + r.height + "\n" );
			//o.write ( "InputDirName: " + input_dir + "\n" );
			//o.write ( "OutputDirName: " + output_dir + "\n" );
			o.close();
		} catch (Exception e) {
			System.out.println ( "Unable to create a new settings file: \"" + settings_file_name + "\" to store persistent settings." );
		}
	}

	public Dimension getPreferredSize() {
		return new Dimension(pref_w,pref_h);
	}

  int pref_w=1200, pref_h=600;
  boolean combined = true;
  boolean var_y = false;
	boolean annotation = true;
	boolean fit_x = false;
	boolean antialias = false;
	
	JMenu remove_menu = null;
	
	public JMenuBar build_menu_bar() {
    JMenuItem mi;
    ButtonGroup bg;
    JMenuBar menu_bar = new JMenuBar();
	    JMenu file_menu = new JMenu("File");
	    	file_menu.add ( mi = new JMenuItem("Add") );
	    	mi.addActionListener(this);
	    	file_menu.add ( mi = new JMenuItem("Clear") );
	    	mi.addActionListener(this);
	    	file_menu.addSeparator();
	    	file_menu.add ( mi = new JMenuItem("Exit") );
	    	mi.addActionListener(this);
	    	// file_menu.add ( mi = remove_menu = new JMenu("Remove") );
	    	// mi.addActionListener(this);
	    	menu_bar.add ( file_menu );
			JMenu set_menu = new JMenu("Show");
		  	set_menu.add ( mi = new JMenuItem("Full Range") );
		  	mi.addActionListener(this);
		  	set_menu.add ( mi = new JCheckBoxMenuItem("Combined",combined) );
		  	mi.addActionListener(this);
		  	set_menu.add ( mi = new JCheckBoxMenuItem("Variable Y",var_y) );
		  	mi.addActionListener(this);
		  	set_menu.add ( mi = new JCheckBoxMenuItem("Annotation",annotation) );
		  	mi.addActionListener(this);
		  	set_menu.add ( mi = new JCheckBoxMenuItem("Antialiasing",antialias) );
		  	mi.addActionListener(this);
		  	menu_bar.add ( set_menu );
	   return (menu_bar);
	}

	FileDialog fd = null;
	String fd_file_types = ".hst";

	public boolean accept(File dir, String name) {
		if ( name.endsWith ( fd_file_types ) ) {
			return true;
		} else {
			return false;
		}
	}


	public void actionPerformed(ActionEvent e) {
		String cmd = e.getActionCommand();
		// System.out.println ( "ActionPerformed got \"" + cmd + "\"" );
		
		if (cmd.equalsIgnoreCase("Exit")) {
			save_and_exit();
		} else if (cmd.equalsIgnoreCase("Add")) {
			System.out.println ( "Adding a file" );

			// fd_file_types = ".txt";
			// String current_base_path = ".";
			// Change to a new base folder
			// gdata.println ( 50, "Opening new file ..." );
			//String old_path = current_base_path;
			
			if (fd == null) {
				fd = new FileDialog ( frame, "Choose a file" );
			}
			fd.setTitle ( "Open a Reaction File" );
			// fd.setFilenameFilter ( this );
			fd.setMode ( FileDialog.LOAD );
			//if (gdata.histogram_tags_file_name != null) {
			//	fd.setFile ( gdata.histogram_file_name );
			//} else {
			//	fd.setFile ( "*" + fd_file_types );
			//}
			//fd.show();
			fd.setVisible(true);
			fd.toFront();
			
			if (fd.getFile() != null) {
				String file_name = null;
				if (fd.getDirectory() != null) {
					file_name = fd.getDirectory() + fd.getFile();
				} else {
					file_name = fd.getFile();
				}
				System.out.println ( "Reading data from " + file_name );
        file_xy fxy = new file_xy ( file_name );
        fxy.setColor ( data_file.get_next_color() );
        add_file ( fxy );
				//gdata.read_hist_file();
			}
			//gdata.display_histogram = true;
			
		} else if (cmd.equalsIgnoreCase("Clear")) {
      set_files ( null );
		} else if (cmd.equalsIgnoreCase("Combined")) {
			JCheckBoxMenuItem mi = (JCheckBoxMenuItem)(e.getSource());
			if (mi.isSelected()) {
				System.out.println ( "Combining Plots" );
				combined = true;
			} else {
				System.out.println ( "Separate Plots" );
				combined = false;
			}
		} else if (cmd.equalsIgnoreCase("Variable Y")) {
			JCheckBoxMenuItem mi = (JCheckBoxMenuItem)(e.getSource());
			if (mi.isSelected()) {
				System.out.println ( "Variable Y Scaling" );
				var_y = true;
			} else {
				System.out.println ( "Fixed Y Scaling" );
				var_y = false;
			}
		} else if (cmd.equalsIgnoreCase("Annotation")) {
			JCheckBoxMenuItem mi = (JCheckBoxMenuItem)(e.getSource());
			if (mi.isSelected()) {
				System.out.println ( "Annotation On" );
				annotation = true;
			} else {
				System.out.println ( "Annotation Off" );
				annotation = false;
			}
		} else if (cmd.equalsIgnoreCase("Antialiasing")) {
			JCheckBoxMenuItem mi = (JCheckBoxMenuItem)(e.getSource());
			if (mi.isSelected()) {
				System.out.println ( "Antialiasing On" );
				antialias = true;
			} else {
				System.out.println ( "Antialiasing Off" );
				antialias = false;
			}
		} else if (cmd.equalsIgnoreCase("Full Range")) {
			fit_x = true;
		}

		repaint();
	}


  int move_direction = 1;
  public void keyTyped ( KeyEvent e ) {
  	System.out.println ( "Key: " + e );
  	if (Character.toUpperCase(e.getKeyChar()) == 'N') {
  		// Move to the next
  		move_direction = 1;
		} else if (Character.toUpperCase(e.getKeyChar()) == 'P') {
			// Move to the previous
  		move_direction = -1;
		}
  	repaint();
  }
  public void keyPressed ( KeyEvent e ) {
  	// System.out.println ( "Key Pressed" );
  }
  public void keyReleased ( KeyEvent e ) {
  	// System.out.println ( "Key Released" );
  }


	public void paintComponent(Graphics g) {

		super.paintComponent(g);

    if (antialias) {
      /*
      Hint Key Values
      Antialiasing                   KEY_ANTIALIASING        [ VALUE_ANTIALIAS_ON VALUE_ANTIALIAS_OFF VALUE_ANTIALIAS_DEFAULT ]
      Alpha Interpolation            KEY_ALPHA_INTERPOLATION [ VALUE_ALPHA_INTERPOLATION_QUALITY VALUE_ALPHA_INTERPOLATION_SPEED VALUE_ALPHA_INTERPOLATION_DEFAULT ]
      Color Rendering                KEY_COLOR_RENDERING     [ VALUE_COLOR_RENDER_QUALITY VALUE_COLOR_RENDER_SPEED VALUE_COLOR_RENDER_DEFAULT ]
      Dithering                      KEY_DITHERING           [ VALUE_DITHER_DISABLE VALUE_DITHER_ENABLE VALUE_DITHER_DEFAULT ]
      Fractional Text Metrics        KEY_FRACTIONALMETRICS   [ VALUE_FRACTIONALMETRICS_ON VALUE_FRACTIONALMETRICS_OFF VALUE_FRACTIONALMETRICS_DEFAULT ]
      Image Interpolation            KEY_INTERPOLATION       [ VALUE_INTERPOLATION_BICUBIC VALUE_INTERPOLATION_BILINEAR VALUE_INTERPOLATION_NEAREST_NEIGHBOR ]
      Rendering                      KEY_RENDERING           [ VALUE_RENDER_QUALITY VALUE_RENDER_SPEED VALUE_RENDER_DEFAULT ]
      Stroke Normalization Control   KEY_STROKE_CONTROL      [ VALUE_STROKE_NORMALIZE VALUE_STROKE_DEFAULT VALUE_STROKE_PURE ]
      Text Antialiasing              KEY_TEXT_ANTIALIASING   [ VALUE_TEXT_ANTIALIAS_ON VALUE_TEXT_ANTIALIAS_OFF VALUE_TEXT_ANTIALIAS_DEFAULT VALUE_TEXT_ANTIALIAS_GASP VALUE_TEXT_ANTIALIAS_LCD_HRGB VALUE_TEXT_ANTIALIAS_LCD_HBGR VALUE_TEXT_ANTIALIAS_LCD_VRGB VALUE_TEXT_ANTIALIAS_LCD_VBGR ]
      LCD Text Contrast              KEY_TEXT_LCD_CONTRAST   [ Values should be a positive integer in the range 100 to 250. ]    
      */
      Graphics2D g2d = (Graphics2D) g;
      g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
      g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
      g2d.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
      g = g2d;
    }

		int win_w, win_h, w, h, time_h;
		win_w = getSize().width;
		win_h = getSize().height;
		
		if (loading) {
		  Font cur_font = g.getFont();
		  g.setFont ( new Font("SansSerif", Font.BOLD, 50) );
      g.setColor ( Color.white );
	  	g.drawString ( "Loading...", 70, 100 );
	  	g.setFont ( cur_font );
    }		

	  // Draw the normal spike pattern showing all channels
	  if (func_set == null) {
	  	return;
	  }
	  
	  data_file f[] = func_set.flist;

  	int num_panels = f.length;
  	if (num_panels == 0) {
  	  return;
  	}
  	if (fit_x) {
      System.out.println ( "Scale = " + x_scale );
			if ( (func_set != null) && (func_set.flist.length > 0) ) {
				func_set.find_x_range();
				func_set.find_y_range();
		    x0 = func_set.min_x;
			  x_scale = win_w/(func_set.max_x-func_set.min_x);
			  // Reset zoom = 1.0;

        System.out.println ( "Scale = " + x_scale + " = " + win_w + "/ ( " + func_set.max_x + " - " + func_set.min_x + " )" );
			}
			fit_x = false;
		}


	  // Draw the time lines and time annotations

	  time_h = 20; // Height of the window to reserve for the time marking area

	  w = win_w;
	  if (combined) {
	    h = (win_h-time_h);
	  } else {
  	  h = (win_h-time_h)/num_panels;
  	}
	
	  // Time relationship between time and x is:
	  // x = (int)(( input_spike_times[i][j] - x0 ) * x_scale);
	  //  so...
	  // t = ( x / x_scale ) + x0
	  // tleft = ( x / x_scale ) + x0
	  // tright = ( (x+w) / x_scale ) + x0
	  // tright - tleft = [ ( (x+w) / x_scale ) + x0 ]  -  [ ( x / x_scale ) + x0 ]
	  //                = ( (x+w) / x_scale ) + x0  - ( x / x_scale ) - x0
	  //                = ( (x+w) / x_scale ) - ( x / x_scale )
	  //                = ( x + w - x ) / x_scale
	  //                =  w / x_scale
	
	  double window_time_extent = w / x_scale;
	  // System.out.println ( "Time extent = " + window_time_extent );
	
	  int nominal_pixels_per_division = 100;
	  int nominal_divisions_per_window = (win_w + (nominal_pixels_per_division/2)) / nominal_pixels_per_division;
	  double nominal_time_per_division = window_time_extent / nominal_divisions_per_window;
	
	  // We generally want our divisions to be 1's, 2's, or 5's  (eg every .01, or every .02, or every .05, or every .1 ...)
	
	  // First normalize the value between 1 and 10
	  int factors_of_10 = 0;
	  double tpd = nominal_time_per_division;
	  while (tpd > 1) {
		  tpd = tpd / 10;
		  factors_of_10 ++;
	  }
	  while (tpd < 1) {
		  tpd = tpd * 10;
		  factors_of_10 --;
	  }
	  // Now we have tpd as a floating value >= 1 and less than 10 so make some decisions
	  double tpdi = 0;
	  if (tpd < 1.5) {
		  tpdi = 1;
	  } else if (tpd < 3) {
		  tpdi = 2;
	  } else {
		  tpdi = 5;
	  }
	  // Now restore the magnitude
	  while (factors_of_10 > 0) {
		  tpdi = tpdi * 10;
		  factors_of_10 --;
	  }
	  while (factors_of_10 < 0) {
		  tpdi = tpdi / 10;
		  factors_of_10 ++;
	  }

	  // System.out.println ( "Time per division = " + tpdi );

	  // Now we're ready to draw the time lines
	  // x = (int)(( input_spike_times[i][j] - x0 ) * x_scale);
	  // t = ( x / x_scale ) + x0
	  // so the left side of the window is x=0 and t = x0 (which is why x0 is named x0!!)
	  double x0i = 0;
	  while (x0i < x0) {
		  x0i = x0i + tpdi;
	  }
	  while (x0i > x0) {
		  x0i = x0i - tpdi;
	  }

	  g.setClip (0,0,win_w,win_h);
	  g.translate (0,0);
	  int grid_x;
	  do {
		  grid_x = (int)(( x0i - x0 ) * x_scale);
		  // System.out.println ( "Grid line at " + grid_x + " = " + x0i );
		  g.setColor ( new Color ( 50, 50, 50 ) );
		  g.drawLine ( grid_x, 0, grid_x, h * num_panels );
	    g.setColor ( Color.gray );
		  g.drawString ( ""+ Math.round(1000000*x0i)/1000000.0, grid_x, win_h-5 );
		  x0i += tpdi;
	  } while (grid_x < w);

	  // Now draw the data panels
	  
		double x, y;
		double y_min=Double.NaN, y_max=Double.NaN;
		if (combined) {
		  // Need to find the y_min and y_max of combined data
      if (var_y) {
        for (int p=0; p<num_panels; p++) {
			    for (int i=0; i<w; i++) {
				    x = (i / x_scale) + x0;
				    y = f[p].f ( x );
				    if (!Double.isNaN(y)) {
    				  if (Double.isNaN(y_min)) y_min = y;
    				  if (Double.isNaN(y_max)) y_max = y;
    				  if (!Double.isNaN(y_min)) {
    				    if (y < y_min) {
    				      y_min = y;
    				    }
    				  }
    				  if (!Double.isNaN(y_max)) {
    				    if (y > y_max) {
    				      y_max = y;
    				    }
    				  }
    				}
			    }
			  }
			} else {
        for (int p=0; p<num_panels; p++) {
          f[p].find_y_range();
				  if (Double.isNaN(y_min)) y_min = f[p].min_y;
				  if (Double.isNaN(y_max)) y_max = f[p].max_y;
				  if (!Double.isNaN(y_min)) {
				    if (f[p].min_y < y_min) {
				      y_min = f[p].min_y;
				    }
				  }
				  if (!Double.isNaN(y_max)) {
				    if (f[p].max_y > y_max) {
				      y_max = f[p].max_y;
				    }
				  }
			  }
			}
			// System.out.println ( "Combined: y_min = " + y_min + ", y_max = " + y_max );
		}

    for (int p=0; p<num_panels; p++) {
		
			if (f[p].valid_data == false) {
			  continue;
			}

		  // Clip the subplot window
		  if (combined) {
  		  g.setClip (0,0,w,win_h);
		  } else {
  		  g.setClip (0,0,w,h);
  		}

		  // Draw the actual subplot
      g.setColor ( Color.black );
      // g.fillRect (0,0,w,h	);
      g.setColor ( Color.white );
      if (combined) {
        //g.drawRect (0,0,w-1,win_h-1);
      } else {
        g.drawRect (0,0,w-1,h-1);
      }

		  g.setColor ( Color.gray );
		  
		  // Fill in the data_file's values across the entire display area (while finding min and max)
			f[p].num_samples = w;
			f[p].samples = new double[w];

		  if (!combined) {
		    y_min=Double.NaN;
		    y_max=Double.NaN;
		  }
		  
		  // System.out.println ( "Plotting from 0 to " + w );

      if (var_y) {
        // Compute samples and y range based on what's showing in the window
			  for (int i=0; i<w; i++) {
				  x = (i / x_scale) + x0;
				  y = f[p].samples[i] = f[p].f ( x );  // Save the data_file values so the data_file doesn't have to get called twice
				  // y = f[p].samples[i] = Math.sin(x);

			    if (!Double.isNaN(y)) {
				    if (Double.isNaN(y_min)) y_min = y;
				    if (Double.isNaN(y_max)) y_max = y;
				    if (!Double.isNaN(y_min)) {
				      if (y < y_min) {
				        y_min = y;
				      }
				    }
				    if (!Double.isNaN(y_max)) {
				      if (y > y_max) {
				        y_max = y;
				      }
				    }
				  }

				  if (!combined) {
				    if (!Double.isNaN(y)) {
    				  if (Double.isNaN(y_min)) y_min = y;
    				  if (Double.isNaN(y_max)) y_max = y;
    				  if (!Double.isNaN(y_min)) {
    				    if (y < y_min) {
    				      y_min = y;
    				    }
    				  }
    				  if (!Double.isNaN(y_max)) {
    				    if (y > y_max) {
    				      y_max = y;
    				    }
    				  }
    				}
				  }
			  }
			} else {
        // Compute samples and y range based on the entire data set
  		  if (!combined) {
          // Compute y range based on the entire data set
          f[p].find_y_range();
          y_min = f[p].min_y;
          y_max = f[p].max_y;
        }

			  for (int i=0; i<w; i++) {
				  x = (i / x_scale) + x0;
				  f[p].samples[i] = f[p].f ( x );  // Save the data_file values so the data_file doesn't have to get called twice
			  }

			}
      // System.out.println ( "Set " + p + " range: " + y_min + " to " + y_max );
			
			if ((Double.isNaN(y_min)) && (Double.isNaN(y_max))) {
			  y_min = y_max = 0.0;
			} else if (Double.isNaN(y_min)) {
			  y_min = y_max;
			} else if (Double.isNaN(y_max)) {
			  y_max = y_min;
			}

			if (y_min == y_max) {
			  y_min = y_min - 0.000000001;
			  y_max = y_max + 0.000000001;
			}

		  if (annotation) {
        if (combined) {
	        g.setColor ( f[p].color );
  		  	g.drawString ( f[p].getName() + ": " + y_min + " < y < " + y_max, 10, 20*(p+1) );
        } else {
  		  	g.drawString ( f[p].getName() + ": " + y_min + " < y < " + y_max, 10, 20 );
  		  }
		  }

		  g.setColor ( f[p].color );

			// Now make the plot
			double old_y=Double.NaN;
			for (int i=0; i<w; i++) {
				x = (i / x_scale) + x0;
				y = f[p].samples[i];
				// Scale y to be between 0 and 1
				if (!Double.isNaN(y)) {
				  y = (y-y_min) / (y_max - y_min);
				  y = 1 - y;
				  if (!Double.isNaN(old_y)) {
				    if (combined) {
				      g.drawLine ( i-1, (int)(old_y*win_h), i, (int)(y*win_h) );
				      // System.out.println ( "  draw ( " + ((int)(old_y*win_h)) + " to " + ((int)(y*win_h)) + ")" );
				    } else {
				      g.drawLine ( i-1, (int)(old_y*h), i, (int)(y*h) );
				      // System.out.println ( "  draw ( " + ((int)(old_y*h)) + " to " + ((int)(y*h)) + ")" );
				    }
				  }
				}
				old_y = y;
			}

		  // Translate the coordinate system for the next subplot
		  if (!combined) {
  		  g.translate (0,h);
  		}
    }

	}  

	int mouse_down_x = 0;
	int mouse_down_y = 0;
	int mouse_delta_x = 0;
	int mouse_delta_y = 0;

	Cursor current_cursor = null;
	Cursor h_cursor = null;
	Cursor v_cursor = null;
	Cursor b_cursor = null;
	int cursor_size = 33;
	

	public void mouseWheelMoved(MouseWheelEvent e) {

    if ( (current_cursor == h_cursor) || (current_cursor == b_cursor) ) {
	    // Expand or Contract the Horizontal Scale

	    // x = (int)(( input_spike_times[i][j] - x0 ) * x_scale);
	    //  so...
	    // t = ( x / x_scale ) + x0
	    // x0 = x0 + (x/s_old) - (x/s_new)
	    double old_x_scale = x_scale;
	    int x = e.getX();
	    // System.out.print ( "MouseWheel: " + e.getWheelRotation() + ", x: " + e.getX() + ", x0: " + x0 + ", pre-x_scale: " + x_scale);
	    int w = -e.getWheelRotation();
	    if (w > 0) {
		    x_scale = 1.25 * w * x_scale;
	    } else if (w < 0) {
		    x_scale = x_scale / (1.25 * (-w));
	    }
	    // System.out.println ( ", post-x_scale: " + x_scale);
	    x0 += (x/old_x_scale) - (x/x_scale);
	  }
	  
    if ( (current_cursor == v_cursor) || (current_cursor == b_cursor) ) {
	    // Expand or Contract the Vertical Scale

	  }
	  
	  repaint();

	}
	
	boolean drag_button_down = false;

	public void mouseDragged(MouseEvent e) {
	  if (drag_button_down) {
      if ( (current_cursor == h_cursor) || (current_cursor == b_cursor) ) {
	      // Slide the display sideways
	      mouse_delta_x = e.getX() - mouse_down_x;
	      x0 = x0 - (mouse_delta_x / x_scale);
	      // if (x0 > 0) x0 = 0;
	      mouse_down_x = e.getX();
	      // System.out.println ( "Mouse Dragged " + mouse_delta_x + ", new x0 = " + x0 );
	    }
      if ( (current_cursor == v_cursor) || (current_cursor == b_cursor) ) {
	      // Slide the display vertically

	    }
	    repaint();
	  }
	}

	public void mouseMoved(MouseEvent e) { }
	public void mouseClicked(MouseEvent e) { }

  public void mouseEntered ( MouseEvent e ) {
    if ( (h_cursor == null) || (v_cursor == null) || (b_cursor == null) ) {
      Toolkit tk = Toolkit.getDefaultToolkit();
      Graphics2D cg = null;
      BufferedImage cursor_image = null;
      Polygon p = null;
      int h = cursor_size;
      int w = cursor_size;

      // Create the horizontal cursor
      p = new Polygon();
      p.addPoint ( 0, h/2 );
      p.addPoint ( w/4, (h/2)-(h/4) );
      p.addPoint ( w/4, (h/2)-(h/8) );
      p.addPoint ( 3*w/4, (h/2)-(h/8) );
      p.addPoint ( 3*w/4, (h/2)-(h/4) );
      p.addPoint ( w-1, h/2 );
      p.addPoint ( 3*w/4, (h/2)+(h/4) );
      p.addPoint ( 3*w/4, (h/2)+(h/8) );
      p.addPoint ( w/4, (h/2)+(h/8) );
      p.addPoint ( w/4, (h/2)+(h/4) );

      cursor_image = new BufferedImage(cursor_size,cursor_size,BufferedImage.TYPE_4BYTE_ABGR);
      cg = cursor_image.createGraphics();
      cg.setColor ( new Color(255,255,255) );
      cg.fillPolygon ( p );
      cg.setColor ( new Color(0,0,0) );
      cg.drawPolygon ( p );
      
      h_cursor = tk.createCustomCursor ( cursor_image, new Point(cursor_size/2,cursor_size/2), "Horizontal" );

      // Create the vertical cursor
      p = new Polygon();
      p.addPoint ( w/2, 0 );
      p.addPoint ( (w/2)+(w/4), h/4 );
      p.addPoint ( (w/2)+(w/8), h/4 );
      p.addPoint ( (w/2)+(w/8), 3*h/4 );
      p.addPoint ( (w/2)+(w/4), 3*h/4 );
      p.addPoint ( w/2, h-1 );
      p.addPoint ( (w/2)-(w/4), 3*h/4 );
      p.addPoint ( (w/2)-(w/8), 3*h/4 );
      p.addPoint ( (w/2)-(w/8), h/4 );
      p.addPoint ( (w/2)-(w/4), h/4 );

      cursor_image = new BufferedImage(cursor_size,cursor_size,BufferedImage.TYPE_4BYTE_ABGR);
      cg = cursor_image.createGraphics();
      cg.setColor ( new Color(255,255,255) );
      cg.fillPolygon ( p );
      cg.setColor ( new Color(0,0,0) );
      cg.drawPolygon ( p );
      
      v_cursor = tk.createCustomCursor ( cursor_image, new Point(cursor_size/2,cursor_size/2), "Vertical" );
      
      // Create the both cursor
      p = new Polygon();
      p.addPoint ( 0, h/2 );
      p.addPoint ( w/4, (h/2)-(h/4) );
      p.addPoint ( w/4, (h/2)-(h/8) );
      p.addPoint ( (w/2)-(w/8), (h/2)-(h/8) );
      p.addPoint ( (w/2)-(w/8), h/4 );
      p.addPoint ( (w/2)-(w/4), h/4 );
      p.addPoint ( w/2, 0 );
      p.addPoint ( (w/2)+(w/4), h/4 );
      p.addPoint ( (w/2)+(w/8), h/4 );
      p.addPoint ( (w/2)+(w/8), (h/2)-(h/8) );
      p.addPoint ( (w/2)+(w/4), (h/2)-(h/8) );
      p.addPoint ( (w/2)+(w/4), (h/2)-(h/4) );
      p.addPoint ( w-1, h/2 );
      p.addPoint ( (w/2)+(w/4), (h/2)+(h/4) );
      p.addPoint ( (w/2)+(w/4), (h/2)+(h/8) );
      p.addPoint ( (w/2)+(w/8), (h/2)+(h/8) );
      p.addPoint ( (w/2)+(w/8), 3*h/4 );
      p.addPoint ( (w/2)+(w/4), 3*h/4 );
      p.addPoint ( w/2, h-1 );
      p.addPoint ( (w/2)-(w/4), 3*h/4 );
      p.addPoint ( (w/2)-(w/8), 3*h/4 );
      p.addPoint ( (w/2)-(w/8), (h/2)+(h/8) );
      p.addPoint ( (w/2)-(w/4), (h/2)+(h/8) );
      p.addPoint ( (w/2)-(w/4), (h/2)+(h/4) );

      cursor_image = new BufferedImage(cursor_size,cursor_size,BufferedImage.TYPE_4BYTE_ABGR);
      cg = cursor_image.createGraphics();
      cg.setColor ( new Color(255,255,255) );
      cg.fillPolygon ( p );
      cg.setColor ( new Color(0,0,0) );
      cg.drawPolygon ( p );
      
      b_cursor = tk.createCustomCursor ( cursor_image, new Point(cursor_size/2,cursor_size/2), "Both" );
      
    }
    if (current_cursor == null) {
      current_cursor = h_cursor;
    }
    setCursor ( current_cursor );
  }
	public void mouseExited(MouseEvent e) { }
	public void mousePressed(MouseEvent e) {
	  // System.out.println ( "Clicked Button = " + e.getButton() );
	  // This is a normal spike display so scroll sideways
	  if (e.getButton() == e.BUTTON1) {
		  mouse_down_x = e.getX();
		  mouse_down_y = e.getY();
    	drag_button_down = true;
	  } else {
		  // System.out.println ( "Alternate button" );
		  // Disable cursor changing because it's not used in this version
		  /*
		  if ( (current_cursor == null) || (current_cursor == b_cursor) ) {
		    current_cursor = h_cursor;
		  } else if (current_cursor == h_cursor) {
		    current_cursor = v_cursor;
		  } else {
		    current_cursor = b_cursor;
		  }
		  setCursor ( current_cursor );
		  */
	  }
	}
	public void mouseReleased(MouseEvent e) {
	  if (e.getButton() == e.BUTTON1) {
    	drag_button_down = false;
    }
	}

}



public class PlotData extends JFrame implements WindowListener {

	static DisplayPanel dp = null;

	PlotData ( String s ) {
		super(s);
	}
	
	public static String[] append_string ( String slist[], String s ) {
    String news[] = new String[slist.length+1];
    for (int i=0; i<slist.length; i++) {
      news[i] = slist[i];
    }
    news[slist.length] = s;
    return news;
	}

  public static void main(String[] args) {
		System.out.println ( "Data Plotting Program ..." );
		
		dp = new DisplayPanel();
    dp.loading = true;

		String file_names[] = new String[0];
		double x0 = 0.0;
		double dx = 1.0;

    System.out.println ( "Creating the frame early..." );
    PlotData frame = new PlotData("Plot Data");

    dp.set_frame ( frame );
    frame.setSize(400, 150);
    frame.setJMenuBar ( dp.build_menu_bar() );

    Container content = frame.getContentPane();
    content.setBackground(Color.white);
    content.setLayout(new BorderLayout()); 

		frame.add(dp);
		dp.addMouseWheelListener ( dp );
		dp.addMouseMotionListener ( dp );
		dp.addMouseListener ( dp );
		frame.addKeyListener ( dp );
    frame.pack();
    frame.addWindowListener(frame);
    frame.setVisible(true);

    if (args.length > 0) {
      Color next_color = null;
      for (int arg=0; arg<args.length; arg++) {
        try {
          if ( (args[arg].equals("?")) || (args[arg].equals("/?")) ) {
            System.out.println ( "Args: [fxy=filename ...] [GenTestFiles] [?]" );
            System.out.println ( "  fxy=filename - Add file 'filename' to the plot" );
            System.exit(0);
          } else if ( args[arg].equalsIgnoreCase("GenTestFiles") ) {
            System.out.println ( "Generating Test Data Files" );
            try {
              String fname;
              PrintStream ps;
              file_xy fxy;
              file_y fy;

              fname = "test_constant3.txt";
              ps = new PrintStream ( new FileOutputStream ( fname ) );
              for (int i=-20; i<100; i++) {
                ps.println ( i + " " + (0.3) );
              }
              fxy = new file_xy ( fname );
              fxy.setColor ( data_file.get_next_color() );
              dp.add_file ( fxy );
              ps.flush();

              fname = "test_linear_sorted.txt";
              ps = new PrintStream ( new FileOutputStream ( fname ) );
              for (int i=-20; i<20; i++) {
                ps.println ( i + " " + (3*i/20.0) );
              }
              fxy = new file_xy ( fname );
              fxy.setColor ( data_file.get_next_color() );
              dp.add_file ( fxy );
              ps.flush();

              fname = "test_linear_random.txt";
              ps = new PrintStream ( new FileOutputStream ( fname ) );
              for (int i=0; i<100; i++) {
                double x = 20 * (Math.random() - 0.5);
                ps.println ( x + " " + (-3*x/30.0) );
              }
              fxy = new file_xy ( fname );
              fxy.setColor ( data_file.get_next_color() );
              dp.add_file ( fxy );
              ps.flush();

              fname = "test_sine_sorted.txt";
              ps = new PrintStream ( new FileOutputStream ( fname ) );
              for (int i=0; i<1000; i++) {
                double x = 0.1 * (i-500);
                ps.println ( x + " " + Math.sin(x) );
              }
              fxy = new file_xy ( fname );
              fxy.setColor ( data_file.get_next_color() );
              dp.add_file ( fxy );
              ps.flush();

              fname = "test_sine_random.txt";
              ps = new PrintStream ( new FileOutputStream ( fname ) );
              for (int i=0; i<1000; i++) {
                double x = 0.1 * (500 * (2*(Math.random() - 0.5)));
                ps.println ( x + " " + Math.sin(x) );
              }
              fxy = new file_xy ( fname );
              fxy.setColor ( data_file.get_next_color() );
              dp.add_file ( fxy );
              ps.flush();

              fname = "test_cos_y_only.txt";
              ps = new PrintStream ( new FileOutputStream ( fname ) );
              for (int i=0; i<1000; i++) {
                double x = 0.1 * (i-500);
                ps.println ( Math.cos(x) );
              }
              fy = new file_y ( fname, -20, 0.1 );
              fy.setColor ( data_file.get_next_color() );
              dp.add_file ( fy );
              ps.flush();

              fname = "test_cos2_y_only.txt";
              ps = new PrintStream ( new FileOutputStream ( fname ) );
              for (int i=0; i<1000; i++) {
                double x = 0.2 * (i-500);
                ps.println ( Math.cos(2 * x) );
              }
              fy = new file_y ( fname, -20, 0.4 );
              fy.setColor ( data_file.get_next_color() );
              dp.add_file ( fy );
              ps.flush();

              fname = "test_gaussian.txt";
              ps = new PrintStream ( new FileOutputStream ( fname ) );
              for (int i=0; i<1000; i++) {
                double x = 0.1 * (i-500);
                ps.println ( x + " " + (Math.exp(-(x*x/100))) );
              }
              fxy = new file_xy ( fname );
              fxy.setColor ( data_file.get_next_color() );
              dp.add_file ( fxy );
              ps.flush();

              fname = "test_sigmoid.txt";
              ps = new PrintStream ( new FileOutputStream ( fname ) );
              for (int i=0; i<1000; i++) {
                double x = 0.1 * (i-500);
                ps.println ( x + " " + (1.0 / (1.0 + Math.exp(-x/2))) );
              }
              fxy = new file_xy ( fname );
              fxy.setColor ( data_file.get_next_color() );
              dp.add_file ( fxy );
              ps.flush();

            } catch (Exception e) {
              System.out.println ( "Error generating test files: " + e );
              System.exit(0);
            }
          } else if ( args[arg].equalsIgnoreCase("auto") ) {
            System.out.println ( "Autoscaling = true" );
          } else if ( (args[arg].length() > 4) && (args[arg].substring(0,4).equalsIgnoreCase("fxy=")) ) {
            System.out.println ( "Reading file " + args[arg].substring(4) + " ..." );
            file_xy fxy = new file_xy ( args[arg].substring(4) );
            System.out.println ( "   ... done reading file " + args[arg].substring(4) );
            if (next_color == null) {
              fxy.setColor ( data_file.get_next_color() );
            } else {
              fxy.setColor ( next_color );
            }
            dp.add_file ( fxy );
          } else if ( (args[arg].length() > 6) && (args[arg].substring(0,6).equalsIgnoreCase("color=")) ) {
            System.out.println ( "Setting Color to " + args[arg].substring(6) );
            try {
              next_color = Color.decode("0x" + args[arg].substring(6));
            } catch (NumberFormatException e) {
              System.out.println ( "Error decoding \"" + args[arg].substring(6) + "\" as a color" );
            }
          } else if ( (args[arg].length() > 3) && (args[arg].substring(0,3).equalsIgnoreCase("x0=")) ) {
            x0 = Double.parseDouble ( args[arg].substring(3) );
          } else if ( (args[arg].length() > 3) && (args[arg].substring(0,3).equalsIgnoreCase("dx=")) ) {
            dx = Double.parseDouble ( args[arg].substring(3) );
          } else if ( (args[arg].length() > 3) && (args[arg].substring(0,3).equalsIgnoreCase("fy=")) ) {
            file_y fy = new file_y ( args[arg].substring(3), x0, dx );
            fy.setColor ( data_file.get_next_color() );
            dp.add_file ( fy );
          } else {
           System.out.println ( "Unrecognized Argument: " + args[arg] );
           System.exit(0);
          }
        } catch (Exception e) {
           System.out.println ( "Error Parsing Argument: " + args[arg] + ", Error = " + e );
           System.exit(0);
        }
        content.repaint();
      }
    } else {
      file_xy fxy;
      file_y fy;
      double x[], y[];

      for (int phase=0; phase<5; phase++) {
        int num_samples = 3000;
        x = new double[num_samples];
        y = new double[num_samples];
        for (int i=0; i<num_samples; i++) {
          x[i] = 0.01 * (i+0);
          y[i] = Math.sin(x[i]-phase)/(phase+2);
          x[i] = x[i] * 50;
        }
        fxy = new file_xy ( "Test"+phase, x, y );
        fxy.setColor ( data_file.get_next_color() );
        dp.add_file ( fxy );
      }

    }

    dp.loading = false;
    dp.fit_x = true;
    content.repaint();


    //dp.set_frame ( frame );
		// dp.set_files ( file_names );
		/* 
    frame.setSize(400, 150);
    frame.setJMenuBar ( dp.build_menu_bar() );

    Container content = frame.getContentPane();
    content.setBackground(Color.white);
    content.setLayout(new BorderLayout()); 

		frame.add(dp);
		dp.addMouseWheelListener ( dp );
		dp.addMouseMotionListener ( dp );
		dp.addMouseListener ( dp );
		frame.addKeyListener ( dp );
    frame.pack();
    frame.addWindowListener(frame);
    frame.setVisible(true);
    */
  }

  public void windowActivated(WindowEvent event) { }
  public void windowClosed(WindowEvent event) { }
  public void windowClosing(WindowEvent event) { if (dp != null) dp.save_and_exit(); System.exit(1); }
  public void windowDeactivated(WindowEvent event) { }
  public void windowDeiconified(WindowEvent event) { }
  public void windowIconified(WindowEvent event) { }
  public void windowOpened(WindowEvent event) { }

}

