use std::mem;
use std::ptr;
use std::str;
use std::ffi::CString;
use gl;
use gl::types::*;
use gfx::image::Image;

pub struct Texture {
    pub name: String,
	pub id: GLuint,
	pub tex_unit: GLuint,
}

static mut TEX_UNITS_USED: GLuint = 0;

impl Texture {
	pub fn new(name: &str, image: &Image) -> Texture {
		let tex_unit = Texture::allocate_tex_unit();
		let mut tex = Texture { name: String::from(name), id: 0, tex_unit };
		let slice = &image.data[0..];
		
		unsafe {
			gl::GenTextures(1, &mut tex.id);
			tex.bind();
			
			gl::TexImage2D(gl::TEXTURE_2D, 0, image.color_type as i32, image.width as i32, image.height as i32, 0, image.color_type, gl::UNSIGNED_BYTE, mem::transmute(&slice[0]));
			
			gl::TexParameteri(gl::TEXTURE_2D, gl::TEXTURE_MIN_FILTER, gl::LINEAR as i32);
			gl::TexParameteri(gl::TEXTURE_2D, gl::TEXTURE_MAG_FILTER, gl::LINEAR as i32);
			
			gl::TexParameteri(gl::TEXTURE_2D, gl::TEXTURE_WRAP_S, gl::CLAMP_TO_EDGE as i32);
			gl::TexParameteri(gl::TEXTURE_2D, gl::TEXTURE_WRAP_T, gl::CLAMP_TO_EDGE as i32);
		};
		
		tex
	}

    fn allocate_tex_unit() -> GLuint {
		unsafe {
			let tex_unit = TEX_UNITS_USED;
			TEX_UNITS_USED += 1;
			tex_unit
		}
    }
	
	pub fn bind(&self) {
		unsafe {
			gl::ActiveTexture(gl::TEXTURE0 + self.tex_unit);
			gl::BindTexture(gl::TEXTURE_2D, self.id);
		};
	}
}

impl Drop for Texture {
	fn drop(&mut self) {
		unsafe {
			gl::DeleteTextures(1, &self.id);
		}
	}
}
