import numpy as np 

T0 = 294
gamma = 1.4
R = 287
T_Tt = 0.68966
T_inf = 300
a = (gamma*R*T_inf)**0.5
M = 1.5
V = M*a
P_inf = 75514.72
# P_inf = 53000 # Pa
rho = P_inf/(R*T_inf)
MU_REF= 1.716E-5
MU_T_REF= 273.15
SUTHERLAND_CONSTANT= 110.4
mu = MU_REF * ((T_inf/MU_T_REF)**1.5) * ((MU_T_REF+SUTHERLAND_CONSTANT)/(T_inf+SUTHERLAND_CONSTANT))
L_ref = 0.810491484086 # m
Re = (rho*V*L_ref)/mu
#Re = 14.6e6
#rho = Re*mu/(V*L_ref)
#P_inf = T_inf*R/rho
print(f"Reynolds:{Re/1e7} E7")
print("Densidad: " ,rho)
print("Viscocidad: ",mu)
print("a:", a)
print("Temp_inf", T_inf)
print("P_inf", P_inf)