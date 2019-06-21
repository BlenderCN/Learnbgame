from os.path import dirname
from pkgutil import iter_modules
from sys import modules
from importlib import reload, import_module


class PackageReloader:
    def __init__(self):
        pass

    @staticmethod
    def reload_module(module):
        print("Reloading module", module.__name__)
        reload(module)

    def reload_packages(self, pkg_list):
        """
        Reloads all pacakges in the list
        :param pkg_list: List of packages
        :return: None
        """
        for pkg in pkg_list:
            if self._type_name(pkg) == "str":
                pkg = import_module(pkg)
            self.reload_package(pkg)

    def reload_package(self, pkg):
        """
        Reloads the package and the modules it contains
        As for now it doesn't got deeper than the first level

        :param pkg: can be a module obj or a module name string
        :return: execptions if the pkg is not loaded or if pkg is not a module. Otherwise None if everything is okay.
        """
        if self._type_name(pkg) == "str":
            pkg = modules[pkg]
        if self._type_name(pkg) != "module":
            raise ValueError("PKG is not a module type")

        for module_loader, name, ispkg in self._get_modules_for_package(pkg):
            module_name = ".".join([pkg.__name__, name])

            module = import_module(module_name)
            self.reload_module(module)

        self.reload_module(pkg)

    def _get_modules_for_package(self, package):
        pkgpath = dirname(package.__file__)
        return [(module_loader, name, ispkg) for module_loader, name, ispkg in iter_modules([pkgpath])]

    def _type_name(self, pkg):
        return type(pkg).__name__