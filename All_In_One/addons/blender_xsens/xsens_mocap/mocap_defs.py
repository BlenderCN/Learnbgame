

class Subject(object):
  def __init__(self):
    self._observers = []

  ##attach a new Observer
  def attach(self, observer):
    if not observer in self._observers:
      self._observers.append(observer)

  ##detach an Observer
  def detach(self, observer):
    try:
      self._observers.remove(observer)
    except ValueError:
      pass

  #notify all observers
  def notify(self, modifier=None):
    for observer in self._observers:
      if modifier != observer:
        observer.update(self)


    
