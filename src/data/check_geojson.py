import json
from shapely.geometry import shape

with open("data/vector/south_lhonak_aoi.geojson", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Feature count: {len(data['features'])}")
for feat in data["features"]:
    props = feat["properties"]
    geom = shape(feat["geometry"])
    print(f"ID: {props.get('id')} | Name: {props.get('name')}")
    print(f"  Geometry Type: {geom.geom_type}, Is Valid: {geom.is_valid}")
    print(f"  Bounds: minx={geom.bounds[0]:.4f}, miny={geom.bounds[1]:.4f}, maxx={geom.bounds[2]:.4f}, maxy={geom.bounds[3]:.4f}")
