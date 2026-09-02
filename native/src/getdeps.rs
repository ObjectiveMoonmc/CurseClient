use crate::{Dependency, client};
use regex::Regex;

pub async fn get_deps_mod(modpath: &str) -> Result<Vec<Dependency>, reqwest::Error> {
    let response = client()
        .get(format!(
            "https://www.curseforge.com{modpath}/relations/dependencies"
        ))
        .send()
        .await?;
    let data = response.text().await?;
    Ok(parse_dependencies(&data))
}

fn parse_dependencies(data: &str) -> Vec<Dependency> {
    let relations_re = Regex::new(r#"relations\\":\[(.*?)\],\\"pagination"#).unwrap();
    let relation_re = Regex::new(
        r#"\{\\"id\\":\d+,\\"name\\":\\"([^\"]*)\\",\\"slug\\":\\"([^\"]*)\\",\\"type\\":\\"[^\"]+\\".*?\\"authorName\\":\\"([^\"]*)\\""#,
    )
    .unwrap();

    let Some(relations) = relations_re.captures(data).map(|m| m[1].to_owned()) else {
        return Vec::new();
    };

    relation_re
        .captures_iter(&relations)
        .map(|relation| {
            let name = relation[1].to_owned();
            let slug = relation[2].to_owned();
            let author = relation[3].to_owned();
            Dependency {
                name,
                author,
                dllink: format!("https://www.curseforge.com/minecraft/mc-mods/{slug}"),
            }
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::parse_dependencies;

    #[test]
    fn parses_embedded_relations() {
        let data = r#"relations\":[{\"id\":1,\"name\":\"Dependency\",\"slug\":\"dependency\",\"type\":\"required\",\"authorName\":\"Author\"}],\"pagination"#;
        let dependencies = parse_dependencies(data);

        assert_eq!(dependencies.len(), 1);
        assert_eq!(dependencies[0].name, "Dependency");
        assert_eq!(dependencies[0].author, "Author");
        assert_eq!(
            dependencies[0].dllink,
            "https://www.curseforge.com/minecraft/mc-mods/dependency"
        );
    }
}
