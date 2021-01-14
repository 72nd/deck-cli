import setuptools

setuptools.setup(
        name="deck_cli",
        version="0.0.1",
        author="72nd",
        author_email="msg@frg72.com",
        packages=setuptools.find_packages(),
        entry_points="""
            [console_scripts]
            deck-cli=deck_cli.cli.main:cli
        """
)
