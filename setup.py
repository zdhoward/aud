from distutils.core import setup

setup(
    name="aud",
    packages=["aud"],
    version="0.8.0",
    license="MIT",
    description="aud is a python package that aims to make bulk file edits easy enough for anyone with minimal scripting or python knowledge",
    author="Zach Howard",
    author_email="zach.d.howard@gmail.com",
    url="https://github.com/zdhoward/aud",
    download_url="https://github.com/zdhoward/aud/archive/v_080.tar.gz",
    keywords=["audio", "studio", "batch", "easy"],
    install_requires=["pydub", "colorama"],
)
