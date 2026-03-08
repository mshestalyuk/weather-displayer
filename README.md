# 🌤️ Kraków Weather Dashboard

A static weather dashboard for Kraków, Poland — automatically updated every hour via GitHub Actions and served through GitHub Pages.

## 🔗 Live Site

👉 **[View the live dashboard](https://<YOUR_GITHUB_USERNAME>.github.io/krakow-weather/)**

> Replace `<YOUR_GITHUB_USERNAME>` with your actual GitHub username after deploying.

---

## 📡 Data Source

This project uses the **[Open-Meteo API](https://open-meteo.com/)** — a free, open-source weather API that requires **no API key** and **no registration**.

**Why Open-Meteo?**
- Completely free with no rate limits for reasonable usage
- No authentication required — perfect for GitHub Actions
- Provides current weather + 7-day forecast
- High-quality data sourced from national weather services
- Covers Kraków coordinates (50.0647°N, 19.9450°E)

---

## ⚙️ How It Works

1. **GitHub Actions** runs on a cron schedule (every hour) or on manual trigger
2. A **Python script** (`update_weather.py`) fetches fresh weather data from the Open-Meteo API
3. The script generates a styled **`index.html`** page with current conditions and a 7-day forecast
4. The workflow **commits and pushes** the updated HTML file
5. **GitHub Pages** automatically deploys the new version

---

## 🚀 How to Run the Workflow Manually

1. Go to the **Actions** tab of this repository
2. Select **"Update Weather Data"** from the left sidebar
3. Click the **"Run workflow"** button on the right
4. Select the branch (default: `main`) and click **"Run workflow"**

Alternatively, use the GitHub CLI:

```bash
gh workflow run update-weather.yml
```

---

## 📁 Project Structure

```
├── .github/
│   └── workflows/
│       └── update-weather.yml   # GitHub Actions workflow (hourly cron)
├── update_weather.py            # Python script to fetch data & generate HTML
├── index.html                   # Generated weather page (auto-updated)
└── README.md                    # This file
```

---

## 🛠️ Setup Instructions

1. **Fork or clone** this repository
2. **Enable GitHub Pages**:
   - Go to Settings → Pages
   - Source: **Deploy from a branch**
   - Branch: `main` / `/ (root)`
   - Save
3. **Enable Actions**:
   - Go to Settings → Actions → General
   - Under "Workflow permissions", select **Read and write permissions**
   - Check **"Allow GitHub Actions to create and approve pull requests"**
   - Save
4. **Update the README** with your actual GitHub Pages URL
5. Optionally **trigger the workflow manually** to get the first data update

---

## 📊 What's Displayed

| Section            | Details                                              |
|--------------------|------------------------------------------------------|
| Current Weather    | Temperature, feels-like, humidity, wind, conditions   |
| Today's Summary    | High/low temperature, precipitation, sunrise/sunset   |
| 7-Day Forecast     | Daily high/low, weather condition, precipitation      |
| Last Updated       | Timestamp of the most recent data fetch              |