"""Composition Root - wires everything together."""

from app.infrastructure.web.app import create_app

app = create_app()
