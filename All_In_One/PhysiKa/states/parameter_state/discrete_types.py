discrete_method = (
    ('fem', 'FEM', 'finte element method'),
    ('mass_spring', 'mass_spring', 'mass spring method'),
    ('meshless', 'meshless', 'meshless method')
)
#(para_name, data_type, if exposed, (Enum))
fem_parameter = ()
mass_spring_parameter = (('stiffness', 'float', True,''),
                         ('solver','enum',True,(('newton', 'Newton','newton method to solve'),
                                                ('fastMS_original','Fast Mass Spring','Fast mass spring to solve'),
                                                ('fastMS_ChebyshevSIM','Chebyshev','Fase mass spring with Chebyshev')
                                                ))
)
meshless_parameter = ()
