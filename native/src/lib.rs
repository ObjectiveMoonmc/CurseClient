#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct Dependency {
    pub name: String,
    pub author: String,
    pub dllink: String,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct ModFile {
    pub filename: String,
    pub versions: Vec<String>,
    pub loaders: Vec<String>,
    pub uploaded: String,
    pub size: String,
    pub downloads: String,
    pub fileurl: String,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct Mod {
    pub name: String,
    pub author: String,
    pub description: String,
    pub downloads: String,
    pub updated: String,
    pub gameversion: String,
    pub mainmodloader: String,
    pub dllink: String,
    pub dependencies: Vec<Dependency>,
}

pub(crate) fn client() -> reqwest::Client {
    reqwest::Client::builder()
        .user_agent("Mozilla/5.0 (X11; Linux x86_64; rv:155.0) Gecko/20100101 Firefox/155.0")
        .build()
        .expect("valid default HTTP client")
}

pub(crate) fn absolute_url(path: &str) -> String {
    if path.starts_with("http://") || path.starts_with("https://") {
        path.to_owned()
    } else {
        format!("https://www.curseforge.com{path}")
    }
}

pub mod getdeps;
pub mod getjardlurl;
pub mod getldrfiles;
pub mod getmodfiles;
pub mod getmodlist;

pub use getdeps::get_deps_mod;
pub use getjardlurl::get_jardlurl;
pub use getldrfiles::get_ldrfiles;
pub use getmodfiles::get_mod_files;
pub use getmodlist::{get_mods_list, get_mods_list_json};
