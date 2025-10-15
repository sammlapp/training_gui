#!/usr/bin/env python3
"""Simple test to verify NiceGUI is working"""

from nicegui import ui

ui.label('Hello NiceGUI!').classes('text-h3')
ui.button('Click me', on_click=lambda: ui.notify('Button clicked!'))

ui.run(port=8080, show=False)
