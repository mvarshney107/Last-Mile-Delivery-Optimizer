import os
import time
import random
import requests
import pandas as pd

def build_ann_arbor_dataset(num_stops=30, seed=42):
    random.seed(seed)
    
    # Resolve path safely so it always saves inside the data/ folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_csv = os.path.join(script_dir, "stops_ann_arbor.csv")

    # Multiple public Overpass mirrors in case the main one is busy
    overpass_urls = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
    ]
    
    query = """
    [out:json][timeout:25];
    node["amenity"~"cafe|restaurant|pharmacy"](42.2400,-83.7800,42.3100,-83.6900);
    out body 60;
    """
    headers = {
        "User-Agent": "LastMileOptimizerStudentProject/1.0 (contact@umich.edu)"
    }

    places = []
    for url in overpass_urls:
        try:
            print(f"Querying {url}...")
            resp = requests.post(url, data={"data": query}, headers=headers, timeout=30)
            if resp.status_code == 200 and resp.text.strip().startswith("{"):
                data = resp.json()
                places = [
                    el for el in data.get("elements", [])
                    if "name" in el.get("tags", {})
                ]
                if len(places) >= num_stops:
                    print(f"Successfully fetched {len(places)} locations!")
                    break
            else:
                print(f"Server returned status {resp.status_code}, trying next mirror...")
        except Exception as e:
            print(f"Request failed ({e}), trying next mirror...")
        time.sleep(1)

    # Row 0: Central Depot (industrial area near State St / I-94)
    rows = [{
        "stop_id": 0,
        "name": "Ann Arbor Central Depot",
        "lat": 42.2450,
        "lon": -83.7380,
        "demand_lbs": 0,
        "window_start_min": 0,
        "window_end_min": 480,
        "service_time_min": 0
    }]

    if len(places) >= num_stops:
        selected = random.sample(places, num_stops)
        for i, place in enumerate(selected, start=1):
            win_start = random.choice([0, 60, 120, 180, 240, 300])
            rows.append({
                "stop_id": i,
                "name": place["tags"]["name"],
                "lat": round(place["lat"], 6),
                "lon": round(place["lon"], 6),
                "demand_lbs": random.randint(50, 250),
                "window_start_min": win_start,
                "window_end_min": win_start + 120,
                "service_time_min": random.choice([5, 10, 15])
            })
    else:
        # Fallback: generate realistic coordinates bounded within Ann Arbor streets
        print("Overpass mirrors busy. Generating fallback coordinates in Ann Arbor...")
        for i in range(1, num_stops + 1):
            win_start = random.choice([0, 60, 120, 180, 240, 300])
            rows.append({
                "stop_id": i,
                "name": f"Customer Stop #{i}",
                "lat": round(random.uniform(42.2450, 42.3050), 6),
                "lon": round(random.uniform(-83.7750, -83.7000), 6),
                "demand_lbs": random.randint(50, 250),
                "window_start_min": win_start,
                "window_end_min": win_start + 120,
                "service_time_min": random.choice([5, 10, 15])
            })

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"Saved {len(df)} locations to {output_csv}")

if __name__ == "__main__":
    build_ann_arbor_dataset()