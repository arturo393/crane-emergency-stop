#!/usr/bin/env python3
"""
Script de lanzamiento rápido para Desktop GUI
"""
import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.web_ui.desktop_gui import main

if __name__ == "__main__":
    main()
