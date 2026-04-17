from CoolProp.CoolProp import PropsSI

fluid = "Methane"

# values from CFD
h_in = 6.902e+5     # inlet static enthalpy (J/kg)           6.902e+5 [J kg^-1]
h_out = 6.794e+5    # outlet static enthalpy (J/kg)          6.794e+5 [J kg^-1]

s_in = 3.622e+3     # inlet static entropy (J/kg-K)          3.622e+3 [J kg^-1 K^-1]
P_out = 6.245e+6    # outlet static pressure (Pa)                 6.245e+6 [Pa]

# isentropic outlet enthalpy
h_out_s = PropsSI('H','P',P_out,'S',s_in,fluid)

# enthalpy drops
delta_h_actual = h_in - h_out
delta_h_isentropic = h_in - h_out_s

# efficiency
eta = delta_h_actual / delta_h_isentropic

print("Isentropic outlet enthalpy:", h_out_s)
print("Efficiency:", eta*100, "%")

# Power Calculation

mdot = 4.000e-2     # kg/s                        4.000e-2 [kg s^-1]

r1 = 1.626e-2      # m                                1.771e-2 [m]
r2 = 1.000e-2      # m                                1.000e-2 [m]

V_theta_1 = -8.279e+1     # m/s
V_theta_2 = -3.247e+2     # m/s

omega = 2618    # rad/s

# Euler's Turbomachinery Equation

Torque = mdot * (r1 * V_theta_1 - r2 * V_theta_2)
print("Torque:", Torque, "N")

Power = omega * Torque
print("Power:", Power, "W")