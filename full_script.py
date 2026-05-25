import numpy as np
import pandas as pd
import os
import shutil

#MODE = "rotating"   # or "stationary"
MODE = "rotating"
# =========================================
# USER INPUT (ONLY THIS SECTION)
# =========================================
diameter = "d5"
rpm = "25k"

if diameter == "d2":
    r_start = 0.01
    r_end = 0.017711374999993368
    height = 0.061689180574821464
    N = 4.909213797136834
    length = 0.432

elif diameter == "d3":
    r_start = 0.01
    r_end = 0.02102387500000713
    height = 0.08818839902226061
    N = 7.018016793113211
    length = 0.690

elif diameter == "d4":
    r_start = 0.01
    r_end = 0.024020000000021437
    height = 0.11215669211535731
    N = 8.925409208607137
    length = 0.961

elif diameter == "d5":
    r_start = 0.01
    r_end = 0.026768000000034556
    height = 0.13414004375116345
    N = 10.674840343081605
    length = 1.241

else:
    raise ValueError(f"Invalid diameter: {diameter}")

def x_func(t):
    return (r_start + (r_end-r_start)*t/(2*np.pi*N))*np.cos(t)


def y_func(t):
    return (r_start + (r_end-r_start)*t/(2*np.pi*N))*np.sin(t)


def z_func(t):
    return (height/(2*np.pi*N))*t

t_start = 0
t_end   = 2*np.pi* N

# =========================================
# OUTPUT PATHS
# =========================================

folder_path = fr"E:\Dhairya_Internship_IITKGP\rotation_case_hpc\{diameter}\{diameter}_{rpm}_rpm\data analysis"
os.makedirs(folder_path, exist_ok=True)
common_folder_path = fr"C:\Dhairya_internship\cfdpost_script_files"
os.makedirs(common_folder_path, exist_ok=True)

centerline_csv = os.path.join(folder_path, f"{diameter}_centerline.csv")
arclength_csv  = os.path.join(folder_path, f"{diameter}_centerline_arclength.csv")
output_cse     = os.path.join(folder_path, f"{diameter}_{rpm}_script.cse")
output_cse_common = os.path.join(common_folder_path, f"{diameter}_{rpm}_script.cse")
output_csv     = os.path.join( f"{diameter}_{rpm}_extracted_data.csv")

bound_radius    = 0.005 #m
ds_target = 0.0005  # meters
n_points = int(length / ds_target)


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

# Generate arc-length locations at 1 mm spacing
#s_uniform = np.arange(0, s[-1], ds_target)

# Ensure last point is included (optional but recommended)
#s_uniform = np.append(s_uniform, s[-1])

# Interpolate corresponding parameter t
#t_uniform = np.interp(s_uniform, s, t_dense)

print(f"Total planes created: {len(s_uniform)}")

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

common_header = (
"Pressure,Pressure Coefficient,Dynamic Pressure,"
"Temperature,Density,"
"Dynamic Viscosity,Effective Viscosity,Eddy Viscosity,"
"Thermal Conductivity,Effective Thermal Conductivity,"
"Prandtl Number,Effective Prandtl Number,"
"R Gas Constant,Specific Heat Capacity,"
"Static Enthalpy,Entropy,Total Energy,Speed Of Sound,"
"Velocity (mwa),Density (mwa),Mach Number (mwa),"
"Total Pressure (mwa),Total Temperature (mwa),Total Enthalpy (mwa),"
"Velocity Axial (mwa),Velocity Radial (mwa),Velocity Circumferential (mwa),"
"Dp Dx,Dp Dy,Dp Dz,"
"Vorticity X,Vorticity Y,Vorticity Z,Vorticity Magnitude,"
"Q Criterion Normalized,Q Criterion Raw,Lambda 2 Criterion,Helicity,"
"Turbulence Kinetic Energy,Turbulence Eddy Frequency,Turbulence Eddy Dissipation,Turbulence Intensity,"
"Wall Shear,Wall Shear X,Wall Shear Y,Wall Shear Z,"
"Wall Temperature,Wall Adjacent Temperature,"
"Heat Flux,"
"X,Y,Z,Angular Coordinate,Radial Angular Coordinate"
)

# -------- rotating-only --------
rot_header = (
"Radial Angular Coordinate,"
"Velocity Circumferential (mwa),"
"Velocity Axial (mwa),"
"Velocity Radial (mwa),"
"Relative Total Pressure (mwa),"
"Rothalpy (mwa)"
)
rot_print = "$r_a,$V_theta,$Vax,$Vr,$P0_rel,$roth"

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
!print FILE "{common_header},{extra_header},mdot\\n";
""")

    # Loop
    for i in range(len(x)):

        # -------- COMMON DEFINITIONS (IMPORTANT: f-string) --------
        defs_block = f"""
# -------------------------------
# AREA AVERAGES (local properties)
# -------------------------------

! $P        = areaAve("Pressure","scriptingplane");
! $Cp_coef  = areaAve("Pressure Coefficient","scriptingplane");
! $q_dyn    = areaAve("Dynamic Pressure","scriptingplane");

! $T        = areaAve("Temperature","scriptingplane");
! $rho      = areaAve("Density","scriptingplane");

! $mu       = areaAve("Dynamic Viscosity","scriptingplane");
! $mu_eff   = areaAve("Effective Viscosity","scriptingplane");
! $mut      = areaAve("Eddy Viscosity","scriptingplane");

! $k_th     = areaAve("Thermal Conductivity","scriptingplane");
! $k_eff    = areaAve("Effective Thermal Conductivity","scriptingplane");

! $Pr       = areaAve("Prandtl Number","scriptingplane");
! $Pr_eff   = areaAve("Effective Prandtl Number","scriptingplane");

! $R        = areaAve("R Gas Constant","scriptingplane");
! $Cp       = areaAve("Specific Heat Capacity at Constant Pressure","scriptingplane");

! $h        = areaAve("Static Enthalpy","scriptingplane");
! $s        = areaAve("Static Entropy","scriptingplane");

! $Et       = areaAve("Total Energy","scriptingplane");

! $a        = areaAve("Local Speed of Sound","scriptingplane");

# -------------------------------
# MASS FLOW AVERAGES (flow physics)
# -------------------------------

! $V        = massFlowAve("Velocity","scriptingplane");
! $rho_m    = massFlowAve("Density","scriptingplane");

! $M        = massFlowAve("Mach Number","scriptingplane");

! $P0       = massFlowAve("Total Pressure","scriptingplane");
! $T0       = massFlowAve("Total Temperature","scriptingplane");

! $ht       = massFlowAve("Total Enthalpy","scriptingplane");

! $Vax      = massFlowAve("Velocity Axial","scriptingplane");
! $Vr       = massFlowAve("Velocity Radial","scriptingplane");
! $Vtheta   = massFlowAve("Velocity Circumferential","scriptingplane");

# -------------------------------
# GRADIENTS (components only)
# -------------------------------

! $Pg_x     = areaAve("Dp Dx","scriptingplane");
! $Pg_y     = areaAve("Dp Dy","scriptingplane");
! $Pg_z     = areaAve("Dp Dz","scriptingplane");

# -------------------------------
# VORTEX / FLOW STRUCTURE
# -------------------------------

! $vort_x   = areaAve("Vorticity X","scriptingplane");
! $vort_y   = areaAve("Vorticity Y","scriptingplane");
! $vort_z   = areaAve("Vorticity Z","scriptingplane");
! $vort_mag = areaAve("Vorticity","scriptingplane");

! $Qcritnorm    = areaAve("Q Criterion Normalized","scriptingplane");
! $Qcritraw    = areaAve("Q Criterion Raw","scriptingplane");
! $lambda2  = areaAve("Lambda 2 Criterion","scriptingplane");
! $hel      = areaAve("Helicity","scriptingplane");

# -------------------------------
# TURBULENCE
# -------------------------------

! $k_turb   = areaAve("Turbulence Kinetic Energy","scriptingplane");
! $omega    = areaAve("Turbulence Eddy Frequency","scriptingplane");
! $eps      = areaAve("Turbulence Eddy Dissipation","scriptingplane");
! $TI       = areaAve("Turbulence Intensity","scriptingplane");

# -------------------------------
# WALL / HEAT TRANSFER
# -------------------------------

! $tau      = areaAve("Wall Shear","scriptingplane");
! $tau_x    = areaAve("Wall Shear X","scriptingplane");
! $tau_y    = areaAve("Wall Shear Y","scriptingplane");
! $tau_z    = areaAve("Wall Shear Z","scriptingplane");

! $T_wall   = areaAve("Wall Temperature","scriptingplane");
! $T_adj    = areaAve("Wall Adjacent Temperature","scriptingplane");

! $q_flux   = areaAve("Heat Flux","scriptingplane");

# -------------------------------
# COORDINATES
# -------------------------------

! $x        = areaAve("X","scriptingplane");
! $y        = areaAve("Y","scriptingplane");
! $z        = areaAve("Z","scriptingplane");

! $theta    = areaAve("Angular Coordinate","scriptingplane");
! $r_theta  = areaAve("Radial Angular Coordinate","scriptingplane");
"""

        # -------- MODE-SPECIFIC DEFINITIONS --------
        if MODE == "rotating":
            extra_defs_block = f"""
! $r_a = areaAve("Radial Angular Coordinate","scriptingplane");

! $V_theta = massFlowAve("Velocity Circumferential","scriptingplane");
! $Vax     = massFlowAve("Velocity Axial","scriptingplane");
! $Vr      = massFlowAve("Velocity Radial","scriptingplane");

! $P0_rel   = massFlowAve("Relative Total Pressure","scriptingplane");
! $roth     = massFlowAve("Rothalpy","scriptingplane");
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

!print FILE "$P,$Cp_coef,$q_dyn,\
$T,$rho,\
$mu,$mu_eff,$mut,\
$k_th,$k_eff,\
$Pr,$Pr_eff,\
$R,$Cp,\
$h,$s,$Et,$a,\
$V,$rho_m,$M,$P0,$T0,$ht,\
$Vax,$Vr,$Vtheta,\
$Pg_x,$Pg_y,$Pg_z,\
$vort_x,$vort_y,$vort_z,$vort_mag,\
$Qcritnorm,$Qcritraw,$lambda2,$hel,\
$k_turb,$omega,$eps,$TI,\
$tau,$tau_x,$tau_y,$tau_z,\
$T_wall,$T_adj,\
$q_flux,\
$x,$y,$z,$theta,$r_theta,\
{extra_print},$mdot\\n";
""")

    f.write("\n!close(FILE);\n")

print(f"CSE script generated → {output_cse}")

# copy file to another location
shutil.copy(output_cse, common_folder_path)