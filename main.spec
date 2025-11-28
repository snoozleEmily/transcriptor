# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec: includes llama_cpp DLLs, llm_models, whisper assets.

import os
import whisper
import llama_cpp
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files
from PyInstaller.building.build_main import COLLECT


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
project_dir = os.path.abspath(os.getcwd())

# llama_cpp package dir
llama_pkg_dir = os.path.dirname(llama_cpp.__file__)

# whisper package dir
whisper_pkg_dir = os.path.dirname(whisper.__file__)


# -------------------------------------------------------------------
# Llama: dynamic libs
# -------------------------------------------------------------------
llama_binaries = collect_dynamic_libs('llama_cpp')  # auto DLL discovery


# -------------------------------------------------------------------
# Llama: manual DLL/lib folder include (fallback)
# -------------------------------------------------------------------
llama_lib_src = os.path.join(llama_pkg_dir, 'lib')
llama_lib_datas = []

if os.path.isdir(llama_lib_src):
    for root, _, files in os.walk(llama_lib_src):
        for fname in files:
            src_path = os.path.join(root, fname)
            rel_dir = os.path.relpath(root, llama_pkg_dir)   # "lib"
            dest_dir = os.path.join('llama_cpp', rel_dir)
            llama_lib_datas.append((src_path, dest_dir))


# -------------------------------------------------------------------
# Llama model folder ("llm_models")
# -------------------------------------------------------------------
models_src = os.path.join(project_dir, 'llm_models')
models_datas = []

if os.path.isdir(models_src):
    for root, _, files in os.walk(models_src):
        for fname in files:
            src_path = os.path.join(root, fname)
            rel_path = os.path.relpath(src_path, project_dir)  # "llm_models/…"
            dest_dir = os.path.dirname(rel_path)
            models_datas.append((src_path, dest_dir))


# -------------------------------------------------------------------
# Whisper: auto collect
# -------------------------------------------------------------------
whisper_datas = collect_data_files('whisper')

# -------------------------------------------------------------------
# Whisper: manual (fallback) 
# -------------------------------------------------------------------
if not whisper_datas:
    whisper_pkg_dir = os.path.dirname(whisper.__file__)
    assets_dir = os.path.join(whisper_pkg_dir, "assets")

    if os.path.isdir(assets_dir):
        for root, _, files in os.walk(assets_dir):
            for fname in files:
                src_path = os.path.join(root, fname)
                rel_dir = os.path.relpath(root, whisper_pkg_dir)  # "assets/"
                dest_dir = os.path.join('whisper', rel_dir)
                whisper_datas.append((src_path, dest_dir))


# -------------------------------------------------------------------
# Combine all datas
# -------------------------------------------------------------------
all_datas = (
    list(collect_data_files('llama_cpp')) +
    llama_lib_datas +
    models_datas +
    whisper_datas
)


# -------------------------------------------------------------------
# Analysis
# -------------------------------------------------------------------
a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=llama_binaries,
    datas=all_datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=['pyinstaller_hooks/add_llama_dll.py'],
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
    debug=True,      # DEV: True for testing 
    strip=False,
    upx=False,
    console=True,    # DEV: True for testing 
)


# -------------------------------------------------------------------
# Final bundle (one-folder)
# -------------------------------------------------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='main'
)
