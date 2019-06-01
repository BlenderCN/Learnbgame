
class objRegion:
  def __init__(self,name):
    self.name = name
    self.faces = []
    self.viz_value = -1
  def set_faces(self,faces):
    self.faces = faces
  def set_viz_value(self,viz_value):
    self.viz_value = viz_value

class mdlObject:
  def __init__(self,name):
    self.name = name
    self.next = None
    self.parent = None
    self.first_child = None
    self.last_child = None
    self.object_type = None
    self.vertices = []
    self.faces = []
    self.regions = {}
    self.cur_reg = None
  def set_next(self,obj):
    self.next = obj
  def set_parent(self,obj):
    self.parent = obj
  def set_first_child(self,obj):
    self.first_child = obj
  def set_last_child(self,obj):
    self.last_child = obj
  def set_object_type(self,obj_type):
    self.object_type = obj_type
  def set_vertices(self,vertices):
    self.vertices = vertices
  def set_faces(self,faces):
    self.faces = faces
  def set_regions(self,regions):
    self.regions = regions

