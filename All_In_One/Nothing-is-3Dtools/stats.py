import bpy
from . import selection_sets
"""todo for optimisation:
        first run:
            custom property for each objects containing stats data
        then updating each time user get back from edit mode:
            update only custom stats from object just edited
"""


def calculate_mesh_stats():
    # thanks to sambler for some piece of code https://github.com/sambler/addonsByMe/blob/master/mesh_summary.py

    totalTriInSelection = 0
    totalVertsInSelection = 0
    meshesStats = []
    totalStats = 0

    # test only selected meshes
    selectedMeshes = selection_sets.meshes_in_selection()

    for element in selectedMeshes:
        triCount = 0
        hasNGon = False
        for poly in element.data.polygons:
            # first check if quad
            if len(poly.vertices) == 4:
                triCount += 2
            # or tri
            elif len(poly.vertices) == 3:
                triCount += 1
            # or oops, ngon here, alert!
            else:
                triCount += 3
                hasNGon = True
        # adding element stats to total count
        totalTriInSelection += triCount
        totalVertsInSelection += len(element.data.vertices)
        # generate table
        currentMeshStats = [element.name, len(
            element.data.vertices), triCount, hasNGon]
        meshesStats.append(currentMeshStats)
        totalStats = [totalVertsInSelection, totalTriInSelection]
    return meshesStats, totalStats


if __name__ == "__main__":
    calculate_mesh_stats()
