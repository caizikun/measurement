import numpy as np

def simplex_method(f,initial_simplex,
                   a=1.,y=2.,p=-0.5,s=0.5, 
                   tolerance=0.001, max_cycles=25,
                   verbose=False):
    """
    This implements the Nelder Mead minimisation method. This is
    a gradient free minimisation method that starts with an simplex shape
    (which is a special polytope of N + 1 vertices in N dimensions)
    and uses reflection, expansion, contraction and shrinking to find a 
    minimum. See also http://en.wikipedia.org/wiki/Nelder Mead_method.
    Arguments:
    - f is the function call that produces the value to be minimized.
    f should accept a single argument, that is a tuple of size N, 
    where N is the dimension of the search space, and return a single real value.
    - initial_simplex is the initial guess simplex: An array of size (N+1) x N
    - a,y,p,s are respectively the reflection, the expansion, the contraction and 
    the shrink coefficient.
    - If the variance in the location of the vertices is less than the tolerance
    in all dimensions, the optimisation is halted.
    - If the number of iterations is max_cycles, the optimisation is halted.

    """
    N=len(initial_simplex)
    J=np.zeros(N)
    V = initial_simplex.copy()
    eval_all=True
    J[0]=f(V[0])

    for j in range(max_cycles):
        if verbose: print '\n ============== \n j: ', j
        #0. Measure value at initial simplex vertices:
        if eval_all:
            for i in range(1,N):
              J[i]=f(V[i])
              eval_all = False
            if verbose: print 'Simplex J values:',J
        else:
            J[-1]=f(V[-1])
            if verbose: print 'New vertex value:',J[-1]


        #1. Order according to the values at the vertices:
        J_o=np.sort(J)
        V_o=V[np.argsort(J)]

        #2. Calculate v_c the centroid of all points except worst
        v_c=1./(N-1.)*np.sum(V_o[:-1],axis=0)

        #3. Reflection
        v_r=v_c + a*(v_c-V_o[-1])
        j_r=f(v_r)

        if J_o[0]<=j_r<J_o[-1]:
            V_o[-1]=v_r
            if verbose: print 'case 1: replace'
        elif j_r<J_o[0]:
            #4 Expansion
            v_e=v_c+y*(v_c-V_o[-1])
            j_e=f(v_e)
            if j_e<j_r:
                if verbose: print 'case 2: expand success'
                V_o[-1]=v_e
            else:
                if verbose: print 'case 2: expand fail'
                V_o[-1]=v_r
        else:
            #5. Contraction
            v_s=v_c+p*(v_c-V_o[-1])
            j_s=f(v_s)
            if j_s<J_o[-1]:
                if verbose: print 'case 3: contract'
                V_o[-1]=v_s
            else:
                #6. Reduction
                if verbose: print 'case 4: shrink/reduct'
                V_o[1:]=V_o[1:]+s*(V_o[1:]-V_o[0])
                eval_all=True

        V=V_o
        J=J_o
          
        var=np.var(V,axis=0)
        if verbose: print 'Average xyz_var', np.sum(var)
        if (var<tolerance).all():
            print '========================='
            print 'Convex success'
            print '========================='
            break    

    return V[0]

def test_simplex_method(**kw):
    def f(x):   # The rosenbrock function
        return .5*(1 - x[0])**2 + (x[1] - x[0]**2)**2

    initial_simplex = np.array([[ 2, 2],
                        [3,3],
                        [2, 1],
                      ],dtype=np.float)

    print simplex_method(f,initial_simplex, **kw)