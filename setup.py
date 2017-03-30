from setuptools import setup

tests_require = (
    'mock>=1.0.1',
)

setup(
    author="@LoisaidaSam",
    author_email="sam.sandberg@gmail.com",
    description="A Python wrapper for Slack's API",
    install_requires=["requests"],
    keywords="slack api wrapper",
    license="MIT",
    name="pyslack-real",
    packages=["pyslack"],
    test_suite="tests",
    tests_require=tests_require,
    url="https://github.com/loisaidasam/pyslack",
    version="0.6.1",
)
