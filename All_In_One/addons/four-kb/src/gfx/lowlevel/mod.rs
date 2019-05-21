use std::mem;
use std::ptr;
use std::str;
use std::ffi::CString;
use gl;
use gl::types::*;
use gfx::image::Image;

pub mod program;
pub mod uniform;
pub mod texture;
pub use self::program::*;
pub use self::uniform::*;
pub use self::texture::*;

pub struct VBO {
	id: GLuint,
}

impl VBO {
	pub fn new<T>(data: &[T]) -> Option<VBO> {
		let mut vbo = VBO { id: 0 };

		if data.len() == 0 {
            panic!("Attempted to create invalid VBO");
		}
		
		unsafe {
			gl::GenBuffers(1, &mut vbo.id);
			gl::BindBuffer(gl::ARRAY_BUFFER, vbo.id);
			gl::BufferData(gl::ARRAY_BUFFER,
						   (data.len() * mem::size_of::<T>()) as GLsizeiptr,
						   mem::transmute(&data[0]),
						   gl::STATIC_DRAW);
		};
		
		Some(vbo)
	}
	
	pub fn bind(&self) {
		unsafe {
			gl::BindBuffer(gl::ARRAY_BUFFER, self.id);
		}
	}
}

impl Drop for VBO {
	fn drop(&mut self) {
		unsafe {
			gl::DeleteBuffers(1, &self.id);
		}
	}
}

pub struct IBO {
	id: GLuint,
}

impl IBO {
	pub fn new<T>(data: &[T]) -> Option<IBO> {
		let mut ibo = IBO { id: 0 };

		if data.len() == 0 {
            panic!("Attempted to create invalid IBO");
		}
		
		unsafe {
			gl::GenBuffers(1, &mut ibo.id);
			gl::BindBuffer(gl::ELEMENT_ARRAY_BUFFER, ibo.id);
			gl::BufferData(gl::ELEMENT_ARRAY_BUFFER,
						   (data.len() * mem::size_of::<T>()) as GLsizeiptr,
						   mem::transmute(&data[0]),
						   gl::STATIC_DRAW);
		};
		
		Some(ibo)
	}
	
	pub fn bind(&self) {
		unsafe {
			gl::BindBuffer(gl::ELEMENT_ARRAY_BUFFER, self.id);
		}
	}
}

impl Drop for IBO {
	fn drop(&mut self) {
		unsafe {
			gl::DeleteBuffers(1, &self.id);
		}
	}
}

pub struct VAO {
	id: GLuint,
	verts: VBO,
    normals: VBO,
	texcoords: VBO,
    tangents: VBO,
}

impl VAO {
	pub fn new(verts: VBO, normals: VBO, texcoords: VBO, tangents: VBO,
               program: &Program) -> VAO {
		let mut vao = VAO { id: 0, verts, normals, texcoords, tangents };

		unsafe {
			gl::GenVertexArrays(1, &mut vao.id);
			gl::BindVertexArray(vao.id);
		};

		VAO::bind_attribute("position", &vao.verts, 3, program);
        VAO::bind_attribute("normal", &vao.normals, 3, program);
		VAO::bind_attribute("tangent", &vao.tangents, 3, program);
		VAO::bind_attribute("texcoord", &vao.texcoords, 2, program);

		VAO::set_frag_data_name("out_color", program);

		vao
	}
	
	pub fn bind(&self) {
		unsafe {
			gl::BindVertexArray(self.id);
		}
	}

	fn bind_attribute(name: &str, vbo: &VBO, num_components: u16, program: &Program) {
		unsafe {
			let attr = gl::GetAttribLocation(program.id, CString::new(name).unwrap().as_ptr());
			gl::EnableVertexAttribArray(attr as GLuint);
			
			vbo.bind();
			gl::VertexAttribPointer(attr as GLuint,
									num_components as i32,
									gl::FLOAT,
									gl::FALSE as GLboolean,
									0,
									ptr::null());
		};
	}

	fn set_frag_data_name(name: &str, program: &Program) {
		unsafe {
			gl::BindFragDataLocation(program.id, 0, CString::new(name).unwrap().as_ptr());
		};
	}
}

impl Drop for VAO {
	fn drop(&mut self) {
		unsafe {
			gl::DeleteVertexArrays(1, &self.id);
		}
	}
}
