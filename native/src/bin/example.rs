use native::{get_jardlurl, get_mod_files, get_mods_list};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let query = std::env::args().nth(1).unwrap_or_else(|| "JEI".to_owned());

    let mods = get_mods_list(&query).await?;
    println!(
        "Search results for {query}:\n{}",
        serde_json::to_string_pretty(&mods)?
    );

    let first_mod = mods.first().ok_or("search returned no mods")?;
    println!("\nFiles for first result: {}", first_mod.name);
    let files = get_mod_files(&first_mod.dllink).await?;
    println!("{}", serde_json::to_string_pretty(&files)?);

    let latest_file = files.first().ok_or("first mod has no files")?;
    let download_url = get_jardlurl(&latest_file.fileurl, Some(&latest_file.filename))
        .await?
        .ok_or("could not resolve latest release download URL")?;
    println!(
        "\nLatest release: {}\nDownload URL: {}",
        latest_file.filename, download_url
    );
    Ok(())
}
