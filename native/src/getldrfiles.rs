use crate::ModFile;
use regex::Regex;

pub async fn parser(data: &str, base_url: &str) -> Vec<ModFile> {
    let file_id_re = Regex::new(r#"file-details-(\d+)"#).unwrap();
    let name_re = Regex::new(r#"class="name" title="([^"]+)""#).unwrap();
    let download_re = Regex::new(r#"/download/(\d+)"#).unwrap();
    let version_re =
        Regex::new(r#"class="file-row-chip(?: file-row-chip-more)?" title="([^"]+)""#).unwrap();
    let loader_re = Regex::new(r#"class="ellipsis">(Forge|Fabric|NeoForge|Quilt)</span>"#).unwrap();
    let size_re = Regex::new(
        r#"<div class="row-detail"><div class=" tooltip-wrapper"><span>([^<]+(?:KB|MB|GB))</span>"#,
    )
    .unwrap();
    let downloads_re =
        Regex::new(r#"class="row-detail downloads".*?<span class="ellipsis">([^<]+)</span>"#)
            .unwrap();
    let uploaded_re =
        Regex::new(r#"class="row-detail".*?<span>([A-Z][a-z]{2} \d{1,2}, \d{4})</span>"#).unwrap();
    let base = base_url.trim_end_matches('/');

    data.split(r#"<div class=" file-row">"#)
        .skip(1)
        .filter_map(|row| {
            let row = row
                .split(r#"</div><div class="files-results-bar files-results-bar--bottom"#)
                .next()
                .unwrap_or(row);
            let id = file_id_re
                .captures(row)
                .or_else(|| download_re.captures(row))?;
            let name = name_re.captures(row)?;
            Some(ModFile {
                filename: name[1].to_owned(),
                versions: version_re
                    .captures_iter(row)
                    .map(|m| m[1].to_owned())
                    .collect(),
                loaders: loader_re
                    .captures(row)
                    .map(|m| vec![m[1].to_owned()])
                    .unwrap_or_default(),
                uploaded: uploaded_re
                    .captures(row)
                    .map(|m| m[1].to_owned())
                    .unwrap_or_default(),
                size: size_re
                    .captures(row)
                    .map(|m| m[1].to_owned())
                    .unwrap_or_default(),
                downloads: downloads_re
                    .captures(row)
                    .map(|m| m[1].to_owned())
                    .unwrap_or_default(),
                fileurl: format!("{base}/files/{}", &id[1]),
            })
        })
        .collect()
}

pub async fn get_ldrfiles(
    http: &reqwest::Client,
    base_url: &str,
    page: u32,
    page_size: u32,
) -> Result<(Vec<ModFile>, u32), reqwest::Error> {
    let url = format!(
        "{}/files/all?page={page}&pageSize={page_size}&showAlphaFiles=hide",
        base_url.trim_end_matches('/')
    );
    let data = http.get(url).send().await?.text().await?;
    let page_re = Regex::new(r#"<li[^>]*>\s*<button>(\d+)</button>\s*</li>"#).unwrap();
    let pages = page_re
        .captures_iter(&data)
        .filter_map(|m| m[1].parse().ok())
        .max()
        .unwrap_or(page);
    let file_re = Regex::new(r#"\\?"id\\?":(\d+),\\?"fileName\\?":\\?"([^\\"]+)\\?""#).unwrap();
    let fallback_re = Regex::new(r#""id":(\d+),"fileName":"([^"]+)""#).unwrap();
    let mut names = std::collections::HashMap::new();
    for captures in file_re
        .captures_iter(&data)
        .chain(fallback_re.captures_iter(&data))
    {
        if captures[2].to_ascii_lowercase().ends_with(".jar") {
            names.insert(captures[1].to_owned(), captures[2].to_owned());
        }
    }
    let files = parser(&data, base_url)
        .await
        .into_iter()
        .map(|mut file| {
            let id = file.fileurl.rsplit('/').next().unwrap_or_default();
            if let Some(filename) = names.get(id) {
                file.filename = filename.clone();
            }
            file
        })
        .collect();
    Ok((files, pages))
}
