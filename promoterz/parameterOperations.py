

#!/bin/python
def flattenParameters(Parameters):
    result = {}

    def iter(D, path= []):
        for q in D.keys():
            if type(D[q]) == dict:
                iter(D[q], path + [q])
            else:
                path_keyname = ".".join(path + [q])
                result.update({path_keyname: D[q]})

    iter(Parameters)
    return result


def expandNestedParameters(Parameters):
    _Parameters = {}
    for K in Parameters.keys():
        if '.' in K:
            Q = K.split('.')
            cursor = 0
            base = _Parameters
            while cursor < len(Q) - 1:
                if not Q[cursor] in base.keys():
                    base[Q[cursor]] = {}
                base = base[Q[cursor]]
                cursor += 1
            base[Q[cursor]] = Parameters[K]
        else:
            _Parameters[K] = Parameters[K]
    return _Parameters


def parameterValuesToRangeOfValues(TargetParameters, Spread):
    for parameter in TargetParameters.keys():
        P = TargetParameters[parameter]
        if type(P) not in [tuple, list]:
            spread_change = Spread * P / 200
            if P < 0:
                spread_change = -spread_change
            TargetParameters[parameter] = (P - spread_change, P + spread_change)
    return TargetParameters
