'''
Created on Aug 10, 2011

@author: BogdanC
'''
class Anon:    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
