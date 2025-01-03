import numpy as np
import pytest
from mandelbrot import MandelbrotGenerator
import time


# locally it takes 30 seconds
@pytest.mark.timeout(100)
def test_mandelbrot_parallel():
    # Test with different numbers of workers
    width, height, max_iter = 399, 399, 1250
    generators = [MandelbrotGenerator(num_workers=i) for i in range(4, 0, -1)]
    
    results = []
    times = []
    for gen in generators:
        start_time = time.time()
        result = gen.generate(width, height, max_iter)
        assert len(result) == height, f"Incorrect height for {gen.num_workers} workers"
        assert len(result[0]) == width, f"Incorrect width for {gen.num_workers} workers"
        end_time = time.time()
        results.append(result)
        times.append(end_time - start_time)
    
    # Check that all results are the same
    for i in range(0, len(results) - 1):
        assert np.array_equal(results[-1], results[i]), f"Results differ for {i} workers {np.array(results[0]) - np.array(results[i])}"
    
    # Check that using more workers is generally faster
    assert min(times[:-1]) < times[-1], f"Parallel is not faster than single process, times: {times}"
