import setuptools

setuptools.setup(
    name="deck_cli",
    version="0.1.0",
    author="72nd",
    author_email="msg@frg72.com",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points="""
            [console_scripts]
            deck-cli=deck_cli.cli.main:cli
        """,
    install_requires=[
        "click==7.1.2",
        "Jinja2==2.11.2",
        "marshmallow==3.10.0",
        "marshmallow-dataclass==8.3.0",
        "marshmallow-enum==1.5.1",
        "pytz==2021.1",
        "PyYAML==5.3.1",
        "requests==2.25.1",
        "typeguard==2.10.0",
    ],
)
