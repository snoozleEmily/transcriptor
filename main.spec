# -*- mode: python ; coding: utf-8 -*-
# Robust PyInstaller spec: explicitly collects llama_cpp DLLs and llm_models files
# Avoids using Tree import (not stable across PyInstaller versions).

import os
import llama_cpp
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

project_dir = os.path.abspath(os.getcwd())

# Where llama_cpp is installed
llama_pkg_dir = os.path.dirname(llama_cpp.__file__)

# Collect dynamic libs from the package (this finds many DLLs automatically)
llama_binaries = collect_dynamic_libs('llama_cpp')  # list of (src, dest, type) tuples


# Manually include every file from llama_cpp/lib into datas so it exists at runtime
llama_lib_src = os.path.join(llama_pkg_dir, 'lib')
llama_lib_datas = []
if os.path.isdir(llama_lib_src):
    for root, _, files in os.walk(llama_lib_src):
        for fname in files:
            src_path = os.path.join(root, fname)
            # destination path inside the package in the bundle
            rel_dir = os.path.relpath(root, llama_pkg_dir)  # typically 'lib' or 'lib\\sub'
            dest_dir = os.path.join('llama_cpp', rel_dir)
            llama_lib_datas.append((src_path, dest_dir))
# else: no lib folder found; we still proceed


# Include your llm_models folder (so your gguf is available inside the bundle)
models_src = os.path.join(project_dir, 'llm_models')
models_datas = []
if os.path.isdir(models_src):
    for root, _, files in os.walk(models_src):
        for fname in files:
            src_path = os.path.join(root, fname)
            # preserve the models directory structure under llm_models/ in the bundle
            rel_path = os.path.relpath(src_path, project_dir)  # e.g. 'llm_models/...'
            dest_dir = os.path.dirname(rel_path)
            models_datas.append((src_path, dest_dir))

# 4) Also collect standard package data for llama_cpp (python files, etc.)
llama_datas = collect_data_files('llama_cpp')  # list of (src, dest)

# Combine all datas
all_datas = list(llama_datas) + list(llama_lib_datas) + list(models_datas)

# Analysis: include binaries and datas
a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=llama_binaries,
    datas=all_datas,
    hiddenimports=[],                         # add module names here if you know them
    hookspath=[],
    runtime_hooks=['pyinstaller_hooks/add_llama_dll.py'],  # ensure DLL dir registered
    hooksconfig={},
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=True,            # verbose bootloader output for easier debugging
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,             # avoid UPX compression
    runtime_tmpdir=None,
    console=True,          # keep console to see errors during debug
)


# verify files
from PyInstaller.building.build_main import COLLECT

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='main'
)
