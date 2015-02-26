import numpy as np
from scipy.misc import factorial
import matplotlib.pyplot as plt

zernike_noll=[]
for i in range(15):
    pols = range(-i,i+1,2)
    pols = sorted(pols, key = lambda x: abs(x))
    for p in pols:
        zernike_noll.append((i,p))
print len(zernike_noll)

def rnm(n,m,rho):
    """
    Return an array with the zernike Rnm polynomial calculated at rho points.
    
    
    **ARGUMENTS:**
    
        === ==========================================
        n    n order of the Zernike polynomial
        m    m order of the Zernike polynomial
        rho  Matrix containing the radial coordinates. 
        === ==========================================       
    
    .. note:: For rho>1 the returned value is 0
    
    .. note:: Values for rho<0 are silently returned as rho=0
    
    """
    
    if(type(n) is not int):
        raise Exception, "n must be integer"
    if(type(m) is not int):
        raise Exception, "m must be integer"
    if (n-m)%2!=0:
        raise Exception, "n-m must be even"
    if abs(m)>n:
        raise Exception, "The following must be true |m|<=n"
    mask=(rho<=1)
    
    if(n==0 and m==0):
        ret = np.zeros(rho.shape)
        ret[mask]+=1
        return ret
    rho=np.where(rho<0,0,rho)
    Rnm=np.zeros(rho.shape)
    S=(n-abs(m))/2
    for s in range (0,S+1):
        CR=pow(-1,s)*factorial(n-s)/ \
            (factorial(s)*factorial(-s+(n+abs(m))/2)* \
            factorial(-s+(n-abs(m))/2))
        p=CR*pow(rho,n-2*s)
        Rnm=Rnm+p
    ret = np.zeros(rho.shape)
    ret[mask]+=Rnm[mask]
    return ret
    
def zernike(n,m,rho,theta):
    """
    Returns the an array with the Zernike polynomial evaluated in the rho and 
    theta.
    
    **ARGUMENTS:** 
    
    ===== ==========================================     
    n     n order of the Zernike polynomial
    m     m order of the Zernike polynomial
    rho   Matrix containing the radial coordinates. 
    theta Matrix containing the angular coordinates.
    ===== ==========================================
 
    .. note:: For rho>1 the returned value is 0
    
    .. note:: Values for rho<0 are silently returned as rho=0
    """
    
    
    Rnm=rnm(n,m,rho)
    
    NC=np.sqrt(2*(n+1))
    S=(n-np.abs(m))/2
    
    if m>0:
        Zmn=NC*Rnm*np.cos(m*theta)
    
    elif m<0:
        Zmn=NC*Rnm*np.sin(m*theta)
    else:
        Zmn=np.sqrt(0.5)*NC*Rnm
    return Zmn

def zernike_grid(n,m,grid_size):
    x=np.linspace(-1.,1.,grid_size)
    y=np.linspace(-1.,1.,grid_size)
    X,Y = np.meshgrid(x,y)
    rho = np.sqrt(X**2+Y**2)
    theta = np.arctan2(Y,X)
    return X,Y,zernike(n,m,rho,theta)

def zernike_grid_i(noll_index,grid_size):
    n,m=zernike_noll[noll_index-1]
    return zernike_grid(n,m,grid_size)

if __name__ == '__main__':
    f, axarr = plt.subplots(7, 7, figsize=(7,7))
    for i,ax in enumerate(axarr.flatten()):
        X,Y,Z=zernike_grid_i(i+1,12)
        ax.set_title('zern_'+str(i+1))
        ax.imshow(Z)
    plt.tight_layout()