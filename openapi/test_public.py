import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from solution import create_app


@pytest.fixture()
def client() -> TestClient:
    """Получить тест-клиент."""
    app = create_app()
    return TestClient(app)


@pytest.fixture()
def root() -> Path:
    """Получить корень задачи."""
    return Path(__file__).parent


@pytest.fixture()
def openapi_specification(root: Path) -> dict[str, Any]:
    """Получить спецификацию `OpenAPI`."""
    path = root / "docs" / "openapi.json"
    with path.open() as file:
        return json.load(file)


def test__openapi(client: TestClient, openapi_specification: dict[str, Any]) -> None:
    """Тест равенства спецификаций `OpenAPI`."""
    response = client.get("/openapi.json")
    actual_specification = json.loads(response.content)

    assert actual_specification == openapi_specification
