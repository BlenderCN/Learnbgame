use std::ptr;
use std::str;
use std::ffi::CString;
use std::fs::File;
use std::path::Path;
use std::io::Read;
use cgmath::{Matrix,Matrix4};
use gfx::lowlevel::Program;
use gl;
use gl::types::*;

pub trait Uniformable {
    fn bind(&self, name: &str, program: &Program);
}
	
impl Uniformable for Matrix4<f32> {
    fn bind(&self, name: &str, program: &Program) {
        unsafe {
            let loc = gl::GetUniformLocation(program.id, CString::new(name).unwrap().as_ptr());
            gl::UniformMatrix4fv(loc, 1, gl::FALSE, self.as_ptr());
        };
    }
}

impl Uniformable for i32 {
    fn bind(&self, name: &str, program: &Program) {
        unsafe {
            let loc = gl::GetUniformLocation(program.id, CString::new(name).unwrap().as_ptr());
            gl::Uniform1i(loc, *self);
        };
    }
}

impl Uniformable for u32 {
    fn bind(&self, name: &str, program: &Program) {
        unsafe {
            let loc = gl::GetUniformLocation(program.id, CString::new(name).unwrap().as_ptr());
            gl::Uniform1ui(loc, *self);
        };
    }
}

pub struct Uniform<'a> {
    pub name: &'static str,
    pub value: &'a Uniformable,
}

impl<'a> Uniform<'a> {
    pub fn bind(&self, program: &Program) {
        self.value.bind(&self.name, program);
    }
}
