use cgmath::{Vector3, Basis3, Decomposed, Matrix4, Deg, Rotation3, Transform};
use time;
use gfx::mesh::Mesh;
use scene::SceneObject;

pub struct MeshObject {
    pub mesh: Mesh,
    pub trans: Decomposed<Vector3<f32>, Basis3<f32>>,
}

impl SceneObject for MeshObject {
    fn render(&self, view: &Decomposed<Vector3<f32>, Basis3<f32>>, proj: &Matrix4<f32>) {
        self.mesh.draw(view, proj);
    }

    fn think(&mut self, time: time::Timespec) {
        let nt = Decomposed::<Vector3<f32>, Basis3<f32>> {
            scale: 1.0,
            rot: Basis3::from_angle_y(Deg(1.0)),
            disp: Vector3::new(0.0, 0.0, 0.0),
        };
        self.trans.concat_self(&nt);

        self.mesh.transform = self.trans.clone().into();        // FIXME: optimize
    }

    fn get_transform(&self) -> Decomposed<Vector3<f32>, Basis3<f32>> {
        self.trans.clone()
    }
}
