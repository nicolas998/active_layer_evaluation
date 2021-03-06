# AUTOGENERATED! DO NOT EDIT! File to edit: 00_core.ipynb (unless otherwise specified).

__all__ = ['get_intersec', 'percentiles', 'plot_hist2d', 'get_histogram', 'summary_metric', 'get_intersec_events',
           'colors']

# Cell
import numpy as np
import pandas as pd
import pylab as pl

colors = ['#52270C','#A1623B','#E7A011','#F3DE0A']

def get_intersec(metric, prod1, prod2, Me ,y1 = '2002', y2 = '2018'):
    '''Get the intersection for a given metric between two products of the event metrics data
    Inputs:
        -metric: the nme of the metric to analize.
        -prod1 and prod2: the products from to get the interserctio.
        -Me: Metrics table with the products and the metrics.
        -y1 and y2: initial and end years to analize.'''
    Mec = Me.loc[y1:y2]
    a = Mec[[metric,'link']][Mec['product'] == prod1]
    a.set_index([a.index, a.link], inplace=True)
    #a.drop_duplicates(inplace = True)
    b = Mec[[metric,'link']][Mec['product'] == prod2]
    b.set_index([b.index, b.link], inplace=True)
    #b.drop_duplicates(inplace = True)
    idx = a.index.intersection(b.index)
    return a,b,idx

def percentiles(obs, sim, steps = 10, bins = None, perc = 50, percMax = 99.5):
    '''Obtains the percentile for the sim value that corresponds to
    an oberved value.
    Parameters:
        -obs: observed peaks or time serie.
        -sim: simulated peaks or time serie.
        -steps: number of splits to estimate the percentile.
        -perc: percentile to estimate
        -percMax: Max value to divide the observations.
    Returns:
        -A vector (2,N) where the first row corresponds to the percentiles
        at the observation and the second to the percentiles at the simulation'''
    if bins is None:
        bins = np.linspace(obs.min(), np.percentile(obs, percMax), steps)
    X = []; Y = []
    for i,j in zip(bins[:-1], bins[1:]):
        Y.append(np.percentile(sim[(obs>i) & (obs<=j)], perc))
        X.append((i+j)/2.)
        #Y.append(np.percentile(sim[(obs>i) & (obs<=j)], perc))
    return np.vstack([X,Y])

def plot_hist2d(ax, Met, prod1, prod2, bins, metric='kge',x1=-1,x2=1,y = 2016,
                cmap = False, vmin = 0, vmax = 10000, cmin = 0, cmax = 10000):
    '''Make a 2d hist plot of a metric using two products from the metrics file.'''
    #Get the intersection
    B = Met.loc[y]
    a = B[[metric,'link']][B['product'] == prod1]
    b = B[[metric,'link']][B['product'] == prod2]
    idx = a.index.intersection(b.index)
    #Make the plot
    pl.hist2d(a.loc[idx][metric], b.loc[idx][metric], cmap = pl.get_cmap('coolwarm'),
              bins=bins, cmin = cmin, cmax = cmax, vmin = vmin, vmax = vmax)

    if cmap:
        cmap = pl.colorbar(orientation = 'horizontal', pad = 0.15)
        cmap.ax.tick_params(labelsize = 20)
    #cmap.set_ticks(t)
    ax.plot([x1,x2], [x1,x2], c = 'k', lw = 2)
    ax.tick_params(labelsize = 21)
    ax.set_xlim(x1,x2)
    ax.set_ylim(x1,x2)
    ax.set_xlabel(prod1, size = 21)
    ax.set_ylabel(prod2, size = 21)
    ax.set_title(prod2+' vs '+prod1, size = 23)
    return ax, cmap

def get_histogram(data, bins, inf = None, sup = None):
    '''Get an histogram for the given data taking into account
    an inferior limit to add there all the values less than it.'''
    h,b = np.histogram(data, bins)
    if inf is not None:
        h[0] +=  data[data<inf].size
    if sup is not None:
        h[-1] +=  data[data> sup].size
    h = h / h.sum()
    return h, b

def summary_metric(Met, products, metric, min_max = 'max', absolute = False):
    '''Produces a summary of a given metric including only the assigned products
    Parameters:
        - Met: Metric file DataFrame.
        - products: list of the products to be included.
        - metric: Name of the metric to evaluate, must be in the Metrics File.
        - min_max: is the metric a maximum or a minimum.
        - absolute: The value is absolute or not.'''
    G = Met.groupby(['link','product']).mean()
    Mres = {}
    for l in Met.link.unique():
        D = {}
        for p in products:
            D.update({p: G.loc[(l, p)][metric]})
            Mres.update({l: D})
    Mres = pd.DataFrame.from_dict(Mres).T
    Mres.dropna(inplace=True)
    if min_max =='max':
        if absolute:
            _t1 = Mres.apply(lambda x: x[np.argmax(np.abs(x))], axis = 1)
            _t2 = Mres.abs().idxmax(axis=1)
            Mres['max_'+metric] = _t1
            Mres['best'] = _t2
        else:
            Mres['best'] = Mres.idxmax(axis=1)
            Mres['max_'+metric] = Mres.max(axis = 1)
    else:
        if absolute:
            _t1 = Mres.apply(lambda x: x[np.argmin(np.abs(x))], axis = 1)
            _t2 = Mres.abs().idxmin(axis=1)
            Mres['min_'+metric] = _t1
            Mres['best'] = _t2
        else:
            Mres['best'] = Mres.idxmin(axis=1)
            Mres['min_'+metric] = Mres.min(axis = 1)
    return Mres

def get_intersec_events(Emet, prod1, prod2, metric, qpeak_cond = 0.2):
    '''Get the intersection of two products using the event metric table'''
    a = Emet.loc[Emet['product'] == prod1, [metric, 'qpeak','qmax_anual','link']]
    b = Emet.loc[Emet['product'] == prod2, [metric, 'qpeak','qmax_anual','link']]
    a.dropna(inplace=True)
    b.dropna(inplace=True)

    if qpeak_cond is not None:
        a['qsca'] = a['qpeak'] / a['qmax_anual']
        b['qsca'] = b['qpeak'] / b['qmax_anual']
        a.drop(a.loc[a['qsca'] < qpeak_cond].index, inplace = True)
        b.drop(b.loc[b['qsca'] < qpeak_cond].index, inplace = True)

    idx = a.index.intersection(b.index)
    a = a.loc[idx]
    b = b.loc[idx]
    return a,b