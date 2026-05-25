import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from mpl_toolkits.mplot3d import Axes3D
# =====================================================
# READ DATA
# =====================================================

data = pd.read_csv(
    "C:/Dhairya_internship/extracted_data/state_point_data/power_efficiency_results.csv"
)

pi1 = data["pi1"].values
pi2 = data["pi2"].values
pi3 = data["pi3"].values

eta = data["Efficiency Total-to-Total"].values

# =====================================================
# LOG TRANSFORM
# =====================================================

X = np.column_stack([
    np.log(pi1),
    np.log(pi2),
    np.log(pi3)
])

Y = np.log(eta)

# =====================================================
# LINEAR REGRESSION
# =====================================================

model = LinearRegression()
model.fit(X, Y)

# =====================================================
# EXTRACT COEFFICIENTS
# =====================================================

a = model.coef_[0]
b = model.coef_[1]
c = model.coef_[2]

C = np.exp(model.intercept_)

print("\n=================================================")
print("Correlation")
print("=================================================\n")

print(f"eta = {C:.6f} * pi1^{a:.6f} * pi2^{b:.6f} * pi3^{c:.6f}")

# =====================================================
# PREDICTION SECTION
# =====================================================

new_pi1 = 7.925961829
new_pi2 = 219.450324
new_pi3 = 59.81966207

X_new = np.array([[
    np.log(new_pi1),
    np.log(new_pi2),
    np.log(new_pi3)
]])

log_eta_pred = model.predict(X_new)

eta_pred = np.exp(log_eta_pred[0])

print("\n=================================================")
print("Prediction")
print("=================================================\n")

print(f"pi1 = {new_pi1}")
print(f"pi2 = {new_pi2}")
print(f"pi3 = {new_pi3}")

print(f"\nPredicted Efficiency = {eta_pred:.6f}")

# =====================================================
# 3D PLOT
# =====================================================

fig = plt.figure(figsize=(10,8))

ax = fig.add_subplot(111, projection='3d')

# Scatter plot
scatter = ax.scatter(
    pi1,
    pi2,
    pi3,
    c=eta,          # color based on efficiency
    s=80
)

# Axis labels
ax.set_xlabel("Pi 1")
ax.set_ylabel("Pi 2")
ax.set_zlabel("Pi 3")

# Title
ax.set_title("3D Buckingham Pi Space")

# Color bar
cbar = plt.colorbar(scatter)

cbar.set_label("Efficiency")

plt.show()

