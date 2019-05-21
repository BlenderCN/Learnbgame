import os

from lxml import etree

schemaPath = "xml-schema"
schemas = {
  'map'      : 'map.xsd',
  'material' : 'material.xsd',
  'screen'   : 'screen.xsd'
}


def validate(filePath="", type="map"):
  """Validate given file against xsd"""
  if not filePath or not os.path.isfile(filePath):
    print("File '" + filePath + "' does not exist !")
    return False

  if type not in schemas:
    print("Schema '" + type + "' does not exist !")
    return False

  try:
    xsdFile = os.path.join(schemaPath, schemas[type])
    schema = etree.XMLSchema(file=xsdFile)
    xmlparser = etree.XMLParser(schema=schema)

    with open(filePath, 'r') as file:
      etree.fromstring(file.read(), xmlparser)

    return True
  except etree.XMLSchemaError:
    print("File is not valid")
    return False
