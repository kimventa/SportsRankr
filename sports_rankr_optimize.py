from scipy.optimize import fmin_tnc
import final_algorithm2010

x0 = [13.5,8.3,0.0001,0.6,5,7.6] #initial guesses for all TrueSkillfn inputs
bounds = [(0.00001,None), (0.00001,None), (0.00001,None), (0.00001,None), 
	(0.00001,None), (0.00001,None)]

x, nfeval, rc = fmin_tnc(func=TrueSkillTNCv5quicktest.main, x0=x0, fprime=None, 
	approx_grad=True, bounds=bounds)