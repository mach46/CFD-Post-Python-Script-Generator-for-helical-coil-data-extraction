import numpy as np
import pandas as pd

#MODE = "rotating"   # or "stationary"
MODE = "stationary"
# =========================================
# USER INPUT (ONLY THIS SECTION)
# =========================================

def x_func(t):
    return (0.01 + (0.024020000000021437-0.01)*t/(2*np.pi*8.925409208607137))*np.cos(t)


def y_func(t):
    return (0.01 + (0.024020000000021437-0.01)*t/(2*np.pi*8.925409208607137))*np.sin(t)


def z_func(t):
    return (0.11215669211535731/(2*np.pi*8.925409208607137))*t

t_start = 0
t_end   = 2*np.pi* 8.925409208607137

# =========================================
# OUTPUT PATHS
# =========================================

centerline_csv  = r"E:\rotation_case_hpc\d4_stationary\data analysis\d4_centerline.csv"
arclength_csv   = r"E:\rotation_case_hpc\d4_stationary\data analysis\d4_centerline_arclength.csv"
output_cse      = r"E:\rotation_case_hpc\d4_stationary\data analysis\d4_stationary_script.cse"
output_csv      = r"E:\rotation_case_hpc\d4_stationary\data analysis\d4_stationary_extracted_data.csv"
bound_radius    = 0.005 #m
n_points = 1000

# =========================================
# STEP 1: DENSE SAMPLING
# =========================================

t_dense = np.linspace(t_start, t_end, 3000)

x_dense = x_func(t_dense)
y_dense = y_func(t_dense)
z_dense = z_func(t_dense)

# =========================================
# STEP 2: ARC LENGTH
# =========================================

dx = np.gradient(x_dense, t_dense)
dy = np.gradient(y_dense, t_dense)
dz = np.gradient(z_dense, t_dense)

dt = np.gradient(t_dense)
ds = np.sqrt(dx**2 + dy**2 + dz**2) * dt

s = np.cumsum(ds)
s = s - s[0]

# =========================================
# STEP 3: UNIFORM ARC-LENGTH POINTS
# =========================================



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

df_s.to_csv(arclength_csv, index=False, header=True)

print(f"Arclength CSV saved -→ {arclength_csv}")
# =========================================
# STEP 7: GENERATE CSE
# =========================================

# =========================
# VARIABLE CONFIG
# =========================

common_header = "Pressure,Pressure Gradient,Temperature,Velocity,Density,Dynamic Viscosity,Effective Viscosity,Eddy Viscosity,Speed Of Sound,Mach number,Rgas,Cp,Static Enthalpy,Static Entropy,Total Enthalpy,Total Energy,Wall Shear,Total Pressure,Total Temperature,Total Pressure Gradient,Density mwa,Velocity awa,"

# -------- rotating-only --------
rot_header = "Radial coordinate,V_theta,V_axial,V_radial,V_theta_stn,"
rot_print = "$r_a,$V_theta,$Vax,$Vr,$Vtheta_stn,"

# -------- stationary --------
stat_header = "V_axial,"
stat_print = "$Vax,"

if MODE == "rotating":
    extra_header = rot_header
    extra_print = rot_print
else:
    extra_header = stat_header
    extra_print = stat_print

# =========================================
# WRITE CSE
# =========================================

with open(output_cse, "w") as f:

    f.write("COMMAND FILE:\n  CFX Post Version = 23.2\nEND\n\n")

    # Header
    f.write(f"""!open(FILE, '> {output_csv}');
!print FILE "{common_header}{extra_header}mdot\\n";
""")

    # Loop
    for i in range(len(x)):

        # -------- COMMON DEFINITIONS (IMPORTANT: f-string) --------
        defs_block = f"""
! $P      = areaAve("Pressure","scriptingplane");
! $Pg     = areaAve("Pressure.Gradient","scriptingplane");
! $T      = areaAve("Temperature","scriptingplane");
! $V      = massFlowAve("Velocity","scriptingplane");
! $rho    = areaAve("Density","scriptingplane");
! $mu     = areaAve("Dynamic Viscosity","scriptingplane");
! $mu_eff = areaAve("Effective Viscosity","scriptingplane");
! $mut    = areaAve("Eddy Viscosity","scriptingplane");
! $a      = areaAve("Local Speed of Sound","scriptingplane");
! $M      = areaAve("Mach Number","scriptingplane");
! $R      = areaAve("R Gas Constant","scriptingplane");
! $Cp     = areaAve("Specific Heat Capacity at Constant Pressure","scriptingplane");
! $h      = areaAve("Static Enthalpy","scriptingplane");
! $s      = areaAve("Static Entropy","scriptingplane");
! $ht     = areaAve("Total Enthalpy","scriptingplane");
! $Et     = areaAve("Total Energy","scriptingplane");
! $tau    = areaAve("Wall Shear","scriptingplane");
! $P0     = areaAve("Total Pressure","scriptingplane");
! $T0     = areaAve("Total Temperature","scriptingplane");
! $P0_g   = areaAve("Total Pressure.Gradient","scriptingplane");
! $rho_m  = massFlowAve("Density","scriptingplane");
! $V_a    = areaAve("Velocity","scriptingplane");
"""

        # -------- MODE-SPECIFIC DEFINITIONS --------
        if MODE == "rotating":
            extra_defs_block = f"""
! $r_a = areaAve("Radial Angular Coordinate","scriptingplane");
! $V_theta = areaAve("Velocity Circumferential","scriptingplane");
! $Vax   = areaAve("Velocity Axial","scriptingplane");
! $Vr    = areaAve("Velocity Radial","scriptingplane");
! $Vtheta_stn = areaAve("Velocity Circumferential In Stn Frame","scriptingplane");
"""
        else:
            extra_defs_block = f"""
! $Vax = areaAve("Velocity Axial","scriptingplane");
"""

        # -------- WRITE BLOCK --------
        f.write(f""" 
PLANE: scriptingplane
  Option = Point and Normal 
  Point = {x[i]} [m], {y[i]} [m], {z[i]} [m] 
  Normal = {tx[i]}, {ty[i]}, {tz[i]} 
  Plane Bound = Circular 
  Bound Radius = {bound_radius} [m] 
END

{defs_block}
{extra_defs_block}

! $mdot = massFlow(scriptingplane);

!print FILE "$P,$Pg,$T,$V,$rho,$mu,$mu_eff,$mut,$a,$M,$R,$Cp,$h,$s,$ht,$Et,$tau,$P0,$T0,$P0_g,$rho_m,$V_a,{extra_print}$mdot\\n";
""")

    f.write("\n!close(FILE);\n")

print(f"CSE script generated → {output_cse}")