################################################
###### Copyright (c) 2019, Alexandre Popoff 
### 

class Category(object):
    def __init__(self,objects,generators):
        if len(set([x.__class__ for x in objects]))>1:
            raise Exception("Objects must be of the same class")
        if len(set([x.__class__ for x in generators]))>1:
            raise Exception("Generators must be of the same class")
        
        self.objects = set(objects)
        self.object_type = objects[0].__class__
        self.morphism_type = generators[0].__class__
        
        for f in generators:
            if not f.source in self.objects:
                raise Exception("Generator source not in objects")
            if not f.target in self.objects:
                raise Exception("Generator target not in objects")

        self.generators = generators
        for x in self.objects:
            self.generators.append(self.morphism_type.get_identity_morphism(x))
        
        self.generators = set(self.generators)
        self.morphisms = []
        self.generate_category()
    
    def _itergenerate(self,new_maps):
        x=[g*x for g in self.generators for x in new_maps if ((not g*x is None) and (not g*x in self.morphisms))]
        if len(x):
            self.morphisms += x
            self._itergenerate(x)
        else:
            return None
        
    def __eq__(self,rhs):
        return (self.objects == rhs.objects) and (self.morphisms == rhs.morphisms)
    
    def __hash__(self):
        hash_val = sum([hash(x) for x in self.objects])
        hash_val += sum([hash(x) for x in self.morphisms])
        return hash_val
    
    def generate_category(self):
        new_maps = list(self.generators)
        
        self._itergenerate(new_maps)
        self.morphisms = set(self.morphisms)
        
    
class Functor(object):
    def __init__(self,source,target,obj_mapping,morph_mapping,from_generators=False):
        if not isinstance(source,Category):
            raise Exception("Source is not a valid Category class\n")
        if not isinstance(target,Category):
            raise Exception("Target is not a valid Category class\n")
        self.source = source
        self.target = target

        self.obj_mapping = {k:v for k,v in obj_mapping.items() if v is not None}
        self.morph_mapping = {k:v for k,v in morph_mapping.items() if v is not None}
        if not from_generators:
            self._check_validity()
        else:
            for k,v in self.obj_mapping.items():
                self.morph_mapping[self.source.morphism_type.get_identity_morphism(k)] = self.target.morphism_type.get_identity_morphism(v)
            if not set(self.morph_mapping.keys())==self.source.generators:
                raise Exception("Functor should define image of all generators")
            self.generator_mapping = {k:v for k,v in morph_mapping.items() if v is not None}
            self._generate()
            self._check_validity()
            
    def _generate(self):
        while not set(self.morph_mapping.keys())==set(self.source.morphisms):
            temp_list = [(k,v) for k,v in self.morph_mapping.items()]
            for f,im_f in temp_list:
                for g,im_g in self.generator_mapping.items():
                    k,v = g*f,im_g*im_f
                    if k is not None:
                        if k in self.morph_mapping:
                            if not self.morph_mapping[k]==v:
                                raise Exception("Not a valid Functor")
                        else:
                            self.morph_mapping[k]=v
        
    def _check_validity(self):
        for f in self.source.morphisms:
            if not self(f).source==self(f.source):
                raise Exception("Not a valid Functor")
            if not self(f).target==self(f.target):
                raise Exception("Not a valid Functor")
        for x in self.source.objects:
            if not self(self.source.morphism_type.get_identity_morphism(x))==self.target.morphism_type.get_identity_morphism(self(x)):
                raise Exception("Not a valid Functor")
        for f in self.source.morphisms:
            for g in self.source.generators:
                if not (g*f) is None:
                    if not self(g*f)==(self(g)*self(f)):
                        raise Exception("Not a valid Functor")
        
    def __eq__(self,rhs):
        if not isinstance(rhs,Functor):
            raise Exception("RHS is not a valid Functor class\n")
        return (self.source == rhs.source) \
               and (self.target == rhs.target) \
               and (self.obj_mapping==rhs.obj_mapping) \
               and (self.morph_mapping==rhs.morph_mapping)

    def __mul__(self,rhs):
        if not isinstance(rhs,Functor):
            raise Exception("RHS is not a valid Functor class\n")
        if not self.source==rhs.target:
            return None
        new_map_obj = {x:self(y) for x,y in rhs.obj_mapping.items()}
        new_map_morph = {x:self(y) for x,y in rhs.morph_mapping.items()}
        return Functor(rhs.source,self.target,new_map_obj,new_map_morph)
    
    def __call__(self,x):
        if isinstance(x,self.source.object_type):
            return self.obj_mapping.get(x)
        if isinstance(x,self.source.morphism_type):
            return self.morph_mapping.get(x)
        return None
    
    def __hash__(self):
        hash_val = hash(self.source)
        hash_val += hash(self.target)
        hash_val += sum([hash(x) for x in self.obj_mapping.items()])
        hash_val += sum([hash(x) for x in self.morph_mapping.items()])
        return hash_val

    @staticmethod
    def get_identity_morphism(X):
        if not isinstance(X,Category):
            raise Exception("Not a valid Category class\n")
        return Functor(X,X,{x:x for x in X.objects},{x:x for x in X.morphisms})
        
    
class NaturalTransformation(object):
    def __init__(self,source,target,mapping):
        if not isinstance(source,Functor):
            raise Exception("Source is not a valid Functor class\n")
        if not isinstance(target,Functor):
            raise Exception("Target is not a valid Functor class\n")
        if not source.source == target.source:
            raise Exception("Not a valid natural transformation")
        if not source.target == target.target:
            raise Exception("Not a valid natural transformation")
        self.source = source
        self.target = target
        self.mapping = {k:v for k,v in mapping.items() if v is not None}
        self._check_validity()
        
    def _check_validity(self):
        if not set(self.mapping.keys())==self.source.source.objects:
            raise Exception("Not a valid natural transformation")
        for x,fx in self.mapping.items():
            if not fx.source==(self.source)(x):
                raise Exception("Not a valid natural transformation")
            if not fx.target==(self.target)(x):
                raise Exception("Not a valid natural transformation")
        for f in (self.source).source.morphisms:
            X,Y = f.source,f.target
            if not self.mapping[Y]*(self.source)(f)==(self.target)(f)*self.mapping[X]:
                raise Exception("Not a valid natural transformation")
        
    def __eq__(self,rhs):
        if not isinstance(rhs,NaturalTransformation):
            raise Exception("RHS is not a valid NaturalTransformation class\n")
        return (self.source == rhs.source) \
               and (self.target == rhs.target) \
               and (self.mapping==rhs.mapping)

    def __mul__(self,rhs):
        if not isinstance(rhs,NaturalTransformation):
            raise Exception("RHS is not a valid NaturalTransformation class\n")
        if not self.source==rhs.target:
            return None
        new_map = {x:self.mapping[x]*y for x,y in rhs.mapping.items()}
        return NaturalTransformation(rhs.source,self.target,new_map)

    def __xor__(self,rhs):
        if not isinstance(rhs,NaturalTransformation):
            raise Exception("RHS is not a valid NaturalTransformation class\n")
        if not self.source.source==rhs.source.target:
            return None
        if not self.target.source==rhs.target.target:
            return None
        new_map = {x:self.mapping[rhs.target(x)]*self.target(y) for x,y in rhs.mapping.items()}
        return NaturalTransformation(self.source*rhs.source,self.target*rhs.target,new_map)
    
    def __hash__(self):
        hash_val = hash(self.source)
        hash_val += hash(self.target)
        hash_val += sum([hash(x) for x in self.mapping.items()])
        return hash_val
    
    @staticmethod
    def get_identity_morphism(F):
        if not isinstance(F,Functor):
            raise Exception("Not a valid Functor class\n")
        return NaturalTransformation(F,F,{x:F.target.morphism_type.get_identity_morphism(F(x)) for x in F.source.objects})
