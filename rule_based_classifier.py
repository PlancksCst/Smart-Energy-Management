import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin

class RuleBasedPriorityClassifier(BaseEstimator, ClassifierMixin):
    def fit(self, X, y=None):
        return self

    def predict(self, X):
        if isinstance(X, dict):
            X = pd.DataFrame([X])
        elif not isinstance(X, pd.DataFrame):
            raise ValueError("Input must be a DataFrame or dict")

        priorities = []

        for _, row in X.iterrows():
            is_critical = row.get("is_critical", False)
            avg_power = row.get("average_consumption_Wh", 0)
            max_power = row.get("max_consumption_Wh", 0)
            running_ratio = row.get("average_continuous_running_hours_ratio", 0)
            avg_temp = row.get("temperature", 25)

            priority = 1

            if is_critical:
                priority = 5
            else:
                if avg_power >= 2000:
                    priority = 4
                elif avg_power >= 1000:
                    priority = 3
                elif avg_power >= 500:
                    priority = 2
                elif avg_power >= 100:
                    priority = 1

                if running_ratio > 0.8:
                    priority = max(priority, 4)
                elif running_ratio > 0.5:
                    priority = max(priority, 3)
                elif running_ratio > 0.2:
                    priority = max(priority, 2)

                if max_power > 3000:
                    priority = max(priority, 5)
                elif max_power > 2000:
                    priority = max(priority, 4)

                if avg_temp > 40:
                    priority = min(priority + 1, 5)

            priorities.append(priority)

        return priorities

def classify_circuit_priority(circuit_dict):
    classifier = RuleBasedPriorityClassifier()
    predicted_priority = classifier.predict(circuit_dict)[0]
    return predicted_priority