from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Excel read (header row = 2)
data = pd.read_excel("Book1.xlsx", header=1)
# Remove spaces in column names
data.columns = data.columns.str.strip()

# Convert ranks to numbers
data["Closing Rank"] = pd.to_numeric(data["Closing Rank"], errors="coerce")
data["Opening Rank"] = pd.to_numeric(data["Opening Rank"], errors="coerce")

print("Columns detected:", data.columns)
print("Total rows:", len(data))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict")
def predict():

    rank = int(request.args.get("rank"))

    branch = request.args.get("branch")
    category = request.args.get("category")
    institute = request.args.get("institute")

    lower = rank - 2000
    upper = rank + 4000

    result = data[
        (data["Closing Rank"] >= lower) &
        (data["Closing Rank"] <= upper)
    ]

    # Branch filter
    if branch and branch != "All":
        result = result[
            result["Academic Program Name"].str.contains(branch, case=False, na=False)
        ]

    # Category filter
    if category and category != "All":
        result = result[
            result["Seat Type"].str.contains(category, case=False, na=False)
        ]

    # Institute filter
    if institute and institute != "All":
        result = result[
            result["Institute"].str.contains(institute, case=False, na=False)
        ]

    # Remove duplicate institutes
    result = result.drop_duplicates(subset=["Institute"])

    # Sort by best closing rank
    result = result.sort_values(by="Closing Rank")

    print("Colleges found:", len(result))

    colleges = result[["Institute","Academic Program Name","Closing Rank"]]

    return jsonify(colleges.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True)