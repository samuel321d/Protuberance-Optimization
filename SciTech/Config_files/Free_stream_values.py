import numpy as np 

T0 = 294
gamma = 1.4
R = 287
T_Tt = 0.68966
T_inf = T_Tt*T0
a = (gamma*R*T_inf)**0.5
M = 1.5
V = M*a
P_inf = 53000 # Pa
rho = P_inf/(R*T_inf)
MU_REF= 1.716E-5
MU_T_REF= 273.15
SUTHERLAND_CONSTANT= 110.4
mu = MU_REF * ((T_inf/MU_T_REF)**1.5) * ((MU_T_REF+SUTHERLAND_CONSTANT)/(T_inf+SUTHERLAND_CONSTANT))
L_ref = 3.24 # m
Re = (rho*V*L_ref)/mu
print(f"Reynolds:{Re/1e7} E7")
print("Densidad: " ,rho)
print("Viscocidad: ",mu)

print("Temp_inf", T_inf)