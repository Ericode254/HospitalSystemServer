import joblib
import pandas as pd
import os

# Load the pre-trained model and the label encodings
def load_model():
    # Set the base directory for models (use environment variable or default path)
    BASE_DIR = os.getenv('MODEL_BASE_PATH', '/home/code/MyProjects/Systems/HospitalSystemServer/app/StrokeModels')

    # Load the mappings for categorical variables
    gender_map = joblib.load(os.path.join(BASE_DIR, 'gender_map.pkl'))
    ever_married_map = joblib.load(os.path.join(BASE_DIR, 'ever_married_map.pkl'))
    work_type_map = joblib.load(os.path.join(BASE_DIR, 'work_type_map.pkl'))
    residence_type_map = joblib.load(os.path.join(BASE_DIR, 'residence_type_map.pkl'))
    smoking_status_map = joblib.load(os.path.join(BASE_DIR, 'smoking_status_map.pkl'))

    # Load the pre-trained stroke prediction model
    model = joblib.load(os.path.join(BASE_DIR, 'stroke_prediction_model.pkl'))

    return model, gender_map, ever_married_map, work_type_map, residence_type_map, smoking_status_map

# Preprocess the input data
def preprocess_input(data, gender_map, ever_married_map, work_type_map, residence_type_map, smoking_status_map):
    # List of required features
    required_features = [
        'gender', 'age', 'hypertension', 'heart_disease',
        'ever_married', 'work_type', 'Residence_type',
        'avg_glucose_level', 'bmi', 'smoking_status'
    ]

    # Check if all required features are present
    missing_features = [feature for feature in required_features if feature not in data]
    if missing_features:
        raise ValueError(f"Missing required features: {', '.join(missing_features)}")

    # Convert the input data into a pandas DataFrame
    input_data = pd.DataFrame([{key: data[key] for key in required_features}])

    # Apply the mappings to the categorical columns
    input_data['gender'] = input_data['gender'].map(gender_map)
    input_data['ever_married'] = input_data['ever_married'].map(ever_married_map)
    input_data['work_type'] = input_data['work_type'].map(work_type_map)
    input_data['Residence_type'] = input_data['Residence_type'].map(residence_type_map)
    input_data['smoking_status'] = input_data['smoking_status'].map(smoking_status_map)

    # Check for any unmapped values (resulting in NaN)
    if input_data.isnull().values.any():
        unmapped_columns = input_data.columns[input_data.isnull().any()].tolist()
        raise ValueError(f"Some categorical variables have invalid values. Unmapped columns: {unmapped_columns}")

    return input_data

# Make prediction using the model
def predict_stroke_risk(data):
    # Load the model and label encodings
    model, gender_map, ever_married_map, work_type_map, residence_type_map, smoking_status_map = load_model()

    # Preprocess the input data
    try:
        processed_data = preprocess_input(data, gender_map, ever_married_map, work_type_map, residence_type_map, smoking_status_map)
    except ValueError as e:
        raise ValueError(f"Preprocessing Error: {e}")

    # Ensure input features match the model's training features
    expected_features = model.feature_names_in_  # This contains the features the model was trained on
    print(expected_features)
    if not all(feature in processed_data.columns for feature in expected_features):
        missing_from_input = [feature for feature in expected_features if feature not in processed_data.columns]
        raise ValueError(f"Input data does not match the model's expected features. Missing: {missing_from_input}")

    # Make prediction
    prediction = model.predict(processed_data)

    # Interpret prediction: 1 means high risk, 0 means low risk
    stroke_risk = "High" if prediction[0] == 1 else "Low"

    return stroke_risk, prediction[0]

