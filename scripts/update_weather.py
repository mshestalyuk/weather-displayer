#!/usr/bin/env python3
"""
Fetch current weather + 7-day forecast for Kraków from Open-Meteo
and generate a styled static HTML dashboard.
"""

import json
import os
import requests
from datetime import datetime, timezone, timedelta

# ── Kraków coordinates ──────────────────────────────────────────────
LAT = 50.0647
LON = 19.9450
TIMEZONE = "Europe/Warsaw"

# ── Open-Meteo API (no key required) ───────────────────────────────
API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}"
    "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
    "precipitation,weather_code,wind_speed_10m,wind_direction_10m,"
    "surface_pressure,cloud_cover"
    "&daily=weather_code,temperature_2m_max,temperature_2m_min,"
    "apparent_temperature_max,apparent_temperature_min,"
    "sunrise,sunset,precipitation_sum,precipitation_probability_max,"
    "wind_speed_10m_max"
    "&timezone=Europe%2FWarsaw"
    "&forecast_days=7"
)

# ── Output path (relative to repo root) ───────────────────────────
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "html", "index.html")

# ── WMO Weather Code mapping ──────────────────────────────────────
WMO = {
    0:  ("Clear sky",            "☀️"),
    1:  ("Mainly clear",         "🌤️"),
    2:  ("Partly cloudy",        "⛅"),
    3:  ("Overcast",             "☁️"),
    45: ("Fog",                  "🌫️"),
    48: ("Rime fog",             "🌫️"),
    51: ("Light drizzle",        "🌦️"),
    53: ("Moderate drizzle",     "🌦️"),
    55: ("Dense drizzle",        "🌧️"),
    56: ("Light freezing drizzle","🌧️"),
    57: ("Dense freezing drizzle","🌧️"),
    61: ("Slight rain",          "🌦️"),
    63: ("Moderate rain",        "🌧️"),
    65: ("Heavy rain",           "🌧️"),
    66: ("Light freezing rain",  "🌧️"),
    67: ("Heavy freezing rain",  "🌧️"),
    71: ("Slight snow",          "🌨️"),
    73: ("Moderate snow",        "🌨️"),
    75: ("Heavy snow",           "❄️"),
    77: ("Snow grains",          "❄️"),
    80: ("Slight rain showers",  "🌦️"),
    81: ("Moderate rain showers","🌧️"),
    82: ("Violent rain showers", "⛈️"),
    85: ("Slight snow showers",  "🌨️"),
    86: ("Heavy snow showers",   "❄️"),
    95: ("Thunderstorm",         "⛈️"),
    96: ("Thunderstorm + hail",  "⛈️"),
    99: ("Thunderstorm + heavy hail", "⛈️"),
}


def wmo_label(code):
    return WMO.get(code, ("Unknown", "❓"))


def wind_direction_arrow(deg):
    """Return a compass arrow character for wind direction in degrees."""
    arrows = ["↓", "↙", "←", "↖", "↑", "↗", "→", "↘"]
    idx = round(deg / 45) % 8
    return arrows[idx]


def fetch_weather():
    resp = requests.get(API_URL, timeout=30)
    resp.raise_for_status()
    return resp.json()


def generate_html(data):
    now_utc = datetime.now(timezone.utc)
    now_warsaw = now_utc + timedelta(hours=1)  # CET rough offset
    timestamp = now_utc.strftime("%Y-%m-%d %H:%M UTC")

    cur = data["current"]
    daily = data["daily"]

    code = cur.get("weather_code", 0)
    label, icon = wmo_label(code)
    temp = cur["temperature_2m"]
    feels = cur["apparent_temperature"]
    humidity = cur["relative_humidity_2m"]
    wind = cur["wind_speed_10m"]
    wind_dir = cur.get("wind_direction_10m", 0)
    pressure = cur.get("surface_pressure", "—")
    cloud = cur.get("cloud_cover", "—")
    precip = cur.get("precipitation", 0)

    arrow = wind_direction_arrow(wind_dir)

    # ── Build forecast rows ─────────────────────────────────────────
    forecast_cards = ""
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for i in range(len(daily["time"])):
        d = datetime.strptime(daily["time"][i], "%Y-%m-%d")
        day_label = "Today" if i == 0 else day_names[d.weekday()]
        date_label = d.strftime("%d %b")
        fc_code = daily["weather_code"][i]
        fc_label, fc_icon = wmo_label(fc_code)
        hi = daily["temperature_2m_max"][i]
        lo = daily["temperature_2m_min"][i]
        rain = daily["precipitation_sum"][i]
        prob = daily["precipitation_probability_max"][i]
        wind_max = daily["wind_speed_10m_max"][i]

        sunrise_raw = daily["sunrise"][i]
        sunset_raw = daily["sunset"][i]
        sunrise_t = datetime.fromisoformat(sunrise_raw).strftime("%H:%M")
        sunset_t = datetime.fromisoformat(sunset_raw).strftime("%H:%M")

        forecast_cards += f"""
        <div class="forecast-card {'forecast-today' if i == 0 else ''}">
            <div class="fc-day">{day_label}</div>
            <div class="fc-date">{date_label}</div>
            <div class="fc-icon">{fc_icon}</div>
            <div class="fc-label">{fc_label}</div>
            <div class="fc-temps">
                <span class="fc-hi">{hi:.0f}°</span>
                <span class="fc-lo">{lo:.0f}°</span>
            </div>
            <div class="fc-detail">💧 {rain:.1f} mm ({prob}%)</div>
            <div class="fc-detail">💨 {wind_max:.0f} km/h</div>
            <div class="fc-detail">🌅 {sunrise_t} · 🌇 {sunset_t}</div>
        </div>"""

    # ── Determine background theme ──────────────────────────────────
    if code <= 1:
        bg_class = "theme-clear"
    elif code <= 3:
        bg_class = "theme-cloudy"
    elif code in (45, 48):
        bg_class = "theme-fog"
    elif code >= 95:
        bg_class = "theme-storm"
    elif code >= 71:
        bg_class = "theme-snow"
    elif code >= 51:
        bg_class = "theme-rain"
    else:
        bg_class = "theme-cloudy"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kraków Weather</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ── Reset & base ─────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
    --bg-primary:    #0f1923;
    --bg-card:       rgba(255,255,255,0.06);
    --bg-card-hover: rgba(255,255,255,0.10);
    --text-primary:  #f0f2f5;
    --text-muted:    #8a93a1;
    --accent:        #4fc3f7;
    --accent-warm:   #ffb74d;
    --border:        rgba(255,255,255,0.08);
    --radius:        16px;
}}

/* ── Theme gradients ──────────────────────────────────── */
.theme-clear  {{ --grad: linear-gradient(160deg, #0d1b2a 0%, #1b3a5c 40%, #3a6186 100%); }}
.theme-cloudy {{ --grad: linear-gradient(160deg, #1a1a2e 0%, #2d3250 50%, #424769 100%); }}
.theme-rain   {{ --grad: linear-gradient(160deg, #0f1626 0%, #1a2744 50%, #2c3e6b 100%); }}
.theme-snow   {{ --grad: linear-gradient(160deg, #1c2333 0%, #34495e 50%, #5d7b93 100%); }}
.theme-fog    {{ --grad: linear-gradient(160deg, #1a1a2e 0%, #3d3d5c 50%, #52527a 100%); }}
.theme-storm  {{ --grad: linear-gradient(160deg, #0a0a14 0%, #1a1a30 50%, #2a2040 100%); }}

body {{
    font-family: 'Outfit', sans-serif;
    background: var(--grad, linear-gradient(160deg, #0f1923, #1b3a5c));
    color: var(--text-primary);
    min-height: 100vh;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
}}

/* floating particles */
body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(1.5px 1.5px at 20% 30%, rgba(255,255,255,0.12), transparent),
        radial-gradient(1px 1px at 60% 70%, rgba(255,255,255,0.08), transparent),
        radial-gradient(1.5px 1.5px at 80% 20%, rgba(255,255,255,0.10), transparent);
    pointer-events: none;
    z-index: 0;
}}

.container {{
    position: relative;
    z-index: 1;
    max-width: 960px;
    margin: 0 auto;
    padding: 40px 24px 60px;
}}

/* ── Header ───────────────────────────────────────────── */
header {{
    text-align: center;
    margin-bottom: 48px;
}}
header h1 {{
    font-family: 'DM Serif Display', serif;
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 400;
    letter-spacing: 0.02em;
    margin-bottom: 6px;
}}
header h1 span {{ color: var(--accent); }}
.subtitle {{
    color: var(--text-muted);
    font-size: 0.95rem;
    font-weight: 300;
}}

/* ── Current weather hero ─────────────────────────────── */
.current {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-bottom: 48px;
}}
@media (max-width: 640px) {{
    .current {{ grid-template-columns: 1fr; }}
}}

.hero-card {{
    background: var(--bg-card);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 36px 32px;
    text-align: center;
    position: relative;
    overflow: hidden;
}}
.hero-card::after {{
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at 30% 30%, rgba(79,195,247,0.06), transparent 60%);
    pointer-events: none;
}}
.hero-icon {{
    font-size: 4.5rem;
    line-height: 1;
    margin-bottom: 12px;
    filter: drop-shadow(0 4px 24px rgba(79,195,247,0.25));
}}
.hero-temp {{
    font-family: 'DM Serif Display', serif;
    font-size: 4.5rem;
    line-height: 1;
    margin-bottom: 4px;
}}
.hero-feels {{
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-bottom: 8px;
}}
.hero-label {{
    font-size: 1.1rem;
    font-weight: 500;
    color: var(--accent);
}}

/* ── Detail grid ──────────────────────────────────────── */
.details-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}}
.detail-item {{
    background: var(--bg-card);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 16px;
    transition: background 0.2s;
}}
.detail-item:hover {{ background: var(--bg-card-hover); }}
.detail-label {{
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 4px;
}}
.detail-value {{
    font-size: 1.3rem;
    font-weight: 600;
}}

/* ── Forecast section ─────────────────────────────────── */
.forecast-heading {{
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    margin-bottom: 20px;
}}
.forecast-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(125px, 1fr));
    gap: 14px;
    margin-bottom: 48px;
}}
.forecast-card {{
    background: var(--bg-card);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 14px;
    text-align: center;
    transition: transform 0.2s, background 0.2s;
}}
.forecast-card:hover {{
    transform: translateY(-4px);
    background: var(--bg-card-hover);
}}
.forecast-today {{
    border-color: var(--accent);
    box-shadow: 0 0 24px rgba(79,195,247,0.10);
}}
.fc-day   {{ font-weight: 600; font-size: 0.95rem; }}
.fc-date  {{ font-size: 0.75rem; color: var(--text-muted); margin-bottom: 8px; }}
.fc-icon  {{ font-size: 2rem; margin-bottom: 4px; }}
.fc-label {{ font-size: 0.72rem; color: var(--text-muted); margin-bottom: 10px; min-height: 2em; }}
.fc-temps {{ font-size: 1.05rem; margin-bottom: 8px; }}
.fc-hi    {{ font-weight: 700; color: var(--accent-warm); }}
.fc-lo    {{ font-weight: 400; color: var(--text-muted); margin-left: 6px; }}
.fc-detail {{ font-size: 0.7rem; color: var(--text-muted); line-height: 1.7; }}

/* ── Footer ───────────────────────────────────────────── */
footer {{
    text-align: center;
    padding-top: 24px;
    border-top: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 0.8rem;
}}
footer a {{
    color: var(--accent);
    text-decoration: none;
}}
footer a:hover {{ text-decoration: underline; }}
.timestamp {{
    display: inline-block;
    background: rgba(79,195,247,0.10);
    border: 1px solid rgba(79,195,247,0.20);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.82rem;
    color: var(--accent);
    margin-bottom: 10px;
}}

/* ── Animations ───────────────────────────────────────── */
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(16px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.current, .forecast-heading, .forecast-grid, footer {{
    animation: fadeUp 0.6s ease-out both;
}}
.forecast-grid {{ animation-delay: 0.15s; }}
footer          {{ animation-delay: 0.3s; }}
</style>
</head>
<body class="{bg_class}">
<div class="container">

    <header>
        <h1>🏰 <span>Kraków</span> Weather</h1>
        <p class="subtitle">Latitude {LAT}° N · Longitude {LON}° E · Updated automatically every hour</p>
    </header>

    <!-- ── Current ────────────────────────────────────── -->
    <div class="current">
        <div class="hero-card">
            <div class="hero-icon">{icon}</div>
            <div class="hero-temp">{temp:.1f}°C</div>
            <div class="hero-feels">Feels like {feels:.1f}°C</div>
            <div class="hero-label">{label}</div>
        </div>

        <div class="details-grid">
            <div class="detail-item">
                <div class="detail-label">Humidity</div>
                <div class="detail-value">{humidity}%</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Wind</div>
                <div class="detail-value">{arrow} {wind:.0f} km/h</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Pressure</div>
                <div class="detail-value">{pressure:.0f} hPa</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Cloud cover</div>
                <div class="detail-value">{cloud}%</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Precipitation</div>
                <div class="detail-value">{precip:.1f} mm</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Conditions</div>
                <div class="detail-value">{icon} {label}</div>
            </div>
        </div>
    </div>

    <!-- ── 7-day forecast ─────────────────────────────── -->
    <h2 class="forecast-heading">📅 7-Day Forecast</h2>
    <div class="forecast-grid">
        {forecast_cards}
    </div>

    <!-- ── Footer ─────────────────────────────────────── -->
    <footer>
        <div class="timestamp">🕐 Last updated: {timestamp}</div>
        <p>Data from <a href="https://open-meteo.com/" target="_blank">Open-Meteo API</a> · Auto-updated via GitHub Actions</p>
    </footer>

</div>
</body>
</html>"""
    return html


def main():
    print("Fetching weather data for Kraków…")
    data = fetch_weather()
    print("Generating html/index.html…")
    html = generate_html(data)

    output = os.path.normpath(OUTPUT_PATH)
    os.makedirs(os.path.dirname(output), exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Done ✓  Wrote {output}")


if __name__ == "__main__":
    main()