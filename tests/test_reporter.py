# ruff: noqa: S101, ANN001
from pathlib import Path

import pytest

from trivy_image_slack_reporter.trivy_image_slack_reporter import main

reports = [str(p) for p in Path("tests/fixtures").glob("*-report.json")]


@pytest.mark.parametrize("report", reports, ids=lambda x: x.split("/")[-1])
def test_reports(monkeypatch, capsys, snapshot, report) -> None:
    monkeypatch.setenv("DRY_RUN", "1")
    monkeypatch.setenv("RESULTS_FILE", report)
    monkeypatch.setenv("IMAGE_TITLE", "test-image:latest")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "123456789")
    monkeypatch.setenv("SLACK_CHANNEL_ID", "123456789")
    monkeypatch.setenv("SEVERITY", "HIGH,CRITICAL,MEDIUM")

    main()

    output = capsys.readouterr().out

    assert output == snapshot


severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "CRITICAL,HIGH"]


@pytest.mark.parametrize("severity", severities, ids=lambda x: x)
def test_severity(monkeypatch, capsys, snapshot, severity) -> None:
    monkeypatch.setenv("DRY_RUN", "1")
    monkeypatch.setenv("RESULTS_FILE", "tests/fixtures/python-3.9-report.json")
    monkeypatch.setenv("IMAGE_TITLE", "test-image:latest")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "123456789")
    monkeypatch.setenv("SLACK_CHANNEL_ID", "123456789")
    monkeypatch.setenv("SEVERITY", "HIGH,CRITICAL,MEDIUM")

    main()

    output = capsys.readouterr().out

    assert output == snapshot


def test_artefact_url(monkeypatch, capsys, snapshot) -> None:
    monkeypatch.setenv("DRY_RUN", "1")
    monkeypatch.setenv("RESULTS_FILE", "tests/fixtures/python-3.9-report.json")
    monkeypatch.setenv("IMAGE_TITLE", "test-image:latest")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "123456789")
    monkeypatch.setenv("SLACK_CHANNEL_ID", "123456789")
    monkeypatch.setenv("SEVERITY", "HIGH,CRITICAL,MEDIUM")
    monkeypatch.setenv("ARTIFACT_URL", "https://example.com/artifact")

    main()

    output = capsys.readouterr().out

    assert output == snapshot


def test_no_vulnerabilities(monkeypatch, capsys, snapshot) -> None:
    monkeypatch.setenv("DRY_RUN", "1")
    monkeypatch.setenv("RESULTS_FILE", "tests/fixtures/python-3.9-report.json")
    monkeypatch.setenv("IMAGE_TITLE", "test-image:latest")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "123456789")
    monkeypatch.setenv("SLACK_CHANNEL_ID", "123456789")
    monkeypatch.setenv("SEVERITY", "CRITICAL")

    main()

    output = capsys.readouterr().out

    assert output == snapshot
