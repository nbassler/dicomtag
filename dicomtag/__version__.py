try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # For Python <3.8 compatibility
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("dicomtag")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"  # Fallback for local testing
