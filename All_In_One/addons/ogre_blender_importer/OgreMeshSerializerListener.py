from abc import ABCMeta

class OgreMeshSerializerListener(metaclass=ABCMeta):
    """
    This class allows users to hook into the mesh loading process and
        modify references within the mesh as they are loading. Material and
        skeletal references can be processed using this interface which allows
        finer control over resources.
    """
    @abstractmethod
    def processMaterialName(self, mesh, name):
        raise NotImplementedError;

    @abstractmethod
    def processSkeletonName(self,mesh,name):
        raise NotImplementedError;

    @abstractmethod
    def processMeshCompleted(self, mesh):
        raise NotImplementedError;
