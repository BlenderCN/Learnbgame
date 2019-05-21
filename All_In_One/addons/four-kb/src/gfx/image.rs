use png;
use std::fs::File;
use std::path::Path;
use std::io;
use gl;

#[derive(Debug)]
pub struct Image {
	pub width: u32,
	pub height: u32,
	pub data: Vec<u8>,
	pub color_type: u32,
}

/// Load the image using `png`
pub fn load_image(path: &Path) -> io::Result<Image> {
    let decoder = png::Decoder::new(try!(File::open(path)));
    let (info, mut reader) = try!(decoder.read_info());
    let mut img_data = vec![0; info.buffer_size()];
    try!(reader.next_frame(&mut img_data));
			
	let color_type = match info.color_type {
		png::ColorType::RGB => gl::RGB,
		png::ColorType::RGBA => gl::RGBA,
		_ => panic!("Bad color type"),
	};
    
    Ok(Image {
		width: info.width,
		height: info.height,
		data: img_data,
		color_type: color_type,
	})
}