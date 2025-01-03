# Фрактал Мандельброта

Необходимо реализовать алгоритм рисования [фрактала](https://ru.wikipedia.org/wiki/%D0%9C%D0%BD%D0%BE%D0%B6%D0%B5%D1%81%D1%82%D0%B2%D0%BE_%D0%9C%D0%B0%D0%BD%D0%B4%D0%B5%D0%BB%D1%8C%D0%B1%D1%80%D0%BE%D1%82%D0%B0).

Некоторые уточнения по задаче:
1. Необходимо реализовать [цветной вариант](https://ru.wikipedia.org/wiki/%D0%9C%D0%BD%D0%BE%D0%B6%D0%B5%D1%81%D1%82%D0%B2%D0%BE_%D0%9C%D0%B0%D0%BD%D0%B4%D0%B5%D0%BB%D1%8C%D0%B1%D1%80%D0%BE%D1%82%D0%B0#%D0%A6%D0%B2%D0%B5%D1%82%D0%BD%D1%8B%D0%B5_%D0%B2%D0%B0%D1%80%D0%B8%D0%B0%D0%BD%D1%82%D1%8B). Число итераций будет параметром алгоритма, в каждой точке как предлагается на wiki рисуем число итераций, или если достигли max_iter 0.
2. Разделить на паралельные вычисления необходимо попиксельно, например разбив пиксели на квадратики и запуская внутренний цикл независимо в каждом блоке. Не используйте numpy в своей реализации. Для определённости поворота / позиции на комплексной плоскости используйте функцию `_scale`.
3. В условии специально не указано чем пользоваться threading или multiprocessing, нужно выбрать подходящий инструмент самим.
4. Для дебага вам предложено использовать matplotlib. Будьте готовы к тому что в тесте разрешения изображений на выходе должно будут хотя бы 2k пикселей на 2k. В то же время для дебага рекомендую пробовать поменьше.
5. В папке target_images содержатся примеры того как фрактал должен выглядеть на разных количествах итераций и с разным разрешением.
6. Для самых главных любителей питона предложено реализовать векторизованную версию на numpy (отдельно). За нее можно получить доп балл, тогда нужно сделать jupyter notebook в котором вы сравниваете время работы векторизованной и своей параллельной версии. Приложите этот jupyter notebook ссылкой отдельно в энитаск.

```python
import matplotlib.pyplot as plt

class MandelbrotGenerator:
    def __init__(self, num_workers: int):
        self.num_workers = num_workers

    def generate(self, width: int, height: int, max_iter: int) -> list[list[float]]:
        # Implement the parallel version of the Mandelbrot set generation
        pass

    @staticmethod
    def _scale(x: int, y: int, width: int, height: int) -> complex:
        return complex(3.5 * x / width - 2.5, 2 * y / height - 1)

def visualize(data: list[list[float]], colormap: str = 'magma', save_path: str | None = None) -> None:
    plt.imshow(data, cmap=colormap)
    # plt.colorbar()
    plt.axis('off')
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0, transparent=True, format='png')
    else:
        plt.show()
```

## Тесты

Тесты к этому заданию занимают время и кушают наши деньги, в задаче есть только публичные тесты, поэтому пожалуйста прогоните их локально с помощью команды `pytest`. Когда локально все будет ок, запушите и запустите тесты на github.
