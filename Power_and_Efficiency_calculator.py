from CoolProp.CoolProp import PropsSI

fluid = "Methane"

# values from CFD
h_in = 6.624e+5      # inlet static enthalpy (J/kg)               6.624e+5 [J kg^-1]            =areaAve(Static Enthalpy)@inlet
h_out = 6.333e+5      # outlet static enthalpy (J/kg)              6.333e+5 [J kg^-1]             =areaAve(Static Enthalpy)@outlet

s_in = 3.425e+3       # inlet static entropy (J/kg-K)              3.425e+3 [J kg^-1 K^-1]        =areaAve(Static Entropy)@inlet      =areaAve(Static Entropy)@outlet
P_out = 6.245e+6      # outlet static pressure (Pa)                6.245e+6 [Pa]             =areaAve(Pressure)@outlet           =areaAve(Pressure)@inlet

# Power Calculation
mdot = 5.875e-2       # kg/s                                5.875e-2 [kg s^-1]

r1 = 1.771e-2        # m                                    1.771e-2 [m]          =areaAve(r )@inlet           sqrt(X^2 + Y^2)
r2 = 1.000e-2      # m                                1.000e-2 [m]          =areaAve(r )@outlet

V_theta_1 = 1.440e+2       # m/s                        -1.440e+2 [m s^-1]     =areaAve(Velocity Circumferential)@inlet
V_theta_2 = 2.396e+2       # m/s                        -2.396e+2 [m s^-1]     =areaAve(Velocity Circumferential)@outlet

omega = 2618    # rad/s


# isentropic outlet enthalpy
h_out_s = PropsSI('H','P',P_out,'S',s_in,fluid)

# enthalpy drops
delta_h_actual = h_in - h_out
delta_h_isentropic = h_in - h_out_s

# efficiency
eta = delta_h_actual / delta_h_isentropic

print("Isentropic outlet enthalpy:", h_out_s)
print("Efficiency:", eta*100, "%")

# Euler's Turbomachinery Equation

Torque = mdot * (r1 * V_theta_1 - r2 * V_theta_2)
print("Torque:", Torque, "N")

Power = omega * Torque
print("Power:", Power, "W")