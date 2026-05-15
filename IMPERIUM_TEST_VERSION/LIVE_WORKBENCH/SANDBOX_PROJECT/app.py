#!/usr/bin/env python3
"""
app.py - Sample sandbox application for Live Workbench testing.

This is a simple calculator module used to demonstrate the Live Workbench.
"""


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


def divide(a: int, b: int) -> float:
    """Divide a by b. Raises ValueError if b is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def is_even(n: int) -> bool:
    """Check if a number is even."""
    return n % 2 == 0


def factorial(n: int) -> int:
    """Calculate factorial of n. Raises ValueError if n is negative."""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n <= 1:
        return 1
    return n * factorial(n - 1)


if __name__ == "__main__":
    print("Sandbox Calculator App")
    print(f"add(2, 3) = {add(2, 3)}")
    print(f"subtract(5, 2) = {subtract(5, 2)}")
    print(f"multiply(4, 3) = {multiply(4, 3)}")
    print(f"divide(10, 2) = {divide(10, 2)}")
    print(f"is_even(4) = {is_even(4)}")
    print(f"factorial(5) = {factorial(5)}")
