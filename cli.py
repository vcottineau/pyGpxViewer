#  MIT License
#
#  Copyright (c) 2022 Vincent Cottineau
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
import subprocess

import click


@click.group()
def cli():
    pass


@cli.command()
def run():
    click.echo("Run locally...")
    cmd = ["_build/pygpxviewer_local"]
    call_with_output(cmd, echo_stdout=True)


@cli.command()
def build():
    click.echo("Sort imports...")
    cmd = ["isort", "pygpxviewer"]
    call_with_output(cmd, echo_stdout=True)

    click.echo("Lint with flake8...")
    cmd = ["flake8", "pygpxviewer"]
    call_with_output(cmd, echo_stdout=True)

    click.echo("Lint with mypy...")
    cmd = ["mypy", "--strict-equality", "--ignore-missing-imports", "--disallow-incomplete-defs", "pygpxviewer"]
    call_with_output(cmd, echo_stdout=True)

    click.echo("Compile with meson...")
    cmd = ["meson", "compile", "-C", "_build"]
    call_with_output(cmd, echo_stdout=True)


@cli.command()
def locales():
    click.echo("Compile with meson...")
    cmd = ["meson", "compile", "-C", "_build", "com.github.pygpxviewer-pot"]
    call_with_output(cmd, echo_stdout=True)

    click.echo("Compile with meson...")
    cmd = ["meson", "compile", "-C", "_build", "com.github.pygpxviewer-update-po"]
    call_with_output(cmd, echo_stdout=True)


@cli.command()
def docs():
    click.echo("Generate documentation...")
    cmd = ["sphinx-build", "-b", "html", "docs/source/", "docs/build/html"]
    call_with_output(cmd, echo_stdout=True)


def call_with_output(cmd, stdin_text=None, echo_stdout=True, abort_on_fail=True, timeout=30):
    pipe = subprocess.PIPE
    with subprocess.Popen(cmd, stdin=pipe, stdout=pipe, stderr=pipe) as proc:
        stdout, stderr = proc.communicate(stdin_text, timeout=timeout)
    if stdout and echo_stdout:
        click.echo('\n' + stdout.decode("utf-8"))
    if stderr or proc.returncode:
        click.secho('\n' + stderr.decode("utf-8"), fg="red")
    if abort_on_fail and proc.returncode:
        raise click.Abort()
    return proc.returncode


if __name__ == "__main__":
    cli()
