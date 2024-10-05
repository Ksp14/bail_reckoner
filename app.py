from flask import Flask, jsonify, request, render_template
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import logging

app = Flask(__name__)

# Set up logging for error tracking
logging.basicConfig(level=logging.DEBUG)

# Load the dataset
df = pd.read_csv('Book 7(Sheet1).csv')

# Preprocess the data
label_encoders = {}
for column in ['Bailable', 'Cognizable', 'Compoundable', 'Escape Risk', 'Influence Risk', 'Offence', 'Behavior', 'Special Statutes']:
    le = LabelEncoder()
    df[column] = le.fit_transform(df[column].astype(str))
    label_encoders[column] = le

# Define feature columns and the target (bail decision)
features = ['Severity(%)', 'Bailable', 'Cognizable', 'Escape Risk', 'Influence Risk', 'Previous_Convictions', 'Behavior']
X = df[features]
y = (df['Bailable'] == 1).astype(int)

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Initialize the Random Forest model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

@app.route('/')
def home():
    return render_template('new.html')

@app.route("/api/bail", methods=["POST"])  # Fix the route to match your JavaScript request
def check_prisoner_bail():
    try:
        data = request.json
        logging.debug(f"Received data: {data}")
        
        prisoner_id = int(data['prisoner_id'])  # Ensure it's treated as an integer
        prisoner_row = df[df['Prisoner_ID'] == prisoner_id]

        if prisoner_row.empty:
            logging.error(f"No prisoner found with ID {prisoner_id}")
            return jsonify({"error": f"Prisoner with ID {prisoner_id} not found"}), 404
        
        prisoner_details = prisoner_row.iloc[0]
        logging.debug(f"Prisoner details: {prisoner_details}")

        prisoner_features = prisoner_details[features].values.reshape(1, -1)
        bail_decision = model.predict(prisoner_features)[0]
        decision_str = 'Grant Bail' if bail_decision == 1 else 'Deny Bail'

        # Generate a simple report (can add more details if needed)
        report = f"""
        Bail Decision for Prisoner ID {prisoner_id}:
        Severity: {prisoner_details['Severity(%)']}
        Bailable: {prisoner_details['Bailable']}
        Cognizable: {prisoner_details['Cognizable']}
        Escape Risk: {prisoner_details['Escape Risk']}
        Influence Risk: {prisoner_details['Influence Risk']}
        Previous Convictions: {prisoner_details['Previous_Convictions']}
        Behavior: {prisoner_details['Behavior']}
        Bail Decision: {decision_str}
        """

        logging.debug(f"Generated report: {report}")

        return jsonify({"bail_decision": decision_str, "report": report})

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, port=8000)
