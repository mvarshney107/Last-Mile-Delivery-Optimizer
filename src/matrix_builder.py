import os
import json
import requests
import pandas as pd

def get_osrm_matrices(csv_path, cache_path="data/osrm_cache.json", force_refresh=False):
    df = pd.read_csv(csv_path)

    # 1. Load from local JSON cache if it exists and refresh isn't forced
    if os.path.exists(cache_path) and not force_refresh:
        print(f"Loading travel matrices from local cache: {cache_path}")
        with open(cache_path, "r") as f:
            cached_data = json.load(f)
        return df, cached_data["time_matrix"], cached_data["dist_matrix"]

    # 2. Otherwise, query the OSRM API
    print("Fetching fresh travel matrices from OSRM API...")
    coords = ";".join(f"{row.lon},{row.lat}" for _, row in df.iterrows())
    url = f"http://router.project-osrm.org/table/v1/driving/{coords}?annotations=duration,distance"
    
    headers = {"User-Agent": "LastMileOptimizerStudentProject/1.0"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    # Convert seconds -> integer minutes, meters -> integer meters
    time_matrix = [[int(round(t / 60)) for t in row] for row in data["durations"]]
    dist_matrix = [[int(round(d)) for d in row] for row in data["distances"]]

    # 3. Save matrices to JSON for future runs
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump({
            "time_matrix": time_matrix,
            "dist_matrix": dist_matrix
        }, f, indent=2)
    print(f"Saved matrices to {cache_path}")

    return df, time_matrix, dist_matrix