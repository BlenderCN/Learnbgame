extern crate byteorder;
extern crate cgmath;
extern crate gl;
extern crate glutin;
extern crate png;
extern crate time;
mod gfx;
mod scene;

use std::fs::File;
use std::path::Path;
use time::Duration;
use cgmath::{Vector3,Decomposed,Basis3,Deg,Rotation3,One};
use glutin::GlContext;
use gfx::model::model_loader;

fn init_gl() -> (glutin::EventsLoop, glutin::GlWindow) {
	let events_loop = glutin::EventsLoop::new();
    let window = glutin::WindowBuilder::new().with_title("four-kb");
    let context = glutin::ContextBuilder::new();
    let gl_window = glutin::GlWindow::new(window, context, &events_loop).unwrap();

    // It is essential to make the context current before calling `gl::load_with`.
    let _ = unsafe { gl_window.make_current() };

    // Load the OpenGL function pointers
    gl::load_with(|symbol| gl_window.get_proc_address(symbol) as *const _);

	unsafe {
		gl::Enable(gl::DEPTH_TEST);
		gl::Enable(gl::CULL_FACE);
        gl::FrontFace(gl::CCW);
		
		gl::ActiveTexture(gl::TEXTURE0);
		gl::ActiveTexture(gl::TEXTURE1);
		gl::ActiveTexture(gl::TEXTURE2);
	}

    (events_loop, gl_window)
}

fn main() {
    let (mut events_loop, gl_window) = init_gl();

    let mut scene = scene::Scene {
        objects: Vec::new(),
    };

    let mut file = File::open(&Path::new("assets/mesh.mdl")).unwrap();
    let mdl = model_loader::load_model(&mut file);

    scene.objects.push(Box::new(scene::MeshObject {
        mesh: mdl.into(),
        trans: Decomposed::<Vector3<f32>, Basis3<f32>> {
            scale: 1.0,
            rot: Basis3::one(),
            disp: Vector3::new(0.0, 0.0, -0.5),
        },
    }));

    let view = Decomposed::<Vector3<f32>, Basis3<f32>> {
        scale: 1.0,
        rot: Basis3::one(),
        disp: Vector3::new(0.0, 0.0, 0.0),
    };
    
	let mut proj = cgmath::PerspectiveFov {
		fovy: Deg(90.0).into(),
		aspect: 1.0,                                // placeholder, window will receive resize event on first frame
		near: 0.1,
		far: 100.0,
    };

	let mut running = true;

    let mut frames = 0;
    let mut duration = Duration::zero();

    while running {
        scene.think(time::get_time());

        let time1 = time::get_time();

        unsafe {
            gl::ClearColor(0.3, 0.3, 0.3, 1.0);
            gl::Clear(gl::COLOR_BUFFER_BIT | gl::DEPTH_BUFFER_BIT);
        };

        let proj_mat = proj.into();
        scene.render(&view, &proj_mat);

        gl_window.swap_buffers().unwrap();

		events_loop.poll_events(|event| {
			match event {
				glutin::Event::WindowEvent { event: glutin::WindowEvent::Closed, .. } => {
					running = false;
				},

                glutin::Event::WindowEvent { event: glutin::WindowEvent::Resized(width, height), .. } => {
                    gl_window.resize(width, height);

                    proj = cgmath::PerspectiveFov {
                        fovy: Deg(90.0).into(),
                        aspect: width as f32 / height as f32,
                        near: 0.1,
                        far: 100.0,
                    };

                    unsafe {
                        gl::Viewport(0, 0, width as i32, height as i32);
                    };
                },
				_ => (),
			}
		});

        let time2 = time::get_time();
        let frame_duration = time2 - time1;

        frames = frames + 1;
        duration = duration + frame_duration;

        if duration >= Duration::seconds(1) {
            println!("{} FPS", frames);

            frames = 0;
            duration = Duration::zero();
        };
    };
}
