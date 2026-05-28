from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

setup_args = generate_distutils_setup(
    packages=[
        'robocon_gui',
        'robocon_gui.core',
        'robocon_gui.ros',
        'robocon_gui.services',
        'robocon_gui.ui',
    ],
    package_dir={'': '.'},
)

setup(**setup_args)
