import numpy as np

from lagom.core.processor import BaseProcessor


class Normalize(BaseProcessor):
    def __init__(self, eps=np.finfo(np.float32).eps):
        self.eps = eps
    
    def process(self, x):
        """
        Normalize the input data: Subtracted by minimal and divided by range (maximal - minimal)
        
        Args:
            x (numpy array): input data.
            
        Returns:
            out (numpy array): normalized data
        """
        
        x = self._make_input(x)
        
        # Calculate the min and max values for input vector
        min_val = x.min()
        max_val = x.max()
        
        out = (x - min_val)/(max_val - min_val + self.eps)
        
        return out
    
    def _make_input(self, x):
        # make sure DType as numpy array
        if type(x) is not np.ndarray:
            x = np.array(x)
         
        # TODO: Currently only deal with single vector, maybe vectorization in Agent code ?
        # Add batch dimension if single vector
        #if len(x.shape) == 1:
        #    x = x.reshape([1, -1])
            
        return x