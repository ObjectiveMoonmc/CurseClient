use crate::client;
use regex::Regex;

pub async fn get_jardlurl(
    fileurl: &str,
    _filename: Option<&str>,
) -> Result<Option<String>, reqwest::Error> {
    let file_re = Regex::new(r"/files/(\d+)$").unwrap();
    let Some(file_match) = file_re.captures(fileurl) else {
        return Ok(None);
    };
    let file_id = &file_match[1];
    let http = client();
    let data = http.get(fileurl).send().await?.text().await?;
    let project_re = Regex::new(r#"\\?"id\\?":(\d+),\\?"gameId\\?":\d+"#).unwrap();
    let Some(project_match) = project_re.captures(&data) else {
        return Ok(None);
    };
    let api_url = format!(
        "https://www.curseforge.com/api/v1/mods/{}/files/{file_id}/download",
        &project_match[1]
    );
    let first = http.get(&api_url).send().await?;
    let first_url = first
        .headers()
        .get(reqwest::header::LOCATION)
        .and_then(|value| value.to_str().ok())
        .unwrap_or(&api_url)
        .to_owned();
    let second = http.get(&first_url).send().await?;
    Ok(Some(
        second
            .headers()
            .get(reqwest::header::LOCATION)
            .and_then(|value| value.to_str().ok())
            .unwrap_or(&first_url)
            .to_owned(),
    ))
}
