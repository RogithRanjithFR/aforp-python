import json

import watchdog


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code


def test_check_http_500(monkeypatch):
    monkeypatch.setattr(watchdog.requests, "get",
                        lambda url, timeout: FakeResponse(500))
    assert watchdog.check_http("http://fake/") is False


def test_check_http_200(monkeypatch):
    monkeypatch.setattr(watchdog.requests, "get",
                        lambda url, timeout: FakeResponse(200))
    assert watchdog.check_http("http://fake/") is True


def test_main_code_1_si_http_500(monkeypatch, tmp_path):
    cfg = tmp_path / "t.yaml"
    cfg.write_text(
        'targets:\n'
        '  - {name: api, host: 127.0.0.1, port: 8000, health_url: "http://fake/"}\n'
    )
    out = tmp_path / "r.json"
    monkeypatch.setattr(watchdog, "check_port", lambda h, p, timeout=2.0: (True, 1))
    monkeypatch.setattr(watchdog.requests, "get",
                        lambda url, timeout: FakeResponse(500))

    assert watchdog.main([str(cfg), "-o", str(out)]) == 1
    assert json.loads(out.read_text()) == [{"name": "api", "ok": False, "ms": 1}]


def test_main_fichier_absent(tmp_path):
    assert watchdog.main([str(tmp_path / "absent.yaml")]) == 2
