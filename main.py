import requests
from bs4 import BeautifulSoup
import streamlit as st
import time
import pandas as pd

COLLECTION_URL_DEFAULT = "https://modrinth.com/collection/fGMhGZGh"
HEADERS = {"User-Agent": "ModrinthAPI-Scraper/1.0"}
API_BASE = "https://api.modrinth.com/v2/project"

def get_mod_ids_from_collection(url):
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select('a[href^="/mod/"]')
    mod_ids = set()
    for link in links:
        href = link['href']
        parts = href.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "mod":
            mod_ids.add(parts[1])
    return list(mod_ids)

def get_mod_data(mod_id, selected_versions, include_fabric, include_forge):
    try:
        project_resp = requests.get(f"{API_BASE}/{mod_id}", headers=HEADERS)
        project_resp.raise_for_status()
        project_data = project_resp.json()

        versions_resp = requests.get(f"{API_BASE}/{mod_id}/version", headers=HEADERS)
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

        version_flags = {
            "Minecraft Version 1.19.x": any(v.startswith("1.19") for v in mc_versions),
            "Minecraft Version 1.20.x": any(v.startswith("1.20") for v in mc_versions),
            "Minecraft Version 1.21.x": any(v.startswith("1.21") for v in mc_versions),
        }

        data = {
            "Name": project_data.get("title"),
            "Mod URL": f"https://modrinth.com/mod/{mod_id}",
            "Forge Modloader": forge,
            "Fabric Modloader": fabric,
            "All Minecraft Versions Listed": ", ".join(sorted(mc_versions)),
        }

        for version_label, value in version_flags.items():
            if version_label in selected_versions:
                data[version_label] = value

        return data
    except Exception as e:
        st.error(f"Failed to fetch data for mod {mod_id}: {e}")
        return None

def main():
    st.title("Modrinth Collection Scraper with API")

    collection_url = st.text_input("Collection URL", COLLECTION_URL_DEFAULT)

    st.markdown("### Select Fields to Extract")
    include_fabric = st.checkbox("Include Fabric Modloader", value=True)
    include_forge = st.checkbox("Include Forge Modloader", value=True)
    selected_versions = []
    if st.checkbox("Include Minecraft 1.19.x", value=True):
        selected_versions.append("Minecraft Version 1.19.x")
    if st.checkbox("Include Minecraft 1.20.x", value=True):
        selected_versions.append("Minecraft Version 1.20.x")
    if st.checkbox("Include Minecraft 1.21.x", value=True):
        selected_versions.append("Minecraft Version 1.21.x")

    if st.button("Scrape Collection and Fetch Mod Data"):
        with st.spinner("Fetching mod IDs from collection..."):
            mod_ids = get_mod_ids_from_collection(collection_url)
        st.success(f"Found {len(mod_ids)} mods in collection.")

        all_mod_data = []
        for i, mod_id in enumerate(mod_ids):
            st.write(f"Fetching data for mod {i+1}/{len(mod_ids)}: {mod_id}")
            mod_data = get_mod_data(mod_id, selected_versions, include_fabric, include_forge)
            if mod_data:
                all_mod_data.append(mod_data)
            time.sleep(0.5)  # polite delay

        if all_mod_data:
            df = pd.DataFrame(all_mod_data)
            st.dataframe(df)
        else:
            st.warning("No mod data fetched.")

if __name__ == "__main__":
    main()
