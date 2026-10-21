"""Домашнее задание 7, вариант 1: тестирование Restful Booker API.

Условие:
    Использовать Page Object Model-подход для API и проверить создание брони,
    частичное изменение брони и негативный сценарий.

Запуск из папки домашнего задания:

    cd "/Users/core/Dev/auto-qa-homework/13__Auto QA 13 - Введение в Requests/homework_07"
    uv sync --locked
    uv run pytest -q

Интерпретатор:
    Python 3.12 в окружении `.venv`, созданном командой `uv sync --locked`.

Тесты обращаются к публичному учебному API Restful Booker и удаляют созданные
тестовые брони после завершения проверок.
"""

from collections.abc import Iterator
from uuid import uuid4

import pytest

from restful_booker_api import RestfulBookerApi


@pytest.fixture()
def api() -> Iterator[RestfulBookerApi]:
    """Создаёт API-клиент и закрывает HTTP-сессию после теста."""
    client = RestfulBookerApi()
    try:
        yield client
    finally:
        client.close()


@pytest.fixture()
def booking_payload() -> dict[str, object]:
    """Возвращает уникальные данные для тестовой брони."""
    suffix = uuid4().hex[:8]
    return {
        "firstname": f"QA{suffix}",
        "lastname": "Student",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-01-01",
            "checkout": "2026-01-10",
        },
        "additionalneeds": "Breakfast",
    }


@pytest.fixture()
def auth_token(api: RestfulBookerApi) -> str:
    """Получает токен для операций PATCH и DELETE."""
    response = api.create_token()
    assert response.status_code == 200, (
        f"Не удалось получить токен: HTTP {response.status_code}; "
        f"ответ: {response.text}"
    )

    token = response.json().get("token")
    assert token, "API вернул пустой токен"
    return token


@pytest.fixture()
def created_booking(
    api: RestfulBookerApi,
    auth_token: str,
    booking_payload: dict[str, object],
) -> Iterator[int]:
    """Создаёт бронь для теста и удаляет её после завершения."""
    response = api.create_booking(booking_payload)
    assert response.status_code == 200, (
        f"Не удалось создать бронь: HTTP {response.status_code}; ответ: {response.text}"
    )

    booking_id = response.json().get("bookingid")
    assert isinstance(booking_id, int), "API не вернул числовой bookingid"

    try:
        yield booking_id
    finally:
        api.delete_booking(booking_id, auth_token)


def test_create_booking(
    api: RestfulBookerApi,
    auth_token: str,
    booking_payload: dict[str, object],
) -> None:
    """Проверяет успешное создание новой брони."""
    response = api.create_booking(booking_payload)
    assert response.status_code == 200

    body = response.json()
    booking_id = body.get("bookingid")
    assert isinstance(booking_id, int), "В ответе отсутствует bookingid"
    try:
        assert body["booking"] == booking_payload
    finally:
        api.delete_booking(booking_id, auth_token)


def test_created_booking_can_be_retrieved(
    api: RestfulBookerApi,
    created_booking: int,
    booking_payload: dict[str, object],
) -> None:
    """Проверяет, что созданную бронь можно получить по её ID."""
    response = api.get_booking(created_booking)
    assert response.status_code == 200
    assert response.json() == booking_payload


def test_partial_update_booking(
    api: RestfulBookerApi,
    auth_token: str,
    created_booking: int,
    booking_payload: dict[str, object],
) -> None:
    """Проверяет частичное изменение имени гостя через PATCH."""
    patch_data = {"firstname": "Updated Guest"}

    response = api.partial_update_booking(
        created_booking,
        patch_data,
        auth_token,
    )
    assert response.status_code == 200
    assert response.json()["firstname"] == patch_data["firstname"]

    updated_booking = api.get_booking(created_booking)
    assert updated_booking.status_code == 200
    assert updated_booking.json()["firstname"] == "Updated Guest"
    assert updated_booking.json()["lastname"] == booking_payload["lastname"]


def test_get_missing_booking_returns_not_found(api: RestfulBookerApi) -> None:
    """Проверяет негативный сценарий для несуществующего booking ID."""
    response = api.get_booking(0)
    assert response.status_code == 404
