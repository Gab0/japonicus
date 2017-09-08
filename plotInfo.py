#!/bin/python
import numpy as np
import matplotlib
matplotlib.use("AGG")
matplotlib.rcsetup.validate_backend("AGG")
import matplotlib.pyplot as plt

def plotEvolutionSummary(DATA, filename):
    DataSequence = list(DATA.keys())
    DataSequence.sort()
    print(DataSequence)
    fig, Information = plt.subplots(figsize=(32, 2), dpi=300)
    Information.xlim=(0, DataSequence[-1])
    Information.ylim=(-20,20)
    print('okkkkk')
    for w in DataSequence:
        print(w)
        _X=w
        _Yb=round(DATA[w]['best'],4)
        _Ym=round(DATA[w]['med'],4)
        Information.plot([_X], [_Yb], 'go')
        Information.plot([_X], [_Ym], 'ro')
        
    plt.savefig('%s.png' % filename, format='png')

D={0: {'best': 3.3463756384586816, 'med': 1.2633447709674437}, 1: {'best': 3.3463756384586816, 'med': 1.4928755672735656}, 2: {'best': 3.3463756384586816, 'med': 1.6094502571427676}, 3: {'best': 3.3463756384586816, 'med': 1.8532354131847841}, 4: {'best': 3.3463756384586816, 'med': 2.093424423404808}, 5: {'best': 3.3463756384586816, 'med': 2.289154292685223}, 6: {'best': 3.3463756384586816, 'med': 2.5490086717823504}, 7: {'best': 3.3463756384586816, 'med': 2.678739866249536}, 8: {'best': 3.3463756384586816, 'med': 2.724835797195404}, 9: {'best': 3.3463756384586816, 'med': 2.7640750965983734}, 10: {'best': 3.665294249446575, 'med': 2.840910631678982}, 11: {'best': 3.665294249446575, 'med': 2.8605302813804667}, 12: {'best': 3.665294249446575, 'med': 2.862342558135727}, 13: {'best': 3.665294249446575, 'med': 2.8999387938133663}, 14: {'best': 3.665294249446575, 'med': 2.92477828505149}, 15: {'best': 3.665294249446575, 'med': 2.9872140119672523}, 16: {'best': 3.665294249446575, 'med': 2.9872140119672523}, 17: {'best': 3.665294249446575, 'med': 3.0496497388830153}, 18: {'best': 3.665294249446575, 'med': 3.0872459745606546}, 19: {'best': 3.665294249446575, 'med': 3.149681701476417}}

if __name__ == '__main__':
    plotEvolutionSummary(D, 'test')
