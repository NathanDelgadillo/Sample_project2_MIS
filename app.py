from flask import Flask, render_template, request, url_for
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Load dataset
df = pd.read_csv("TableauSalesData.csv")

# Create chart directory if missing
os.makedirs("static/charts", exist_ok=True)


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def index():
    categories = sorted(df["Category"].dropna().unique())
    subcategories = sorted(df["Sub-Category"].dropna().unique())
    regions = sorted(df["Region"].dropna().unique())
    segments = sorted(df["Segment"].dropna().unique())

    return render_template(
        "index.html",
        categories=categories,
        subcategories=subcategories,
        regions=regions,
        segments=segments,
    )


# -----------------------------
# RESULTS PAGE
# -----------------------------
@app.route("/results", methods=["POST"])
def results():
    category = request.form["category"]
    subcategory = request.form["subcategory"]
    region = request.form["region"]
    segment = request.form["segment"]
    query = request.form["query"]

    # Filter data
    filtered = df[
        (df["Category"] == category) &
        (df["Sub-Category"] == subcategory) &
        (df["Region"] == region) &
        (df["Segment"] == segment)
    ]

    # Decide which query to run
    chart_path = None

    if query == "total_sales":
        result = filtered.groupby("Sub-Category")["Sales"].sum().reset_index()
        title = "Total Sales"
        filename = "chart_total_sales.png"

        plt.figure()
        plt.bar(result["Sub-Category"], result["Sales"])
        plt.xticks(rotation=45)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(f"static/charts/{filename}")
        plt.close()

        chart_path = f"charts/{filename}"

    elif query == "avg_sales":
        result = filtered.groupby("Sub-Category")["Sales"].mean().reset_index()
        title = "Average Sales"
        filename = "chart_avg_sales.png"

        plt.figure()
        plt.bar(result["Sub-Category"], result["Sales"])
        plt.xticks(rotation=45)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(f"static/charts/{filename}")
        plt.close()

        chart_path = f"charts/{filename}"

    elif query == "top_products":
        result = (
            filtered.groupby("Product Name")["Sales"].sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        title = "Top 10 Products"
        filename = "chart_top_products.png"

        plt.figure()
        plt.barh(result["Product Name"], result["Sales"])
        plt.title(title)
        plt.tight_layout()
        plt.savefig(f"static/charts/{filename}")
        plt.close()

        chart_path = f"charts/{filename}"

    elif query == "monthly_sales":
        filtered["Order Date"] = pd.to_datetime(filtered["Order Date"])
        result = (
            filtered.groupby(filtered["Order Date"].dt.to_period("M"))["Sales"].sum()
            .reset_index()
        )
        result["Order Date"] = result["Order Date"].astype(str)

        title = "Monthly Sales Trend"
        filename = "chart_monthly_sales.png"

        plt.figure()
        plt.plot(result["Order Date"], result["Sales"])
        plt.xticks(rotation=45)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(f"static/charts/{filename}")
        plt.close()

        chart_path = f"charts/{filename}"

    else:
        result = filtered.copy()

    return render_template(
        "results.html",
        category=category,
        subcategory=subcategory,
        region=region,
        segment=segment,
        table=result,
        chart_path=chart_path
    )


# -----------------------------
# START APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
