import numpy as np

import pytest

from lagom.core.transform import Clip
from lagom.core.transform import Centralize
from lagom.core.transform import Normalize 
from lagom.core.transform import Standardize
from lagom.core.transform import ExpFactorCumSum
from lagom.core.transform import RunningMeanStd
from lagom.core.transform import RankTransform
from lagom.core.transform import PolySmooth


class TestTransform(object):
    def test_clip(self):
        clip = Clip()
        
        # Test scalar
        assert clip(x=2, a_min=0, a_max=1) == 1
        assert clip(x=0.5, a_min=0, a_max=1) == 0.5
        assert clip(x=-1, a_min=0, a_max=1) == 0
        
        # Test numpy scalar
        assert clip(x=np.array(2), a_min=0, a_max=1) == 1
        assert clip(x=np.array(0.5), a_min=0, a_max=1) == 0.5
        assert clip(x=np.array(-1), a_min=0, a_max=1) == 0
        
        #
        # Test vector
        #
        def _test_vec(x):
            assert np.alltrue(clip(x=x, a_min=2, a_max=3) == [2, 2, 3, 3])
        
        # Tuple
        a = (1, 2, 3, 4)
        _test_vec(a)
        
        # List
        b = [1, 2, 3, 4]
        _test_vec(b)
        
        # ndarray
        c = np.array([1, 2, 3, 4])
        _test_vec(c)
        
        #
        # Test exceptions
        #
        # ndarray more than 1-dim is not allowed
        d = np.array([[1, 2, 3, 4]])
        with pytest.raises(ValueError):
            clip(x=d, a_min=2, a_max=3)
        
    def test_centralize(self):
        centralize = Centralize()
        
        # Test scalar
        assert centralize(x=1) == 1
        assert centralize(x=0) == 0
        assert centralize(x=2) == 2
        
        assert centralize(x=1, mean=1) == 1
        assert centralize(x=0, mean=1) == 0
        assert centralize(x=2, mean=1) == 2
        
        # Test numpy scalar
        assert centralize(x=np.array(1)) == 1
        assert centralize(x=np.array(0)) == 0
        assert centralize(x=np.array(2)) == 2
        
        assert centralize(x=np.array(1), mean=1) == 1
        assert centralize(x=np.array(0), mean=1) == 0
        assert centralize(x=np.array(2), mean=1) == 2
        
        #
        # Test vector
        #
        def _test_vec(x):
            assert np.alltrue(centralize(x=x) == [-1.5, -0.5, 0.5, 1.5])
            assert np.alltrue(centralize(x=x, mean=1) == [0, 1, 2, 3])
        
        # Tuple
        a = (1, 2, 3, 4)
        _test_vec(a)
        
        # List
        b = [1, 2, 3, 4]
        _test_vec(b)
        
        # ndarray
        c = np.array([1, 2, 3, 4])
        _test_vec(c)
        
        #
        # Test exceptions
        #
        # ndarray more than 1-dim is not allowed
        d = np.array([[1, 2, 3, 4]])
        with pytest.raises(ValueError):
            centralize(x=d)
        
    def test_normalize(self):
        normalize = Normalize(eps=1.1920929e-07)
        
        # Test scalar
        assert normalize(x=-1) == 0
        assert normalize(x=0.5) == 0.5
        assert normalize(x=2) == 1
        
        assert normalize(x=-1, min_val=0, max_val=1) == 0
        assert normalize(x=0.5, min_val=0, max_val=1) == 0.5
        assert normalize(x=2, min_val=0, max_val=1) == 1
        
        # Test numpy scalar
        assert normalize(x=np.array(-1)) == 0
        assert normalize(x=np.array(0.5)) == 0.5
        assert normalize(x=np.array(2)) == 1
        
        assert normalize(x=np.array(-1), min_val=0, max_val=1) == 0
        assert normalize(x=np.array(0.5), min_val=0, max_val=1) == 0.5
        assert normalize(x=np.array(2), min_val=0, max_val=1) == 1
        
        #
        # Test vector
        #
        def _test_vec(x):
            assert np.allclose(normalize(x=x), 
                               [0., 0.33333332, 0.66666664, 0.99999996])
        
            assert np.allclose(normalize(x=x, min_val=0, max_val=1), 
                               [0.99999988, 1.99999976, 2.99999964, 3.99999952])
        # Tuple
        a = (1, 2, 3, 4)
        _test_vec(a)
        
        # List
        b = [1, 2, 3, 4]
        _test_vec(b)
        
        # ndarray
        c = np.array([1, 2, 3, 4])
        _test_vec(c)
        
        #
        # Test exceptions
        #
        # ndarray more than 1-dim is not allowed
        d = np.array([[1, 2, 3, 4]])
        with pytest.raises(ValueError):
            normalize(x=d)
        
    def test_standardize(self):
        standardize = Standardize(eps=1.1920929e-07)
        
        # Test scalar
        assert standardize(x=-1) == -1
        assert standardize(x=0) == 0
        assert standardize(x=1) == 1
        
        assert standardize(x=-1, mean=0, std=1) == -1
        assert standardize(x=0, mean=0, std=1) == 0
        assert standardize(x=1, mean=0, std=1) == 1
        
        # Test numpy scalar
        assert standardize(x=np.array(-1)) == -1
        assert standardize(x=np.array(0)) == 0
        assert standardize(x=np.array(1)) == 1
        
        assert standardize(x=np.array(-1), mean=0, std=1) == -1
        assert standardize(x=np.array(0), mean=0, std=1) == 0
        assert standardize(x=np.array(1), mean=0, std=1) == 1
        
        #
        # Test vector
        #
        def _test_vec(x):
            assert np.allclose(standardize(x=x), 
                               [-1.34164064, -0.44721355, 0.44721355, 1.34164064])
        
            assert np.allclose(standardize(x=x, mean=0, std=1), 
                               [0.99999988, 1.99999976, 2.99999964, 3.99999952])
        
        # Tuple
        a = (1, 2, 3, 4)
        _test_vec(a)
        
        # List
        b = [1, 2, 3, 4]
        _test_vec(b)
        
        # ndarray
        c = np.array([1, 2, 3, 4])
        _test_vec(c)
        
        #
        # Test exceptions
        #
        # ndarray more than 1-dim is not allowed
        d = np.array([[1, 2, 3, 4]])
        with pytest.raises(ValueError):
            standardize(x=d)
        
    def test_expfactorcumsum(self):
        expfactorcumsum = ExpFactorCumSum(alpha=0.1)
        
        #
        # Test vector
        #
        def _test_vec(x):
            assert np.allclose(expfactorcumsum(x=x, mask=None), 
                               [1.23, 2.3, 3.0])
        
        # Tuple
        a = (1, 2, 3)
        _test_vec(a)
            
        # List
        b = [1, 2, 3]
        _test_vec(b)
        
        # ndarray
        c = np.array([1, 2, 3])
        _test_vec(c)
        
        # 
        # Test with mask
        # 
        def _test_vec_mask(x, mask):
            assert np.allclose(expfactorcumsum(x=x, mask=mask), 
                               [1.23, 2.3, 3.0, 4.56, 5.6, 6.0])
        dones = [False, False, True, False, False, False]
        mask = np.logical_not(dones).astype(int).tolist()
        
        # Tuple
        d = (1, 2, 3, 4, 5, 6)
        _test_vec_mask(d, mask)
        
        # List
        e = [1, 2, 3, 4, 5, 6]
        _test_vec_mask(e, mask)
        
        # ndarray
        f = np.array([1, 2, 3, 4, 5, 6])
        _test_vec_mask(f, mask)
        
        #
        # Test exceptions
        #
        # Scalar is not allowed
        with pytest.raises(AssertionError):
            expfactorcumsum(x=1)
        
        # ndarray more than 1-dim is not allowed
        g = np.array([[1, 2, 3]])
        with pytest.raises(ValueError):
            expfactorcumsum(g)
            
        # mask must be list dtype
        h = [1, 2, 3]
        dones_h = np.array([True, False, True])
        mask_h = np.logical_not(dones_h).astype(int)
        with pytest.raises(AssertionError):
            expfactorcumsum(h, mask_h)
        
        # mask must have same length with input data
        i = [1, 2, 3]
        dones_i = [True, False, True, True]
        mask_i = np.logical_not(dones_i).astype(int).tolist()
        with pytest.raises(AssertionError):
            expfactorcumsum(i, mask_i)
            
        # mask must be binary
        j = [1, 2, 3]
        mask_j = [0, 0.5, 1]
        with pytest.raises(AssertionError):
            expfactorcumsum(j, mask_j)
            
        # boolean mask is not allowed, because it is easy to get bug
        k = [1, 2, 3]
        mask_k = [True, False, False]
        with pytest.raises(AssertionError):
            expfactorcumsum(k, mask_k)

    def test_runningmeanstd(self):
        def _test_moments(runningmeanstd, x):
            assert np.allclose(runningmeanstd.mu, np.mean(x))
            assert np.allclose(runningmeanstd.sigma, np.std(x))

        a = [1, 2, 3, 4]

        # Scalar
        runningmeanstd = RunningMeanStd()
        [runningmeanstd(i) for i in a]
        _test_moments(runningmeanstd=runningmeanstd, x=a)

        # Vector
        runningmeanstd = RunningMeanStd()
        runningmeanstd(a)
        _test_moments(runningmeanstd=runningmeanstd, x=a)

        # n-dim array
        b = np.array([[1, 10, 100], [2, 20, 200], [3, 30, 300], [4, 40, 400]])
        runningmeanstd = RunningMeanStd()
        runningmeanstd(b)
        assert np.allclose(runningmeanstd.mu, b.mean(0))
        assert np.allclose(runningmeanstd.sigma, b.std(0))
        
    def test_rank_transform(self):
        rank_transform = RankTransform()
        
        # List
        a = [3, 14, 1]
        assert np.allclose(rank_transform(a, centered=False), [1, 2, 0])
        assert np.allclose(rank_transform(a), [0, 0.5, -0.5])
        
        # ndarray
        b = np.array([3, 14, 1])
        assert np.allclose(rank_transform(b, centered=False), [1, 2, 0])
        assert np.allclose(rank_transform(b), [0, 0.5, -0.5])
        
        #
        # Test exceptions
        #
        # Scalar is not allowed
        with pytest.raises(AssertionError):
            rank_transform(5)
            
        # ndarray more than 1-dim is not allowed
        c = np.array([[3, 14, 1]])
        with pytest.raises(ValueError):
            rank_transform(c)
            
    def test_polysmooth(self):
        smooth = PolySmooth()

        #
        # Test vector
        #
        def _test_vec(x):
            smoothed_x = smooth(x, 2)
            assert np.allclose(smoothed_x, [0.96, 0.58, 0.1, -0.48, -1.16])

        # Tuple
        a = (0.8, 0.9, 0.1, -0.8, -1.0)
        _test_vec(a)

        # List
        b = [0.8, 0.9, 0.1, -0.8, -1.0]
        _test_vec(b)

        # ndarray
        c = np.array([0.8, 0.9, 0.1, -0.8, -1.0])
        _test_vec(c)

        #
        # Test exceptions
        #
        # ndarray more than 1-dim is not allowed
        d = np.array([[0.8, 0.9, 0.1, -0.8, -1.0]])
        with pytest.raises(ValueError):
            smooth(d, 2)
