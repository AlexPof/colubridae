################################################
###### Copyright (c) 2019, Alexandre Popoff 
### 

class SetObject(object):
    def __init__(self,elems,name=None):
        self.elems = set(elems)
        self.name = name
        
    def __mul__(self,setobj2):
        return SetObject([(x,y) for x in self.elems for y in setobj2.elems])

    def __eq__(self,set2):
        if not isinstance(set2,SetObject):
            raise Exception("RHS is not a valid SetObject class\n")
        return self.elems==set2.elems
     
    def __hash__(self):
        return sum([hash(x) for x in self.elems])
    
    def __repr__(self):
        if self.name is None:
            return str(self.elems)
        else:
            return self.name
        
class Function(object):
    def __init__(self,source,target,mapping):
        if not isinstance(source,SetObject):
            raise Exception("Source is not a valid SetObject class\n")
        if not isinstance(target,SetObject):
            raise Exception("Source is not a valid SetObject class\n")
        self.source = source
        self.target = target

        if not self.source.elems == set(mapping.keys()):
            raise Exception("Not a valid function mapping\n")
        if not set(mapping.values()).issubset(self.target.elems):
            raise Exception("Not a valid function mapping\n")
        self.mapping = {k:v for k,v in mapping.items()}
        
    def __eq__(self,rhs):
        if rhs is None:
            return False
        if not isinstance(rhs,Function):
            raise Exception("RHS is not a valid Function class\n")
        return (self.mapping==rhs.mapping) and \
               (self.source == rhs.source) and \
               (self.target == rhs.target)

    def __mul__(self,rhs):
        if not isinstance(rhs,Function):
            raise Exception("RHS is not a valid Function class\n")
        if not self.source==rhs.target:
            return None
        new_map = {x:self(y) for x,y in rhs.mapping.items()}
        return Function(rhs.source,self.target,new_map)
    
    def __call__(self,x):
        return self.mapping.get(x)
    
    def __hash__(self):
        hash_val = hash(self.source)
        hash_val += hash(self.target)
        hash_val += sum([hash(x) for x in self.mapping.items()])
        return hash_val
    
    @staticmethod
    def get_identity_morphism(X):
        if not isinstance(X,SetObject):
            raise Exception("Not a valid SetObject class\n")
        return Function(X,X,{x:x for x in X.elems})

    
class PartialFunction(object):
    def __init__(self,source,target,mapping):
        if not isinstance(source,SetObject):
            raise Exception("Source is not a valid SetObject class\n")
        if not isinstance(target,SetObject):
            raise Exception("Source is not a valid SetObject class\n")
        self.source = source
        self.target = target
        self.mapping = {k:v for k,v in mapping.items() if v is not None}
        
    def __eq__(self,rhs):
        if rhs is None:
            return False
        if not isinstance(rhs,PartialFunction):
            raise Exception("RHS is not a valid PartialFunction class\n")
        return (self.mapping==rhs.mapping) and \
               (self.source == rhs.source) and \
               (self.target == rhs.target)

    def __mul__(self,rhs):
        if not isinstance(rhs,Function):
            raise Exception("RHS is not a valid PartialFunction class\n")
        if not self.source==rhs.target:
            return None
        new_map = {x:self(y) for x,y in rhs.mapping.items()}
        return PartialFunction(rhs.source,self.target,new_map)
    
    def __call__(self,x):
        return self.mapping.get(x)
    
    def __hash__(self):
        hash_val = hash(self.source)
        hash_val += hash(self.target)
        hash_val += sum([hash(x) for x in self.mapping.items()])
        return hash_val
    
    @staticmethod
    def get_identity_morphism(X):
        if not isinstance(X,SetObject):
            raise Exception("Not a valid SetObject class\n")
        return PartialFunction(X,X,{x:x for x in X.elems})
    
class Relation(object):
    def __init__(self,source,target,mapping):
        if not isinstance(source,SetObject):
            raise Exception("Source is not a valid SetObject class\n")
        if not isinstance(target,SetObject):
            raise Exception("Source is not a valid SetObject class\n")
        self.source = source
        self.target = target
        self.mapping = {k:v for k,v in mapping.items() if (v is not None and type(v)==set)}
        
    def __eq__(self,rhs):
        if rhs is None:
            return False
        if not isinstance(rhs,Relation):
            raise Exception("RHS is not a valid Relation class\n")
        return (self.mapping==rhs.mapping) and \
               (self.source == rhs.source) and \
               (self.target == rhs.target)

    def __mul__(self,rhs):
        if not isinstance(rhs,Relation):
            raise Exception("RHS is not a valid Relation class\n")
        if not self.source==rhs.target:
            return None
        new_map={}
        for x,y in rhs.mapping.items():
            ## Rel is the Kleisli category for the powerset monad
            image = [self(z) for z in y]
            image = [v for u in image if u is not None for v in u ]
            new_map[x] = set(image)
        return Relation(rhs.source,self.target,new_map)
    
    def __call__(self,x):
        return self.mapping.get(x)
    
    def __hash__(self):
        hash_val = hash(self.source)
        hash_val += hash(self.target)
        hash_val += sum([hash((x,*y)) for x,y in self.mapping.items()])
        return hash_val
    
    @staticmethod
    def get_identity_morphism(X):
        if not isinstance(X,SetObject):
            raise Exception("Not a valid SetObject class\n")
        return Relation(X,X,{x:{x} for x in X.elems})
