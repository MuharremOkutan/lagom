import numpy as np

from lagom.envs.spaces.base import Space


class Product(Space):
    """
    A product (tuple) of elementary spaces.
    """
    def __init__(self, spaces):
        """
        Define a product of elementary spaces.
        
        Example:
            Product((Discrete(5), Box(-1.0, 1.0, dtype=np.float32, shape=(2, 3))))
        """
        self.spaces = tuple(spaces)
        
        super().__init__(None, None)
        
    def sample(self):
        return tuple([space.sample() for space in self.spaces])
    
    def contains(self, x):
        x = tuple(x)  # ensure tuple type
        
        print(x)
        
        return np.all([space.contains(x_part) for x_part, space in zip(x, self.spaces)])
    
    @property
    def flat_dim(self):
        return int(np.sum([space.flat_dim for space in self.spaces]))  # PyTorch Tensor dimension only accepts raw int type
    
    def flatten(self, x):
        return np.concatenate([space.flatten(x_part)  for x_part, space in zip(x, self.spaces)])
        
    def unflatten(self, x):
        dims = [space.flat_dim for space in self.spaces]
        # Split big vector into list of vectors for each space
        list_flattened = np.split(x, np.cumsum(dims)[:-1])
        # Unflatten for each space
        list_unflattened = [space.unflatten(flattened) for flattened, space in zip(list_flattened, self.spaces)]
        
        return tuple(list_unflattened)
        
    def __repr__(self):
        return f'Product({", ".join([str(space) for space in self.spaces])})'
    
    def __eq__(self, x):
        return isinstance(x, Product) and tuple(x.spaces) == tuple(self.spaces)