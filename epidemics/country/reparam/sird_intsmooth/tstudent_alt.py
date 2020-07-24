import numpy as np

from .model_base import ModelBase


class Model( ModelBase ):


  def __init__( self, **kwargs ):

    self.modelName        = 'country.reparam.sird_intsmooth.tstudent_alt'
    self.modelDescription = 'Fit SIRD with smooth interventions on Daily Data with Positive StudentT Likelihood'
    self.likelihoodModel  = 'Positive StudentT'

    super().__init__( **kwargs )

 
  def get_variables_and_distributions( self ):
 
    self.nParameters = 7
    js = self.get_uniform_priors(
            ('R0', *self.defaults['R0']), 
            ('D', *self.defaults['D']), 
            ('eps', *self.defaults['eps']), 
            ('tact', *self.defaults['tact']),
            ('dtact', *self.defaults['dtact']),
            ('kbeta', *self.defaults['kbeta']),
            ('Degrees Of Freedom', *self.defaults['dof'])
            )
    
    return js
