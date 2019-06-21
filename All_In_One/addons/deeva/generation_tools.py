import bpy

from deeva.generation import IndividualsTable, AttributesTable


def export_mblab_attributes(mesh_obj: bpy.types.Object, outfilepath: str) -> None:
    """Export the list of the attributes used by MBLab.
    The attributes are extracted as properties of a non-finalized Mesh object."""

    import inspect
    import csv

    #
    # List attributes
    print("Start gathering attributes...")

    attributes = []

    # Filter for float only attributes
    for attr in inspect.getmembers(mesh_obj, lambda a: isinstance(a, float)):
        attribute_name = attr[0]  # type: str
        # filter for uppercase only attributes
        if attribute_name[0].isupper():
            # print(attr[0])
            if not attribute_name.startswith("Expressions_"):
                attributes.append({'name': attr[0], 'type': 'nc'})  # 'nc' stands for 'numerical continuous'

    print("Found {} attributes.".format(len(attributes)))

    #
    # Write attribute list to a file
    print("Writing csv file '{}'...".format(outfilepath))
    with open(outfilepath, 'w') as csvfile:
        fieldnames = ['name', 'type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for attribute in attributes:
            writer.writerow(attribute)

    print("Finished.")


def create_mblab_chars_json_dir(individuals: IndividualsTable, attributes: AttributesTable, dirpath: str) -> None:
    """Save the list of individuals in a format that can be used by MBLab to load back the character.
    The individuals are saved into the directory specified. The methos saves one JSOn file for each character"""

    import os
    import json

    consistency_check(individuals=individuals, attributes=attributes)

    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    attr_ids = attributes.attribute_ids()

    for individual_id in individuals.ids():
        attr_vals = individuals.attribute_values(individual_id=individual_id)
        if len(attr_ids) != len(attr_vals):
            raise Exception("Number of attribute IDs should be the same of Attribute values. Found {} {}"
                            .format(len(attr_ids), len(attr_vals)))

        attributes_dict = {}
        for attr_id, attr_val in zip(attr_ids, attr_vals):
            attr_name = attributes.attribute_name(attr_id=attr_id)
            attributes_dict[attr_name] = attr_val

        out_dict = {
            "materialproperties": {},
            "metaproperties": {},
            "manuellab_vers": [1, 6, 1],
            "structural": attributes_dict
        }

        with open(os.path.join(dirpath, "{}.json".format(individual_id)), 'w') as outfile:
            json.dump(obj=out_dict, fp=outfile, indent=2)


def consistency_check(individuals: IndividualsTable, attributes: AttributesTable) -> None:
    """Check if the attributes used in the IndividualsTable are consistent
     with the ones reported in the AttributesTable.

     :raises Exception: if the tables are not consistent."""

    attrib_ids_1 = individuals.attribute_ids()
    print(attrib_ids_1)

    attrib_ids_2 = attributes.attribute_ids()
    print(attrib_ids_2)

    if len(attrib_ids_1) != len(attrib_ids_2):
        raise Exception("Number of attribute IDs should be the same. Found {} {}"
                        .format(len(attrib_ids_1), len(attrib_ids_2)))

    attrib_set = set(attrib_ids_1)
    for attr_id in attrib_ids_2:
        if attr_id not in attrib_set:
            raise Exception("Attribute {} from attributes table not found in individuals table".format(attr_id))


