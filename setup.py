from setuptools import find_packages, setup

setup(
    name='backt',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'pymysql',
        'flask-restful',
        'passlib',
        'flask_jwt_extended',
        'flask_mail',
        'requests',
        'flask-cors',
        'flask_expects_json',
        #'sys',#,'flask-marshmallow'
    ],
)