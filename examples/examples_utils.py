from copy import deepcopy
import itertools
import numpy as np

def pfunc2array(func, outcomes=[2, 2, 2], settings=[1, 1, 1]):
    p = np.zeros([*outcomes, *settings])
    for a,b,c,x,y,z in itertools.product(*[range(i) for i in [*outcomes, *settings]]):
        p[a,b,c,x,y,z] = func(a,b,c,x,y,z)
    return p

def P_2PR(a, b, c, x, y, z):
    return ( 1 + (-1) ** (a + b + c + x*y + y*z) ) / 8

P_2PR_array = pfunc2array(P_2PR, [2, 2, 2], [2, 2, 2])


def P_W(a, b, c, x, y, z):
    if  a+ b + c == 1:
        return 1 / 3
    else:
        return 0
    
P_W_array = pfunc2array(P_W, [2, 2, 2], [1, 1, 1])

def P_PRbox():
    P_PRbox_array = np.zeros((2,2,2,2))
    for x, y, a, b in itertools.product(range(2), repeat=4):
        if (x, y) == (1, 1):
            if a != b:
                P_PRbox_array[a, b, x, y] = 1/2
        else:
            if a == b:
                P_PRbox_array[a, b, x, y] = 1/2
    return P_PRbox_array

P_PRbox_array = P_PRbox()

def P_GHZ():
    v = 1
    dist = np.zeros((2,2,2,1,1,1))
    for a in [0, 1]:
        for b in [0, 1]:
            for c in [0, 1]:
                if (a == b) and (b == c):
                    dist[a,b,c,0,0,0] = v/2 + (1-v)/8
                else:
                    dist[a,b,c,0,0,0] = (1-v)/8
    return dist

P_GHZ_array = P_GHZ()  

def bisection(InfSDP, probarray, tol_vis=1e-4, verbose=0, max_iter=20, use_lpi_constraints=False, feas_as_optim = True):
    v0, v1 = 0, 1
    vm = 1 # (v0 + v1)/2
    
    InfSDP.verbose = 0
    iteration = 0
    last_good = deepcopy(InfSDP)

    outputdims = probarray.shape[:int(len(probarray.shape)/2)]
    nroutputs = np.prod(outputdims)

    while abs(v1 - v0) >= tol_vis and iteration < max_iter:
        pnoisy = vm * probarray + (1-vm) * np.ones(outputdims) / nroutputs#distribution(visibility=vm)
        InfSDP.set_distribution(pnoisy, use_lpi_constraints=use_lpi_constraints)
        InfSDP.solve(feas_as_optim=feas_as_optim, dualise=True)
        if feas_as_optim:
            if verbose:
                print(iteration, "Maximum smallest eigenvalue:", "{:10.4g}".format(
                    InfSDP.primal_objective), "\tvisibility =", "{:.4g}".format(vm))
            if InfSDP.objective_value >= 0:
                v0 = vm
                vm = (v0 + v1)/2
            elif InfSDP.objective_value < 0:
                v1 = vm
                vm = (v0 + v1)/2
                last_good = deepcopy(InfSDP)
            # if abs(InfSDP.objective_value) <= 1e-7:
            #     break
        else:
            if verbose:
                if InfSDP.status in ['feasible', 'infeasible']:
                    print(iteration, "Feasibility status:\t", InfSDP.status, "\tvisibility =", "{:.4g}".format(vm))
            if InfSDP.status == 'feasible':
                v0 = vm
                vm = (v0 + v1)/2
            else:  # 'infeasible' or 'unknown'
                v1 = vm
                vm = (v0 + v1)/2
                last_good = deepcopy(InfSDP)
        
        iteration += 1
    
    return last_good, vm



