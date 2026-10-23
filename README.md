# Rainfall Data Analyzer — Phase 3

A responsive, interactive Python web application for exploring rainfall records. Built with Flask, Pandas, Chart.js, HTML and CSS.

## Features
- Animated rain background with a toggle button
- Upload and analyze your own CSV rainfall data
- Total rainfall, average rainfall, rainiest day, rainy days and dry days
- Monthly rainfall trend chart and year-wise comparison
- Recent records table with rainfall intensity labels
- Export summary and cleaned records to an Excel `.xlsx` report
- Responsive layout for laptop and mobile screens
- Includes sample rainfall data so you can test the app immediately

## CSV format
Your CSV should contain:
- `date` — date such as `2025-06-15`
- `rainfall_mm` — numeric rainfall amount in millimetres
- `location` — optional station/city name

Example:

```csv
date,location,rainfall_mm
2025-06-15,Nagpur,41.7
2025-06-16,Nagpur,0
```

## Run on Windows (VS Code)

1. Extract the ZIP file.
2. Open the extracted `Rainfall_Data_Analyzer_Phase3` folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:

   ```powershell
   python -m venv venv
   ```

5. Activate it:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run `venv\\Scripts\\activate.bat`.

6. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

7. Start the website:

   ```powershell
   python app.py
   ```

8. Open **http://127.0.0.1:5000** in your browser.

## One-click Windows launch
You can also double-click `run-local.bat`. It creates a virtual environment if needed, installs requirements, and starts Flask.

## Notes
- Charts load Chart.js from a CDN, so internet access is needed for the chart library and Google Fonts.
- The included data is sample/demo data, not an official meteorological record.
- The app analyzes the rows provided in your CSV; it does not fetch live weather or forecast future rainfall.
