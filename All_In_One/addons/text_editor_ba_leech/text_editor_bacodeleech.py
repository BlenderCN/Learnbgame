"""
BEGIN GPL LICENSE BLOCK

(c) Dealga McArdle 2012 / blenderscripting.blogspot / digitalaphasia.com

This program is free software; you may redistribute it, and/or
modify it, under the terms of the GNU General Public License
as published by the Free Software Foundation - either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, write to:

  the Free Software Foundation Inc.
  51 Franklin Street, Fifth Floor
  Boston, MA 02110-1301, USA

or go online at: http://www.gnu.org/licenses/ to view license options.

END GPL LICENCE BLOCK
"""

import bpy


def unescape(s):
    print(repr(s))
    s = s.replace("&gt;", ">")
    s = s.replace("&lt;", "<")
    s = s.replace("&quot;", '\"')
    s = s.replace('\r\n', '\n')
    return s



def get_snippets(x, post_number):
    import re

    # get post
    post_re_left = "post_message_{}".format(post_number)
    post_pattern = post_re_left + '(.*?)<!-- <\/div> -->'
    post_RE = re.compile(post_pattern, re.S)
    post_matched = post_RE.findall(x)[0]

    # get code snippet(s)
    snippet_pattern = "<pre class=\"bbcode_code.*?>(.*?)<\/pre>"
    snippet_RE = re.compile(snippet_pattern, re.S)
    snippets_matched = snippet_RE.findall(post_matched)

    email_protector = "<a id=\"__cf_email__\"(.*?)<\/script>"

    big_string = ""
    for idx, snip in enumerate(snippets_matched):
        # remove CDATA scripts, respect email protection
        big_string += '# ----- snippet {} ----\n'.format(idx)
        snip = re.sub(email_protector, "email protected\n", snip, flags=re.S)
        big_string += snip
        big_string += "\n\n"

    # they arrive butchered by html escape, reverse escape!
    return unescape(big_string)

def get_x_and_post_number(link_to_post):
    from urllib.request import urlopen

    p = urlopen(link_to_post)
    x = p.read().decode()
    post_number = link_to_post.rsplit("#post", 1)[1]

    return x, post_number



class BASnippetOperator(bpy.types.Operator):
    bl_idname = "scene.download_codesnippet"
    bl_label = "Uses post link to populate new Text with code"

    def execute(self, context):
        link_to_post = context.scene.ba_post_id
        soft_data = get_x_and_post_number(link_to_post)
        text_data = get_snippets(*soft_data)


        text_name = soft_data[1]
        bpy.data.texts.new(text_name)
        bpy.data.texts[text_name].write(text_data)
        return{'FINISHED'}


class BACodeSnippets(bpy.types.Panel):
    bl_label = "BA Code Snippets"
    bl_idname = "OBJECT_PT_codesnipper"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        scn = context.scene
        layout.prop(scn, "ba_post_id")
        layout.operator("scene.download_codesnippet", text='Download to Text')


