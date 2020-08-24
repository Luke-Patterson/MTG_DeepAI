
import time
from pathos.pools import ProcessPool

def basic_func(x):
    if x == 0:
        return 'zero'
    elif x%2 == 0:
        return 'even'
    else:
        return 'odd'

def multiprocessing_func(x):
    y = x*x
    time.sleep(2)
    print('{} squared results in a/an {} number'.format(x, basic_func(y)))
    return(y)

if __name__ == '__main__':
    starttime = time.time()
    processes = []
    pool = ProcessPool(nodes=4)
    results=pool.map(multiprocessing_func,[i for i in range(10)])
    print(results)
