# chatgpt_dataextraction
A small tool using Python and the ChatGPT API to answer questions about the content of a PDF file

# Database Setup (sqlite3)
CREATE TABLE chatgpt (
    key INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT,
    answer TEXT
);

# Installation
I used conda with the following setup command:
conda create -n [venv_name] python openai pandas sqlite pdfminer.six

## List of all packages in the environment:
This file may be used to create an environment using:
$ conda create --name <env> --file <this file>
platform: osx-arm64

aiohttp=3.8.4=py311heffc1b2_1
aiosignal=1.3.1=pyhd8ed1ab_0
appdirs=1.4.4=pyh9f0ad1d_0
appnope=0.1.3=pyhd8ed1ab_0
asttokens=2.2.1=pyhd8ed1ab_0
async-timeout=4.0.2=pyhd8ed1ab_0
attrs=23.1.0=pyh71513ae_1
backcall=0.2.0=pyh9f0ad1d_0
backports=1.0=pyhd8ed1ab_3
backports.functools_lru_cache=1.6.5=pyhd8ed1ab_0
beautifulsoup4=4.12.2=pyha770c72_0
brotli=1.0.9=h1a8c8d9_9
brotli-bin=1.0.9=h1a8c8d9_9
brotli-python=1.0.9=py311ha397e9f_9
bzip2=1.0.8=h3422bc3_4
ca-certificates=2023.5.7=hf0a4a13_0
certifi=2023.5.7=pyhd8ed1ab_0
cffi=1.15.1=py311hae827db_3
charset-normalizer=3.2.0=pyhd8ed1ab_0
click=8.1.5=unix_pyh707e725_0
colorama=0.4.6=pyhd8ed1ab_0
comm=0.1.3=pyhd8ed1ab_0
contourpy=1.1.0=py311he4fd1f5_0
cryptography=41.0.2=py311h5fb2c35_0
cycler=0.11.0=pyhd8ed1ab_0
debugpy=1.6.7=py311ha397e9f_0
decorator=5.1.1=pyhd8ed1ab_0
docker-pycreds=0.4.0=py_0
et_xmlfile=1.1.0=pyhd8ed1ab_0
executing=1.2.0=pyhd8ed1ab_0
fonttools=4.41.0=py311heffc1b2_0
freetype=2.12.1=hd633e50_1
frozenlist=1.4.0=py311heffc1b2_0
gitdb=4.0.10=pyhd8ed1ab_0
gitpython=3.1.32=pyhd8ed1ab_0
idna=3.4=pyhd8ed1ab_0
importlib-metadata=6.8.0=pyha770c72_0
importlib_metadata=6.8.0=hd8ed1ab_0
ipykernel=6.24.0=pyh5fb750a_0
ipython=8.14.0=pyhd1c38e8_0
jedi=0.18.2=pyhd8ed1ab_0
joblib=1.3.0=pyhd8ed1ab_1
jupyter_client=8.3.0=pyhd8ed1ab_0
jupyter_core=5.3.1=py311h267d04e_0
kiwisolver=1.4.4=py311hd6ee22a_1
lcms2=2.15=hd835a16_1
lerc=4.0.0=h9a09cb3_0
libabseil=20230125.3=cxx17_h13dd4ca_0
libblas=3.9.0=17_osxarm64_openblas
libbrotlicommon=1.0.9=h1a8c8d9_9
libbrotlidec=1.0.9=h1a8c8d9_9
libbrotlienc=1.0.9=h1a8c8d9_9
libcblas=3.9.0=17_osxarm64_openblas
libcxx=16.0.6=h4653b0c_0
libdeflate=1.18=h1a8c8d9_0
libexpat=2.5.0=hb7217d7_1
libffi=3.4.2=h3422bc3_5
libgfortran=5.0.0=12_2_0_hd922786_31
libgfortran5=12.2.0=h0eea778_31
libjpeg-turbo=2.1.5.1=h1a8c8d9_0
liblapack=3.9.0=17_osxarm64_openblas
libopenblas=0.3.23=openmp_hc731615_0
libpng=1.6.39=h76d750c_0
libprotobuf=4.23.3=hf32f9b9_0
libsodium=1.0.18=h27ca646_1
libsqlite=3.42.0=hb31c410_0
libtiff=4.5.1=h23a1a89_0
libwebp-base=1.3.1=hb547adb_0
libxcb=1.15=hf346824_0
libzlib=1.2.13=h53f4e23_5
llvm-openmp=16.0.6=h1c12783_0
matplotlib=3.7.2=py311ha1ab1f8_0
matplotlib-base=3.7.2=py311h3bc9839_0
matplotlib-inline=0.1.6=pyhd8ed1ab_0
multidict=6.0.4=py311he2be06e_0
munkres=1.1.4=pyh9f0ad1d_0
ncurses=6.4=h7ea286d_0
nest-asyncio=1.5.6=pyhd8ed1ab_0
numpy=1.25.1=py311hb8f3215_0
openai=0.27.8=pyhd8ed1ab_0
openjpeg=2.5.0=hbc2ba62_2
openpyxl=3.1.2=py311heffc1b2_0
openssl=3.1.1=h53f4e23_1
packaging=23.1=pyhd8ed1ab_0
pandas=2.0.3=py311h9e438b8_1
pandas-stubs=2.0.2.230605=pyhd8ed1ab_2
parso=0.8.3=pyhd8ed1ab_0
pathtools=0.1.2=py_1
pdfminer.six=20221105=pyhd8ed1ab_0
pexpect=4.8.0=pyh1a96a4e_2
pickleshare=0.7.5=py_1003
pillow=10.0.0=py311h095fde6_0
pip=23.2=pyhd8ed1ab_0
platformdirs=3.8.1=pyhd8ed1ab_0
plotly=5.15.0=pyhd8ed1ab_0
pooch=1.7.0=pyha770c72_3
prompt-toolkit=3.0.39=pyha770c72_0
prompt_toolkit=3.0.39=hd8ed1ab_0
protobuf=4.23.3=py311h4acf6a1_0
psutil=5.9.5=py311he2be06e_0
pthread-stubs=0.4=h27ca646_1001
ptyprocess=0.7.0=pyhd3deb0d_0
pure_eval=0.2.2=pyhd8ed1ab_0
pycparser=2.21=pyhd8ed1ab_0
pygments=2.15.1=pyhd8ed1ab_0
pyparsing=3.0.9=pyhd8ed1ab_0
pysocks=1.7.1=pyha2e5f31_6
python=3.11.4=h47c9636_0_cpython
python-dateutil=2.8.2=pyhd8ed1ab_0
python-tzdata=2023.3=pyhd8ed1ab_0
python_abi=3.11=3_cp311
pytz=2023.3=pyhd8ed1ab_0
pyyaml=6.0=py311he2be06e_5
pyzmq=25.1.0=py311hb1af645_0
readline=8.2=h92ec313_1
requests=2.31.0=pyhd8ed1ab_0
scikit-learn=1.3.0=py311hf0b18b8_0
scipy=1.11.1=py311h93d07a4_0
sentry-sdk=1.28.1=pyhd8ed1ab_0
setproctitle=1.3.2=py311he2be06e_1
setuptools=68.0.0=pyhd8ed1ab_0
six=1.16.0=pyh6c4a22f_0
smmap=3.0.5=pyh44b312d_0
soupsieve=2.3.2.post1=pyhd8ed1ab_0
sqlite=3.42.0=h203b68d_0
stack_data=0.6.2=pyhd8ed1ab_0
tenacity=8.2.2=pyhd8ed1ab_0
threadpoolctl=3.2.0=pyha21a80b_0
tk=8.6.12=he1e0b03_0
tornado=6.3.2=py311heffc1b2_0
tqdm=4.65.0=pyhd8ed1ab_1
traitlets=5.9.0=pyhd8ed1ab_0
types-pytz=2023.3.0.0=pyhd8ed1ab_0
typing-extensions=4.7.1=hd8ed1ab_0
typing_extensions=4.7.1=pyha770c72_0
tzdata=2023c=h71feb2d_0
urllib3=2.0.3=pyhd8ed1ab_1
wandb=0.15.5=pyhd8ed1ab_0
wcwidth=0.2.6=pyhd8ed1ab_0
wheel=0.40.0=pyhd8ed1ab_0
xorg-libxau=1.0.11=hb547adb_0
xorg-libxdmcp=1.1.3=h27ca646_0
xz=5.2.6=h57fd34a_0
yaml=0.2.5=h3422bc3_2
yarl=1.9.2=py311heffc1b2_0
zeromq=4.3.4=hbdafb3b_1
zipp=3.16.2=pyhd8ed1ab_0
zstd=1.5.2=h4f39d0f_7
