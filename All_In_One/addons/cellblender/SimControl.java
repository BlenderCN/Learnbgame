import java.io.*;
import java.util.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.*;
import javax.swing.*;
import java.awt.datatransfer.*;



class DisplayPanel extends JPanel implements ActionListener,MouseListener,MouseWheelListener,MouseMotionListener,KeyListener,Runnable {

	static final String S = File.separator;
	
	class TaggedLine {
	  public char tag;
	  public String line;
	}
	public Vector lines = null;
	
	boolean new_line = false;
	
	JFrame frame=null;

	public DisplayPanel() {
	  lines = new Vector();
		setBorder(BorderFactory.createLineBorder(Color.black));
		setBackground ( new Color ( 0, 0, 0 ) );
	}
	
	Thread running_thread = null;
	String command_to_run = null;
	Process sub_process = null;

  public void end_job() {
    System.out.println ( "Terminating the supprocess..." );
    sub_process.destroy();
    System.out.println ( "Subprocess terminated" );
  }

  public String read_stream_with_tag ( String remaining, BufferedInputStream stream, char tag ) {
    try {
      int available = stream.available();
      byte buffer[] = new byte[available];
      stream.read ( buffer, 0, available );

      String total_so_far = remaining + new String(buffer);

      String line_array[] = total_so_far.split ( "[\r\n]+" );
      int num_lines = 0;
      String still_remaining = "";
      
      if ( total_so_far.endsWith("\r") || total_so_far.endsWith("\n") ) {
        num_lines = line_array.length;
      } else {
        num_lines = line_array.length - 1;
        still_remaining = line_array[num_lines];
      }
      for (int i=0; i<num_lines; i++) {
  	    TaggedLine tl = new TaggedLine();
        tl.tag = tag;
  	    tl.line = line_array[i];
  	    lines.addElement ( tl );
      }
      return ( still_remaining );
    } catch (Exception e) {
      return ( remaining );
    }
  }

  public void set_background_done () {
		setBackground ( new Color ( 0, 100, 0 ) );
		repaint();
  }

	public void run() {
	  System.out.println ( "Running..." );
	  if (command_to_run != null) {
	    try {
	      System.out.println ( "Starting the subprocess..." );
	      
	      sub_process = Runtime.getRuntime().exec ( command_to_run );
	      
	      BufferedInputStream input_stream = new BufferedInputStream ( sub_process.getInputStream() );
	      BufferedInputStream error_stream = new BufferedInputStream ( sub_process.getErrorStream() );
	      BufferedOutputStream output_stream = new BufferedOutputStream ( sub_process.getOutputStream() );
	      
	      String input_remaining = "";
	      String error_remaining = "";

	      int exit_value = 0;
	      boolean done;
	      done = false;
	      while (!done) {
	        try {
      	    running_thread.sleep(2);
      	    int in_available = input_stream.available();
      	    int err_available = error_stream.available();
      	    // System.out.println ( "Available: " + in_available + " " + err_available );
      	    if ( (in_available>0) || (err_available>0) ) {
      	      // Got some data!!
      	      if (in_available > err_available) {
      	        input_remaining = read_stream_with_tag ( input_remaining, input_stream, 'o' );
      	        error_remaining = read_stream_with_tag ( error_remaining, error_stream, 'e' );
      	      } else {
      	        error_remaining = read_stream_with_tag ( error_remaining, error_stream, 'e' );
      	        input_remaining = read_stream_with_tag ( input_remaining, input_stream, 'o' );
      	      }
        	    new_line = true;
          		repaint();
      	    }
      	    try {
      	      exit_value = sub_process.exitValue();
      	      done = true;
      	    } catch ( IllegalThreadStateException itse ) {
      	    }
      	  } catch (Exception e) {
      	  }
	      }

	      System.out.println ( "The subprocess has finished!!" );
    		set_background_done();
  	    // running_thread.sleep(5000);
  	    // System.exit(0);

  	  } catch (Exception e) {
  	  }
	  }
	}


	public void set_frame ( JFrame f ) {
		frame = f;
	}
	
  int pref_w=600, pref_h=600;
	public Dimension getPreferredSize() {
		return new Dimension(pref_w,pref_h);
	}

	
  int lines_per_scrollwheel_click = 10;
	String scroll_prefix = "Scroll by ";

	public JMenuBar build_menu_bar() {
    JMenuItem mi;
    ButtonGroup bg;
    JMenuBar menu_bar = new JMenuBar();
	    JMenu file_menu = new JMenu("Simulation");
	    	file_menu.add ( mi = new JMenuItem("Kill") );  mi.addActionListener(this);
	    	file_menu.add ( mi = new JMenuItem("Exit") );  mi.addActionListener(this);
	    	menu_bar.add ( file_menu );
	    JMenu set_menu = new JMenu("Set");
	    	set_menu.add ( mi = new JMenuItem(scroll_prefix+"1") );    mi.addActionListener(this);
	    	set_menu.add ( mi = new JMenuItem(scroll_prefix+"2") );    mi.addActionListener(this);
	    	set_menu.add ( mi = new JMenuItem(scroll_prefix+"3") );    mi.addActionListener(this);
	    	set_menu.add ( mi = new JMenuItem(scroll_prefix+"4") );    mi.addActionListener(this);
	    	set_menu.add ( mi = new JMenuItem(scroll_prefix+"5") );    mi.addActionListener(this);
	    	set_menu.add ( mi = new JMenuItem(scroll_prefix+"10") );   mi.addActionListener(this);
	    	set_menu.add ( mi = new JMenuItem(scroll_prefix+"20") );   mi.addActionListener(this);
	    	set_menu.add ( mi = new JMenuItem(scroll_prefix+"50") );   mi.addActionListener(this);
	    	set_menu.add ( mi = new JMenuItem(scroll_prefix+"100") );  mi.addActionListener(this);
	    	set_menu.add ( mi = new JMenuItem(scroll_prefix+"200") );  mi.addActionListener(this);
	    	set_menu.add ( mi = new JMenuItem(scroll_prefix+"500") );  mi.addActionListener(this);
	    	set_menu.add ( mi = new JMenuItem(scroll_prefix+"1000") ); mi.addActionListener(this);
	    	menu_bar.add ( set_menu );
	    JMenu copy_menu = new JMenu("Copy");
	    	copy_menu.add ( mi = new JMenuItem("Copy Normal Output") );  mi.addActionListener(this);
	    	copy_menu.add ( mi = new JMenuItem("Copy Error Output") );  mi.addActionListener(this);
	    	copy_menu.add ( mi = new JMenuItem("Copy All Output") );  mi.addActionListener(this);
	    	menu_bar.add ( copy_menu );
	   return (menu_bar);
	}

  public void copy_to_clipboard ( char output_type ) {
	  try {
	    String data = "";
	    for (int i=0; i<lines.size(); i++) {
        TaggedLine tl = (TaggedLine)(lines.elementAt(i));
        if ( (output_type == 'a') || (output_type == tl.tag) ) {
          data = data + tl.line + "\n";
        }
      }
		  StringSelection ss = new StringSelection(data);

		  Clipboard cb = Toolkit.getDefaultToolkit().getSystemClipboard();
		  
		  cb.setContents ( ss, ss );
		} catch ( Exception e ) {
		}
  }

	public void actionPerformed(ActionEvent e) {
		String cmd = e.getActionCommand();
		// System.out.println ( "ActionPerformed got \"" + cmd + "\"" );
		
		if (cmd.equalsIgnoreCase("Exit")) {
			System.exit(0);
		} else if (cmd.equalsIgnoreCase("Kill")) {
		  System.out.println ( "Killing the subprocess..." );
		  sub_process.destroy();
  		set_background_done();
		} else if (cmd.equalsIgnoreCase("Copy Normal Output")) {
		  copy_to_clipboard ( 'o' );
		  System.out.println ( "Copied Normal Output to the System Clipboard" );
		} else if (cmd.equalsIgnoreCase("Copy Error Output")) {
      copy_to_clipboard ( 'e' );
		  System.out.println ( "Copied Error Output to the System Clipboard" );
		} else if (cmd.equalsIgnoreCase("Copy All Output")) {
      copy_to_clipboard ( 'a' );
		  System.out.println ( "Copied All Output to the System Clipboard" );
		} else if (cmd.startsWith(scroll_prefix)) {
		  try {
		    int new_scroll = Integer.parseInt(cmd.substring(scroll_prefix.length()));
		    lines_per_scrollwheel_click = new_scroll;
		  } catch (Exception ex) {
		  }
		}

		repaint();
	}


  public void keyTyped ( KeyEvent e ) {
  	repaint();
  }
  public void keyPressed ( KeyEvent e ) {
  }
  public void keyReleased ( KeyEvent e ) {
  }


  int top_line = 0;
  int font_size = 12;
  int line_height = 14;
  int line_offset = 6;

	public void paintComponent(Graphics g) {

		super.paintComponent(g);

		int win_w, win_h, w, h, time_h;
		win_w = getSize().width;
		win_h = getSize().height;
		
		int max_lines = win_h / line_height;
		
		if (lines.size() > 0) {
		
	    Font cur_font = g.getFont();
	    g.setFont ( new Font("SansSerif", Font.BOLD, font_size) );
	    if (new_line) {
	      top_line = lines.size() - max_lines;
	      if (top_line < 0) {
	        top_line = 0;
	      }
        new_line = false;
	    }
	    int num_lines = lines.size() - top_line;
	    if ( num_lines < 1 ) num_lines = 1;
	    if ( num_lines > max_lines ) {
	      num_lines = max_lines;
	    }
      
      for (int i=0; i<num_lines; i++) {
        TaggedLine tl = (TaggedLine)(lines.elementAt(i+top_line));
        if (tl.tag == 'o') {
          g.setColor ( Color.gray );
        } else {
          g.setColor ( Color.white );
        }
	    	g.drawString ( tl.line, line_offset, (i+1)*line_height );
        // System.out.println ( tl.line );
      }
    	g.setFont ( cur_font );
    }

	}  

	public void mouseWheelMoved(MouseWheelEvent e) {

    // System.out.println ( "MouseWheel: " + e.getWheelRotation() + ", x: " + e.getX() );
		int win_h = getSize().height;
    top_line += lines_per_scrollwheel_click*e.getWheelRotation();
    if (top_line > lines.size()-(win_h/line_height)) {
      top_line = lines.size()-(win_h/line_height);
    }
    if (top_line < 0) {
      top_line = 0;
    }
    // System.out.println ( "Top line = " + top_line );
	  repaint();

	}
	
	public void mouseDragged(MouseEvent e) { }
	public void mouseMoved(MouseEvent e) { }
	public void mouseClicked(MouseEvent e) { }
  public void mouseEntered ( MouseEvent e ) { }
	public void mouseExited(MouseEvent e) { }
	public void mousePressed(MouseEvent e) { }
	public void mouseReleased(MouseEvent e) { }

}



public class SimControl extends JFrame implements WindowListener {

	static DisplayPanel dp = null;

	SimControl ( String s ) {
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
		System.out.println ( "Simulation Control Program ..." );
		
		dp = new DisplayPanel();

    SimControl frame = new SimControl("Simulation Control");

    dp.set_frame ( frame );

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
    
    String command_string = "";
    int command_arg_sep_index = -1;  // The value of -1 is needed because it will default to 0 (-1 + 1)
    
    int window_x=0;
    int window_y=0;

    if (args.length > 0) {
      // Search for the first command argument separator
      for (int arg=0; arg<args.length; arg++) {
        if ( args[arg].equals(":") ) {
          command_arg_sep_index = arg;
          break;
        }
      }
      
      if (command_arg_sep_index >= 0) {
        // Process the application commands before the command argument separator

        for (int arg=0; arg<command_arg_sep_index; arg++) {
          try {
            if ( (args[arg].equals("?")) || (args[arg].equals("/?")) ) {
              System.out.println ( "Args: [?] [x=#] [y=#] [:] [cmd]" );
              System.out.println ( "  x=# - Set the x location of the window" );
              System.out.println ( "  y=# - Set the y location of the window" );
              System.out.println ( "  : - Separates options from command line (needed when both are present)" );
              System.out.println ( "  cmd - Execute the command showing output" );
              System.exit(0);
            } else if ( args[arg].startsWith("x=") ) {
              window_x = Integer.parseInt(args[arg].substring(2));
            } else if ( args[arg].startsWith("y=") ) {
              window_y = Integer.parseInt(args[arg].substring(2));
            } else {
              System.out.println ( "Unrecognized argument: " + args[arg] );
            }
          } catch (Exception e) {
             System.out.println ( "Error Parsing Argument: " + args[arg] + ", Error = " + e );
             System.exit(0);
          }
        }
      }
        
      // Process the remaining arguments as if they are all parts of the command string

      for (int arg=command_arg_sep_index+1; arg<args.length; arg++) {
        if (command_string.length() > 0) {
          command_string += " ";
        }
        command_string += args[arg];
        content.repaint();
      }
    }

    frame.setLocation ( window_x, window_y );

    System.out.println ( "Command = " + command_string );
    dp.command_to_run = command_string;

    content.repaint();
    dp.running_thread = new Thread(dp);
    dp.running_thread.start();

  }

  public void windowActivated(WindowEvent event) { }
  public void windowClosed(WindowEvent event) { }
  public void windowClosing(WindowEvent event) { 
    dp.end_job();
    System.exit(0);
  }
  public void windowDeactivated(WindowEvent event) { }
  public void windowDeiconified(WindowEvent event) { }
  public void windowIconified(WindowEvent event) { }
  public void windowOpened(WindowEvent event) { }

}

