use crate::{Mod, absolute_url, client, getdeps::get_deps_mod};
use regex::Regex;

pub async fn get_mods_list(query: &str) -> Result<Vec<Mod>, reqwest::Error> {
    let mut search_url = url::Url::parse("https://www.curseforge.com/minecraft/search")
        .expect("valid CurseForge search URL");
    search_url
        .query_pairs_mut()
        .append_pair("page", "1")
        .append_pair("pageSize", "9999")
        .append_pair("sortBy", "relevancy")
        .append_pair("search", query);
    let response = client().get(search_url).send().await?;
    let data = response.text().await?;
    let card_re =
        Regex::new(r#"<div class=" project-card">(.*?)</div>\s*<div class=" project-card">"#)
            .unwrap();
    let name_re = Regex::new(r#"class="name"[^>]*><span[^>]*>(.*?)</span>"#).unwrap();
    let author_re = Regex::new(r#"class="author-name"[^>]*>.*?<span[^>]*>(.*?)</span>"#).unwrap();
    let description_re = Regex::new(r#"class="description">(.*?)</p>"#).unwrap();
    let downloads_re = Regex::new(r#"class="detail-downloads">(.*?)</li>"#).unwrap();
    let updated_re = Regex::new(r#"class="detail-updated"><span[^>]*>(.*?)</span>"#).unwrap();
    let game_version_re = Regex::new(r#"class="detail-game-version">(.*?)</li>"#).unwrap();
    let loader_re = Regex::new(r#"class="detail-flavor">(.*?)</li>"#).unwrap();
    let path_re = Regex::new(r#"class="overlay-link"[^>]*href="([^"]+)""#).unwrap();
    let strip_re = Regex::new(r"<[^>]+>").unwrap();
    let mut mods = Vec::new();

    for card_match in card_re.captures_iter(&format!("{data}<div class=\" project-card\">")) {
        let card = &card_match[1];
        let capture = |pattern: &Regex| {
            pattern
                .captures(card)
                .map(|m| m[1].trim().to_owned())
                .unwrap_or_default()
        };
        let path = capture(&path_re);
        let dependencies = if path.is_empty() {
            Vec::new()
        } else {
            get_deps_mod(&path).await?
        };
        mods.push(Mod {
            name: capture(&name_re),
            author: capture(&author_re),
            description: capture(&description_re),
            downloads: capture(&downloads_re),
            updated: capture(&updated_re),
            gameversion: capture(&game_version_re),
            mainmodloader: strip_re
                .replace_all(&capture(&loader_re), "")
                .trim()
                .to_owned(),
            dllink: absolute_url(&path),
            dependencies,
        });
    }
    Ok(mods)
}

pub async fn get_mods_list_json(query: &str) -> Result<String, reqwest::Error> {
    let mods = get_mods_list(query).await?;
    Ok(serde_json::to_string_pretty(&mods).expect("Mod is serializable"))
}
