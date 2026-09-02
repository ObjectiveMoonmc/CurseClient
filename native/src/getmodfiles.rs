use crate::{ModFile, client, getldrfiles::get_ldrfiles};
use std::collections::HashSet;

pub async fn get_mod_files(dllink: &str) -> Result<Vec<ModFile>, reqwest::Error> {
    let http = client();
    let base = dllink.trim_end_matches('/');
    let (first, total_pages) = get_ldrfiles(&http, base, 1, 50).await?;
    let mut all_files = first;
    for page in 2..=total_pages {
        let (files, _) = get_ldrfiles(&http, base, page, 50).await?;
        all_files.extend(files);
    }

    let mut seen = HashSet::new();
    Ok(all_files
        .into_iter()
        .filter(|file| seen.insert(file.fileurl.clone()))
        .collect())
}
