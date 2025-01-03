# Циклическая ссылка

Студент второго курса по имени Кеша решил прогулять первый семинар по "Продвинутому Python". Но
каково же было его удивление, когда в домашнем задании он увидел номер, который был разобран на
семинаре.

От студента-попугая злые преподаватели захотели функцию, которая проверяет является ли символическая
ссылка циклической. К сожалению, Кеша умеет только купаться в бассейне и пить джюс, оранжад, поэтому
он обратился за помощью к Вам. Дополните функцию `is_circular_symlink`, чтобы тесты проходили.

Замечания:

* Если символической ссылки не существует, то бросайте исключение `FileNotFoundError`;
* Если объект не является символической ссылкой, то бросайте исключение `RuntimeError`;
* Если символическая ссылка сломанная, то возвращайте `False`;
* Запрещено использовать метод `Path.resolve` - используйте `Path.readlink`.

```python
file = Path("file.txt")
file.touch()

symlink = Path("symlink")
symlink.symlink_to(file)

assert not is_circular_symlink(symlink)
```

```python
first_symlink = Path("first_symlink")
second_symlink = Path("second_symlink")

second_symlink.symlink_to(first_symlink)
first_symlink.symlink_to(second_symlink)

assert is_circular_symlink(first_symlink)
assert is_circular_symlink(second_symlink)
```

Эта задача правда была разобрана на Ваших семинарах, поэтому не будьте как Кеша - и посещайте
учебные занятия. Мы частенько рассказываем спойлеры к домашним заданиям!
