import numpy as np
import pytest
from mandelbrot import MandelbrotGenerator, visualize
from PIL import Image
import os

@pytest.fixture
def generator(num_workers: int = 3) -> MandelbrotGenerator:
    return MandelbrotGenerator(num_workers=num_workers)

def test_mandelbrot_tiny_image(generator: MandelbrotGenerator):
    # Test with a tiny 3x3 image
    width, height, max_iter = 3, 3, 50
    expected_output = np.array([
        [1, 3, 9],
        [1, 6, 0],
        [1, 6, 0]
    ])
    result_original = generator.generate(width, height, max_iter)
    result = np.array(result_original)
    assert np.array_equal(result, expected_output), f"Tiny image test failed"

def test_mandelbrot_single_pixel(generator: MandelbrotGenerator):
    # Test with a single pixel
    width, height, max_iter = 1, 1, 50
    expected_output = np.array([[1]])
    result_original = generator.generate(width, height, max_iter)
    result = np.array(result_original)
    assert np.array_equal(result, expected_output), f"Single pixel test failed: {result_original}"

# locally it takes 30 seconds
@pytest.mark.timeout(200)
@pytest.mark.limit_memory("1 GB")
@pytest.mark.parametrize("size,max_iter", [
    ((100, 100), 10),
    ((2000, 2000), 50),
    ((5000, 5000), 100)
])
def test_mandelbrot_target_images(generator: MandelbrotGenerator, size, max_iter):
    width, height = size
    result = generator.generate(width, height, max_iter)
    
    # Generate the image
    temp_file = f"temp_{width}x{height}_{max_iter}.png"
    visualize(result, save_path=temp_file)
    
    # Load the generated image and the target image
    generated_img = Image.open(temp_file)
    target_img = Image.open(f"target_images/{width}x{height}_{max_iter}_mandelbrot.png")
    
    # Compare the images
    diff = np.array(generated_img) - np.array(target_img)
    mse = np.mean(diff ** 2)
    
    # Clean up the temporary file
    os.remove(temp_file)
    
    # Assert that the mean squared error is below a threshold
    assert mse < 0.01, f"Generated image differs significantly from target for size {size} and max_iter {max_iter}, MSE: {mse}"

def test_mandelbrot_edge_cases(generator: MandelbrotGenerator):
    # Test with very small max_iter
    result = generator.generate(10, 10, 1)
    assert np.all(np.array(result) == 0), "All pixels should be 0 for max_iter=1"
    
    # Test with some strange image size
    result = generator.generate(51, 51, 10)
    assert len(result) == 51 and len(result[0]) == 51, "Large image size not handled correctly"

def test_mandelbrot_consistency(generator: MandelbrotGenerator):
    # Test that generating the same image twice produces the same result
    width, height, max_iter = 500, 500, 50
    result1 = generator.generate(width, height, max_iter)
    result2 = generator.generate(width, height, max_iter)
    assert np.array_equal(result1, result2), "Inconsistent results for the same parameters"