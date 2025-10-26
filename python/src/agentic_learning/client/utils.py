def memory_placeholder(label: str) -> str:
    """
    Generate a memory placeholder string for a given label.

    Args:
        label (str): Label of the memory block to generate placeholder string for

    Returns:
        (str): Memory placeholder string
    """
    return f"This is my section of core memory devoted to information about the {label}. " \
           "I don't yet know anything about them. " \
           "I should update this memory over time as I interact with the human " \
           f"and learn more about {label if label != 'human' else 'them'}."
