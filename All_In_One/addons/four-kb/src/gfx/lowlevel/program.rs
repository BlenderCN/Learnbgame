use gl;
use gl::types::*;
use std::ptr;
use std::str;
use std::ffi::CString;
use std::fs::File;
use std::path::Path;
use std::io::Read;
use cgmath::{Matrix,Matrix4};

pub struct Program {
	pub vs: GLuint,
	pub fs: GLuint,
	pub id: GLuint,
}

impl Program {
	fn compile_shader(src: &str, ty: GLenum) -> GLuint {
		let shader;
		unsafe {
			shader = gl::CreateShader(ty);
			
			// Attempt to compile the shader
			let c_str = CString::new(src.as_bytes()).unwrap();
			gl::ShaderSource(shader, 1, &c_str.as_ptr(), ptr::null());
			gl::CompileShader(shader);

			// Get the compile status
			let mut status = gl::FALSE as GLint;
			gl::GetShaderiv(shader, gl::COMPILE_STATUS, &mut status);

			// Fail on error
            let mut len = 0;
            gl::GetShaderiv(shader, gl::INFO_LOG_LENGTH, &mut len);

            if len > 0 {
				let mut buf = Vec::with_capacity(len as usize);
				buf.set_len((len as usize) - 1); // subtract 1 to skip the trailing null character
				gl::GetShaderInfoLog(shader,
									 len,
									 ptr::null_mut(),
									 buf.as_mut_ptr() as *mut GLchar);
				println!("{}",
					   str::from_utf8(&buf)
						   .ok()
						   .expect("ShaderInfoLog not valid utf8"));
            };

			if status != (gl::TRUE as GLint) {
                panic!("Shader failed to link");
			};
		};
		shader
	}

	pub fn new(vs_text: &str, fs_text: &str) -> Program {
		let vs = Program::compile_shader(vs_text, gl::VERTEX_SHADER);
		let fs = Program::compile_shader(fs_text, gl::FRAGMENT_SHADER);
	
		unsafe {
			let program = gl::CreateProgram();
			gl::AttachShader(program, vs);
			gl::AttachShader(program, fs);
			gl::LinkProgram(program);
			
			// Get the link status
			let mut status = gl::FALSE as GLint;
			gl::GetProgramiv(program, gl::LINK_STATUS, &mut status);

			// Fail on error
            let mut len: GLint = 0;
            gl::GetProgramiv(program, gl::INFO_LOG_LENGTH, &mut len);
            
            if len > 0 {
                let mut buf = Vec::with_capacity(len as usize);
                buf.set_len((len as usize) - 1); // subtract 1 to skip the trailing null character
                
                gl::GetProgramInfoLog(program,
                                      len,
                                      ptr::null_mut(),
                                      buf.as_mut_ptr() as *mut GLchar);
                                      
                println!("{}",
                       str::from_utf8(&buf)
                           .ok()
                           .expect("ProgramInfoLog not valid utf8"));
            }

			if status != (gl::TRUE as GLint) {
                panic!("Shader failed to compile");
			}
			
			Program { vs, fs, id: program }
		}
	}
	
	pub fn from_path(vs_path: &Path, fs_path: &Path) -> Program {
		let vs_text = {
			let mut f = File::open(vs_path).unwrap();
			let mut vs_text = String::new();
			f.read_to_string(&mut vs_text).unwrap();
			
			vs_text
		};
		
		let fs_text = {
			let mut f = File::open(fs_path).unwrap();
			let mut fs_text = String::new();
			f.read_to_string(&mut fs_text).unwrap();
			
			fs_text
		};
		
		Program::new(&vs_text, &fs_text)
	}
	
	pub fn bind(&self) {
		unsafe {
			gl::UseProgram(self.id);
		};
	}
}

impl Drop for Program {
	fn drop(&mut self) {
		unsafe {
			gl::DeleteShader(self.fs);
			gl::DeleteShader(self.vs);
			gl::DeleteProgram(self.id);
		};
	}
}
