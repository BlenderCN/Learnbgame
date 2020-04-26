import functools
import pathlib

from pillarsdk.resource import List, Find, Create


class Manager(List, Find):
    """Manager class wrapping the REST nodes endpoint"""
    path = 'flamenco/managers'
    PurePlatformPath = pathlib.PurePath

    @functools.lru_cache()
    def _sorted_path_replacements(self) -> list:
        import platform

        if self.path_replacement is None:
            return []

        items = self.path_replacement.to_dict().items()

        def by_length(item):
            return -len(item[0]), item[0]

        this_platform = platform.system().lower()
        return [(varname, platform_replacements[this_platform])
                for varname, platform_replacements in sorted(items, key=by_length)
                if this_platform in platform_replacements]

    def replace_path(self, some_path: pathlib.PurePath) -> str:
        """Performs path variable replacement.

        Tries to find platform-specific path prefixes, and replaces them with
        variables.
        """

        for varname, path in self._sorted_path_replacements():
            replacement = self.PurePlatformPath(path)
            try:
                relpath = some_path.relative_to(replacement)
            except ValueError:
                # Not relative to each other, so no replacement possible
                continue

            replacement_root = self.PurePlatformPath('{%s}' % varname)
            return (replacement_root / relpath).as_posix()

        return some_path.as_posix()


class Job(List, Find, Create):
    """Job class wrapping the REST nodes endpoint
    """
    path = 'flamenco/jobs'
    ensure_query_projections = {'project': 1}
