import os
import shutil

# ============================
# USER INPUTS
# ============================

diameters = ["d2", "d3", "d4", "d5"]
rpms = ["5k", "10k", "15k", "20k", "25k"]

# boundary names (IMPORTANT)
inlet_name  = "inlet"
outlet_name = "outlet"
wall_name   = "wall"


for diameter in diameters:
    for rpm in rpms:
        # output directory
        output_dir = fr"E:\Dhairya_Internship_IITKGP\rotation_case_hpc\{diameter}\{diameter}_{rpm}_rpm\data analysis"
        os.makedirs(output_dir, exist_ok=True)
        common_folder_path = fr"C:\Dhairya_internship\cfdpost_script_files\state_point_files"
        os.makedirs(common_folder_path, exist_ok=True)

        cse_file     = os.path.join(output_dir, f"rotation_{diameter}_{rpm}_state_point.cse")
        cse_file_common = os.path.join(common_folder_path, f"rotation_{diameter}_{rpm}_state_point.cse")
        output_csv     = os.path.join( f"rotation_{diameter}_{rpm}_state_point_data.csv")

        # ============================
        # WRITE CSE FILE
        # ============================

        with open(cse_file, "w") as f:

            f.write(f"""
COMMAND FILE:
  CFX Post Version = 23.2
END

!open(FILE, '> {output_csv}');
    
# ==============================
# HEADER
# ==============================
!print FILE "Pin,Tin,rhoin,muin,hin,sin,vin,Min,VThetain,P0in,T0in,htin,Pout,Tout,rhoout,muout,hout,sout,vout,Mout,VThetaout,P0out,T0out,htout,mdot,Fx,Fy,Fz,Tx,Ty,Tz,tau_w\\n";

# ==============================
# INLET (massFlowAve preferred)
# ==============================
! $Pin   = massFlowAve("Pressure","{inlet_name}");
! $Tin   = massFlowAve("Temperature","{inlet_name}");
! $rhoin = massFlowAve("Density","{inlet_name}");
! $muin = massFlowAve("Dynamic Viscosity","{inlet_name}");


! $hin   = massFlowAve("Static Enthalpy","{inlet_name}");
! $sin   = massFlowAve("Static Entropy","{inlet_name}");

! $vin   = massFlowAve("Velocity","{inlet_name}");
! $Min   = massFlowAve("Mach Number","{inlet_name}");
! $VThetain  = areaAve("Velocity Circumferential","{inlet_name}");

! $P0in  = massFlowAve("Total Pressure","{inlet_name}");
! $T0in  = massFlowAve("Total Temperature","{inlet_name}");
! $htin  = massFlowAve("Total Enthalpy","{inlet_name}");

# ==============================
# OUTLET
# ==============================
! $Pout   = massFlowAve("Pressure","{outlet_name}");
! $Tout   = massFlowAve("Temperature","{outlet_name}");
! $rhoout = massFlowAve("Density","{outlet_name}");
! $muout = massFlowAve("Dynamic Viscosity","{outlet_name}");


! $hout   = massFlowAve("Static Enthalpy","{outlet_name}");
! $sout   = massFlowAve("Static Entropy","{outlet_name}");

! $vout   = massFlowAve("Velocity","{outlet_name}");
! $Mout   = massFlowAve("Mach Number","{outlet_name}");
! $VThetaout  = areaAve("Velocity Circumferential","{outlet_name}");

! $P0out  = massFlowAve("Total Pressure","{outlet_name}");
! $T0out  = massFlowAve("Total Temperature","{outlet_name}");
! $htout  = massFlowAve("Total Enthalpy","{outlet_name}");

# ==============================
# MASS FLOW
# ==============================
! $mdot = massFlow("{outlet_name}");

# ==============================
# FORCES
# ==============================
! $Fx = force("{wall_name}","X");
! $Fy = force("{wall_name}","Y");
! $Fz = force("{wall_name}","Z");

# ==============================
# TORQUES
# ==============================
! $Tx = torque("{wall_name}","X");
! $Ty = torque("{wall_name}","Y");
! $Tz = torque("{wall_name}","Z");

# ==============================
# WALL SHEAR STRESS
# ==============================
! $tau_w = areaAve("Wall Shear","{wall_name}");

# ==============================
# PRINT
# ==============================
!print FILE "$Pin,$Tin,$rhoin,$muin,$hin,$sin,$vin,$Min,$VThetain,$P0in,$T0in,$htin,$Pout,$Tout,$rhoout,$muout,$hout,$sout,$vout,$Mout,$VThetaout,$P0out,$T0out,$htout,$mdot,$Fx,$Fy,$Fz,$Tx,$Ty,$Tz,$tau_w\\n";

!close(FILE);
""")

            print(f"Full CSE script generated   → {cse_file}")

        shutil.copy(cse_file, cse_file_common)
        print(f"Full CSE script copied      → {cse_file_common}")