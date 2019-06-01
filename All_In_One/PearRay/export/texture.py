import bpy
import tempfile


def export_image(exporter, image):
    path = ''
    if image.source in {'GENERATED', 'FILE'}:
        if image.source == 'GENERATED':
            path = exporter.create_file(name_hint=image.name)
            image.save_render(path, exporter.scene)
        elif image.source == 'FILE':
            if image.packed_file:
                path = exporter.create_file(name_hint=image.name)
                image.save_render(path, exporter.scene)
            else:
                path = image.filepath

    return bpy.path.resolve_ncase(bpy.path.abspath(path))


def export_texture(exporter, texture):
    if not texture:
        return ''
    
    if texture.name in exporter.instances['TEXTURE']:
        return ''

    name = exporter.register_unique_name('TEXTURE', texture.name)

    img_name = ''
    if texture.type == 'IMAGE':
        img_name = export_image(exporter, texture.image)
    else:
        return ''
    
    exporter.w.write("(texture")
    exporter.w.goIn()

    exporter.w.write(":name '%s'" % name)
    exporter.w.write(":type 'color'")
    exporter.w.write(":file '%s'" % img_name)

    exporter.w.goOut()
    exporter.w.write(")")

    return name
    