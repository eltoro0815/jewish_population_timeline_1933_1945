# Data notes

## Spatial resolution

Points are geocoded to city / municipality / memorial-site centroids (WGS84).
Ghetto polygons are represented by approximate centroids of the historical
ghetto footprint where known (Warsaw, Łódź, Kraków, Kovno, Riga, Minsk,
Budapest, Theresienstadt).

## Temporal resolution

Milestone years: 1933, 1935, 1937, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945.
Values approximate year-end or major operational milestones (e.g. ghetto sealing,
peak deportation months, liberation).

## Place types

- `city` — urban Jewish community estimates
- `ghetto` — sealed / designated ghetto populations (may spatially overlap cities)
- `deportation_hub` — transit / concentration holding estimates
- `extermination_site` — prisoner presence estimates (not cumulative deaths)

## Caveats

Figures are secondary, rounded educational estimates for visualization.
Consult USHMM, Yad Vashem, and national archives for research-grade numbers.
See `data/raw/SOURCES.txt`.
