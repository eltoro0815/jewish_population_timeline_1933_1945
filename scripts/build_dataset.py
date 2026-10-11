#!/usr/bin/env python3
"""
Build a city/ghetto/camp-level Jewish population time series for Europe, 1933–1945.

Figures are historically informed order-of-magnitude estimates drawn from
USHMM, Yad Vashem, and standard demographic summaries (pre-war censuses,
ghetto registries, deportation chronologies). Values are rounded and are
NOT a substitute for archival microdata. Coordinates are modern WGS84
centroids of the named places / memorial sites.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

YEARS = [1933, 1935, 1937, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945]

# place_type: city | ghetto | deportation_hub | extermination_site
# Populations for camps are estimated prisoner presence / peak transit
# concentrations at year milestones (not long-term residents).
PLACES: list[dict] = [
    # --- Major urban Jewish communities ---
    {
        "place_id": "warsaw",
        "name": "Warsaw",
        "name_local": "Warszawa",
        "country": "Poland",
        "lat": 52.2297,
        "lon": 21.0122,
        "place_type": "city",
        # Pre-war ~350–380k; ghetto sealed Nov 1940; Großaktion 1942; uprising 1943
        "population": {
            1933: 352000,
            1935: 360000,
            1937: 370000,
            1938: 375000,
            1939: 380000,
            1940: 380000,
            1941: 450000,  # refugees into ghetto area
            1942: 70000,   # after summer deportations to Treblinka
            1943: 5000,    # after uprising / liquidation
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "lodz",
        "name": "Łódź",
        "name_local": "Łódź",
        "country": "Poland",
        "lat": 51.7592,
        "lon": 19.4560,
        "place_type": "city",
        "population": {
            1933: 202000,
            1935: 210000,
            1937: 220000,
            1938: 225000,
            1939: 233000,
            1940: 160000,  # ghetto sealed
            1941: 160000,
            1942: 90000,
            1943: 80000,
            1944: 5000,    # final liquidation summer 1944
            1945: 877,
        },
    },
    {
        "place_id": "krakow",
        "name": "Kraków",
        "name_local": "Kraków",
        "country": "Poland",
        "lat": 50.0647,
        "lon": 19.9450,
        "place_type": "city",
        "population": {
            1933: 56000,
            1935: 58000,
            1937: 60000,
            1938: 64000,
            1939: 68000,
            1940: 55000,
            1941: 20000,  # ghetto
            1942: 6000,
            1943: 0,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "bialystok",
        "name": "Białystok",
        "name_local": "Białystok",
        "country": "Poland",
        "lat": 53.1325,
        "lon": 23.1688,
        "place_type": "city",
        "population": {
            1933: 39000,
            1935: 40000,
            1937: 42000,
            1938: 43000,
            1939: 50000,
            1940: 50000,
            1941: 50000,
            1942: 10000,
            1943: 0,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "lublin",
        "name": "Lublin",
        "name_local": "Lublin",
        "country": "Poland",
        "lat": 51.2465,
        "lon": 22.5684,
        "place_type": "city",
        "population": {
            1933: 39000,
            1935: 40000,
            1937: 41000,
            1938: 42000,
            1939: 43000,
            1940: 40000,
            1941: 34000,
            1942: 2000,
            1943: 0,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "lvov",
        "name": "Lwów / Lviv",
        "name_local": "Lwów",
        "country": "Poland / USSR",
        "lat": 49.8397,
        "lon": 24.0297,
        "place_type": "city",
        "population": {
            1933: 100000,
            1935: 105000,
            1937: 108000,
            1938: 110000,
            1939: 110000,
            1940: 150000,  # refugees
            1941: 100000,
            1942: 20000,
            1943: 0,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "vilnius",
        "name": "Vilnius",
        "name_local": "Wilno",
        "country": "Lithuania / Poland",
        "lat": 54.6872,
        "lon": 25.2797,
        "place_type": "city",
        "population": {
            1933: 55000,
            1935: 57000,
            1937: 58000,
            1938: 59000,
            1939: 60000,
            1940: 60000,
            1941: 40000,
            1942: 15000,
            1943: 2000,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "kaunas",
        "name": "Kaunas",
        "name_local": "Kaunas",
        "country": "Lithuania",
        "lat": 54.8985,
        "lon": 23.9036,
        "place_type": "city",
        "population": {
            1933: 25000,
            1935: 27000,
            1937: 30000,
            1938: 35000,
            1939: 40000,
            1940: 40000,
            1941: 30000,
            1942: 16000,
            1943: 8000,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "berlin",
        "name": "Berlin",
        "name_local": "Berlin",
        "country": "Germany",
        "lat": 52.5200,
        "lon": 13.4050,
        "place_type": "city",
        "population": {
            1933: 160000,
            1935: 150000,
            1937: 140000,
            1938: 120000,  # after Anschluss-era flight wave / Kristallnacht
            1939: 95000,
            1940: 72000,
            1941: 60000,
            1942: 33000,
            1943: 5000,    # Fabrikaktion
            1944: 1500,
            1945: 7000,    # survivors + returning displaced
        },
    },
    {
        "place_id": "frankfurt",
        "name": "Frankfurt am Main",
        "name_local": "Frankfurt",
        "country": "Germany",
        "lat": 50.1109,
        "lon": 8.6821,
        "place_type": "city",
        "population": {
            1933: 26000,
            1935: 24000,
            1937: 22000,
            1938: 14000,
            1939: 10000,
            1940: 6000,
            1941: 3000,
            1942: 500,
            1943: 100,
            1944: 50,
            1945: 200,
        },
    },
    {
        "place_id": "munich",
        "name": "Munich",
        "name_local": "München",
        "country": "Germany",
        "lat": 48.1351,
        "lon": 11.5820,
        "place_type": "city",
        "population": {
            1933: 9000,
            1935: 8000,
            1937: 7000,
            1938: 5000,
            1939: 4000,
            1940: 2500,
            1941: 1500,
            1942: 400,
            1943: 100,
            1944: 50,
            1945: 100,
        },
    },
    {
        "place_id": "vienna",
        "name": "Vienna",
        "name_local": "Wien",
        "country": "Austria",
        "lat": 48.2082,
        "lon": 16.3738,
        "place_type": "city",
        "population": {
            1933: 176000,
            1935: 175000,
            1937: 170000,
            1938: 170000,  # Anschluss March 1938; rapid forced emigration
            1939: 66000,
            1940: 50000,
            1941: 45000,
            1942: 7000,
            1943: 1000,
            1944: 500,
            1945: 4000,
        },
    },
    {
        "place_id": "prague",
        "name": "Prague",
        "name_local": "Praha",
        "country": "Czechoslovakia",
        "lat": 50.0755,
        "lon": 14.4378,
        "place_type": "city",
        "population": {
            1933: 35000,
            1935: 36000,
            1937: 38000,
            1938: 40000,
            1939: 45000,  # refugees from Sudetenland / Germany
            1940: 45000,
            1941: 40000,
            1942: 15000,
            1943: 3000,
            1944: 1000,
            1945: 3000,
        },
    },
    {
        "place_id": "budapest",
        "name": "Budapest",
        "name_local": "Budapest",
        "country": "Hungary",
        "lat": 47.4979,
        "lon": 19.0402,
        "place_type": "city",
        "population": {
            1933: 200000,
            1935: 201000,
            1937: 205000,
            1938: 208000,
            1939: 210000,
            1940: 210000,
            1941: 200000,
            1942: 200000,
            1943: 200000,
            1944: 70000,   # ghetto + Arrow Cross terror; mass deportations May–July
            1945: 100000,  # survivors in city after liberation
        },
    },
    {
        "place_id": "kiev",
        "name": "Kiev",
        "name_local": "Київ",
        "country": "USSR / Ukraine",
        "lat": 50.4501,
        "lon": 30.5234,
        "place_type": "city",
        "population": {
            1933: 140000,
            1935: 150000,
            1937: 160000,
            1938: 170000,
            1939: 175000,
            1940: 175000,
            1941: 20000,   # Babi Yar Sept 1941 and subsequent killings
            1942: 2000,
            1943: 0,
            1944: 0,
            1945: 5000,
        },
    },
    {
        "place_id": "odessa",
        "name": "Odessa",
        "name_local": "Одеса",
        "country": "USSR / Ukraine",
        "lat": 46.4825,
        "lon": 30.7233,
        "place_type": "city",
        "population": {
            1933: 150000,
            1935: 155000,
            1937: 165000,
            1938: 170000,
            1939: 180000,
            1940: 180000,
            1941: 90000,   # Romanian occupation; massacres
            1942: 20000,
            1943: 5000,
            1944: 0,
            1945: 10000,
        },
    },
    {
        "place_id": "minsk",
        "name": "Minsk",
        "name_local": "Мінск",
        "country": "USSR / Belarus",
        "lat": 53.9006,
        "lon": 27.5590,
        "place_type": "city",
        "population": {
            1933: 55000,
            1935: 60000,
            1937: 65000,
            1938: 68000,
            1939: 71000,
            1940: 80000,
            1941: 80000,
            1942: 10000,
            1943: 0,
            1944: 0,
            1945: 2000,
        },
    },
    {
        "place_id": "riga",
        "name": "Riga",
        "name_local": "Rīga",
        "country": "Latvia",
        "lat": 56.9496,
        "lon": 24.1052,
        "place_type": "city",
        "population": {
            1933: 42000,
            1935: 43000,
            1937: 43000,
            1938: 43000,
            1939: 43000,
            1940: 43000,
            1941: 30000,
            1942: 5000,
            1943: 1000,
            1944: 0,
            1945: 150,
        },
    },
    {
        "place_id": "thessaloniki",
        "name": "Thessaloniki",
        "name_local": "Θεσσαλονίκη",
        "country": "Greece",
        "lat": 40.6401,
        "lon": 22.9444,
        "place_type": "city",
        "population": {
            1933: 50000,
            1935: 52000,
            1937: 54000,
            1938: 55000,
            1939: 56000,
            1940: 56000,
            1941: 50000,
            1942: 48000,
            1943: 2000,    # deportations to Auschwitz spring 1943
            1944: 500,
            1945: 2000,
        },
    },
    {
        "place_id": "amsterdam",
        "name": "Amsterdam",
        "name_local": "Amsterdam",
        "country": "Netherlands",
        "lat": 52.3676,
        "lon": 4.9041,
        "place_type": "city",
        "population": {
            1933: 65000,
            1935: 68000,
            1937: 72000,
            1938: 75000,  # German-Jewish refugees
            1939: 80000,
            1940: 79000,
            1941: 75000,
            1942: 50000,
            1943: 15000,
            1944: 5000,
            1945: 10000,
        },
    },
    {
        "place_id": "paris",
        "name": "Paris",
        "name_local": "Paris",
        "country": "France",
        "lat": 48.8566,
        "lon": 2.3522,
        "place_type": "city",
        "population": {
            1933: 150000,
            1935: 160000,
            1937: 170000,
            1938: 180000,
            1939: 200000,
            1940: 150000,
            1941: 120000,
            1942: 80000,   # Vel d'Hiv and subsequent roundups
            1943: 50000,
            1944: 30000,
            1945: 50000,
        },
    },
    {
        "place_id": "brussels",
        "name": "Brussels",
        "name_local": "Bruxelles",
        "country": "Belgium",
        "lat": 50.8503,
        "lon": 4.3517,
        "place_type": "city",
        "population": {
            1933: 30000,
            1935: 32000,
            1937: 35000,
            1938: 40000,
            1939: 45000,
            1940: 40000,
            1941: 35000,
            1942: 20000,
            1943: 8000,
            1944: 3000,
            1945: 15000,
        },
    },
    {
        "place_id": "bucharest",
        "name": "Bucharest",
        "name_local": "București",
        "country": "Romania",
        "lat": 44.4268,
        "lon": 26.1025,
        "place_type": "city",
        "population": {
            1933: 70000,
            1935: 72000,
            1937: 74000,
            1938: 76000,
            1939: 80000,
            1940: 95000,  # refugees from Bessarabia / Bukovina
            1941: 100000,
            1942: 100000,
            1943: 100000,
            1944: 100000,
            1945: 120000,
        },
    },
    {
        "place_id": "salonika_port_note",
        "name": "Salonika Baron Hirsch camp area",
        "name_local": "Θεσσαλονίκη (Baron Hirsch)",
        "country": "Greece",
        "lat": 40.6450,
        "lon": 22.9200,
        "place_type": "deportation_hub",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 0,
            1942: 2000,
            1943: 8000,  # concentration before trains east
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "antwerp",
        "name": "Antwerp",
        "name_local": "Antwerpen",
        "country": "Belgium",
        "lat": 51.2194,
        "lon": 4.4025,
        "place_type": "city",
        "population": {
            1933: 22000,
            1935: 24000,
            1937: 28000,
            1938: 30000,
            1939: 35000,
            1940: 30000,
            1941: 25000,
            1942: 10000,
            1943: 2000,
            1944: 500,
            1945: 5000,
        },
    },
    {
        "place_id": "zagreb",
        "name": "Zagreb",
        "name_local": "Zagreb",
        "country": "Yugoslavia / Croatia",
        "lat": 45.8150,
        "lon": 15.9819,
        "place_type": "city",
        "population": {
            1933: 9000,
            1935: 9500,
            1937: 10000,
            1938: 11000,
            1939: 12000,
            1940: 12000,
            1941: 6000,
            1942: 1000,
            1943: 200,
            1944: 100,
            1945: 1500,
        },
    },
    {
        "place_id": "belgrade",
        "name": "Belgrade",
        "name_local": "Beograd",
        "country": "Yugoslavia",
        "lat": 44.7866,
        "lon": 20.4489,
        "place_type": "city",
        "population": {
            1933: 8000,
            1935: 8500,
            1937: 9000,
            1938: 9500,
            1939: 10000,
            1940: 10000,
            1941: 3000,
            1942: 500,
            1943: 100,
            1944: 50,
            1945: 1000,
        },
    },
    {
        "place_id": "rome",
        "name": "Rome",
        "name_local": "Roma",
        "country": "Italy",
        "lat": 41.9028,
        "lon": 12.4964,
        "place_type": "city",
        "population": {
            1933: 11000,
            1935: 11000,
            1937: 11000,
            1938: 11000,
            1939: 11000,
            1940: 11000,
            1941: 11000,
            1942: 11000,
            1943: 7000,  # Oct 1943 roundup
            1944: 5000,
            1945: 8000,
        },
    },
    {
        "place_id": "copenhagen",
        "name": "Copenhagen",
        "name_local": "København",
        "country": "Denmark",
        "lat": 55.6761,
        "lon": 12.5683,
        "place_type": "city",
        "population": {
            1933: 6000,
            1935: 6500,
            1937: 7000,
            1938: 7500,
            1939: 8000,
            1940: 8000,
            1941: 8000,
            1942: 8000,
            1943: 500,   # most rescued to Sweden Oct 1943
            1944: 400,
            1945: 7000,
        },
    },
    {
        "place_id": "oslo",
        "name": "Oslo",
        "name_local": "Oslo",
        "country": "Norway",
        "lat": 59.9139,
        "lon": 10.7522,
        "place_type": "city",
        "population": {
            1933: 1400,
            1935: 1500,
            1937: 1600,
            1938: 1700,
            1939: 1800,
            1940: 1800,
            1941: 1500,
            1942: 500,
            1943: 100,
            1944: 50,
            1945: 800,
        },
    },
    # --- Ghettos (concentrated urban populations; may overlap city series) ---
    {
        "place_id": "warsaw_ghetto",
        "name": "Warsaw Ghetto",
        "name_local": "Getto warszawskie",
        "country": "Poland",
        "lat": 52.2460,
        "lon": 20.9950,
        "place_type": "ghetto",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 380000,
            1941: 450000,
            1942: 60000,
            1943: 0,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "lodz_ghetto",
        "name": "Łódź Ghetto (Litzmannstadt)",
        "name_local": "Getto łódzkie",
        "country": "Poland",
        "lat": 51.7750,
        "lon": 19.4550,
        "place_type": "ghetto",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 160000,
            1941: 160000,
            1942: 90000,
            1943: 80000,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "krakow_ghetto",
        "name": "Kraków Ghetto",
        "name_local": "Getto krakowskie",
        "country": "Poland",
        "lat": 50.0450,
        "lon": 19.9550,
        "place_type": "ghetto",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 18000,
            1942: 6000,
            1943: 0,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "theresienstadt",
        "name": "Theresienstadt / Terezín",
        "name_local": "Terezín",
        "country": "Czechoslovakia",
        "lat": 50.5110,
        "lon": 14.1500,
        "place_type": "ghetto",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 7000,
            1942: 58000,
            1943: 40000,
            1944: 30000,
            1945: 17000,  # liberated May 1945
        },
    },
    {
        "place_id": "budapest_ghetto",
        "name": "Budapest Ghetto",
        "name_local": "Budapesti gettó",
        "country": "Hungary",
        "lat": 47.4950,
        "lon": 19.0600,
        "place_type": "ghetto",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 0,
            1942: 0,
            1943: 0,
            1944: 70000,
            1945: 0,
        },
    },
    {
        "place_id": "kovno_ghetto",
        "name": "Kovno Ghetto",
        "name_local": "Kauno getas",
        "country": "Lithuania",
        "lat": 54.9150,
        "lon": 23.8900,
        "place_type": "ghetto",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 30000,
            1942: 16000,
            1943: 8000,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "riga_ghetto",
        "name": "Riga Ghetto",
        "name_local": "Rīgas geto",
        "country": "Latvia",
        "lat": 56.9400,
        "lon": 24.1300,
        "place_type": "ghetto",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 30000,
            1942: 5000,
            1943: 0,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "minsk_ghetto",
        "name": "Minsk Ghetto",
        "name_local": "Мінскае гета",
        "country": "USSR / Belarus",
        "lat": 53.9050,
        "lon": 27.5450,
        "place_type": "ghetto",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 80000,
            1942: 10000,
            1943: 0,
            1944: 0,
            1945: 0,
        },
    },
    # --- Deportation hubs ---
    {
        "place_id": "drancy",
        "name": "Drancy internment camp",
        "name_local": "Drancy",
        "country": "France",
        "lat": 48.9230,
        "lon": 2.4450,
        "place_type": "deportation_hub",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 4000,
            1942: 5000,
            1943: 4000,
            1944: 2000,
            1945: 0,
        },
    },
    {
        "place_id": "westerbork",
        "name": "Westerbork transit camp",
        "name_local": "Westerbork",
        "country": "Netherlands",
        "lat": 52.9170,
        "lon": 6.6070,
        "place_type": "deportation_hub",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 1000,
            1940: 1100,
            1941: 1500,
            1942: 10000,
            1943: 10000,
            1944: 5000,
            1945: 900,
        },
    },
    {
        "place_id": "malines",
        "name": "Mechelen / Malines transit camp",
        "name_local": "Mechelen (Dossin)",
        "country": "Belgium",
        "lat": 51.0280,
        "lon": 4.4780,
        "place_type": "deportation_hub",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 0,
            1942: 2000,
            1943: 1500,
            1944: 500,
            1945: 0,
        },
    },
    {
        "place_id": "umschlagsplatz_warsaw",
        "name": "Umschlagplatz Warsaw",
        "name_local": "Umschlagplatz",
        "country": "Poland",
        "lat": 52.2520,
        "lon": 20.9880,
        "place_type": "deportation_hub",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 0,
            1942: 15000,  # peak daily holding during Großaktion
            1943: 2000,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "kolejowa_lodz",
        "name": "Łódź Radegast station",
        "name_local": "Stacja Radegast",
        "country": "Poland",
        "lat": 51.8000,
        "lon": 19.4700,
        "place_type": "deportation_hub",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 2000,
            1942: 5000,
            1943: 2000,
            1944: 8000,
            1945: 0,
        },
    },
    # --- Extermination / killing sites (estimated prisoner presence at milestones) ---
    {
        "place_id": "auschwitz",
        "name": "Auschwitz-Birkenau",
        "name_local": "Oświęcim",
        "country": "Poland",
        "lat": 50.0359,
        "lon": 19.1783,
        "place_type": "extermination_site",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 1000,
            1941: 10000,
            1942: 40000,
            1943: 80000,
            1944: 90000,  # incl. Hungarian deportation peak
            1945: 7000,   # remaining at liberation Jan 1945
        },
    },
    {
        "place_id": "treblinka",
        "name": "Treblinka",
        "name_local": "Treblinka",
        "country": "Poland",
        "lat": 52.6316,
        "lon": 22.0531,
        "place_type": "extermination_site",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 0,
            1942: 1000,  # mostly immediate murder; small Sonderkommando
            1943: 500,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "belzec",
        "name": "Bełżec",
        "name_local": "Bełżec",
        "country": "Poland",
        "lat": 50.3717,
        "lon": 23.4575,
        "place_type": "extermination_site",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 0,
            1942: 500,
            1943: 0,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "sobibor",
        "name": "Sobibór",
        "name_local": "Sobibór",
        "country": "Poland",
        "lat": 51.4467,
        "lon": 23.5950,
        "place_type": "extermination_site",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 0,
            1942: 600,
            1943: 600,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "chelmno",
        "name": "Chełmno / Kulmhof",
        "name_local": "Chełmno nad Nerem",
        "country": "Poland",
        "lat": 52.1540,
        "lon": 18.7230,
        "place_type": "extermination_site",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 100,
            1942: 200,
            1943: 0,
            1944: 100,
            1945: 0,
        },
    },
    {
        "place_id": "majdanek",
        "name": "Majdanek",
        "name_local": "Majdanek",
        "country": "Poland",
        "lat": 51.2220,
        "lon": 22.6000,
        "place_type": "extermination_site",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 5000,
            1942: 15000,
            1943: 20000,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "babyn_yar",
        "name": "Babi Yar",
        "name_local": "Бабин Яр",
        "country": "USSR / Ukraine",
        "lat": 50.4710,
        "lon": 30.4490,
        "place_type": "extermination_site",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 0,  # killing site, not residence; city series captures drop
            1942: 0,
            1943: 0,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "ponary",
        "name": "Ponary / Paneriai",
        "name_local": "Paneriai",
        "country": "Lithuania",
        "lat": 54.6260,
        "lon": 25.1670,
        "place_type": "extermination_site",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 0,
            1942: 0,
            1943: 0,
            1944: 0,
            1945: 0,
        },
    },
    {
        "place_id": "bergen_belsens",
        "name": "Bergen-Belsen",
        "name_local": "Bergen-Belsen",
        "country": "Germany",
        "lat": 52.7580,
        "lon": 9.9070,
        "place_type": "deportation_hub",
        "population": {
            1933: 0,
            1935: 0,
            1937: 0,
            1938: 0,
            1939: 0,
            1940: 0,
            1941: 0,
            1942: 0,
            1943: 4000,
            1944: 15000,
            1945: 60000,  # overcrowding at liberation Apr 1945
        },
    },
    {
        "place_id": "dachau",
        "name": "Dachau",
        "name_local": "Dachau",
        "country": "Germany",
        "lat": 48.2699,
        "lon": 11.4683,
        "place_type": "deportation_hub",
        "population": {
            1933: 2000,
            1935: 2500,
            1937: 3000,
            1938: 10000,
            1939: 4000,
            1940: 5000,
            1941: 6000,
            1942: 8000,
            1943: 12000,
            1944: 22000,
            1945: 30000,
        },
    },
]


SOURCES = """\
Primary reference classes (aggregated secondary estimates):
- USHMM Holocaust Encyclopedia (community and camp pages)
- Yad Vashem / Encyclopedia of Camps and Ghettos (USHMM / Indiana UP)
- Pre-war Polish, German, Austrian, Hungarian, Dutch, Greek censuses / community tallies
- Ghetto population registries (Warsaw, Łódź, Kovno, Riga, Minsk, Theresienstadt)
- Deportation chronologies for Drancy, Westerbork, Mechelen, Radegast, Umschlagplatz

Notes:
- City and ghetto series can overlap spatially for the same metropolitan area;
  visualization scripts may filter by place_type.
- Camp "population" is estimated prisoner presence at year-end / milestone,
  not cumulative murders.
- Killing sites without residential holding (Babi Yar, Ponary) are geocoded
  with zero residential population; the urban drop is in the city series.
"""


def rows_for_places() -> list[dict]:
    rows: list[dict] = []
    for place in PLACES:
        for year in YEARS:
            pop = int(place["population"].get(year, 0))
            rows.append(
                {
                    "place_id": place["place_id"],
                    "name": place["name"],
                    "name_local": place["name_local"],
                    "country": place["country"],
                    "latitude": place["lat"],
                    "longitude": place["lon"],
                    "place_type": place["place_type"],
                    "year": year,
                    "jewish_population": pop,
                }
            )
    return rows


def write_places_catalog(path: Path) -> None:
    catalog = []
    for p in PLACES:
        catalog.append(
            {
                "place_id": p["place_id"],
                "name": p["name"],
                "name_local": p["name_local"],
                "country": p["country"],
                "latitude": p["lat"],
                "longitude": p["lon"],
                "place_type": p["place_type"],
            }
        )
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "place_id",
                "name",
                "name_local",
                "country",
                "latitude",
                "longitude",
                "place_type",
            ],
        )
        writer.writeheader()
        writer.writerows(catalog)


def write_timeseries_csv(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "place_id",
                "name",
                "name_local",
                "country",
                "latitude",
                "longitude",
                "place_type",
                "year",
                "jewish_population",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_geojson(rows: list[dict], path: Path) -> None:
    # One FeatureCollection with a property bag per year on each place,
    # plus a long-form FeatureCollection for animation joins.
    by_place: dict[str, dict] = {}
    for r in rows:
        pid = r["place_id"]
        if pid not in by_place:
            by_place[pid] = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [r["longitude"], r["latitude"]],
                },
                "properties": {
                    "place_id": pid,
                    "name": r["name"],
                    "name_local": r["name_local"],
                    "country": r["country"],
                    "place_type": r["place_type"],
                    "population_by_year": {},
                },
            }
        by_place[pid]["properties"]["population_by_year"][str(r["year"])] = r[
            "jewish_population"
        ]

    wide = {"type": "FeatureCollection", "features": list(by_place.values())}
    path.write_text(json.dumps(wide, ensure_ascii=False, indent=2), encoding="utf-8")

    long_features = []
    for r in rows:
        if r["jewish_population"] <= 0:
            continue
        long_features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [r["longitude"], r["latitude"]],
                },
                "properties": {
                    "place_id": r["place_id"],
                    "name": r["name"],
                    "place_type": r["place_type"],
                    "year": r["year"],
                    "jewish_population": r["jewish_population"],
                },
            }
        )
    long_path = path.with_name("jewish_population_long.geojson")
    long_path.write_text(
        json.dumps(
            {"type": "FeatureCollection", "features": long_features},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def write_density_grid(rows: list[dict], path: Path) -> None:
    """
    Aggregate city+ghetto populations onto a coarse lon/lat grid for 3D
    density extrusion (extermination sites excluded from residential density).
    """
    import math

    cell = 0.75  # degrees (~50–80 km)
    include = {"city", "ghetto"}
    grid_rows = []
    for year in YEARS:
        buckets: dict[tuple[int, int], float] = {}
        for r in rows:
            if r["year"] != year or r["place_type"] not in include:
                continue
            if r["jewish_population"] <= 0:
                continue
            gi = int(math.floor(r["latitude"] / cell))
            gj = int(math.floor(r["longitude"] / cell))
            buckets[(gi, gj)] = buckets.get((gi, gj), 0.0) + float(
                r["jewish_population"]
            )
        for (gi, gj), pop in sorted(buckets.items()):
            lat = (gi + 0.5) * cell
            lon = (gj + 0.5) * cell
            # Approximate local density proxy: population per cell area (deg^2)
            density = pop / (cell * cell)
            grid_rows.append(
                {
                    "year": year,
                    "grid_i": gi,
                    "grid_j": gj,
                    "latitude": round(lat, 4),
                    "longitude": round(lon, 4),
                    "population_sum": int(pop),
                    "density_proxy": round(density, 2),
                }
            )

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "year",
                "grid_i",
                "grid_j",
                "latitude",
                "longitude",
                "population_sum",
                "density_proxy",
            ],
        )
        writer.writeheader()
        writer.writerows(grid_rows)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    rows = rows_for_places()
    write_places_catalog(RAW / "places_catalog.csv")
    (RAW / "SOURCES.txt").write_text(SOURCES, encoding="utf-8")
    write_timeseries_csv(rows, PROCESSED / "jewish_population_timeseries.csv")
    write_geojson(rows, PROCESSED / "jewish_population_by_place.geojson")
    write_density_grid(rows, PROCESSED / "jewish_density_grid.csv")

    # Point-level density for column extrusion (population as height)
    point_density = PROCESSED / "jewish_population_points.csv"
    write_timeseries_csv(rows, point_density)

    n_places = len(PLACES)
    print(f"Wrote {len(rows)} rows for {n_places} places across {len(YEARS)} years")
    print(f"  {RAW / 'places_catalog.csv'}")
    print(f"  {PROCESSED / 'jewish_population_timeseries.csv'}")
    print(f"  {PROCESSED / 'jewish_population_by_place.geojson'}")
    print(f"  {PROCESSED / 'jewish_density_grid.csv'}")


if __name__ == "__main__":
    main()
