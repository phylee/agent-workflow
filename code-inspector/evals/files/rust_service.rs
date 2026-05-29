use std::fs;

pub unsafe fn copy_unchecked(src: *const u8, dst: *mut u8, len: usize) {
    std::ptr::copy_nonoverlapping(src, dst, len);
}

pub fn load_config(path: &str) -> String {
    fs::read_to_string(path).unwrap()
}

pub fn parse_port(value: Option<&str>) -> u16 {
    value.unwrap().parse::<u16>().unwrap()
}
