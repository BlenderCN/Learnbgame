use std::iter::Iterator;
use std::path::Path;
use cgmath::{Vector2, Vector3, Matrix4};
use gfx::mesh::Mesh;
use gfx::image;
use gfx::lowlevel::program::Program;

pub mod model_loader;

#[derive(Debug)]
pub struct Texture {
	pub size: Vector2<u16>,
	pub pixels: Box<[Vector3<u8>]>,
}

#[derive(Debug)]
pub struct Material {
	pub name: String,
	pub shader_vertex: String,
	pub shader_fragment: String,
	pub normals: Option<Texture>,
	pub diffuse: Option<Texture>,
	pub specular: Option<Texture>,
}

#[derive(Debug)]
pub struct Model {
	pub name: String,
	pub transform: Matrix4<f32>,
	pub materials: Box<[Material]>,
    pub indices: Box<[u32]>,
	pub vertices: Box<[Vector3<f32>]>,
	pub normals: Box<[Vector3<f32>]>,
    pub tangents: Box<[Vector3<f32>]>,
	pub texcoords: Box<[Vector2<f32>]>,
}

impl From<Model> for Mesh {
    fn from(model: Model) -> Mesh {
        let image = image::load_image(&Path::new("assets/diffuse.png")).unwrap();
        let normal_map = image::load_image(&Path::new("assets/normals.png")).unwrap();
        let disp_map = image::load_image(&Path::new("assets/displacement.png")).unwrap();
		let program = Program::from_path(&Path::new("assets/shader.vert"), &Path::new("assets/shader.frag"));

        Mesh::new(program, &model.indices[0..], &model.vertices[0..], &model.normals[0..], 
                  &model.texcoords[0..], &model.tangents[0..], &image, 
                  &normal_map, &disp_map, model.transform)
    }
}
