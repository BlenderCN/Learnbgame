# Deeva - Character Generation Platform
# Copyright (C) 2018 Fabrizio Nunnari
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from typing import List
from typing import Tuple

import pandas


class AttributesTable:
    """Support class to load and manage attributes.

    Sample table format:
    id,name,type,min,max,labels
    277,Cheeks_Mass,nc,0.2,0.8,N/A
    287,Chin_Prominence,nc,0.0,1.0,N/A
    300,Eyebrows_Angle,nc,0.0,1.0,N/A
    323,Eyes_Size,nc,0.1,1.0,N/A
    """

    def __init__(self, table_filename: str):

        self._table = pandas.read_csv(filepath_or_buffer=table_filename)
        self._table.set_index('id', inplace=True)
        # print(self._table)

    def attributes_count(self) -> int:
        return len(self._table)

    def attribute_ids(self) -> List[int]:
        return [int(i) for i in self._table.index]

    def attribute_names(self) -> List[str]:
        return [s for s in self._table['name']]

    def attribute_name(self, attr_id: int) -> str:
        return self._table.loc[attr_id]['name']

    def attribute_range(self, attr_id: int) -> Tuple[float, float]:
        entry = self._table.loc[attr_id]
        return entry['min'], entry['max']


class IndividualsTable:
    """Support class to load and manage individuals of a generation.

    Sample table format:
    id,creation_type,has_content_files,277,287,300,323
    35,rm,False,0.35,1.0,0.5,0.775
    36,rm,False,0.575,0.75,0.875,0.55
    37,rm,False,0.425,0.75,0.625,0.6625
    """

    FIRST_ATTRIBUTE_INDEX = 2

    def __init__(self, individuals_filename):
        self._table = pandas.read_csv(filepath_or_buffer=individuals_filename)  # type: pandas.DataFrame
        self._table.set_index('id', inplace=True)

    def count(self) -> int:
        return len(self._table)

    def ids(self) -> List[int]:
        return [int(i) for i in self._table.index]

    def attribute_ids(self) -> List[int]:
        return [int(i) for i in self._table.columns.values[IndividualsTable.FIRST_ATTRIBUTE_INDEX:].tolist()]

    def attribute_values(self, individual_id: int) -> List[float]:
        table_line = self._table.loc[individual_id]
        attrib_values = table_line[IndividualsTable.FIRST_ATTRIBUTE_INDEX:]  # self._table.loc[individual_id]
        return [float(a) for a in attrib_values]


#
#
#
# Invoke register if started from editor
if __name__ == "__main__":

    print("Test attrs")

    import os

    from deeva.generation_tools import create_mblab_chars_json_dir

    print(os.getcwd())

    attributes_tab = AttributesTable("../../BlenderScenes/VS-1-testvarset1.csv")

    print(attributes_tab.attributes_count())
    print(attributes_tab.attribute_ids())
    print(attributes_tab.attribute_names())

    for a in attributes_tab.attribute_ids():
        print(attributes_tab.attribute_name(a))
        print(attributes_tab.attribute_range(a))
    print("")

    # create_random_individuals(attributes_table=attributes_tab, num_individuals=30, out_filename="individuals2.csv", random_segments=9)

    indiv_tab = IndividualsTable("../../BlenderScenes/individuals2-fake.csv")
    print(indiv_tab._table)

    create_mblab_chars_json_dir(individuals=indiv_tab, attributes=attributes_tab, dirpath="generated_indiv")

    print("end.")
