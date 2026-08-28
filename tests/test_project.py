import importlib

import pytest


@pytest.mark.parametrize(
    "module_name",
    ["models", "mcp_main", "langchain_core", "langchain_huggingface", "langchain_openai"],
)
def test_runtime_imports(module_name):
    importlib.import_module(module_name)


def test_mcp_health():
    from fastapi.testclient import TestClient
    from mcp_main import app

    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in {"ready", "ok"}