"""Noxfile."""
import nox


@nox.session(python="3.11", reuse_venv=True)
def lint(session) -> None:
    session.install("poetry")
    session.run("poetry", "install")
    session.run("ruff", "check", "--config=pyproject.toml", ".")
    session.run("mypy", "./upload_service")

@nox.session(python="3.11", reuse_venv=True)
def fixlint(session) -> None:
    session.install("poetry")
    session.run("poetry", "install")
    session.run("ruff", "check", "--config=pyproject.toml", ".", "--fix")

@nox.session(python="3.11", reuse_venv=True)
def build(session) -> None:
    session.install("poetry")
    session.run("poetry", "install", "--only=main")
    session.run("rm", "-rf", "sootworks/led_controller/static", external=True)
    session.run("cp", "-R", "../frontend/dist", "sootworks/led_controller/static", external=True)
    session.run("poetry" ,"build" ,"--format" , "wheel")

@nox.session(python="3.11", reuse_venv=True)
def test(session) -> None:
    session.install("poetry")
    session.run("poetry", "install")
    session.run(
        "pytest",
        "-n=8",
        "--dist=loadscope",  # group all the tests in the same test class
        "--cov",
        "--junitxml=test-results/test.result.xml",
        "--cov-report=xml:test-results/coverage.xml",
    )
