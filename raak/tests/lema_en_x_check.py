"""[raak local] Comprobacion del lema 1 enunciado en las variables x (15-11-2026): cajas no centradas, radios distintos,
bloques arbitrarios. Compara el intervalo en x con el de las cantidades escaladas del codigo y muestrea la caja.
uso: python tests/lema_en_x_check.py  (necesita numpy)"""
import numpy as np
rng=np.random.default_rng(1); worst=0; viol=0
for t in range(4000):
    n=rng.integers(2,8); lo=rng.uniform(-5,5,n); wid=rng.uniform(0.01,4,n); hi=lo+wid
    m=(lo+hi)/2; rho=wid/2
    a=rng.uniform(-2,2,n); b=rng.uniform(-2,2,n); Q=(np.outer(a,b)+np.outer(b,a))/2
    mb=rng.integers(0,4); sig=rng.choice([-1.,1.],mb); W=rng.uniform(-1,1,(mb,n))*(rng.random((mb,n))<0.6)
    R=Q-sum(sig[l]*np.outer(W[l],W[l]) for l in range(mb)) if mb else Q.copy()
    s=np.abs(W)@rho if mb else np.zeros(0)
    L=U=0.0
    for l in range(mb):
        L+=min(0,sig[l]*s[l]**2); U+=max(0,sig[l]*s[l]**2)
    for i in range(n):
        L+=min(0,R[i,i]*rho[i]**2); U+=max(0,R[i,i]*rho[i]**2)
        for j in range(i+1,n):
            L-=2*abs(R[i,j])*rho[i]*rho[j]; U+=2*abs(R[i,j])*rho[i]*rho[j]
    D=np.diag(rho); Rh=D@R@D; Wh=W*rho if mb else W
    L2=U2=0.0
    for l in range(mb):
        sl=np.abs(Wh[l]).sum(); L2+=min(0,sig[l]*sl**2); U2+=max(0,sig[l]*sl**2)
    for i in range(n):
        L2+=min(0,Rh[i,i]); U2+=max(0,Rh[i,i])
        for j in range(i+1,n): L2-=2*abs(Rh[i,j]); U2+=2*abs(Rh[i,j])
    worst=max(worst,abs(L-L2)/(1+abs(L)),abs(U-U2)/(1+abs(U)))
    X=np.where(rng.random((200,n))<0.5,lo,hi); X[100:]=rng.uniform(lo,hi,(100,n))
    f=np.einsum('ki,ij,kj->k',X,Q,X); lin=2*X@(Q@m)-m@Q@m; g=f-lin
    tol=1e-9*(1+abs(L)+abs(U))
    if (g<L-tol).any() or (g>U+tol).any(): viol+=1
print("productos 4000, violaciones",viol,"dif max entre enunciado en x y en eps",worst)
m=np.array([1,1,0.]);Q=np.array([[1,1,0],[1,1,0],[0,0,-1.]]);print("ejemplo guia: 2Qm",2*Q@m,"mQm",m@Q@m)
# ejemplo con radios distintos: x1 en [0,2], x2 en [1,5], x3 en [-1,1]
lo=np.array([0,1,-1.]);hi=np.array([2,5,1.]);m=(lo+hi)/2;rho=(hi-lo)/2
print("ejemplo 2: m",m,"rho",rho,"2Qm",2*Q@m,"mQm",m@Q@m)
import itertools
V=np.array(list(itertools.product(*zip(lo,hi))));G=np.linspace(lo,hi,41)
P=np.array(list(itertools.product(*G.T)));f=np.einsum('ki,ij,kj->k',P,Q,P)-2*P@(Q@m)+m@Q@m
print("rango verdadero del residuo (malla):",f.min(),f.max())
