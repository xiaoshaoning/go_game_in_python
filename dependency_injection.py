#!/usr/bin/env python3
"""
Dependency Injection Container for Go Game

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import Dict, Any, Callable, Type, Optional


class DependencyContainer:
    """Simple dependency injection container."""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}

    def register_service(self, name: str, service: Any):
        """Register a service instance."""
        self._services[name] = service

    def register_factory(self, name: str, factory: Callable):
        """Register a factory function."""
        self._factories[name] = factory

    def register_singleton(self, name: str, factory: Callable):
        """Register a singleton factory."""
        self._factories[name] = factory
        # Singleton will be created on first access

    def get(self, name: str) -> Any:
        """Get a service by name."""
        if name in self._services:
            return self._services[name]

        if name in self._factories:
            if name in self._singletons:
                return self._singletons[name]

            service = self._factories[name](self)
            # Check if it's a singleton
            if name in self._factories:
                self._singletons[name] = service
            return service

        raise KeyError(f"Service '{name}' not found")

    def has(self, name: str) -> bool:
        """Check if a service is registered."""
        return name in self._services or name in self._factories


class ServiceProvider:
    """Service provider for dependency injection."""

    _container: Optional[DependencyContainer] = None

    @classmethod
    def set_container(cls, container: DependencyContainer):
        """Set the global container."""
        cls._container = container

    @classmethod
    def get_service(cls, name: str) -> Any:
        """Get a service from the container."""
        if cls._container is None:
            raise RuntimeError("Dependency container not initialized")
        return cls._container.get(name)

    @classmethod
    def has_service(cls, name: str) -> bool:
        """Check if a service is available."""
        if cls._container is None:
            return False
        return cls._container.has(name)