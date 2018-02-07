import numpy as np

from lagom.envs.spaces.base import Space


class Box(Space):
    """
    A continuous space in R^n. Each dimension is bounded by low/high.
    """
    def __init__(self, low, high, shape=None):
        """
        Define the bound for the space. 
        
        Two cases:
            Identical bound for each dimension: 
                Box(low=-1.0, high=1.0, shape=(2, 3))
            Separate bound for each dimension: 
                Box(low=np.array([-1.0, -2.0]), high=np.array([3.0, 4.0]))
        """
        if shape is None:
            assert low.shape == high.shape
            
            shape = low.shape
            
            self.low = low
            self.high = high
        else:
            assert np.isscalar(low) and np.isscalar(high)
            
            self.low = np.full(shape, low)
            self.high = np.full(shape, high)
            
        super().__init__(shape)
        
    def sample(self):
        return np.random.uniform(low=self.low, high=self.high, size=self.shape)
    
    def contains(self, x):
        return x.shape == self.shape and np.all(x >= self.low) and np.all(x <= self.high)
    
    @property
    def flat_dim(self):
        return int(np.prod(self.shape))  # avoid np.int64
    
    def flatten(self, x):
        return np.asarray(x).flatten()
    
    def unflatten(self, x):
        return np.asarray(x).reshape(self.shape)
    
    def __repr__(self):
        return f'Box{self.shape}'
    
    def __eq__(self, x):
        return isinstance(x, Box) and np.allclose(x.low, self.low) and np.allclose(x.high, self.high)