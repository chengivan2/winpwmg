import os

def print_box(title, content_lines):
    """Prints content inside a line-bounded box."""
    width = max(len(line) for line in content_lines + [title]) + 4
    print("+" + "-" * (width - 2) + "+")
    print(f"| {title.center(width - 4)} |")
    print("+" + "-" * (width - 2) + "+")
    for line in content_lines:
        print(f"| {line.ljust(width - 4)} |")
    print("+" + "-" * (width - 2) + "+")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
