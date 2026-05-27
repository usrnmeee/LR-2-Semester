import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

X = pd.DataFrame({"x":[1,2,3,4,5,6]})
y = pd.Series([0,0,0,1,1,1], name="y_target")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

scaler = StandardScaler()

# fit только на train
X_train_scaled = scaler.fit_transform(X_train)

# test только transform
X_test_scaled = scaler.transform(X_test)