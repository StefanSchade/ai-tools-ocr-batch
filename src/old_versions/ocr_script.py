use clap::{Arg, App};
use enigo::{Direction, Enigo, Key, Keyboard, Settings};
use image::{ImageBuffer, RgbaImage, DynamicImage, ImageOutputFormat, ImageFormat};
use scrap::{Capturer, Display};
use std::error::Error;
use std::path::{Path, PathBuf};
use std::fs::File;
use std::io::BufWriter;
use std::thread;
use std::time::Duration;

fn save_screenshot(buffer: &[u8], width: usize, height: usize, output_dir: &Path, index: usize, total: usize, crop: (usize, usize, usize, usize)) -> Result<(), std::io::Error> {
    let (crop_top, crop_bottom, crop_left, crop_right) = crop;
    let new_width = width - crop_left - crop_right;
    let new_height = height - crop_top - crop_bottom;
    let mut new_buffer = vec![0; new_width * new_height * 4];

    for (new_y, y) in (crop_top..height - crop_bottom).enumerate() {
        for x in 0..new_width {
            let start_new = (new_y * new_width + x) * 4;
            let start_old = ((y * width + x + crop_left) * 4) as usize;

            new_buffer[start_new] = buffer[start_old + 2];     // Red
            new_buffer[start_new + 1] = buffer[start_old + 1]; // Green
            new_buffer[start_new + 2] = buffer[start_old];     // Blue
            new_buffer[start_new + 3] = buffer[start_old + 3]; // Alpha
        }
    }

    let image: RgbaImage = ImageBuffer::from_raw(new_width as u32, new_height as u32, new_buffer)
        .expect("Failed to create image buffer");
    let dynamic_image = DynamicImage::ImageRgba8(image);
    let digits = (total as f32).log10().floor() as usize + 1;
    let filename = output_dir.join(format!("screenshot{:0width$}.jpg", index, width=digits));

    // Save as JPEG with quality setting using a custom encoder
    let fout = File::create(filename)?;
    let mut writer = BufWriter::new(fout);
    let encoder = image::codecs::jpeg::JpegEncoder::new_with_quality(&mut writer, 75);
    encoder.encode_image(&dynamic_image)
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e.to_string()))
}

fn main() -> Result<(), Box<dyn Error>> {
    let matches = App::new("ScreenGrabber")
        .version("1.0")
        .about("Captures and crops screenshots")
        .arg(Arg::with_name("OUTPUT").help("Sets the output directory").required(true).index(1))
        .arg(Arg::with_name("COUNT").help("Sets the number of screenshots").required(true).index(2))
        .arg(Arg::with_name("CROP_TOP").help("Pixels to crop from the top").required(true).index(3))
        .arg(Arg::with_name("CROP_BOTTOM").help("Pixels to crop from the bottom").required(true).index(4))
        .arg(Arg::with_name("CROP_LEFT").help("Pixels to crop from the left").required(true).index(5))
        .arg(Arg::with_name("CROP_RIGHT").help("Pixels to crop from the right").required(true).index(6))
        .get_matches();

    let output_path = PathBuf::from(matches.value_of("OUTPUT").unwrap());
    let count: usize = matches.value_of("COUNT").unwrap().parse()?;
    let crop_top: usize = matches.value_of("CROP_TOP").unwrap().parse()?;
    let crop_bottom: usize = matches.value_of("CROP_BOTTOM").unwrap().parse()?;
    let crop_left: usize = matches.value_of("CROP_LEFT").unwrap().parse()?;
    let crop_right: usize = matches.value_of("CROP_RIGHT").unwrap().parse()?;
