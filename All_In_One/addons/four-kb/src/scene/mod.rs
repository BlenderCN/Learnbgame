use time;
use cgmath::{Vector3, Basis3, Decomposed, Matrix4};

mod mesh_object;
pub use self::mesh_object::MeshObject;

pub trait SceneObject {
    fn render(&self, view: &Decomposed<Vector3<f32>, Basis3<f32>>, proj: &Matrix4<f32>);
    fn think(&mut self, time: time::Timespec);
    fn get_transform(&self) -> Decomposed<Vector3<f32>, Basis3<f32>>;
}

pub struct Scene {
    pub objects: Vec<Box<SceneObject>>,
}

impl Scene {
    pub fn think(&mut self, time: time::Timespec) {
        for object in &mut self.objects {
            object.think(time);
        };
    }

    pub fn render(&self, view: &Decomposed<Vector3<f32>, Basis3<f32>>, proj: &Matrix4<f32>) {
        for object in &self.objects {
            object.render(view, proj);
        };
    }
}
