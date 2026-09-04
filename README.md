# Auto QA Homework

Решения домашних заданий по курсу Auto QA.

## Урок 01: SimpleMath

В папке `01__Auto QA 1 - Введение в автоматизированное тестирование. Unit тестирование/homework_01/` находятся класс `SimpleMath` и pytest-тесты для методов `square` и `cube`.

Проверка из папки задания:

```bash
uv run --locked pytest -q
```

## Урок 03: Введение в Selenium

В папке `03__Auto QA 3 - Введение в Selenium/homework_02/` находится
Selenium-скрипт для Google Chrome. Он открывает сайт IT Career Hub, переходит к
разделу «Способы оплаты» и сохраняет скриншот.

Запуск из папки задания:

```bash
uv run python test_payment_methods.py
```

Итоговый скриншот сохраняется в
`artifacts/payment_methods_section.png`.
