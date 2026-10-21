"""Клиент API Restful Booker для домашнего задания по Requests."""

from collections.abc import Mapping
from typing import Any

import requests

BASE_URL = "https://restful-booker.herokuapp.com"


class RestfulBookerApi:
    """Вспомогательные методы для работы с Restful Booker API."""

    def __init__(self, base_url: str = BASE_URL, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def close(self) -> None:
        """Закрывает HTTP-сессию клиента."""
        self.session.close()

    def create_token(
        self,
        username: str = "admin",
        password: str = "password123",
    ) -> requests.Response:
        """Запрашивает токен для защищённых операций с бронями."""
        return self.session.post(
            f"{self.base_url}/auth",
            json={"username": username, "password": password},
            timeout=self.timeout,
        )

    def create_booking(self, booking: Mapping[str, Any]) -> requests.Response:
        """Создаёт новую бронь."""
        return self.session.post(
            f"{self.base_url}/booking",
            json=booking,
            timeout=self.timeout,
        )

    def get_booking(self, booking_id: int) -> requests.Response:
        """Получает бронь по идентификатору."""
        return self.session.get(
            f"{self.base_url}/booking/{booking_id}",
            timeout=self.timeout,
        )

    def partial_update_booking(
        self,
        booking_id: int,
        patch_data: Mapping[str, Any],
        token: str,
    ) -> requests.Response:
        """Частично изменяет бронь через PATCH."""
        return self.session.patch(
            f"{self.base_url}/booking/{booking_id}",
            json=patch_data,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Cookie": f"token={token}",
            },
            timeout=self.timeout,
        )

    def delete_booking(self, booking_id: int, token: str) -> requests.Response:
        """Удаляет тестовую бронь после проверки."""
        return self.session.delete(
            f"{self.base_url}/booking/{booking_id}",
            headers={"Cookie": f"token={token}"},
            timeout=self.timeout,
        )
