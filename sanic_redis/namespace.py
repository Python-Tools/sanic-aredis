class Namespace:
    def __call__(self,val:str)->str:
        return self.namespace+":"+val
    def __init__(self,namespace:str="default"):
        self.namespace = namespace
