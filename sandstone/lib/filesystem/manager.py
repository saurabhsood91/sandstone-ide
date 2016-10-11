import os
from sandstone import settings



def format_volume_paths():
    volume_patterns = settings.FILESYSTEM_ROOT_DIRECTORIES
    formatted_patterns = []
    for patt in volume_patterns:
        fmt = os.path.expandvars(patt)
        formatted_patterns.append(fmt)
    return formatted_patterns

class VolumeManager:
    """
    This is the manager for volumes configured in Sandstone settings.
    The VolumeManager offers filesystem agnostic utilities for loading,
    requesting, and managing volumes.
    """

    volumes = format_volume_paths()

    @classmethod
    def get_volume_paths(cls):
        return cls.volumes

    @classmethod
    def get_volume_from_path(cls, filepath):
        filepath = os.path.abspath(filepath)
        matches = []
        for volume in cls.volumes:
            if filepath.startswith(volume):
                matches.append(volume)
        if matches:
            # return longest match
            matches.sort()
            return matches[-1]
        return None
