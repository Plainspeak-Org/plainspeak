#!/usr/bin/env python3
"""
Package Submission Script for PlainSpeak

This script automates the submission process for various distribution channels.
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PackageSubmitter:
    def __init__(self, version: str):
        self.version = version
        self.root_dir = Path(__file__).parent.parent
        self.dist_dir = self.root_dir / "dist"
        self.build_dir = self.root_dir / "build"

    def prepare_environment(self):
        """Prepare the environment for submissions."""
        logger.info("Preparing environment...")

        # Create directories if they don't exist
        self.dist_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)

        # Verify version matches across files
        self._verify_version()

        # Clean previous builds
        self._clean_directories()

    def _verify_version(self):
        """Verify version number matches across all files."""
        files_to_check = [
            ("pyproject.toml", r'version = "(.*?)"'),
            ("plainspeak/__init__.py", r'__version__ = "(.*?)"'),
            ("assets/VERSION.txt", r"^([\d.]+)"),
        ]

        versions = {}
        for file_path, pattern in files_to_check:
            full_path = self.root_dir / file_path
            if full_path.exists():
                content = full_path.read_text()
                import re

                match = re.search(pattern, content)
                if match:
                    versions[file_path] = match.group(1)

        if len(set(versions.values())) != 1:
            raise ValueError(f"Version mismatch across files: {versions}")

    def _clean_directories(self):
        """Clean build and dist directories."""
        logger.info("Cleaning build directories...")
        for dir_path in [self.dist_dir, self.build_dir]:
            for file_path in dir_path.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    import shutil

                    shutil.rmtree(file_path)

    def submit_pypi(self, test: bool = True):
        """Submit package to PyPI."""
        logger.info(f"Preparing PyPI submission (test={test})...")

        # Build package
        subprocess.run(["python", "-m", "build"], check=True)

        # Submit to Test PyPI first if requested
        if test:
            logger.info("Uploading to Test PyPI...")
            subprocess.run(
                [
                    "python",
                    "-m",
                    "twine",
                    "upload",
                    "--repository-url",
                    "https://test.pypi.org/legacy/",
                    "dist/*",
                ],
                check=True,
            )

            # Test installation from Test PyPI
            subprocess.run(
                [
                    "python",
                    "-m",
                    "pip",
                    "install",
                    "--index-url",
                    "https://test.pypi.org/simple/",
                    "--no-deps",
                    f"plainspeak=={self.version}",
                ],
                check=True,
            )

        # Submit to production PyPI
        logger.info("Uploading to production PyPI...")
        subprocess.run(["python", "-m", "twine", "upload", "dist/*"], check=True)

    def submit_windows_store(self):
        """Submit package to Microsoft Store."""
        logger.info("Preparing Windows Store submission...")

        # Build MSIX package
        subprocess.run(
            [
                "pyinstaller",
                "--clean",
                "--onefile",
                "--name",
                f"plainspeak-{self.version}",
                "--icon",
                "assets/icons/windows/plainspeak.ico",
                "plainspeak/__main__.py",
            ],
            check=True,
        )

        # Create Windows installer
        subprocess.run(
            [
                "iscc",
                "/DMyAppVersion=" + self.version,
                "installers/windows/installer.iss",
            ],
            check=True,
        )

        logger.info("Windows packages built successfully")
        logger.info("Please submit manually through Partner Center")

    def submit_mac_app_store(self):
        """Submit package to Mac App Store."""
        logger.info("Preparing Mac App Store submission...")

        # Build app bundle
        subprocess.run(
            [
                "pyinstaller",
                "--clean",
                "--windowed",
                "--name",
                "PlainSpeak",
                "--icon",
                "assets/icons/macos/plainspeak.icns",
                "--osx-bundle-identifier",
                "org.plainspeak.app",
                "plainspeak/__main__.py",
            ],
            check=True,
        )

        # Sign and notarize
        subprocess.run(
            [
                "codesign",
                "--force",
                "--options",
                "runtime",
                "--entitlements",
                "installers/macos/entitlements.plist",
                "--sign",
                "Developer ID Application",
                "dist/PlainSpeak.app",
            ],
            check=True,
        )

        # Create DMG
        subprocess.run(
            [
                "create-dmg",
                "--volname",
                "PlainSpeak",
                "--app-drop-link",
                "450",
                "320",
                f"dist/PlainSpeak-{self.version}.dmg",
                "dist/PlainSpeak.app",
            ],
            check=True,
        )

        logger.info("macOS packages built successfully")
        logger.info("Please submit through App Store Connect")

    def submit_homebrew(self):
        """Submit formula to Homebrew."""
        logger.info("Preparing Homebrew submission...")

        # Create Homebrew formula
        formula_path = self.root_dir / "packaging/homebrew/plainspeak.rb"
        formula_template = f"""
class Plainspeak < Formula
  include Language::Python::Virtualenv

  desc "Natural language interface for your computer"
  homepage "https://plainspeak.org"
  url "https://files.pythonhosted.org/packages/source/p/plainspeak/plainspeak-{self.version}.tar.gz"
  sha256 "{{sha256}}"
  license "MIT"

  depends_on "python@3.9"

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"plainspeak", "--version"
  end
end
"""
        formula_path.write_text(formula_template)

        logger.info("Homebrew formula created")
        logger.info("Please submit PR to homebrew-core")

    def submit_linux_packages(self):
        """Create Linux distribution packages."""
        logger.info("Preparing Linux packages...")

        # Build source distribution
        subprocess.run(["python", "-m", "build", "--sdist"], check=True)

        # Create .deb package
        subprocess.run(
            ["python", "packaging/linux/create_deb.py", "--version", self.version],
            check=True,
        )

        # Create .rpm package
        subprocess.run(
            ["python", "packaging/linux/create_rpm.py", "--version", self.version],
            check=True,
        )

        # Create PKGBUILD
        pkgbuild_path = self.root_dir / "packaging/linux/PKGBUILD"
        pkgbuild_template = f"""
pkgname=plainspeak
pkgver={self.version}
pkgrel=1
pkgdesc="Natural language interface for your computer"
arch=('any')
url="https://plainspeak.org"
license=('MIT')
depends=('python>=3.9')
makedepends=('python-build' 'python-installer' 'python-wheel')
source=("https://files.pythonhosted.org/packages/source/p/${{pkgname}}/${{pkgname}}-${{pkgver}}.tar.gz")
sha256sums=('SKIP')

build() {{
    cd "$srcdir/${{pkgname}}-${{pkgver}}"
    python -m build --wheel --no-isolation
}}

package() {{
    cd "$srcdir/${{pkgname}}-${{pkgver}}"
    python -m installer --destdir="$pkgdir" dist/*.whl
}}
"""
        pkgbuild_path.write_text(pkgbuild_template)

        logger.info("Linux packages created")
        logger.info("Please submit to respective repositories")


def main():
    parser = argparse.ArgumentParser(
        description="Submit PlainSpeak packages to distribution channels"
    )
    parser.add_argument("--version", required=True, help="Version to submit")
    parser.add_argument(
        "--channels",
        nargs="+",
        default=["all"],
        choices=["all", "pypi", "windows", "macos", "homebrew", "linux"],
        help="Distribution channels to submit to",
    )
    parser.add_argument(
        "--skip-test", action="store_true", help="Skip Test PyPI submission"
    )

    args = parser.parse_args()

    submitter = PackageSubmitter(args.version)
    submitter.prepare_environment()

    if "all" in args.channels or "pypi" in args.channels:
        submitter.submit_pypi(test=not args.skip_test)

    if "all" in args.channels or "windows" in args.channels:
        submitter.submit_windows_store()

    if "all" in args.channels or "macos" in args.channels:
        submitter.submit_mac_app_store()

    if "all" in args.channels or "homebrew" in args.channels:
        submitter.submit_homebrew()

    if "all" in args.channels or "linux" in args.channels:
        submitter.submit_linux_packages()


if __name__ == "__main__":
    main()
