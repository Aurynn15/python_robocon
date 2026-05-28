from setuptools import setup, find_packages

package_name = "robocon_gui"

setup(
    name=package_name,
    version="0.0.1",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Hybrid Nuuh",
    maintainer_email="hybridthry55@gmail.com",
    description="PyQt5 ROS2 GUI for Robocon command control and telemetry monitoring.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "robocon_gui = robocon_gui.main:main",
        ],
    },
)
