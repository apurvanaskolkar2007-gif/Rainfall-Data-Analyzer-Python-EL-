
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from pathlib import Path
from io import BytesIO

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

# Data directory
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DEFAULT_CSV = DATA_DIR / "sample_rainfall.csv"


def load_rainfall(file_obj=None):
    source = file_obj if file_obj is not None else DEFAULT_CSV
    df = pd.read_csv(source)

    df.columns = [
        str(c).strip().lower().replace(" ", "_")
        for c in df.columns
    ]

    date_col = next(
        (c for c in df.columns
         if c in ("date", "day", "timestamp")),
        None
    )

    rain_col = next(
        (c for c in df.columns
         if c in (
             "rainfall_mm", "rainfall",
             "precipitation_mm", "precipitation"
         )),
        None
    )

    location_col = next(
        (c for c in df.columns
         if c in ("location", "city", "station")),
        None
    )

    if not date_col or not rain_col:
        raise ValueError(
            "CSV must contain a date column and a rainfall_mm column."
        )

    rename_columns = {
        date_col: "date",
        rain_col: "rainfall_mm"
    }

    if location_col:
        rename_columns[location_col] = "location"

    df = df.rename(columns=rename_columns)

    df["date"] = pd.to_datetime(
        df["date"], errors="coerce"
    )

    df["rainfall_mm"] = pd.to_numeric(
        df["rainfall_mm"], errors="coerce"
    )

    df = df.dropna(
        subset=["date", "rainfall_mm"]
    )

    df = df[df["rainfall_mm"] >= 0].copy()

    if df.empty:
        raise ValueError(
            "No valid rainfall records found in the CSV file."
        )

    if "location" not in df.columns:
        df["location"] = "All locations"

    df["month"] = df["date"].dt.strftime("%b")
    df["month_num"] = df["date"].dt.month
    df["year"] = df["date"].dt.year

    return df.sort_values("date")


def analyze(df):
    total = float(df["rainfall_mm"].sum())
    average = float(df["rainfall_mm"].mean())

    wet_day = df.loc[
        df["rainfall_mm"].idxmax()
    ]

    rainy_days = int(
        (df["rainfall_mm"] > 0).sum()
    )

    dry_days = int(
        (df["rainfall_mm"] == 0).sum()
    )

    monthly = (
        df.groupby(["month_num", "month"])["rainfall_mm"]
        .sum()
        .reset_index()
        .sort_values("month_num")
    )

    yearly = (
        df.groupby("year")["rainfall_mm"]
        .sum()
        .reset_index()
    )

    locations = (
        df.groupby("location")["rainfall_mm"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    return {
        "total": round(total, 2),
        "average": round(average, 2),
        "max_day": round(
            float(wet_day["rainfall_mm"]), 2
        ),
        "max_date": wet_day["date"].strftime(
            "%d %b %Y"
        ),
        "rainy_days": rainy_days,
        "dry_days": dry_days,
        "records": int(len(df)),

        "monthly_labels": monthly["month"].tolist(),
        "monthly_values": [
            round(float(v), 2)
            for v in monthly["rainfall_mm"]
        ],

        "year_labels": [
            str(int(y)) for y in yearly["year"]
        ],
        "year_values": [
            round(float(v), 2)
            for v in yearly["rainfall_mm"]
        ],

        "location_labels": (
            locations["location"].astype(str).tolist()
        ),
        "location_values": [
            round(float(v), 2)
            for v in locations["rainfall_mm"]
        ],

        "table": [
            {
                "date": row.date.strftime("%d %b %Y"),
                "location": str(row.location),
                "rainfall_mm": round(
                    float(row.rainfall_mm), 2
                )
            }
            for row in df.sort_values(
                "date", ascending=False
            ).head(12).itertuples()
        ]
    }


@app.route("/")
def index():
    try:
        df = load_rainfall()
        initial = analyze(df)
    except Exception:
        initial = {}

    return render_template(
        "index.html",
        initial=initial
    )


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    uploaded = request.files.get("file")

    try:
        if uploaded and uploaded.filename:
            if not uploaded.filename.lower().endswith(".csv"):
                return jsonify({
                    "error": "Please upload a CSV file."
                }), 400

            df = load_rainfall(uploaded)
            source = uploaded.filename
        else:
            df = load_rainfall()
            source = "sample_rainfall.csv"

        result = analyze(df)

        result["source"] = source

        result["insight"] = (
            f"You recorded {result['rainy_days']} rainy days "
            f"and {result['dry_days']} dry days. "
            f"The highest daily rainfall was "
            f"{result['max_day']} mm on "
            f"{result['max_date']}."
        )

        return jsonify(result)

    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/download-report", methods=["POST"])
def download_report():
    uploaded = request.files.get("file")

    try:
        if uploaded and uploaded.filename:
            df = load_rainfall(uploaded)
        else:
            df = load_rainfall()

        result = analyze(df)

        report = pd.DataFrame([
            ["Total rainfall (mm)", result["total"]],
            [
                "Average rainfall per record (mm)",
                result["average"]
            ],
            [
                "Highest daily rainfall (mm)",
                result["max_day"]
            ],
            [
                "Date of highest rainfall",
                result["max_date"]
            ],
            ["Rainy days", result["rainy_days"]],
            ["Dry days", result["dry_days"]],
            ["Valid records", result["records"]]
        ], columns=["Metric", "Value"])

        output = BytesIO()

        with pd.ExcelWriter(
            output, engine="openpyxl"
        ) as writer:

            report.to_excel(
                writer,
                index=False,
                sheet_name="Summary"
            )

            df[[
                "date", "location", "rainfall_mm"
            ]].to_excel(
                writer,
                index=False,
                sheet_name="Rainfall Data"
            )

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="rainfall_analysis_report.xlsx",
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(debug=True)


