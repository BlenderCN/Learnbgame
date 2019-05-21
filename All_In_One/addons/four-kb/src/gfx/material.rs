use std::ptr;
use gl;
use gl::types::*;
use cgmath;
use cgmath::prelude::*;
use cgmath::{Matrix4, Vector3, Basis3, Vector2, Decomposed, PerspectiveFov};
use gfx::image::Image;
use gfx::lowlevel::*;
use gfx::lowlevel::{Program, Uniform};

pub struct Material {
    pub program: Program,
    pub diffuse_tex: Texture,
    pub normal_tex: Texture,
    // pub spec_tex: Texture,
    pub disp_tex: Texture,
}

impl Material {
    pub fn new(program: Program,
               diffuse_image: &Image,
               normal_image: &Image,
               disp_image: &Image) -> Material {

        Material {
            program,
            diffuse_tex: Texture::new("diffuse", diffuse_image),
            normal_tex: Texture::new("normal", normal_image),
            disp_tex: Texture::new("disp", normal_image),
        }
    }

    pub fn bind(&self, uniforms: &[Uniform]) {
		self.diffuse_tex.bind();
		self.normal_tex.bind();
		self.disp_tex.bind();

		self.program.bind();

        for uniform in uniforms {
            uniform.bind(&self.program);
        };
    }
}
