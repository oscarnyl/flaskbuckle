from setuptools import setup

setup(
    name="flaskbuckle",
    version="0.1.6",
    description="Auto-generated Swagger specifications for your Flask API",
    author="Oscar Nylander",
    url="https://www.github.com/oscarnyl/flaskbuckle",
    packages=["flaskbuckle"],
    install_requires=["Flask>=0.12.2"],
    package_data={
        "flaskbuckle": ["swagger-ui/*"]
    },
    python_requires=">=3.6"
)
