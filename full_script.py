import numpy as np
import pandas as pd

# =========================================
# USER INPUT (ONLY THIS SECTION)
# =========================================

def x_func(t):
    return (0.01 + (0.017711374999993368 - 0.01) * t / (2*np.pi*4.909213797136834)) * np.cos(t)

def y_func(t):
    return (0.01 + (0.017711374999993368 - 0.01) * t / (2*np.pi*4.909213797136834)) * np.sin(t)

def z_func(t):
    return (0.061689180574821464 / (2*np.pi*4.909213797136834)) * t

t_start = 0
t_end   = 2 * np.pi * 4.909213797136834

# =========================================
# OUTPUT PATHS
# =========================================

centerline_csv  = r"E:\rotation_case_hpc\d2_25k_rpm\data analysis\d2_centerline.csv"
arclength_csv   = r"E:\rotation_case_hpc\d2_25k_rpm\data analysis\d2_centerline_arclength.csv"
output_cse      = r"E:\rotation_case_hpc\d2_25k_rpm\data analysis\d2_script.cse"
output_csv      = r"E:\rotation_case_hpc\d2_25k_rpm\data analysis\d2_extracted_data.csv"
bound_radius    = 0.0025 #m

# =========================================
# STEP 1: DENSE SAMPLING
# =========================================

t_dense = np.linspace(t_start, t_end, 5000)

x_dense = x_func(t_dense)
y_dense = y_func(t_dense)
z_dense = z_func(t_dense)

# =========================================
# STEP 2: ARC LENGTH
# =========================================

dx = np.gradient(x_dense, t_dense)
dy = np.gradient(y_dense, t_dense)
dz = np.gradient(z_dense, t_dense)

ds = np.sqrt(dx**2 + dy**2 + dz**2)

s = np.cumsum(ds)
s = s - s[0]

# =========================================
# STEP 3: UNIFORM ARC-LENGTH POINTS
# =========================================

n_points = 1000

s_uniform = np.linspace(0, s[-1], n_points)
t_uniform = np.interp(s_uniform, s, t_dense)

# =========================================
# STEP 4: FINAL POINTS
# =========================================

x = x_func(t_uniform)
y = y_func(t_uniform)
z = z_func(t_uniform)

# =========================================
# STEP 5: TANGENTS
# =========================================

dx = np.gradient(x, t_uniform)
dy = np.gradient(y, t_uniform)
dz = np.gradient(z, t_uniform)

mag = np.sqrt(dx**2 + dy**2 + dz**2)

tx = dx / mag
ty = dy / mag
tz = dz / mag

print("Arc-length spaced centerline generated")

# =========================================
# STEP 6: SAVE CSV
# =========================================

df = pd.DataFrame({
    "x": x,
    "y": y,
    "z": z
})

df.to_csv(centerline_csv, index=False, header=False)

print(f"Centerline CSV saved -→ {centerline_csv}")

df_s = pd.DataFrame({
    "s": s_uniform,
    "x": x,
    "y": y,
    "z": z
})

df_s.to_csv(arclength_csv, index=False, header=False)

print(f"Arclength CSV saved -→ {arclength_csv}")
# =========================================
# STEP 7: GENERATE CSE
# =========================================

with open(output_cse, "w") as f:

    f.write("COMMAND FILE:\n  CFX Post Version = 23.2\nEND\n\n")

    f.write(f"""
    !open(FILE, '> {output_csv}');
    !print FILE "Pressure,Pressure Gradient,Temperature,Velocity,Density,Dynamic Viscosity,Effective Viscosity,Eddy Viscosity,Speed Of Sound,Mach number,Rgas,Cp,Static Enthalpy,Static Entropy,Total Enthalpy,Total Energy,Wall Shear,Total Pressure,Total Temperature,Total Pressure Gradient, Density mwa, Velocity awa, Radial coordinate, V_theta, V_axial, V_radial, V_theta_stn, mdot\\n";
    """)

    for i, row in df.iterrows():
        f.write(
            f""" 
        PLANE: plane_{i}
          Option = Point and Normal 
          Point = {x[i]} [m], {y[i]} [m], {z[i]} [m] 
          Normal = {tx[i]}, {ty[i]}, {tz[i]} 
          Plane Bound = Circular 
          Bound Radius = {bound_radius} [m] 
        END
        
        
        ! $P      = areaAve("Pressure","plane_{i}");
        ! $Pg     = areaAve("Pressure.Gradient","plane_{i}");
        ! $T      = areaAve("Temperature","plane_{i}");
        ! $V      = massFlowAve("Velocity","plane_{i}");
        ! $rho    = areaAve("Density","plane_{i}");
        ! $mu     = areaAve("Dynamic Viscosity","plane_{i}");
        ! $mu_eff = areaAve("Effective Viscosity","plane_{i}");
        ! $mut    = areaAve("Eddy Viscosity","plane_{i}");
        ! $a      = areaAve("Local Speed of Sound","plane_{i}");
        ! $M      = areaAve("Mach Number","plane_{i}");
        ! $R      = areaAve("R Gas Constant","plane_{i}");
        ! $Cp     = areaAve("Specific Heat Capacity at Constant Pressure","plane_{i}");
        
        ! $h      = areaAve("Static Enthalpy","plane_{i}");
        ! $s      = areaAve("Static Entropy","plane_{i}");
        
        ! $ht     = areaAve("Total Enthalpy","plane_{i}");
        
        ! $Et     = areaAve("Total Energy","plane_{i}");
        ! $tau    = areaAve("Wall Shear","plane_{i}");
        
        ! $P0     = areaAve("Total Pressure","plane_{i}");
        ! $T0     = areaAve("Total Temperature","plane_{i}");
        ! $P0_g   = areaAve("Total Pressure.Gradient","plane_{i}");
        
        ! $rho_m  = massFlowAve("Density","plane_{i}");
        ! $V_a    = areaAve("Velocity","plane_{i}");
        
        ! $r_a = areaAve("Radial Angular Coordinate","plane_{i}");
        ! $V_theta = areaAve("Velocity Circumferential","plane_{i}");
        ! $Vax   = areaAve("Velocity Axial","plane_{i}");
        ! $Vr    = areaAve("Velocity Radial","plane_{i}");
        ! $Vtheta_stn = areaAve("Velocity Circumferential In Stn Frame","plane_{i}");
        
        ! $mdot  = massFlow(plane_{i});
        
        
        !print FILE "$P,$Pg,$T,$V,$rho,$mu,$mu_eff,$mut,$a,$M,$R,$Cp,$h,$s,$ht,$Et,$tau,$P0,$T0,$P0_g,$rho_m,$V_a,$r_a,$Vtheta_a,$Vax,$Vr,$Vtheta_stn,$mdot\\n";
        """)

    f.write("\n!close(FILE);\n")

print(f"CSE script generated → {output_cse}")