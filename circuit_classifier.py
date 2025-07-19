import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

# Load the dataset
df = pd.read_csv("circuit_training_data.csv")

# Initialize label encoders
name_encoder = LabelEncoder()
peak_time_encoder = LabelEncoder()

# Encode labels
df['name_label'] = name_encoder.fit_transform(df['name'])
df['peak_time'] = peak_time_encoder.fit_transform(df['peak_time'])
df['is_critical'] = df['is_critical'].astype(int)

# Define features and label
X = df[['priority', 'is_critical', 'avg_run_ratio', 'temperature', 'avg_Wh', 'max_Wh', 'peak_time']]
y = df['name_label']

# Split for training/testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train classifier
clf = DecisionTreeClassifier(max_depth=5, random_state=0)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
target_names = name_encoder.inverse_transform(sorted(y.unique()))
print("Classification Report:\n")
print(classification_report(y_test, y_pred, target_names=target_names))

# ----- Predict a new circuit -----
def predict_circuit(features_dict):
    input_df = pd.DataFrame([features_dict])
    input_df['is_critical'] = int(features_dict['is_critical'])
    input_df['peak_time'] = peak_time_encoder.transform([features_dict['peak_time']])[0]

    X_input = input_df[['priority', 'is_critical', 'avg_run_ratio', 'temperature',
                        'avg_Wh', 'max_Wh', 'peak_time']]
    prediction = clf.predict(X_input)[0]
    return name_encoder.inverse_transform([prediction])[0]

# Example prediction
sample_circuit = {
    "priority": 3,
    "is_critical": True,
    "avg_run_ratio": 0.9,
    "temperature": 30,
    "avg_Wh": 140,
    "max_Wh": 300,
    "peak_time": "all day"
}

predicted = predict_circuit(sample_circuit)
print("\nPredicted Appliance Name:", predicted)
