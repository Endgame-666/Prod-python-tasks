import multiprocessing
from multiprocessing import shared_memory
import numpy as np
import matplotlib.pyplot as plt


class MandelbrotGenerator:
    def __init__(self, num_workers: int):
        self.num_workers = num_workers

    def generate(self, width: int, height: int, max_iter: int, chunk_size: int = 100) -> np.ndarray:
        shm = shared_memory.SharedMemory(create=True, size=width * height * 4)
        shared_array: np.ndarray = np.ndarray((height, width), dtype=np.float32, buffer=shm.buf)

        with multiprocessing.Pool(processes=self.num_workers) as pool:
            for start_y in range(0, height, chunk_size):
                end_y = min(start_y + chunk_size, height)
                pool.starmap(self._mandelbrot_row,
                             ((y, width, height, max_iter, shm.name) for y in range(start_y, end_y)))

        result = shared_array.copy()
        shm.close()
        shm.unlink()
        return result

    @staticmethod
    def _mandelbrot_row(y: int, width: int, height: int, max_iter: int, shm_name: str):
        shm = shared_memory.SharedMemory(name=shm_name)
        shared_array: np.ndarray = np.ndarray((height, width), dtype=np.float32, buffer=shm.buf)
        for x in range(width):
            shared_array[y, x] = MandelbrotGenerator._mandelbrot_value(x, y, width, height, max_iter)
        shm.close()

    @staticmethod
    def _mandelbrot_value(x: int, y: int, width: int, height: int, max_iter: int) -> float:
        c = MandelbrotGenerator._scale(x, y, width, height)
        z = 0.0j
        n = 0
        while abs(z) < 2 and n < max_iter:
            z = z * z + c
            n += 1
        return float(n) if n < max_iter else 0

    @staticmethod
    def _scale(x: int, y: int, width: int, height: int) -> complex:
        return complex(3.5 * x / width - 2.5, 2 * y / height - 1)


def visualize(data: np.ndarray, colormap: str = 'magma', save_path: str | None = None):
    plt.imshow(data, cmap=colormap)
    plt.axis('off')
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0, transparent=True)
    else:
        plt.show()
