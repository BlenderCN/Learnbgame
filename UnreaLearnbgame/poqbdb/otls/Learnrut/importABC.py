import os 
import hou

r = []
abc_sel = hou.ui.selectFile(title="Alembic Path Floder Select",file_type=hou.fileType.Directory)
abc_dir = hou.expandString(abc_sel)
path = os.path.exists(abc_dir)
if path:
    abc_dir_path = os.listdir(abc_dir)
    abc_null = hou.node('/obj').createNode('null','Alembic_Scale')
    abc_null.setDisplayFlag(False)
    abc_null.setColor(hou.Color((0.094,0.369,0.69)))
    abc_null.parm('scale').set(0.01)
    
    for i in abc_dir_path:
    
        b = os.path.splitext(i)[0].find('CAMERA')
        b2 = os.path.splitext(i)[0].find('Camera')
        b3 = os.path.splitext(i)[0].find('camera')
        abc_type = os.path.splitext(i)[1]
        if abc_type == '.abc':           
            if b != -1 or b2 != -1 or b3 != -1:
                node = hou.node('/obj').createNode('alembicarchive',os.path.splitext(i)[0])
                node.setNextInput(abc_null)
                node.setDisplayFlag(False)
                node.setColor(hou.Color((0.094,0.369,0.69)))
                node.parm('fileName').set(abc_sel + i)
                node.parm('buildHierarchy').pressButton()
                child = node.allSubChildren()
                for chd in child:
                    if chd.type().name() == 'cam':
                        cam_node = chd
                        cam_node.parm('resx').set(1920)
                        cam_node.parm('resy').set(1080)
                        cam_node.parm('near').setExpression('0.01')
                        cam_node.parm('far').setExpression('10000')
                        
            else:
                node = hou.node('/obj').createNode('geo',os.path.splitext(i)[0])
                node.setColor(hou.Color((0.094,0.369,0.69)))
                node.parm('vm_rendervisibility').set('primary')
                geo_node = node.createNode('alembic',os.path.splitext(i)[0])
                geo_node.parm('fileName').set(abc_sel + i)
                geo_node.parm('NURBSFilter').set(0)
                geo_node.parm('curveFilter').set(0)
                node.setNextInput(abc_null)
            
            #print node
            hou.node('/obj').layoutChildren()   
            