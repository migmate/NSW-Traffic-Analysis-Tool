import numpy as np
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from matplotlib import pyplot as plt
from sqlalchemy import func
from datetime import datetime
import base64
from io import BytesIO
import sys
import subprocess


# Initialize Flask application
app = Flask(__name__)

# Configure database URI and initialize SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


# Define database model for offences
class OffenceEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    OFFENCE_FINYEAR = db.Column(db.String(50))
    OFFENCE_MONTH = db.Column(db.String(50))
    OFFENCE_CODE = db.Column(db.Integer)
    OFFENCE_DESC = db.Column(db.String(255))
    LEGISLATION = db.Column(db.String(255))
    SECTION_CLAUSE = db.Column(db.String(255))
    FACE_VALUE = db.Column(db.Float)
    CAMERA_IND = db.Column(db.String(10))
    CAMERA_TYPE = db.Column(db.String(255))
    LOCATION_CODE = db.Column(db.Float)
    LOCATION_DETAILS = db.Column(db.String(255))
    SCHOOL_ZONE_IND = db.Column(db.String(10))
    SPEED_BAND = db.Column(db.String(50))
    SPEED_IND = db.Column(db.String(10))
    POINT_TO_POINT_IND = db.Column(db.String(10))
    RED_LIGHT_CAMERA_IND = db.Column(db.String(10))
    SPEED_CAMERA_IND = db.Column(db.String(10))
    SEATBELT_IND = db.Column(db.String(10))
    MOBILE_PHONE_IND = db.Column(db.String(10))
    PARKING_IND = db.Column(db.String(10))
    CINS_IND = db.Column(db.String(10))
    FOOD_IND = db.Column(db.String(10))
    BICYCLE_TOY_ETC_IND = db.Column(db.String(10))
    TOTAL_NUMBER = db.Column(db.Integer)
    TOTAL_VALUE = db.Column(db.Float)


# Ensure the application context is set up
with app.app_context():
    # Create the database tables
    db.create_all()
    # Check if the database is already populated
    if not OffenceEntry.query.first():
        # If empty, populate the database from the CSV file
        print("Populating database...")
        filename = "data/dataSet.csv"
        df = pd.read_csv(filename, low_memory=False)
        for _, row in df.iterrows():
            # For each row in the DataFrame, the row is converted to a Series object.
            # The iterrows() function returns both the index and the row data as a Series.
            # We're using _ to ignore the index since we don't need it here.

            entry = OffenceEntry(**row.to_dict())
            # Here, we convert the Series (row) to a dictionary using to_dict(). The double asterisks (**) is
            # Python's syntax for unpacking keyword arguments from a dictionary. This means we're dynamically setting
            # the attributes of the OffenceEntry object using the key-value pairs from the row.

            db.session.add(entry)
            # Add the created OffenceEntry object (representing a row of data) to the current database session.
            # This schedules the object to be inserted into the database once the session commits.

        db.session.commit()  # Commit changes to the database


    def strip_day(date_str):
        year, month, _ = date_str.split('-')
        return "{}-{}-01".format(year, month)


@app.route('/')
def index():
    # Render the main page
    return render_template("index.html")


@app.route('/penalty_cases', methods=['GET'])
def penalty_cases():
    # current_date = datetime.now().strftime("%Y-%m-%d")  # Just the date, without time
    date_1_str = request.args.get('date1', "2017-07-01")  # Change "date_time_1" to "date1"
    date_2_str = request.args.get('date2', "2017-07-01")  # Change "date_time_2" to "date2"

    date_1_str = strip_day(date_1_str)
    date_2_str = strip_day(date_2_str)

    # Convert the input strings to the desired format
    formatted_date_1 = datetime.strptime(date_1_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    formatted_date_2 = datetime.strptime(date_2_str, "%Y-%m-%d").strftime("%d/%m/%Y")

    # Query based on the formatted dates
    results = OffenceEntry.query.filter(
        (OffenceEntry.OFFENCE_MONTH >= formatted_date_1) &
        (OffenceEntry.OFFENCE_MONTH <= formatted_date_2)
    ).all()

    # Convert results to a format suitable for DataTables
    data = []
    for entry in results:
        data.append({
            'OFFENCE_FINYEAR': entry.OFFENCE_FINYEAR,
            'OFFENCE_MONTH': entry.OFFENCE_MONTH,
            'OFFENCE_CODE': entry.OFFENCE_CODE,
            'OFFENCE_DESC': entry.OFFENCE_DESC,
            'LEGISLATION': entry.LEGISLATION,
            'SECTION_CLAUSE': entry.SECTION_CLAUSE,
            'FACE_VALUE': entry.FACE_VALUE,
            'CAMERA_IND': entry.CAMERA_IND,
            'CAMERA_TYPE': entry.CAMERA_TYPE,
            'LOCATION_CODE': entry.LOCATION_CODE,
            'LOCATION_DETAILS': entry.LOCATION_DETAILS,
            'SCHOOL_ZONE_IND': entry.SCHOOL_ZONE_IND,
            'SPEED_BAND': entry.SPEED_BAND,
            'SPEED_IND': entry.SPEED_IND,
            'POINT_TO_POINT_IND': entry.POINT_TO_POINT_IND,
            'RED_LIGHT_CAMERA_IND': entry.RED_LIGHT_CAMERA_IND,
            'SPEED_CAMERA_IND': entry.SPEED_CAMERA_IND,
            'SEATBELT_IND': entry.SEATBELT_IND,
            'MOBILE_PHONE_IND': entry.MOBILE_PHONE_IND,
            'PARKING_IND': entry.PARKING_IND,
            'CINS_IND': entry.CINS_IND,
            'FOOD_IND': entry.FOOD_IND,
            'BICYCLE_TOY_ETC_IND': entry.BICYCLE_TOY_ETC_IND,
            'TOTAL_NUMBER': entry.TOTAL_NUMBER,
            'TOTAL_VALUE': entry.TOTAL_VALUE
        })

    # Return data as a JSON response
    return jsonify({
        "data": data
    })


@app.route('/route_for_button2', methods=['GET'])
def route2():
    # Generate the figure **without using pyplot**.
    offense_codes = []
    cases = []

    current_date = datetime.now().strftime("%Y-%m-%d")  # Just the date, without time
    date_1_str = request.args.get('date1', "2017-07-01")  # Change "date_time_1" to "date1"
    date_2_str = request.args.get('date2', current_date)  # Change "date_time_2" to "date2"

    date_1_str = strip_day(date_1_str)
    date_2_str = strip_day(date_2_str)

    # Convert the input strings to the desired format
    formatted_date_1 = datetime.strptime(date_1_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    formatted_date_2 = datetime.strptime(date_2_str, "%Y-%m-%d").strftime("%d/%m/%Y")

    results = (
        OffenceEntry.query
        .with_entities(OffenceEntry.OFFENCE_CODE, func.sum(OffenceEntry.TOTAL_NUMBER).label('total_count'))
        .filter(
            (OffenceEntry.OFFENCE_MONTH >= formatted_date_1) &
            (OffenceEntry.OFFENCE_MONTH <= formatted_date_2)

        )
        .group_by(OffenceEntry.OFFENCE_CODE)
        .all()
    )

    for result in results:
        offence_code, total_count = result
        offense_codes.append(str(offence_code))
        cases.append(total_count)

    data_list = [{"OFFENCE_CODE": code, "count": count} for code, count in zip(offense_codes, cases)]

    # Sort results3 based on total_count
    top_10_results = sorted(results, key=lambda x: x.total_count, reverse=True)[:20]

    # Extract offense codes and counts from top_10_results
    top_offence_codes = [str(e.OFFENCE_CODE) for e in top_10_results]
    top_offence_counts = [e.total_count for e in top_10_results]

    fig, ax = plt.subplots(figsize=(15, 8))

    # Set y-axis limits
    ax.set_ylim(0, (max(top_offence_counts)) + 500)

    # Plot the bars
    ax.bar(top_offence_codes, top_offence_counts, color='skyblue', width=0.25)

    # Set and rotate x-tick labels for better clarity
    ax.set_xticks(top_offence_codes)
    ax.set_xticklabels(top_offence_codes, rotation=45, ha="right")

    # Set labels and title
    ax.set_xlabel('Offense Codes')
    ax.set_ylabel('Number of Cases')
    ax.set_title('Distribution of the Top 20 Cases by Offense Code')

    # Add grid lines on the y-axis
    ax.grid(axis='y', linestyle="--")

    # Save the figure to a buffer
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)  # Reset buffer position

    # Encode as base64 and embed in HTML
    data = base64.b64encode(buf.read()).decode("utf-8")
    # print(data)
    buf.close()

    return jsonify({
        "plot": data,
        "table_data": data_list
    })


@app.route('/route_for_button3', methods=['GET'])
def route_for_button3():
    date_1_str = request.args.get('date1')
    date_2_str = request.args.get('date2')
    sort_by = request.args.get('key_word')  # Default sorting by OFFENCE_MONTH
    date_1_str = strip_day(date_1_str)
    date_2_str = strip_day(date_2_str)
    formatted_date_1 = datetime.strptime(date_1_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    formatted_date_2 = datetime.strptime(date_2_str, "%Y-%m-%d").strftime("%d/%m/%Y")

    # Query based on the formatted dates and search for a substring in OFFENCE_DESC
    query = OffenceEntry.query.filter(
        (OffenceEntry.OFFENCE_MONTH >= formatted_date_1) &
        (OffenceEntry.OFFENCE_MONTH <= formatted_date_2) &
        (OffenceEntry.OFFENCE_DESC.ilike(f"%{sort_by}%"))
    ).all()

    data = []
    for entry in query:
        data.append({
            'OFFENCE_FINYEAR': entry.OFFENCE_FINYEAR,
            'OFFENCE_MONTH': entry.OFFENCE_MONTH,
            'OFFENCE_CODE': entry.OFFENCE_CODE,
            'OFFENCE_DESC': entry.OFFENCE_DESC,
            'LEGISLATION': entry.LEGISLATION,
            'SECTION_CLAUSE': entry.SECTION_CLAUSE,
            'FACE_VALUE': entry.FACE_VALUE,
            'CAMERA_IND': entry.CAMERA_IND,
            'CAMERA_TYPE': entry.CAMERA_TYPE,
            'LOCATION_CODE': entry.LOCATION_CODE,
            'LOCATION_DETAILS': entry.LOCATION_DETAILS,
            'SCHOOL_ZONE_IND': entry.SCHOOL_ZONE_IND,
            'SPEED_BAND': entry.SPEED_BAND,
            'SPEED_IND': entry.SPEED_IND,
            'POINT_TO_POINT_IND': entry.POINT_TO_POINT_IND,
            'RED_LIGHT_CAMERA_IND': entry.RED_LIGHT_CAMERA_IND,
            'SPEED_CAMERA_IND': entry.SPEED_CAMERA_IND,
            'SEATBELT_IND': entry.SEATBELT_IND,
            'MOBILE_PHONE_IND': entry.MOBILE_PHONE_IND,
            'PARKING_IND': entry.PARKING_IND,
            'CINS_IND': entry.CINS_IND,
            'FOOD_IND': entry.FOOD_IND,
            'BICYCLE_TOY_ETC_IND': entry.BICYCLE_TOY_ETC_IND,
            'TOTAL_NUMBER': entry.TOTAL_NUMBER,
            'TOTAL_VALUE': entry.TOTAL_VALUE
        })

    return jsonify({
        "data": data
    })


@app.route('/route_for_button4', methods=['GET'])
def route_for_button4():
    offense_months = []
    cases = []
    mobile_cases = 0  # Initialize a counter for all mobile cases
    mobile_cases_in_school_zone = 0  # Initialize a counter for mobile cases in school zones

    date_1_str = request.args.get('date1', "2017-07-01")
    date_2_str = request.args.get('date2', "2017-07-01")
    date_1_str = strip_day(date_1_str)
    date_2_str = strip_day(date_2_str)
    formatted_date_1 = datetime.strptime(date_1_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    formatted_date_2 = datetime.strptime(date_2_str, "%Y-%m-%d").strftime("%d/%m/%Y")

    results = (
        OffenceEntry.query
        .with_entities(OffenceEntry.OFFENCE_MONTH, func.sum(OffenceEntry.TOTAL_NUMBER).label('total_count'))
        .filter(
            (OffenceEntry.OFFENCE_MONTH >= formatted_date_1) &
            (OffenceEntry.OFFENCE_MONTH <= formatted_date_2) &
            (OffenceEntry.MOBILE_PHONE_IND == 'Y')  # Filter cases where MOBILE_PHONE_IND is 'Y'
        )
        .group_by(OffenceEntry.OFFENCE_MONTH)
        .all()
    )

    for result in results:
        offense_month, total_count = result
        offense_months.append(offense_month)
        cases.append(total_count)

    # Calculate the sum of TOTAL_VALUE for all rows where MOBILE_PHONE_IND is "Y"
    mobile_cases = (
        OffenceEntry.query
        .with_entities(func.sum(OffenceEntry.TOTAL_NUMBER).label('total_value_sum'))
        .filter(
            (OffenceEntry.OFFENCE_MONTH >= formatted_date_1) &
            (OffenceEntry.OFFENCE_MONTH <= formatted_date_2) &
            (OffenceEntry.MOBILE_PHONE_IND == 'Y')
        )
        .scalar()  # Get the sum as a scalar value
    )

    mobile_cases_in_school_zone = (
        OffenceEntry.query
        .filter(
            (OffenceEntry.OFFENCE_MONTH >= formatted_date_1) &
            (OffenceEntry.OFFENCE_MONTH <= formatted_date_2) &
            (OffenceEntry.MOBILE_PHONE_IND == 'Y') &
            (OffenceEntry.SCHOOL_ZONE_IND == 'Y')  # Filter cases in school zones
        )
        .count()
    )

    # Query for the OFFENCE_MONTH with the smallest TOTAL_NUMBER
    min_total_number_result = (
        OffenceEntry.query
        .with_entities(OffenceEntry.OFFENCE_MONTH, func.min(OffenceEntry.TOTAL_NUMBER).label('min_total_number'))
        .filter(
            (OffenceEntry.OFFENCE_MONTH >= formatted_date_1) &
            (OffenceEntry.OFFENCE_MONTH <= formatted_date_2) &
            (OffenceEntry.MOBILE_PHONE_IND == 'Y')
        )
        .order_by(func.min(OffenceEntry.TOTAL_NUMBER))
        .limit(1)
        .first()
    )

    # Extract the values from the result
    min_offence_month, min_total_number = min_total_number_result or (None, None)

    max_total_number_result = (
        OffenceEntry.query
        .with_entities(OffenceEntry.OFFENCE_MONTH, func.max(OffenceEntry.TOTAL_NUMBER).label('max_total_number'))
        .filter(
            (OffenceEntry.OFFENCE_MONTH >= formatted_date_1) &
            (OffenceEntry.OFFENCE_MONTH <= formatted_date_2) &
            (OffenceEntry.MOBILE_PHONE_IND == 'Y')
        )
        .order_by(func.max(OffenceEntry.TOTAL_NUMBER))
        .limit(1)
        .first()
    )

    # Extract the values from the result
    max_offence_month, max_total_number = max_total_number_result or (None, None)

    min_total_value_result = (
        OffenceEntry.query
        .with_entities(OffenceEntry.OFFENCE_MONTH, func.min(OffenceEntry.TOTAL_VALUE).label('min_total_value'))
        .filter(
            (OffenceEntry.OFFENCE_MONTH >= formatted_date_1) &
            (OffenceEntry.OFFENCE_MONTH <= formatted_date_2) &
            (OffenceEntry.MOBILE_PHONE_IND == 'Y')
        )
        .order_by(func.min(OffenceEntry.TOTAL_VALUE))
        .limit(1)
        .first()
    )

    # Extract the values from the result
    min_offence_month_total_value, min_total_value = min_total_value_result or (None, None)

    max_total_value_result = (
        OffenceEntry.query
        .with_entities(OffenceEntry.OFFENCE_MONTH, func.max(OffenceEntry.TOTAL_VALUE).label('max_total_value'))
        .filter(
            (OffenceEntry.OFFENCE_MONTH >= formatted_date_1) &
            (OffenceEntry.OFFENCE_MONTH <= formatted_date_2) &
            (OffenceEntry.MOBILE_PHONE_IND == 'Y')
        )
        .order_by(func.max(OffenceEntry.TOTAL_VALUE))
        .limit(1)
        .first()
    )

    # Extract the values from the result
    max_offence_month_total_value, max_total_value = max_total_value_result or (None, None)

    fig, ax = plt.subplots(figsize=(15, 8))
    ax.set_ylim(0, max(cases) + 50)

    # Line plot
    ax.plot(offense_months, cases, marker='o', linestyle='-', color='skyblue')

    # Set x-tick labels and rotate them for clarity
    ax.set_xticks(offense_months)
    ax.set_xticklabels(offense_months, rotation=45, ha="right")

    # Axis labels and title
    ax.set_xlabel('Months')
    ax.set_ylabel('Number of Cases')
    ax.set_title('Trend of Mobile Cases')

    # Grid lines on y-axis
    ax.grid(axis='y', linestyle="--")

    # Save the figure to a buffer
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)  # Reset buffer position

    # Encode as base64 and embed in HTML
    data = base64.b64encode(buf.read()).decode("utf-8")

    return jsonify({
        "plot": data,
        "mobile_cases": mobile_cases,
        "mobile_cases_in_school_zone": mobile_cases_in_school_zone,
        "min_offence_month": min_offence_month,  # OFFENCE_MONTH with the smallest TOTAL_NUMBER
        "max_offence_month": max_offence_month,  # Biggest TOTAL_NUMBER
        "min_offence_month_total_value": min_offence_month_total_value,  # OFFENCE_MONTH with the smallest TOTAL_VALUE
        "max_offence_month_total_value": max_offence_month_total_value,  # OFFENCE_MONTH with the biggest TOTAL_VALUE
        "min_total_value": min_total_value  # Smallest TOTAL_VALUE
    })


@app.route('/plot_offense_codes', methods=['GET'])
def plot_offense_codes():
    offense_codes = []
    cases = []

    date_1_str = request.args.get('date1', "2017-07-01")
    date_2_str = request.args.get('date2', "2017-07-01")
    offense_code_1 = request.args.get('offense_code_1', "")
    offense_code_2 = request.args.get('offense_code_2', "")

    date_1_str = strip_day(date_1_str)
    date_2_str = strip_day(date_2_str)
    formatted_date_1 = datetime.strptime(date_1_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    formatted_date_2 = datetime.strptime(date_2_str, "%Y-%m-%d").strftime("%d/%m/%Y")

    results = (
        OffenceEntry.query
        .with_entities(OffenceEntry.OFFENCE_CODE, func.sum(OffenceEntry.TOTAL_NUMBER).label('total_count'))
        .filter(
            (OffenceEntry.OFFENCE_MONTH >= formatted_date_1) &
            (OffenceEntry.OFFENCE_MONTH <= formatted_date_2) &
            ((OffenceEntry.OFFENCE_CODE == offense_code_1) |
             (OffenceEntry.OFFENCE_CODE == offense_code_2))
        )
        .group_by(OffenceEntry.OFFENCE_CODE)
        .all()
    )

    for result in results:
        offence_code, total_count = result
        offense_codes.append(str(offence_code))
        cases.append(total_count)

    if not cases:  # Check if cases list is empty
        return jsonify({
            "plot": None,  # Return None or a suitable response to indicate no data
        })

    fig, ax = plt.subplots(figsize=(15, 8))
    ax.set_ylim(0, max(cases) + 50)

    # Bar plot
    ax.bar(offense_codes, cases, color='skyblue')

    # Set x-tick labels and rotate them for clarity
    ax.set_xticks(offense_codes)
    ax.set_xticklabels(offense_codes, rotation=90, ha="right")

    # Axis labels and title
    ax.set_xlabel('Offense Codes')
    ax.set_ylabel('Number of Cases')
    ax.set_title('Distribution of Cases by Offense Code')

    # Grid lines on y-axis
    ax.grid(axis='y', linestyle="--")

    # Display the plot
    # Save the figure to a buffer
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)  # Reset buffer position
    # Encode as base64 and embed in HTML
    data = base64.b64encode(buf.read()).decode("utf-8")

    return jsonify({
        "plot": data,
    })


# Start the Flask application
if __name__ == '__main__':
    if "install" in sys.argv:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    else:
        app.run(debug=True)
