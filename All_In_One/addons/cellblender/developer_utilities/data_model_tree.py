#!/usr/bin/env python

import sys
import pickle
import pygtk
pygtk.require ( '2.0' )
import gtk

def responseToOKDialog(entry, dialog, response):
  print ( "OK Clicked" )
  dialog.response(response)

def responseToCancelDialog(entry, dialog, response):
  print ( "Cancel Clicked" )
  dialog.response(response)

class data_model_tree:

  def delete_event(self, widget, event, data=None):
    gtk.main_quit()
    return False

  def __init__(self, dm):
    self.file_name = None

    self.data_model = dm
    self.dump_depth = 0
    # Create a new window
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.set_title("Data Model Tree Viewer")
    self.window.set_size_request(400,600)
    self.window.connect("delete_event", self.delete_event)
    
    self.vbox = gtk.VBox(False, 0)
    self.window.add(self.vbox)
    self.vbox.show()

    self.menu_bar = gtk.MenuBar()

    self.vbox.pack_start(self.menu_bar, False, False, 2)
    
    self.file_menu = gtk.MenuItem ( "File" )
    self.file_menu.show()
    self.menu = gtk.Menu()

    menu_name = "Open"
    menu_item = gtk.MenuItem ( menu_name )
    menu_item.connect ( "activate", self.open_callback, menu_name )
    self.menu.append ( menu_item )

    menu_name = "Save"
    menu_item = gtk.MenuItem ( menu_name )
    menu_item.connect ( "activate", self.save_callback, menu_name )
    self.menu.append ( menu_item )

    menu_name = "Dump Model"
    menu_item = gtk.MenuItem ( menu_name )
    menu_item.connect ( "activate", self.dump_model_callback, menu_name )
    self.menu.append ( menu_item )

    menu_name = "Dump Keys"
    menu_item = gtk.MenuItem ( menu_name )
    menu_item.connect ( "activate", self.dump_keys_callback, menu_name )
    self.menu.append ( menu_item )

    menu_name = "Dump Tree"
    menu_item = gtk.MenuItem ( menu_name )
    menu_item.connect ( "activate", self.dump_tree_callback, menu_name )
    self.menu.append ( menu_item )

    self.file_menu.set_submenu(self.menu)
    self.menu_bar.append(self.file_menu)

    self.treestore = gtk.TreeStore(str,str)
    
    self.build_tree_from_data_model ( None, "Data Model", self.data_model )

    self.treeview = gtk.TreeView(self.treestore)
    self.column = gtk.TreeViewColumn('Data Model')
    self.treeview.append_column(self.column)
    self.cell = gtk.CellRendererText()
    self.column.pack_start(self.cell, True)
    self.column.add_attribute(self.cell, 'text', 0)
    #self.treeview.set_search_column(0)
    #self.column.set_sort_column_id(0)
    #self.treeview.set_reorderable(True)
    
    self.scrolled_window = gtk.ScrolledWindow()
    self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
    self.scrolled_window.add_with_viewport(self.treeview)
    
    self.vbox.pack_end(self.scrolled_window, True, True, 2)

    self.window.show_all()
    
    self.open_dialog = gtk.FileSelection("Open Data Model File")
    self.open_dialog.ok_button.connect("clicked", self.open_ok_callback)
    self.open_dialog.cancel_button.connect("clicked", self.open_cancel_callback)
    
    self.treeview.connect("row-activated", self.row_selected)

  def row_selected ( self, tv, path, col ):
    selected = tv.get_selection().get_selected()
    print ( "Row selected type: " + str(type(selected)) )
    if type(selected) == type((1,2)):
      sel_val = selected[0].get_value(selected[1],0)
      if '=' in sel_val:
        dm_key = sel_val.split("=")[0].strip()
        dm_val = sel_val.split("=")[1].strip()

        sel_path = selected[0].get_path(selected[1])
        print ( "selected = " + str(selected))
        print ( "get_value(): " + str(sel_val) )
        print ( "type(get_value()): " + str(type(sel_val)) )
        print ( "get_path(): " + str(selected[0].get_path(selected[1])) )

        #__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

        #dialog = gtk.MessageDialog ( type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_OK_CANCEL, flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT )
        #dialog.set_markup ( "Enter the <b>new value</b>" )
        #response = dialog.run()
        #print ( "Dialog options = " + str(dir(dialog)) )
        #print ( "Dialog action = " + str(dialog.get_action()) )
        #print ( "Dialog response = " + str(response) )
        

        #dialog = gtk.MessageDialog ( type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_OK_CANCEL, flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT )
        dialog = gtk.MessageDialog ( type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_OK, flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT )
        dialog.set_markup ( "Enter the new value for <b>" + dm_key + "</b>"  )
        #create the text input field
        #dm_key_field = gtk.Entry()
        dm_val_field = gtk.Entry()
        #dm_key_field.set_text ( dm_key )
        dm_val_field.set_text ( dm_val )
        #allow the user to press enter to do ok
        dm_val_field.connect("activate", responseToOKDialog, dialog, gtk.RESPONSE_OK)
        #create a horizontal box to pack the dm_key_field and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label(dm_key + " = "), False, 5, 5)
        #hbox.pack_start(dm_key_field)
        #hbox.pack_start(gtk.Label(" = "), False, 5, 5)
        hbox.pack_end(dm_val_field)
        #some secondary text
        dialog.format_secondary_markup("Current value = <i>" + dm_val + "</i>")
        #add it and show it
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        new_assignment = dm_key + " = " + dm_val_field.get_text()
        print ( "Got: " + new_assignment )
        dialog.destroy()


        #selected[0].set_value( selected[1], 0, "(" + sel_val + ")" )
        selected[0].set_value( selected[1], 0, new_assignment )




  def dump_tree_callback ( self, widget, extra ):
    print ( "===== Data Model GTK Tree =====" )
    tm = self.treeview.get_model()
    print ( "GTK Tree Model " + str(type(tm)) )
    # print ( "GTK Tree Model has " + str(dir(tm)) )
    print ( "GTK Tree Model has " + str(len(tm)) + " rows" )
    iter = tm.get_iter_root()
    while iter != None:
      print ( "Iter not None" )
      iter = tm.iter_next(iter)

    self.dump_tree_recurse ( tm, iter )


  def dump_tree_recurse ( self, tm, iter ):
    self.dump_depth += 1
    next_child = tm.iter_children(iter)
    while next_child != None:
      val = str(tm.get_value(next_child,0))
      typ = str(tm.get_value(next_child,1))
      print ( str(self.dump_depth*"  ")+ val + "  " + typ )
      if typ == str(type({'a':1})):
        self.dump_tree_recurse ( tm, next_child )
      elif typ == str(type(['a',1])):
        self.dump_tree_recurse ( tm, next_child )
      else:
        self.dump_tree_recurse ( tm, next_child )
      next_child = tm.iter_next(next_child)
    self.dump_depth += -1



  def build_dm_from_tree_recurse ( self, tm, iter, store_in ):
    self.dump_depth += 1
    next_child = tm.iter_children(iter)
    while next_child != None:
      if not ( type(store_in) in [ type({'a':1}), type(['a',1]) ] ):
        print ( "Attempting to store into type " + str(type(store_in)) )
        exit(999)

      val = str(tm.get_value(next_child,0))
      typ = str(tm.get_value(next_child,1))
      detected_type = "Unknown"
      converted_name = None
      converted_val = None
      if typ == str(type({'a':1})):
        detected_type = "dict"
        converted_name = val.split("{}")[0].strip()
        converted_val = self.build_dm_from_tree_recurse ( tm, next_child, {} )
      elif typ == str(type(['a',1])):
        detected_type = "list"
        converted_name = val.split("[]")[0].strip()
        converted_val = self.build_dm_from_tree_recurse ( tm, next_child, [] )
      elif typ == str(type(True)):
        detected_type = "bool"
        converted_name = val.split("=")[0].strip()
        converted_val = bool ( val.split("=")[1].strip().upper() == "TRUE" )
        # print ( "Found a Bool: val = " + str(val) + ", typ = " + str(typ) + ", converted_name = " + str(converted_name) + ", converted_val = " + str(converted_val) )
      elif typ == str(type(1)):
        detected_type = "int"
        converted_name = val.split("=")[0].strip()
        converted_val = int(val.split("=")[1].strip())
      elif typ == str(type(1111111111111111111111111111)):
        detected_type = "long"
        converted_name = val.split("=")[0].strip()
        converted_val = long(val.split("=")[1].strip())
      elif typ == str(type(1.5)):
        detected_type = "float"
        converted_name = val.split("=")[0].strip()
        converted_val = float(val.split("=")[1].strip())
      elif typ == str(type('abc')):
        detected_type = "string"
        converted_name = val.split("=")[0].strip()
        converted_val = val.split("=")[1].strip().strip('"')
      elif typ == str(type(u'abc')):
        detected_type = "unicode"
        converted_name = val.split("=")[0].strip()
        converted_val = val.split("=")[1].strip().strip('"')
      else:
        print ( "Exiting with unknown type of " + str(typ) )
        exit(999)

      #print ( str(self.dump_depth*"  ")+ val + " :  storing " + str(converted_name) + " = " + str(converted_val) + " of type " + str(detected_type) + " into a " + str(type(store_in)) )
      print ( str(self.dump_depth*"  ")+ val + " :  storing " + str(converted_name) + " of type " + str(detected_type) + " into a " + str(type(store_in)) )

      if type(store_in) == type({'a':1}):
        store_in.update ( { converted_name: converted_val } )
      if type(store_in) == type(['a',1]):
        store_in = store_in + [ converted_val ]

      next_child = tm.iter_next(next_child)
    self.dump_depth += -1
    return store_in


  def build_dm_from_tree ( self, widget, extra ):
    tm = self.treeview.get_model()
    print ( "Building Data Model from GTK Tree Model " + str(type(tm)) )
    # print ( "GTK Tree Model has " + str(dir(tm)) )
    print ( "GTK Tree Model has " + str(len(tm)) + " rows" )
    iter = tm.get_iter_root()
    while iter != None:
      print ( "Iter not None" )
      iter = tm.iter_next(iter)

    dm_from_tree = {}
    dm_from_tree = self.build_dm_from_tree_recurse ( tm, iter, dm_from_tree )
    return dm_from_tree



  def pickle_data_model ( self, dm ):
    """ Return a pickle string containing a data model """
    return ( pickle.dumps(dm,protocol=0).decode('latin1') )

  def unpickle_data_model ( self, dmp ):
    """ Return a data model from a pickle string """
    return ( pickle.loads ( dmp.encode('latin1') ) )

  def read_data_model ( self, file_name ):
    """ Return a data model read from a named file """
    f = open ( file_name, 'r' )
    pickled_model = f.read()
    data_model = self.unpickle_data_model ( pickled_model )
    return data_model

  def write_data_model ( self, dm, file_name ):
    """ Write a data model to a named file """
    f = open ( file_name, 'w' )
    status = f.write ( self.pickle_data_model(dm) )
    f.close()
    return status


  def open_ok_callback ( self, widget ):
    self.file_name = self.open_dialog.get_filename()
    print ( "Opening file: " + self.file_name )
    self.data_model = self.read_data_model ( self.file_name )
    root = self.treestore.get_iter_root()
    self.treestore.remove(root)
    #  __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
    self.build_tree_from_data_model ( None, "Data Model", self.data_model )
    self.open_dialog.hide()


  def open_cancel_callback ( self, widget ):
    self.open_dialog.hide()
  
  def open_callback ( self, widget, extra ):
    self.open_dialog.show()
    
  def save_callback ( self, widget, extra ):
    print ( "Saving file: " + self.file_name )

    dm_from_tree = self.build_dm_from_tree ( widget, extra )

    self.dump_data_model ( "DM From Tree", dm_from_tree )
    self.data_model = dm_from_tree['Data Model']

    #__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
    self.write_data_model ( self.data_model, self.file_name )


    
  def build_tree_from_data_model ( self, parent, name, dm ):
    if type(dm) == type({'a':1}):  #dm is a dictionary
      name_str = name + " {} (" + str(len(dm)) + ")"
      if 'name' in dm:
        name_str += " = " + dm['name']
      else:
        name_keys = [k for k in dm.keys() if k.endswith('_name')]
        if len(name_keys) == 1:
          name_str += " = " + str(dm[name_keys[0]])
      # name_str += " " + str(len(dm)) + " item(s)"
      new_parent = self.treestore.append(parent,[name_str,str(type(dm))])
      for k,v in sorted(dm.items()):
        self.build_tree_from_data_model ( new_parent, k, v )
    elif type(dm) == type(['a',1]):  #dm is a list
      i = 0
      new_parent = self.treestore.append(parent,[name+" [] ("+str(len(dm))+")",str(type(dm))])
      for v in dm:
        self.build_tree_from_data_model ( new_parent, name + "["+str(i)+"]", v )
        i += 1
    elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')):  #dm is a string
      new_parent = self.treestore.append(parent,[name + " = " + "\"" + str(dm) + "\"",str(type(dm))])
    else:
      new_parent = self.treestore.append(parent,[name + " = " + str(dm),str(type(dm))])



  def dump_model_callback ( self, widget, extra ):
    print ( "===== Data Model =====" )
    self.dump_data_model ( "Data Model", self.data_model )

  def dump_data_model ( self, name, dm ):
    if type(dm) == type({'a':1}):  #dm is a dictionary
      print ( str(self.dump_depth*"  ") + name + " {}" )
      self.dump_depth += 1
      for k,v in sorted(dm.items()):
        self.dump_data_model ( k, v )
      self.dump_depth += -1
    elif type(dm) == type(['a',1]):  #dm is a list
      print ( str(self.dump_depth*"  ") + name + " []" )
      self.dump_depth += 1
      i = 0
      for v in dm:
        k = name + "["+str(i)+"]"
        self.dump_data_model ( k, v )
        i += 1
      self.dump_depth += -1
    elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')):  #dm is a string
      print ( str(self.dump_depth*"  ") + name + " = " + "\"" + str(dm) + "\"" )
    else:
      print ( str(self.dump_depth*"  ") + name + " = " + str(dm) )



  def dump_keys_callback ( self, widget, extra ):
    print ( "===== Data Model Keys =====" )

    self.data_model_keys = set([])
    key_set = self.get_data_model_keys ( self.data_model, "" )

    key_list = [k for k in key_set]
    key_list.sort()

    for s in key_list:
        print ( s )

  def get_data_model_keys ( self, dm, key_prefix ):
      #global data_model_keys
      if type(dm) == type({'a':1}): # dm is a dictionary
          for k,v in sorted(dm.items()):
              self.get_data_model_keys ( v, key_prefix + "['" + str(k) + "']" )
      elif type(dm) == type(['a',1]): # dm is a list
          i = 0
          for v in dm:
              #get_data_model_keys ( v, key_prefix + "[" + str(i) + "]" )
              self.get_data_model_keys ( v, key_prefix + "[" + "#" + "]" )
              i += 1
      #elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')): # dm is a string
      #    print ( str(data_model_depth*"  ") + "\"" + str(dm) + "\"" )
      else: # dm is anything else
          dm_type = str(type(dm)).split("'")[1]
          self.data_model_keys.update ( [key_prefix + "   (" + dm_type + ")"] )
      return self.data_model_keys



  def dump_data_model ( self, name, dm ):
    if type(dm) == type({'a':1}):  #dm is a dictionary
      print ( str(self.dump_depth*"  ") + name + " {}" )
      self.dump_depth += 1
      for k,v in sorted(dm.items()):
        self.dump_data_model ( k, v )
      self.dump_depth += -1
    elif type(dm) == type(['a',1]):  #dm is a list
      print ( str(self.dump_depth*"  ") + name + " []" )
      self.dump_depth += 1
      i = 0
      for v in dm:
        k = name + "["+str(i)+"]"
        self.dump_data_model ( k, v )
        i += 1
      self.dump_depth += -1
    elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')):  #dm is a string
      print ( str(self.dump_depth*"  ") + name + " = " + "\"" + str(dm) + "\"" )
    else:
      print ( str(self.dump_depth*"  ") + name + " = " + str(dm) )


    


def main():
  gtk.main()
  

data_model_depth = 0
def dump_data_model ( name, dm ):
  global data_model_depth
  if type(dm) == type({'a':1}):  #dm is a dictionary
    print ( str(data_model_depth*"  ") + name + " {}" )
    data_model_depth += 1
    for k,v in sorted(dm.items()):
      dump_data_model ( k, v )
    data_model_depth += -1
  elif type(dm) == type(['a',1]):  #dm is a list
    print ( str(data_model_depth*"  ") + name + " []" )
    data_model_depth += 1
    i = 0
    for v in dm:
      k = name + "["+str(i)+"]"
      dump_data_model ( k, v )
      i += 1
    data_model_depth += -1
  elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')):  #dm is a string
    print ( str(data_model_depth*"  ") + name + " = " + "\"" + str(dm) + "\"" )
  else:
    print ( str(data_model_depth*"  ") + name + " = " + str(dm) )


if __name__ == "__main__":
  dm = {}
  if len(sys.argv) > 1:
    file_name = sys.argv[1]
    print ( "Opening Data Model File: \"" + file_name + "\"" )
    f = open ( file_name, 'r' )
    pickled_model = f.read()
    dm = pickle.loads ( pickled_model.encode('latin1') )
  else:
    # Build a fictional data model for testing
    """
    mols = {}
    mol_list = []
    for i in range(4):
      mol = {}
      mol['mol_name'] = "M" + str(i)
      mol['diff_const'] = str(0.00001*i)
      mol_list = mol_list + [ mol ]
    mols.update ( { 'molecule_list': mol_list } )
    dm.update ( { 'molecules': mols } )
    dm.update ( { 'api_version': 1 } )
    init = {}
    init.update ( { 'iterations': '321' } )
    init.update ( { 'time_step': '1e-6' } )
    dm.update ( { 'initialization': init } )
    dm.update ( { 'compatibility': ['2.67', '2.68', '2.69', '2.70'] } )
    """
  
  dmt = data_model_tree(dm)
  dmt.dump_data_model ( "Data Model", dm )
  
  main()

