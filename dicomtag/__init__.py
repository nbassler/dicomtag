from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("dicomtag")
except PackageNotFoundError:
    __version__ = "unknown"
