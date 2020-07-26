#!/usr/bin/env python
import os
import argparse
import regex
import shutil
import tempfile
import contextlib
import glob
import subprocess
from pathlib import Path

import semver
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader("./templates/"),
    autoescape=select_autoescape(["html", "xml"]),
)
# The root directory containing the language-specific package templates
TEMPLATE_DIR_NAME = os.environ.get("TEMPLATE_DIR_NAME", "templates")

# Relative path to the directory containing all services
SERVICE_ROOT = os.environ.get("SERVICE_ROOT", "./protos")

# Relative paths from the root to each SUPPORTED_LANGUAGES template directory
TEMPLATE_DIR_PATHS = {}

SUPPORTED_LANGUAGES = os.listdir(TEMPLATE_DIR_NAME)

# The directory within the package to write the service protofiles to
PROTOS_DIR_NAME = os.environ.get("PROTOS_DIR_NAME", "proto")

# Name of the script within each template that will build and publish the
# package
BUILD_AND_PUBLISH_FILENAME = "build_and_publish.sh"

# Sanity check to ensure support
for language_name in SUPPORTED_LANGUAGES:
    template_dir_path = os.path.join(TEMPLATE_DIR_NAME, language_name)

    assert os.path.exists(
        os.path.join(template_dir_path, BUILD_AND_PUBLISH_FILENAME)
    ), "supported language {} does not have a {}".format(
        language_name, BUILD_AND_PUBLISH_FILENAME
    )
    TEMPLATE_DIR_PATHS[language_name] = template_dir_path

@contextlib.contextmanager
def chdir(dirname=None):
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)


def build(service, version):
    version = semver.VersionInfo.parse(version)
    service_dir = os.path.join(SERVICE_ROOT, service)

    assert os.path.exists(service_dir) and os.path.isdir(
        service_dir
    ), "Service {} does not exist (directory not found)".format(service)

    for language_name in SUPPORTED_LANGUAGES:
        with tempfile.TemporaryDirectory() as tmpdirname:
            shutil.copytree(
                service_dir,
                os.path.join(tmpdirname, PROTOS_DIR_NAME),
                dirs_exist_ok=True,
            )
            shutil.copytree(
                TEMPLATE_DIR_PATHS[language_name], tmpdirname, dirs_exist_ok=True
            )

            templates = []

            with chdir(tmpdirname):
                for filename in glob.glob("**/*.j2", recursive=True):
                    templates.append((os.path.join(tmpdirname, filename), filename))

            for full_path, template_name in templates:
                template = env.get_template(os.path.join(language_name, template_name))
                new_path = full_path.replace(".j2", "")
                with open(new_path, "w") as write_handle:
                    write_handle.write(
                        template.render(
                            SERVICE_NAME=service,
                            SERVICE_VERSION=version,
                            PROTOS_DIR_NAME=PROTOS_DIR_NAME,
                        )
                    )
                os.remove(full_path)

            with chdir(tmpdirname):
                subprocess.run(["bash", BUILD_AND_PUBLISH_FILENAME], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Helper tool for building polygot protobuf libraries. Currently supports the following languages: {}.".format(
            ", ".join(SUPPORTED_LANGUAGES)
        )
    )

    parser.add_argument("service", help="Name of service to build.")
    parser.add_argument(
        "version", help="Version of the new service in Semver 2.0 format."
    )
    args = parser.parse_args()
    build(args.service, args.version)
