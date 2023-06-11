import axios from "axios";

export async function fetchPlatformsApi() {
  return axios.get("/api/platforms");
}

export async function fetchRomsApi({
  platform,
  cursor = "",
  size = 60,
  searchTerm = "",
}) {
  return axios.get(
    `/api/platforms/${platform}/roms?cursor=${cursor}&size=${size}&search_term=${searchTerm}`
  );
}

export async function fetchRomApi(platform, rom) {
  return axios.get(`/api/platforms/${platform}/roms/${rom}`);
}

export async function downloadRomApi(rom, files) {
  axios
    .get(
      `/api/platforms/${rom.p_slug}/roms/${rom.id}/download?files=${files || rom.files}`,
      {
        responseType: "blob",
      }
    )
    .then((response) => {
      const a = document.createElement("a");
      a.href = window.URL.createObjectURL(new Blob([response.data]));
      a.download = `${rom.r_name}.zip`;
      a.click();
    });
}

export async function updateRomApi(rom, updatedRom) {
  return axios.patch(`/api/platforms/${rom.p_slug}/roms/${rom.id}`, {
    updatedRom,
  });
}

export async function deleteRomApi(rom, deleteFromFs) {
  return axios.delete(
    `/api/platforms/${rom.p_slug}/roms/${rom.id}?filesystem=${deleteFromFs}`
  );
}

export async function searchRomIGDBApi(searchTerm, searchBy, rom) {
  return axios.put(
    `/api/search/roms/igdb?search_term=${searchTerm}&search_by=${searchBy}`,
    { rom: rom }
  );
}
