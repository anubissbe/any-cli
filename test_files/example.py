"""Example Python file for testing LSP functionality."""


class ExampleClass:
    """Example class with methods and attributes."""

    def __init__(self, name: str):
        """Initialize the example class."""
        self.name = name
        self.count = 0

    def greet(self) -> str:
        """Return a greeting message."""
        return f"Hello, {self.name}!"

    def increment(self) -> None:
        """Increment the counter."""
        self.count += 1


def example_function(x: int, y: int) -> int:
    """Example function that adds two numbers."""
    return x + y


# Global variable
GLOBAL_CONFIG = {"debug": True, "version": "1.0.0"}
