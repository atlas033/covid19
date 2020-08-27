import os
import numpy as np

from epidemics.country.country import EpidemicsCountry

import libepidemics #cpp backend

class Object(object):
        pass

class ModelBase( EpidemicsCountry ):


  def __init__( self, **kwargs ):

    super().__init__( **kwargs )

  def solve_ode( self, y0, T, t_eval, N, p ):
    
    seird_int = libepidemics.country.seirdg_int_reparam
    dp        = libepidemics.country.DesignParameters(N=N)
    cppsolver = seird_int.Solver(dp)

    params = seird_int.Parameters(R0=p[0], D=p[1], F=p[2], Z=p[3],eps=p[4], tact=self.intday+p[5], dtact=p[6], kbeta=p[7])
  
    beta = p[0]/p[1]
    
    s0, i0 = y0

    e0 = beta*p[2]*i0
    s0 = s0 - e0

    y0cpp   = (s0, e0, i0, 0.0, 0.0) # S E I R D
    initial = seird_int.State(y0cpp)
    
    cpp_res = cppsolver.solve(params, initial, t_eval=t_eval, dt = 0.01)
    
    infected  = np.zeros(len(cpp_res))
    recovered = np.zeros(len(cpp_res))
    exposed   = np.zeros(len(cpp_res))
    deaths    = np.zeros(len(cpp_res))

    for idx,entry in enumerate(cpp_res):
        infected[idx]  = N-entry.S()-entry.E()
        exposed[idx]   = N-entry.S()
        recovered[idx] = entry.R()
        deaths[idx]    = entry.D()

    # Fix bad values
    infected[np.isnan(infected)] = 0
    deaths[np.isnan(deaths)]     = 0
    
    # Create Solution Object
    sol = Object()
    sol.y = infected
    sol.e = exposed
    sol.r = recovered
    sol.d = deaths
 
    return sol
