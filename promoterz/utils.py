#!/bin/python
def flattenParameters(Parameters):
    result = {}
    def iter(D, path=[]):
        for q in D.keys():
            if type(D[q]) == dict:
                iter(D[q], path+[q])
            else:
                path_keyname= ".".join(path+[q])
                result.update({path_keyname: D[q]})

    iter(Parameters)
    return result
