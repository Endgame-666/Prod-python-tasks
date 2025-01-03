### Robot

В этой домашке вам предлагается улучшить читаемость кода робота пылесоса,
который был у нас на семинаре с помощью класса Enum.

Вкратце об `Enum`:

Класс `Enum` в Python используется для создания перечислений — наборов именованных констант.

```python
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

print(Color.RED)
# Output: Color.RED

print(Color.RED.name)
# Output: RED

print(Color.RED.value)
# Output: 1
```

Как мы помним, мы говорили о принципе метода `DRY` (don't repeat yourself).
И в этой домашке вам нужно взять и высушить код, чтобы у нас все было красиво.

Вам нужно:

1. Применять метод `Enum`

2. Переписать код таким образом, чтобы методы `turn_left` и `turn_right` были объеденины в один метод `turn`,
который принимает на вход объект класса `TurnDirection`

3. Переписать код таким образом, чтобы методы `move_forward` и `move_backward` были объеденины в один метод `move`,
который принимает на вход `distance (int)` и объект класса `Movement`