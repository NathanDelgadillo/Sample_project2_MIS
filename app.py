from flask import Flask, render_template, request
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Load data once
df = pd.read_csv("TableauSalesData.csv")

# Predefined query choices
QUERY_OPTIONS = {
    "total_sales": lambda d: d["Sales"].sum(),
    "average_profit": lambda d: d["Profit"].mean(),
    "top_product": lambda d: d.groupby("Product Name")["Sales"].sum().idxmax(),
    "sales_by_order": lambda d: d[["Order ID", "Sales"]].groupby("Order ID").sum()
}

@app.route("/", methods=["GET", "POST"])
def index():
    categories = sorted(df["Category"].unique())
    subcategories = sorted(df["Sub-Category"].unique())
    regions = sorted(df["Region"].unique())
    segments = sorted(df["Segment"].unique())

    if request.method == "POST":
        selected_category = request.form["category"]
        selected_subcategory = request.form["subcategory"]
        selected_region = request.form["region"]
        selected_segment = request.form["segment"]
        selected_query = request.form["query"]

        # Filter data based on user selections
        filtered = df[
            (df["Category"] == selected_category) &
            (df["Sub-Category"] == selected_subcategory) &
            (df["Region"] == selected_region) &
            (df["Segment"] == selected_segment)
        ]

        # Run selected query
        result = QUERY_OPTIONS[selected_query](filtered)

        # Generate Monthly Sales Chart
        chart_url = None
        try:
            time_data = filtered.copy()
            time_data['Order Date'] = pd.to_datetime(time_data['Order Date'])
            monthly = time_data.groupby(pd.Grouper(key='Order Date', freq='M'))['Sales'].sum()

            fig, ax = plt.subplots()
            monthly.plot(ax=ax)
            ax.set_title("Sales Over Time")
            ax.set_xlabel("Month")
            ax.set_ylabel("Total Sales")

            img = io.BytesIO()
            plt.savefig(img, format="png", bbox_inches="tight")
            img.seek(0)
            chart_url = base64.b64encode(img.getvalue()).decode()
            plt.close()
        except:
            chart_url = None

        return render_template(
            "results.html",
            result=result,
            query_name=selected_query,
            chart_url=chart_url
        )

    return render_template(
        "index.html",
        categories=categories,
        subcategories=subcategories,
        regions=regions,
        segments=segments,
        queries=QUERY_OPTIONS
    )


if __name__ == "__main__":
    app.run(debug=True)
