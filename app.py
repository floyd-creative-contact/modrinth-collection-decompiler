import requests
from bs4 import BeautifulSoup
import streamlit as st
import time

# Constants
COLLECTION_URL = "https://modrinth.com/collection/fGMhGZGh"
HEADERS = {"User-Agent": "ModrinthAPI-Scraper/1.0"}
API_BASE = "https://api.modrinth.com/v2/project"


# Scrape mod IDs from collection page (only once per run)
def get_mod_ids_from_collection(url):
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select('a[href^="/mod/"]')
    mod_ids = set()
    for link in links:
        href = link['href']
        # Extract mod ID from URL: /mod/{mod_id}
        parts = href.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "mod":
            mod_ids.add(parts[1])
    return list(mod_ids)


# Fetch mod info from Modrinth API
def get_mod_data(mod_id):
    try:
        project_resp = requests.get(f"{API_BASE}/{mod_id}", headers=HEADERS)
        project_resp.raise_for_status()
        project_data = project_resp.json()

        versions_resp = requests.get(f"{API_BASE}/{mod_id}/version",
                                     headers=HEADERS)
        versions_resp.raise_for_status()
        versions_data = versions_resp.json()

        forge = False
        fabric = False
        mc_versions = set()

        for version in versions_data:
            loaders = version.get('loaders', [])
            if "fabric" in loaders:
                fabric = True
            if "forge" in loaders:
                forge = True
            mc_versions.update(version.get('game_versions', []))

        return {
            "Name": project_data.get("title"),
            "Mod URL": f"https://modrinth.com/mod/{mod_id}",
            "Forge Modloader": forge,
            "Fabric Modloader": fabric,
            "Minecraft Version 1.20": "1.20" in mc_versions,
            "Minecraft Version 1.20.1": "1.20.1" in mc_versions,
            "All Minecraft Versions Listed": ", ".join(sorted(mc_versions)),
        }
    except Exception as e:
        st.error(f"Failed to fetch data for mod {mod_id}: {e}")
        return None


# Streamlit app
def main():
    st.title("Modrinth Collection Scraper with API")

    if st.button("Scrape Collection and Fetch Mod Data"):
        with st.spinner("Fetching mod IDs from collection..."):
            mod_ids = get_mod_ids_from_collection(COLLECTION_URL)
        st.success(f"Found {len(mod_ids)} mods in collection.")

        all_mod_data = []
        for i, mod_id in enumerate(mod_ids):
            st.write(f"Fetching data for mod {i+1}/{len(mod_ids)}: {mod_id}")
            mod_data = get_mod_data(mod_id)
            if mod_data:
                all_mod_data.append(mod_data)
            time.sleep(1)  # polite delay to avoid hammering API

        if all_mod_data:
            import pandas as pd
            df = pd.DataFrame(all_mod_data)
            st.dataframe(df)
        else:
            st.warning("No mod data fetched.")


if __name__ == "__main__":
    main()
