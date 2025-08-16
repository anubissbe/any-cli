"""
Sample Python file for testing LSP integration.

This file contains various Python constructs to test symbol detection,
references, definitions, and other LSP features.
"""

import os
import sys
from typing import List, Dict, Optional


class Person:
    """A simple person class for testing."""

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
        self._private_data = {}

    def get_name(self) -> str:
        """Get the person's name."""
        return self.name

    def set_name(self, name: str) -> None:
        """Set the person's name."""
        self.name = name

    def calculate_birth_year(self, current_year: int = 2024) -> int:
        """Calculate approximate birth year."""
        return current_year - self.age

    @property
    def display_name(self) -> str:
        """Get display name."""
        return f"{self.name} ({self.age} years old)"


def create_person(name: str, age: int) -> Person:
    """Factory function to create a Person."""
    return Person(name, age)


def process_people(people: List[Person]) -> Dict[str, int]:
    """Process a list of people and return name-age mapping."""
    result = {}
    for person in people:
        # Test reference to method
        name = person.get_name()
        result[name] = person.age
    return result


# Test variables and constants
DEFAULT_AGE = 25
people_list: List[Person] = []

# Create some test instances
alice = create_person("Alice", 30)
bob = Person("Bob", 25)

# Test method calls and references
people_list.append(alice)
people_list.append(bob)

# Test function call
age_mapping = process_people(people_list)

# Test property access
for person in people_list:
    print(person.display_name)
    birth_year = person.calculate_birth_year()
    print(f"Born around: {birth_year}")


# Test with some syntax that might cause diagnostics
def function_with_unused_param(param1, param2):
    """Function with unused parameter to test diagnostics."""
    return param1  # param2 is unused


# Missing type annotation (might trigger warning)
def untyped_function(x):
    return x * 2


if __name__ == "__main__":
    # Test module-level code
    print("Testing LSP integration...")
    for name, age in age_mapping.items():
        print(f"{name}: {age} years old")
