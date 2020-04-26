import imp, importlib

# Provides an easy interface to import an unloaded module, or reload it if it has been previously imported
# Always local, i.e. from . import X
class Importer:
    def __init__( self, locals ):
        self.locals = locals
    
    # Imports the given module, or reloads it if it has been previously imported
    def loadOrReload( self, moduleName ):
        if not self.loadOnce( moduleName):
            print( "Reloading module {}".format( moduleName ) )
            imp.reload( self.locals[ moduleName ] )
    
    # Imports the given module only if it hasn't been imported yet
    def loadOnce( self, moduleName ):
        if moduleName not in self.locals:
            print( "Loading module {}".format( moduleName ) )
            #self.locals[ moduleName ] = importlib.import_module( moduleName )
            self.locals[ moduleName ] = __import__( moduleName, fromlist=[ "." ] )
            return True
        else:
            return False
