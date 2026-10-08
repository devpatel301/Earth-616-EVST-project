import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")

WORLDCLIM_HIST_BASE = "https://geodata.ucdavis.edu/climate/worldclim/2_1/hist/cts4.09/"
SACKS_BASE = "https://sage-public-files.s3.amazonaws.com/crop-calendar-dataset/netcdf5min/"

DOWNLOADS = [
    ("worldclim", "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_prec.zip"),
    *[("worldclim", f"{WORLDCLIM_HIST_BASE}wc2.1_cruts4.09_10m_prec_{period}.zip")
      for period in ["1970-1979", "1980-1989", "1990-1999", "2000-2009", "2010-2019", "2020-2024"]],
    *[("tmax", f"{WORLDCLIM_HIST_BASE}wc2.1_cruts4.09_10m_tmax_{period}.zip")
      for period in ["1970-1979", "1980-1989", "1990-1999", "2000-2009", "2010-2019", "2020-2024"]],
    *[("tmin", f"{WORLDCLIM_HIST_BASE}wc2.1_cruts4.09_10m_tmin_{period}.zip")
      for period in ["1970-1979", "1980-1989", "1990-1999", "2000-2009", "2010-2019", "2020-2024"]],
    ("spam", "https://dataverse.harvard.edu/api/access/datafile/3985008"),
    ("spam", "https://dataverse.harvard.edu/api/access/datafile/3984174"),
    ("sacks", SACKS_BASE + "Rice.crop.calendar.fill.nc.gz"),
    ("sacks", SACKS_BASE + "Rice.2.crop.calendar.fill.nc.gz"),
    ("sacks", SACKS_BASE + "Wheat.crop.calendar.fill.nc.gz"),
    ("sacks", SACKS_BASE + "Wheat.Winter.crop.calendar.fill.nc.gz"),
    ("sacks", SACKS_BASE + "Maize.crop.calendar.fill.nc.gz"),
    ("sacks", SACKS_BASE + "Maize.2.crop.calendar.fill.nc.gz"),
    ("sacks", SACKS_BASE + "Soybeans.crop.calendar.fill.nc.gz"),
    ("sacks", SACKS_BASE + "Rice.crop.calendar.nc.gz"),
    ("sacks", SACKS_BASE + "Rice.2.crop.calendar.nc.gz"),
    ("sacks", SACKS_BASE + "Wheat.crop.calendar.nc.gz"),
    ("sacks", SACKS_BASE + "Wheat.Winter.crop.calendar.nc.gz"),
    ("sacks", SACKS_BASE + "Maize.crop.calendar.nc.gz"),
    ("sacks", SACKS_BASE + "Soybeans.crop.calendar.nc.gz"),
    ("sacks", "https://sage-public-files.s3.amazonaws.com/crop-calendar-dataset/crop-readme.txt"),
    ("faostat", "https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_All_Data_(Normalized).zip"),
    ("faostat", "https://bulks-faostat.fao.org/production/FoodBalanceSheets_E_All_Data_(Normalized).zip"),
    ("naturalearth", "https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_0_countries.zip"),
    ("faostat", "https://bulks-faostat.fao.org/production/Food_Security_Data_E_All_Data_(Normalized).zip"),
    ("faostat", "https://bulks-faostat.fao.org/production/FoodBalanceSheetsHistoric_E_All_Data_(Normalized).zip"),
    ("worldclim", "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_elev.zip"),
    ("usda", "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip"),
]

TARGET_FILENAMES = {
    "3985008": "spam2010v2r0_global_harv_area.geotiff.zip",
    "3984174": "ReadMe_v2r0_Global.txt",
}

USER_AGENT = {"User-Agent": "Mozilla/5.0 (EVS student project)"}
CHUNK_SIZE = 4 << 20
WORKERS_COUNT = 24
HOST_LIMITS = {}


def resolve_url_and_size(target_url):
    request_obj = urllib.request.Request(target_url, headers={**USER_AGENT, "Range": "bytes=0-0"})
    with urllib.request.urlopen(request_obj, timeout=120) as response:
        resolved_url = response.geturl()
        content_range_header = response.headers.get("Content-Range")
        total_size = int(content_range_header.split("/")[-1]) if content_range_header else None
    return resolved_url, total_size


def download_byte_range(download_url, start_byte, end_byte, output_chunk_path, max_retries=8):
    for attempt in range(max_retries):
        try:
            request_obj = urllib.request.Request(
                download_url,
                headers={**USER_AGENT, "Range": f"bytes={start_byte}-{end_byte}"}
            )
            with urllib.request.urlopen(request_obj, timeout=300) as response:
                chunk_bytes = response.read()
            if len(chunk_bytes) == end_byte - start_byte + 1:
                with open(output_chunk_path, "wb") as chunk_file:
                    chunk_file.write(chunk_bytes)
                return
        except Exception as error_msg:
            print(f"       retry {attempt+1} chunk {start_byte}: {error_msg}")
    raise RuntimeError(f"chunk {start_byte}-{end_byte} failed")


def fetch_file(target_folder, source_url):
    filename = source_url.rstrip("/").split("/")[-1]
    filename = TARGET_FILENAMES.get(filename, filename)
    target_dir = os.path.join(RAW_DIR, target_folder)
    os.makedirs(target_dir, exist_ok=True)
    destination_file_path = os.path.join(target_dir, filename)

    if os.path.exists(destination_file_path) and os.path.getsize(destination_file_path) > 0:
        print(f"[skip] {filename}")
        return

    print(f"[get ] {source_url}", flush=True)
    resolved_url, file_size = resolve_url_and_size(source_url)
    if file_size is None:
        request_obj = urllib.request.Request(resolved_url, headers=USER_AGENT)
        with urllib.request.urlopen(request_obj, timeout=600) as response:
            payload = response.read()
        with open(destination_file_path, "wb") as dest_file:
            dest_file.write(payload)
    else:
        temp_chunks_dir = destination_file_path + ".chunks"
        os.makedirs(temp_chunks_dir, exist_ok=True)
        chunk_bytes, worker_threads = HOST_LIMITS.get(target_folder, (CHUNK_SIZE, WORKERS_COUNT))
        chunk_jobs = [
            (
                byte_offset,
                min(byte_offset + chunk_bytes, file_size) - 1,
                os.path.join(temp_chunks_dir, f"{byte_offset:012d}")
            )
            for byte_offset in range(0, file_size, chunk_bytes)
        ]
        pending_jobs = [
            job for job in chunk_jobs
            if not (os.path.exists(job[2]) and os.path.getsize(job[2]) == job[1] - job[0] + 1)
        ]
        with ThreadPoolExecutor(worker_threads) as executor:
            list(executor.map(lambda job_args: download_byte_range(resolved_url, *job_args), pending_jobs))

        partial_path = destination_file_path + ".part"
        with open(partial_path, "wb") as combined_output:
            for _, _, part_path in chunk_jobs:
                with open(part_path, "rb") as part_file:
                    combined_output.write(part_file.read())

        assert os.path.getsize(partial_path) == file_size, "size mismatch"
        os.replace(partial_path, destination_file_path)
        for _, _, part_path in chunk_jobs:
            os.remove(part_path)
        os.rmdir(temp_chunks_dir)
    print(f"       -> {destination_file_path} ({os.path.getsize(destination_file_path)/1e6:.1f} MB)", flush=True)


if __name__ == "__main__":
    folder_filter = sys.argv[1:]
    for folder_name, download_url in DOWNLOADS:
        if not folder_filter or folder_name in folder_filter:
            fetch_file(folder_name, download_url)
