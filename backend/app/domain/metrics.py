import numpy as np
from scipy.stats import kendalltau, pearsonr

def mae(p, g): p,g=np.array(p),np.array(g); return float(np.abs(p-g).mean())
def rmse(p,g): p,g=np.array(p),np.array(g); return float(np.sqrt(((p-g)**2).mean()))
def brier(p,g): p,g=np.array(p),np.array(g); return float(((p-g)**2).sum())
def corr_pearson(p,g): p,g=np.array(p),np.array(g); return float(pearsonr(p,g)[0])
def corr_kendall(p,g): p,g=np.array(p),np.array(g); return float(kendalltau(p,g).correlation)
