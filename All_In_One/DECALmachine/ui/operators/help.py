import bpy
import os
from ... utils.registration import get_path
from ... utils.system import makedir, open_folder
from ... import bl_info


class GetSupport(bpy.types.Operator):
    bl_idname = "machin3.get_decalmachine_support"
    bl_label = "MACHIN3: Get DECALmachine Support"
    bl_description = "Generate Log Files and Instructions for a Support Request."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        logpath = makedir(os.path.join(get_path(), "logs"))
        resourcespath = makedir(os.path.join(get_path(), "resources"))


        # PIL

        pillog = []

        if not os.path.exists(os.path.join(logpath, "pil.log")):
            pillog.append("'pil.log' not found!")

            try:
                import PIL
                pillog.append("PIL imported successfully")
                pil = True

            except:
                pillog.append("PIL could not be imported")
                pil = False

            if pil:
                try:
                    from PIL import Image
                    pillog.append("PIL's Image module imported successfully")

                except:
                    pillog.append("PIL's Image module could not be imported")


            with open(os.path.join(logpath, "pil.log"), "w") as f:
                f.writelines([l + "\n" for l in pillog])


        # SYSTEM INFO

        sysinfopath = os.path.join(logpath, "system_info.txt")
        bpy.ops.wm.sysinfo(filepath=sysinfopath)

        revision = bl_info.get("revision")
        if revision and os.path.exists(sysinfopath):
            with open(sysinfopath, 'r+') as f:
                content = f.read()
                f.seek(0, 0)
                f.write(revision.rstrip('\r\n') + '\n' + content)

        # README

        with open(os.path.join(resourcespath, "readme.html"), "r") as f:
            html = f.read()

        html = html.replace("VERSION", ".".join((str(v) for v in bl_info['version'])))

        with open(os.path.join(logpath, "README.html"), "w") as f:
            f.write(html)


        # OPEN FOLDER

        open_folder(logpath)

        return {'FINISHED'}
