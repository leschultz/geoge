import numpy as np

def autocovariance(x, n, mean, k, bias=0):
    '''
    Compute the autocovariance of a set.

    inputs:
            x = the list of data
            n = the size of data
            mean = the mean of the x-data
            k = the k-lag between values
            bias = adjust the bias calculation

    outputs:
            autocov = the autocovariance at a k-lag
    '''

    autocov = 0.0
    for i in np.arange(0, n-k):
        autocov += (x[i+k]-mean)*(x[i]-mean)

    autocov /= n-bias

    return autocov


def autocorrelation(x):
    '''
    Compute the autocorrelation for all possible k-lags.

    inputs:
            x = the data
    outputs:
            r = the autocorrelation at a k-lag
    '''

    n = len(x)  # Number of values
    mean = np.mean(x)  # Mean values
    denominator = autocovariance(x, n, mean, 0)  # Normalization factor
    k = np.arange(0, n+1)  # k-lag

    r = list(map(lambda lag: autocovariance(x, n, mean, lag)/denominator, k))

    return r


def batch_means(x, k):
    '''
    Divide data into bins to calculate error from batch means.

    inputs:
        x = data
        k = the correlation length
    outputs:
        e = the error
    '''

    bins = len(x)//k  # Approximate the number of bins with lenght k
    splits = np.array_split(x, bins)  # Split into bins
    means = list(map(np.mean, splits))  # Average each of the bins
    e = (np.var(means, ddof=1)/bins)**0.5  # Error

    return e
