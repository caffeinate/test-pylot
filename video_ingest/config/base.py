
class BaseConfig:
    """
    Defaults and doc. detailing requirements for values set by subclasses.
    """
    source_path = None  # must be set by subclass. (str) filesystem directory
    destination_path = None  # must be set by subclass. (str) filesystem directory
