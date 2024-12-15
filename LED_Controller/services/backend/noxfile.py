"""Noxfile."""
import nox


@nox.session(python="3.12", reuse_venv=True)
def lint(session) -> None:
    session.install("poetry", external=True)
    session.run("poetry", "install", external=True)
    session.run("ruff", "check", "--config=pyproject.toml", ".")
    session.run("mypy", "./upload_service")

@nox.session(python="3.12", reuse_venv=True)
def fixlint(session) -> None:
    session.install("poetry", external=True)
    session.run("poetry", "install", external=True)
    session.run("ruff", "check", "--config=pyproject.toml", ".", "--fix")

@nox.session(python="3.12", reuse_venv=True)
def build(session) -> None:
    session.install("poetry")
    session.run("poetry", "install", "--only=main", external=True)
    session.run("rm", "-rf", "sootworks/led_controller/static", external=True)
    session.run("cp", "-R", "../frontend/dist", "sootworks/led_controller/static", external=True)
    session.run("poetry" ,"build" ,"--format" , "wheel", external=True)

@nox.session(python="3.12", reuse_venv=True)
def test(session) -> None:
    session.install("poetry", external=True)
    session.run("poetry", "install", external=True)
    session.run(
        "pytest",
        "-n=8",
        "--dist=loadscope",  # group all the tests in the same test class
        "--cov",
        "--junitxml=test-results/test.result.xml",
        "--cov-report=xml:test-results/coverage.xml",
        external=True,
    )
