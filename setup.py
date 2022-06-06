import setuptools

setuptools.setup(
	name="anylog-api",
	version="0.0.1",
	author="Ori Shadmon",
	author_email="info@anylog.co",
	packages=["anylog_pyrest"],
	description="The AnyLog API is intended to act an easy-to-use interface between AnyLog and third-party applications via REST.",
	url="https://anylog.co",
	python_requires='>=3.5',
	install_requires=["requests", "json"]
)
