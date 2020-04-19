from setuptools import setup

setup(
    name="auto_crop",
    version="0.0.1",
    description="Tool to automatically crop images based on shapes",
    url="https://github.com/sgenheden/auto-crop",
    author="Samuel Genheden",
    author_email="samuel.genheden@gmail.com",
    packages=["auto_crop"],
    install_requires=["pillow", "imutils", "black"],
    entry_points={"console_scripts": ["autocrop = auto_crop.main:main"]},
)
