import os

import pytest


@pytest.fixture(autouse=True)
def default_settings(monkeypatch):
    monkeypatch.syspath_prepend(os.path.join(os.path.dirname(__file__)))
    monkeypatch.setenv('DJANGO_SETTINGS_MODULE', 'test_project.settings')
    from django import setup
    setup()


@pytest.fixture
def rf():
    from django.test import RequestFactory
    return RequestFactory()
