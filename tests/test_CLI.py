import subprocess


class TestCLI:
    def test_cli_one_jsonl(self):
        result = subprocess.run(
            ["python", "-m", "streamstats", "analyze", "../data/events.jsonl", "--format", "jsonl", "--skip-invalid", "--output", "rep.json"],
            capture_output=True,
            text=True,
            cwd="src"
        )

        assert result.returncode == 0

    def test_cli_two_csv(self):
        result = subprocess.run(
            ["python", "-m", "streamstats", "analyze", "../data/events.csv", "../data/badevents.csv", "--format", "csv", "--skip-invalid"],
            capture_output=True,
            text=True,
            cwd="src"
        )

        assert result.returncode == 0

    def test_cli_help(self):
        result = subprocess.run(
            ["python", "-m", "streamstats", "--help"],
            capture_output=True,
            text=True,
            cwd="src"
        )

        assert result.returncode == 0

    def test_cli_errors_in_file(self):
        result = subprocess.run(
            ["python", "-m", "streamstats", "analyze", "../data/events.csv", "../data/badevents.csv", "--format", "csv"],
            capture_output=True,
            text=True,
            cwd="src"
        )

        assert result.returncode == 2

    def test_cli_incorrect_flag(self):
        result = subprocess.run(
            ["python", "-m", "streamstats", "analyze", "../data/events.jsonl", "--format", "jsonl", "--skip-invalid", "--output"],
            capture_output=True,
            text=True,
            cwd="src"
        )

        assert result.returncode == 2

    def test_cli_empty(self):
        result = subprocess.run(
            ["python", "-m", "streamstats"],
            capture_output=True,
            text=True,
            cwd="src"
        )

        assert result.returncode == 2