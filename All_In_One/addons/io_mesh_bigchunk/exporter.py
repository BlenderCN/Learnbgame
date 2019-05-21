import bpy;
import struct;
from bpy_extras.io_utils import ExportHelper

class BigchunkWriter:
	def __init__(self,dest):
		self.stream=dest;
		self.stream.write(bytes("BIGCHUNK",'UTF-8'));

	def chunkIDWrite(self,chunk_id):
		buffer_out=bytearray(8);
		for i in range(0,min(8,len(chunk_id))):
			buffer_out[i]=ord(chunk_id[i]);
		self.stream.write(buffer_out);

	def chunkSizeWrite(self,size):
		self.stream.write(struct.pack('<Q',size));

	def dataWrite(self,data):
		self.stream.write(data);


import bpy
from bpy_extras.io_utils import ExportHelper

class Exporter(bpy.types.Operator, ExportHelper):
	bl_idname = "export_bigchunk.fmt";
	bl_label = "BIGCHUNK Exporter";
	bl_options = {'PRESET'};

	filename_ext = ".bmo";

	def execute(self, context):
		self.meshGet(context);

		# Set the default return state to FINISHED
		result = {'FINISHED'};

		# Check that the currently selected object contains mesh data for exporting


		# Open the file for writing
		file_out = open(self.filepath, 'bw');
		writer=BigchunkWriter(file_out);

		writer.chunkIDWrite("MODELMET");
		writer.chunkSizeWrite(0);

		writer.chunkIDWrite("FRAME");
		writer.chunkSizeWrite(self.sizeFrame());

		writer.chunkIDWrite("VERTICES");
		writer.chunkSizeWrite(self.sizeVertices());
		self.verticesWrite(writer);

		writer.chunkIDWrite("NORMALS");
		writer.chunkSizeWrite(self.sizeNormals());
		self.normalsWrite(writer);

		writer.chunkIDWrite("UVCOORDS");
		writer.chunkSizeWrite(self.sizeUvCoords());
		self.uvcoordsWrite(writer);

		# Close the file
		file_out.close();

		return result;

	def sizeVertices(self):
		return 4+4*3*len(self.vertices);

	def verticesWrite(self,writer):
		writer.dataWrite(struct.pack("<I",len(self.vertices)));
		for i in self.vertices:
			writer.dataWrite(struct.pack("<fff",i.x,i.y,i.z));

			
	def sizeNormals(self):
		return 4+4*3*len(self.normals);

	def normalsWrite(self,writer):
		writer.dataWrite(struct.pack("<I",len(self.normals)));
		for i in self.normals:
			writer.dataWrite(struct.pack("<fff",i.x,i.y,i.z));

			
	def sizeUvCoords(self):
		return 4+4*2*len(self.uvcoords);

	def uvcoordsWrite(self,writer):
		writer.dataWrite(struct.pack("<I",len(self.uvcoords)));
		for i in self.uvcoords:
			writer.dataWrite(struct.pack("<ff",i.x,i.y));
			

	def sizeFrame(self):
		return 0;

				  
	def meshGet(self,context):
		bpy.ops.object.mode_set(mode='OBJECT');
		ob = context.object;
		if not ob or ob.type != 'MESH':
			raise NameError("Cannot export: object %s is not a mesh" % ob);

		self.vertices=[];
		self.normals=[];
		self.uvcoords=[];

		ob.data.calc_tessface();

		uv_layer =ob.data.uv_layers.active.data;
		ik=0;
		for poly in ob.data.polygons:
			if len(poly.loop_indices) > 3:
				raise Exception("To many vertices in face");
			for il in poly.loop_indices:
				iv = ob.data.loops[il].vertex_index;
				self.vertices.append(ob.data.vertices[iv].co.copy());
				self.normals.append(ob.data.vertices[iv].normal.copy());
				uv_temp=uv_layer[il].uv.copy();
				uv_temp.y=1 - uv_temp.y;
				self.uvcoords.append(uv_temp);
				ik = ik+1;