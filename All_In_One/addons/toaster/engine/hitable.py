from abc import ABCMeta, abstractmethod


class Hitable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def hit(self, ray, t_min, t_max, hit_record):pass
