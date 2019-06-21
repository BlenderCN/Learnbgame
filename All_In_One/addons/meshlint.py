# TODO:
#  - Exempt mirror-plane verts. You should not get penalized for them.
#  - Check for intersected faces??
#   - Would probably be O(n^m) or something.
#   - Would need to check the post-modified mesh (e.g., Armature-deformed)
#  - Coplanar check, especially good for Ngons.
#  - Check Normal consistency? I've had several people request this, though I
#    still feel like the Ctrl+n tool has problems solving it, so I am
#    unconfident that I will be able to do as good or better. It is true,
#    though, that you can simply allow the user to enable the check, and if it
#    is acting wonky they can disable it.
#  - Consider adding to the 'n' Properties Panel instead of Object Data. Or,
#    perhaps, a user preference.
#  - Maybe add a "Skip to Next" option. So far at least 1 user has reported
#    this. Personally, I think you should hit Tab and deselect the one you
#    want to skip, but I haven't thought it through too far.

bl_info = {
    "name": "MeshLint: Like Spell-checking for your Meshes",
    "author": "rking",
    "version": (1, 0),
    "blender": (2, 6, 5),
    "location": "Object Data properties > MeshLint",
    "description": "Check objects for: Tris / Ngons / Nonmanifoldness / etc",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Modeling/MeshLint",
    "tracker_url": "https://github.com/ryanjosephking/meshlint/issues",
    "category": "Learnbgame",
}

# For the ./mkblenderwiki script
mkblenderwiki_info = {
    "license": "GPL",
    "py_download": "https://raw.github.com/ryanjosephking/meshlint/master/meshlint.py",
    "git_download": "https://github.com/ryanjosephking/meshlint.git",
    "input_img_prefix": "meshlint/raw/master/img/",
    "wiki_img_prefix": "Scripts-Modeling-MeshLint-"}

# Look for the "seeing error text", below. Something is super-fishy, but this
# is the workaround.
try:
    import bpy
    import bmesh
    import time
    import re
    from mathutils import Vector

    SUBPANEL_LABEL = 'MeshLint'
    COMPLAINT_TIMEOUT = 3 # seconds
    ELEM_TYPES = [ 'verts', 'edges', 'faces' ]

    N_A_STR = '(N/A - disabled)'
    TBD_STR = '...'


    def is_edit_mode():
        return 'EDIT_MESH' == bpy.context.mode

    def ensure_edit_mode():
        if not is_edit_mode():
            bpy.ops.object.editmode_toggle()


    def ensure_not_edit_mode():
        if is_edit_mode():
            bpy.ops.object.editmode_toggle()


    def has_active_mesh(context):
        obj = context.active_object
        return obj and 'MESH' == obj.type


    class MeshLintAnalyzer:
        CHECKS = []

        def __init__(self):
            self.obj = bpy.context.active_object
            ensure_edit_mode()
            self.b = bmesh.from_edit_mesh(self.obj.data)
            self.num_problems_found = None

        def find_problems(self):
            analysis = []
            self.num_problems_found = 0
            for lint in MeshLintAnalyzer.CHECKS:
                sym = lint['symbol']
                should_check = getattr(bpy.context.scene, lint['check_prop'])
                if not should_check:
                    lint['count'] = N_A_STR
                    continue
                lint['count'] = 0
                check_method_name = 'check_' + sym
                check_method = getattr(type(self), check_method_name)
                bad = check_method(self)
                report = { 'lint': lint }
                for elemtype in ELEM_TYPES:
                    indices = bad.get(elemtype, [])
                    report[elemtype] = indices
                    lint['count'] += len(indices)
                    self.num_problems_found += len(indices)
                analysis.append(report)
            return analysis

        def found_zero_problems(self):
            return 0 == self.num_problems_found

        @classmethod
        def none_analysis(cls):
            analysis = []
            for lint in cls.CHECKS:
                row = { elemtype: [] for elemtype in ELEM_TYPES }
                row['lint'] = lint
                analysis.append(row)
            return analysis

        CHECKS.append({
            'symbol': 'tris',
            'label': 'Tris',
            'definition': 'A face with 3 edges. Often bad for modeling because it stops edge loops and does not deform well around bent areas. A mesh might look good until you animate, so beware!',
            'default': True
        })
        def check_tris(self):
            bad = { 'faces': [] }
            for f in self.b.faces:
                if 3 == len(f.verts):
                    bad['faces'].append(f.index)
            return bad

        CHECKS.append({
            'symbol': 'ngons',
            'label': 'Ngons',
            'definition': 'A face with >4 edges. Is generally bad in exactly the same ways as Tris',
            'default': True
        })
        def check_ngons(self):
            bad = { 'faces': [] }
            for f in self.b.faces:
                if 4 < len(f.verts):
                    bad['faces'].append(f.index)
            return bad

        CHECKS.append({
            'symbol': 'nonmanifold',
            'label': 'Nonmanifold Elements',
            'definition': 'Simply, shapes that won\'t hold water. More precisely, nonmanifold edges are those that do not have exactly 2 faces attached to them (either more or less). Nonmanifold verts are more complicated -- you can see their definition in BM_vert_is_manifold() in bmesh_queries.c',
            'default': True
        })
        def check_nonmanifold(self):
            bad = {}
            for elemtype in 'verts', 'edges':
                bad[elemtype] = []
                for elem in getattr(self.b, elemtype):
                    if not elem.is_manifold:
                        bad[elemtype].append(elem.index)
            # TODO: Exempt mirror-plane verts.
            # Plus: ...anybody wanna tackle Mirrors with an Object Offset?
            return bad

        CHECKS.append({
            'symbol': 'interior_faces',
            'label': 'Interior Faces',
            'definition': 'This confuses people. It is very specific: A face whose edges ALL have >2 faces attached. The simplest way to see this is to Ctrl+r a Default Cube and hit \'f\'',
            'default': True
        })
        def check_interior_faces(self): # translated from editmesh_select.c
            bad = { 'faces': [] }
            for f in self.b.faces:
                if not any(3 > len(e.link_faces) for e in f.edges):
                    bad['faces'].append(f.index)
            return bad

        CHECKS.append({
            'symbol': 'sixplus_poles',
            'label': '6+-edge Poles',
            'definition': 'A vertex with 6 or more edges connected to it. Generally this is not something you want, but since some kinds of extrusions will legitimately cause such a pole (imagine extruding each face of a Cube outward, the inner corners are rightful 6+-poles). Still, if you don\'t know for sure that you want them, it is good to enable this',
            'default': False
        })
        def check_sixplus_poles(self):
            bad = { 'verts': [] }
            for v in self.b.verts:
                if 5 < len(v.link_edges):
                    bad['verts'].append(v.index)
            return bad

        # [Your great new idea here] -> Tell me about it: rking@panoptic.com

        # ...plus the 'Default Name' check.

        def enable_anything_select_mode(self):
            self.b.select_mode = {'VERT', 'EDGE', 'FACE'}

        def select_indices(self, elemtype, indices):
            for i in indices:
                if 'verts' == elemtype:
                    self.select_vert(i)
                elif 'edges' == elemtype:
                    self.select_edge(i)
                elif 'faces' == elemtype:
                    self.select_face(i)
                else:
                    print("MeshLint says: Huh?? → elemtype of %s." % elemtype)
        
        def select_vert(self, index):
            self.b.verts[index].select = True

        def select_edge(self, index):
            edge = self.b.edges[index]
            edge.select = True
            for each in edge.verts:
                self.select_vert(each.index)

        def select_face(self, index):
            face = self.b.faces[index]
            face.select = True
            for each in face.edges:
                self.select_edge(each.index)

        def topology_counts(self):
            data = self.obj.data
            return {
                'data': self.obj.data,
                'faces': len(self.b.faces),
                'edges': len(self.b.edges),
                'verts': len(self.b.verts) }

        for lint in CHECKS:
            sym = lint['symbol']
            lint['count'] = TBD_STR
            prop = 'meshlint_check_' + sym
            lint['check_prop'] = prop
            'meshlint_check_' + sym
            setattr(
                bpy.types.Scene,
                prop,
                bpy.props.BoolProperty(
                    default=lint['default'],
                    description=lint['definition']))


    @bpy.app.handlers.persistent
    def global_repeated_check(dummy):
        MeshLintContinuousChecker.check()


    class MeshLintContinuousChecker():
        current_message = ''
        time_complained = 0
        previous_topology_counts = None
        previous_analysis = None

        @classmethod
        def check(cls):
            if not is_edit_mode():
                return
            analyzer = MeshLintAnalyzer()
            now_counts = analyzer.topology_counts()
            previous_topology_counts = \
                cls.previous_topology_counts
            if not None is previous_topology_counts:
                previous_data_name = previous_topology_counts['data'].name
            else:
                previous_data_name = None
            now_name = now_counts['data'].name
            if None is previous_topology_counts \
                    or now_counts != previous_topology_counts:
                if not previous_data_name == now_name:
                    before = MeshLintAnalyzer.none_analysis()
                analysis = analyzer.find_problems()
                diff_msg = cls.diff_analyses(
                    cls.previous_analysis, analysis)
                if not None is diff_msg:
                    cls.announce(diff_msg)
                    cls.time_complained = time.time()
                cls.previous_topology_counts = now_counts
                cls.previous_analysis = analysis
            if not None is cls.time_complained \
                    and COMPLAINT_TIMEOUT < time.time() - cls.time_complained:
                cls.announce(None)
                cls.time_complained = None

        @classmethod
        def diff_analyses(cls, before, after):
            if None is before:
                before = MeshLintAnalyzer.none_analysis()
            report_strings = []
            dict_before = cls.make_labels_dict(before)
            dict_now = cls.make_labels_dict(after)
            for check in MeshLintAnalyzer.CHECKS:
                check_name = check['label']
                if not check_name in dict_now.keys():
                    continue
                report = dict_now[check_name]
                report_before = dict_before.get(check_name, {})
                check_elem_strings = []
                for elemtype, elem_list in report.items():
                    elem_list_before = report_before.get(elemtype, [])
                    if len(elem_list) > len(elem_list_before):
                        count_diff = len(elem_list) - len(elem_list_before)
                        elem_string = depluralize(
                            count=count_diff, string=elemtype)
                        check_elem_strings.append(
                            str(count_diff) + ' ' + elem_string)
                if len(check_elem_strings):
                    report_strings.append(
                        check_name + ': ' + ', '.join(check_elem_strings))
            if len(report_strings):
                return 'Found ' + ', '.join(report_strings)
            return None

        @classmethod
        def make_labels_dict(cls, analysis):
            if None is analysis:
                return {}
            labels_dict = {}
            for check in analysis:
                label = check['lint']['label']
                new_val = check.copy()
                del new_val['lint']
                labels_dict[label] = new_val
            return labels_dict

        @classmethod
        def announce(cls, message):
            for area in bpy.context.screen.areas:
                if 'INFO' != area.type:
                    continue
                if None is message:
                    area.header_text_set()
                else:
                    area.header_text_set('MeshLint: ' + message)


    class MeshLintVitalizer(bpy.types.Operator):
        'Toggles the real-time execution of the checks (Edit Mode only)'
        bl_idname = 'meshlint.live_toggle'
        bl_label = 'MeshLint Live Toggle'

        is_live = False

        @classmethod
        def poll(cls, context):
            return has_active_mesh(context) and is_edit_mode()

        def execute(self, context):
            if MeshLintVitalizer.is_live:
                bpy.app.handlers.scene_update_post.remove(global_repeated_check)
                MeshLintVitalizer.is_live = False
            else:
                bpy.app.handlers.scene_update_post.append(global_repeated_check)
                MeshLintVitalizer.is_live = True
            return {'FINISHED'}


    def activate(obj):
        bpy.context.scene.objects.active = obj


    class MeshLintObjectLooper:
        def examine_active_object(self):
            analyzer = MeshLintAnalyzer()
            analyzer.enable_anything_select_mode()
            self.select_none()
            analysis = analyzer.find_problems()
            for lint in analysis:
                for elemtype in ELEM_TYPES:
                    indices = lint[elemtype]
                    analyzer.select_indices(elemtype, indices)
            return analyzer.found_zero_problems()

        def examine_all_selected_meshes(self):
            self.original_active = bpy.context.active_object
            self.troubled_meshes = []
            examinees = [self.original_active] + bpy.context.selected_objects
            for obj in examinees:
                if 'MESH' != obj.type:
                    continue
                activate(obj)
                good = self.examine_active_object()
                ensure_not_edit_mode()
                if not good:
                    self.troubled_meshes.append(obj)
            priorities = [self.original_active] + self.troubled_meshes
            for obj in priorities:
                if obj.select:
                    activate(obj)
                    break
            self.handle_troubled_meshes()
            bpy.context.area.tag_redraw()

        def select_none(self):
            bpy.ops.mesh.select_all(action='DESELECT')

    class MeshLintSelector(MeshLintObjectLooper, bpy.types.Operator):
        'Uncheck boxes below to prevent those checks from running'
        bl_idname = 'meshlint.select'
        bl_label = 'MeshLint Select'
        bl_options = {'REGISTER', 'UNDO'}

        @classmethod
        def poll(cls, context):
            return has_active_mesh(context)

        def execute(self, context):
            original_mode = bpy.context.mode
            if is_edit_mode():
                self.examine_active_object()
            else:
                self.examine_all_selected_meshes()
                if len(self.troubled_meshes):
                    ensure_edit_mode()
                elif 'EDIT_MESH' != original_mode:
                    ensure_not_edit_mode()
            return {'FINISHED'}
        
        def handle_troubled_meshes(self):
            pass

    class MeshLintObjectDeselector(MeshLintObjectLooper, bpy.types.Operator):
        'Uncheck boxes below to prevent those checks from running (Object Mode only)'
        bl_idname = 'meshlint.objects_deselect'
        bl_label = 'MeshLint Objects Deselect'
        bl_options = {'REGISTER', 'UNDO'}

        @classmethod
        def poll(cls, context):
            selected_meshses = [
                o for o in bpy.context.selected_objects if o.type == 'MESH']
            return 1 < len(selected_meshses) and not is_edit_mode()

        def execute(self, context):
            self.examine_all_selected_meshes()
            return {'FINISHED'}

        def handle_troubled_meshes(self):
            for obj in bpy.context.selected_objects:
                if not obj in self.troubled_meshes:
                    obj.select = False

    class MeshLintControl(bpy.types.Panel):
        bl_space_type = 'PROPERTIES'
        bl_region_type = 'WINDOW'
        bl_context = 'data'
        bl_label = SUBPANEL_LABEL

        @classmethod
        def poll(cls, context):
            return has_active_mesh(context)

        def draw(self, context):
            layout = self.layout
            self.add_main_buttons(layout)
            self.add_criticism(layout, context)
            self.add_toggle_buttons(layout, context)

        def add_main_buttons(self, layout):
            split = layout.split()
            left = split.column()
            left.operator(
                'meshlint.select', text='Select Lint', icon='EDITMODE_HLT')

            right = split.column()
            if MeshLintVitalizer.is_live:
                live_label = 'Pause Checking...'
                play_pause = 'PAUSE'
            else:
                live_label = 'Continuous Check!'
                play_pause = 'PLAY'
            right.operator(
                'meshlint.live_toggle', text=live_label, icon=play_pause)
            
            layout.split().operator(
                'meshlint.objects_deselect',
                text='Deselect all Lint-free Objects',
                icon='UV_ISLANDSEL')

        def add_criticism(self, layout, context):
            col = layout.column()
            active = context.active_object
            if not has_active_mesh(context):
                return
            total_problems = 0
            for lint in MeshLintAnalyzer.CHECKS:
                count = lint['count']
                if count in (TBD_STR, N_A_STR):
                    label = str(count) + ' ' + lint['label']
                    reward = 'SOLO_OFF'
                elif 0 == count:
                    label = 'No %s!' % lint['label']
                    reward = 'SOLO_ON'
                else:
                    total_problems += count
                    label = str(count) + 'x ' + lint['label']
                    label = depluralize(count=count, string=label)
                    reward = 'ERROR'
                col.row().label(text=label, icon=reward)
            name_crits = MeshLintControl.build_object_criticisms(
                            bpy.context.selected_objects, total_problems)
            for crit in name_crits:
                col.row().label(crit)

        def add_toggle_buttons(self, layout, context):
            col = layout.column()
            col.row().label('Toggle:')
            for lint in MeshLintAnalyzer.CHECKS:
                prop_name = lint['check_prop']
                is_enabled = getattr(context.scene, prop_name)
                label = 'Check ' + lint['label']
                col.row().prop(context.scene, prop_name, text=label)

        @classmethod
        def build_object_criticisms(cls, objects, total_problems):
            already_complained = total_problems > 0
            criticisms = []
            def add_crit(crit):
                if already_complained:
                    conjunction = 'and also'
                else:
                    conjunction = 'but'
                criticisms.append('...%s "%s" %s.' % (
                    conjunction, obj.name, crit))
            for obj in objects:
                if MeshLintControl.has_unapplied_scale(obj.scale):
                    add_crit('has an unapplied scale')
                    already_complained = True
                if MeshLintControl.is_bad_name(obj.name):
                    add_crit('is not a great name')
                    already_complained = True
            return criticisms

        @classmethod
        def has_unapplied_scale(cls, scale):
            return 3 != len([c for c in scale if c == 1.0])

        @classmethod
        def is_bad_name(cls, name):
            default_names = [
                'BezierCircle',
                'BezierCurve',
                'Circle',
                'Cone',
                'Cube',
                'CurvePath',
                'Cylinder',
                'Grid',
                'Icosphere',
                'Mball',
                'Monkey',
                'NurbsCircle',
                'NurbsCurve',
                'NurbsPath',
                'Plane',
                'Sphere',
                'Surface',
                'SurfCircle',
                'SurfCurve',
                'SurfCylinder',
                'SurfPatch',
                'SurfSphere',
                'SurfTorus',
                'Text',
                'Torus',
            ]
            pat = '(%s)\.?\d*$' % '|'.join(default_names)
            return not None is re.match(pat, name)


    def depluralize(**args):
        if 1 == args['count']:
            return args['string'].rstrip('s')
        else:
            return args['string']


    # Hrm. Why does it work for some Blender's but not others?
    try:
        import unittest
        import warnings

        class TestControl(unittest.TestCase):
            def test_scale_application(self):
                for bad in [ [0,0,0], [1,2,3], [1,1,1.1] ]:
                    self.assertEqual(
                        True, MeshLintControl.has_unapplied_scale(bad),
                        "Unapplied scale: %s" % bad)
                self.assertEqual(
                    False, MeshLintControl.has_unapplied_scale([1,1,1]),
                    "Applied scale (1,1,1)")

            def test_bad_names(self):
                for bad in [ 'Cube', 'Cube.001', 'Sphere.123' ]:
                    self.assertEqual(
                        True, MeshLintControl.is_bad_name(bad),
                        "Bad name: %s" % bad)
                for ok in [ 'Whatever', 'NumbersOkToo.001' ]:
                    self.assertEqual(
                        False, MeshLintControl.is_bad_name(ok),
                        "OK name: %s" % ok)


        class TestUtilities(unittest.TestCase):
            def test_depluralize(self):
                self.assertEqual(
                    'foo',
                    depluralize(count=1, string='foos'))
                self.assertEqual(
                    'foos',
                    depluralize(count=2, string='foos'))


        class TestAnalysis(unittest.TestCase):
            def test_make_labels_dict(self):
                self.assertEqual(
                    {
                        'Label One': {
                            'edges': [1,2], 'verts': [], 'faces': [] },
                        'Label Two': {
                            'edges': [], 'verts': [5], 'faces': [3] }
                    },
                    MeshLintContinuousChecker.make_labels_dict(
                        [
                            { 'lint': { 'label': 'Label One' },
                                'edges': [1,2], 'verts': [], 'faces': [] },
                            { 'lint': { 'label': 'Label Two' },
                                'edges': [], 'verts': [5], 'faces': [3] }
                        ]),
                    'Conversion of incoming analysis into label-keyed dict')
                self.assertEqual(
                    {},
                    MeshLintContinuousChecker.make_labels_dict(None),
                    'Handles "None" OK.')

            def test_comparison(self):
                self.assertEqual(
                    None,
                    MeshLintContinuousChecker.diff_analyses(
                        MeshLintAnalyzer.none_analysis(),
                        MeshLintAnalyzer.none_analysis()),
                    'Two none_analysis()s')
                self.assertEqual(
                    'Found Tris: 4 verts',
                    MeshLintContinuousChecker.diff_analyses(
                        None,
                        [
                            {
                                'lint': { 'label': 'Tris' },
                                'verts': [1,2,3,4],
                                'edges': [],
                                'faces': [],
                            },
                        ]),
                    'When there was no previous analysis')
                self.assertEqual(
                    'Found Tris: 2 edges, ' +\
                        'Nonmanifold Elements: 4 verts, 1 face',
                    MeshLintContinuousChecker.diff_analyses(
                        [
                            { 'lint': { 'label': 'Tris' },
                              'verts': [], 'edges': [1,4], 'faces': [], },
                            { 'lint': { 'label': 'CheckB' },
                              'verts': [], 'edges': [2,3], 'faces': [], },
                            { 'lint': { 'label': 'Nonmanifold Elements' },
                              'verts': [], 'edges': [], 'faces': [2,3], },
                        ],
                        [
                            { 'lint': { 'label': 'Tris' },
                              'verts': [], 'edges': [1,4,5,6], 'faces': [], },
                            { 'lint': { 'label': 'CheckB' },
                              'verts': [], 'edges': [2,3], 'faces': [], },
                            { 'lint': { 'label': 'Nonmanifold Elements' },
                              'verts': [1,2,3,4], 'edges': [],
                                'faces': [2,3,5], },
                        ]),
                    'Complex comparison of analyses')
                self.assertEqual(
                    'Found Tris: 1 vert, Ngons: 2 faces, ' +
                      'Nonmanifold Elements: 2 edges',
                    MeshLintContinuousChecker.diff_analyses(
                        [
                            { 'lint': { 'label': '6+-edge Poles' },
                              'verts': [], 'edges': [2,3], 'faces': [], },
                            { 'lint': { 'label': 'Nonmanifold Elements' },
                              'verts': [], 'edges': [2,3], 'faces': [], },
                        ],
                        [
                            { 'lint': { 'label': 'Tris' },
                              'verts': [55], 'edges': [], 'faces': [], },
                            { 'lint': { 'label': 'Ngons' },
                              'verts': [], 'edges': [], 'faces': [5,6], },
                            { 'lint': { 'label': 'Nonmanifold Elements' },
                              'verts': [], 'edges': [2,3,4,5], 'faces': [], },
                        ]),
                    'User picked a different set of checks since last run.')


        class MockBlenderObject:
            def __init__(self, name, scale=Vector([1,1,1])):
                self.name = name
                self.scale = scale


        class TestUI(unittest.TestCase):
            def test_complaints(self):
                f = MeshLintControl.build_object_criticisms
                self.assertEqual([], f([], 0), 'Nothing selected')
                self.assertEqual(
                    [],
                    f([MockBlenderObject('lsmft')], 0),
                    'Ok name')
                self.assertEqual(
                    ['...but "Cube" is not a great name.'],
                    f([MockBlenderObject('Cube')], 0),
                    'Bad name, otherwise problem-free.')
                self.assertEqual(
                    [],
                    f([MockBlenderObject('Hassenfrass')], 12),
                    'Good name, but with problems.')
                self.assertEqual(
                    ['...and also "Cube" is not a great name.'],
                    f([MockBlenderObject('Cube')], 23),
                    'Bad name, and problems, too.')
                self.assertEqual(
                    [
                        '...but "Sphere" is not a great name.',
                        '...and also "Cube" is not a great name.'
                    ],
                    f([
                        MockBlenderObject('Sphere'),
                        MockBlenderObject('Cube') ], 0),
                    'Two bad names.')

                scaled = MockBlenderObject('Solartech', scale=Vector([.2,2,1]))
                self.assertEqual(
                    [ '...but "Solartech" has an unapplied scale.' ],
                    f([scaled], 0),
                    'Only problem is unapplied scale.'
                )

        class QuietOnSuccessTestResult(unittest.TextTestResult):
            def startTest(self, test):
                pass

            def addSuccess(self, test):
                pass


        class QuietTestRunner(unittest.TextTestRunner):
            resultclass = QuietOnSuccessTestResult

            # Ugh. I really shouldn't have to include this much code, but they
            # left it so unrefactored I don't know what else to do. My other
            # option is to override the stream and substitute out the success
            # case, but that's a mess, too. - rking
            def run(self, test):
                "Run the given test case or test suite."
                result = self._makeResult()
                unittest.registerResult(result)
                result.failfast = self.failfast
                result.buffer = self.buffer
                with warnings.catch_warnings():
                    if self.warnings:
                        # if self.warnings is set, use it to filter all the
                        # warnings
                        warnings.simplefilter(self.warnings)
                        # if the filter is 'default' or 'always', special-case
                        # the warnings from the deprecated unittest methods to
                        # show them no more than once per module, because they
                        # can be fairly noisy.  The -Wd and -Wa flags can be
                        # used to bypass this only when self.warnings is None.
                        if self.warnings in ['default', 'always']:
                            warnings.filterwarnings('module',
                                    category=DeprecationWarning,
                                    message='Please use assert\w+ instead.')
                    startTime = time.time()
                    startTestRun = getattr(result, 'startTestRun', None)
                    if startTestRun is not None:
                        startTestRun()
                    try:
                        test(result)
                    finally:
                        stopTestRun = getattr(result, 'stopTestRun', None)
                        if stopTestRun is not None:
                            stopTestRun()
                    stopTime = time.time()
                timeTaken = stopTime - startTime
                result.printErrors()
                run = result.testsRun

                expectedFails = unexpectedSuccesses = skipped = 0
                try:
                    results = map(len, (result.expectedFailures,
                                        result.unexpectedSuccesses,
                                        result.skipped))
                except AttributeError:
                    pass
                else:
                    expectedFails, unexpectedSuccesses, skipped = results

                infos = []
                if not result.wasSuccessful():
                    self.stream.write("FAILED")
                    failed, errored = len(result.failures), len(result.errors)
                    if failed:
                        infos.append("failures=%d" % failed)
                    if errored:
                        infos.append("errors=%d" % errored)
                if skipped:
                    infos.append("skipped=%d" % skipped)
                if expectedFails:
                    infos.append("expected failures=%d" % expectedFails)
                if unexpectedSuccesses:
                    infos.append(
                        "unexpected successes=%d" % unexpectedSuccesses)
                return result

        if __name__ == '__main__':
            unittest.main(
                testRunner=QuietTestRunner,
                argv=['dummy'],
                exit=False,
                verbosity=0)

    except ImportError:
        print(
            "MeshLint complains over missing unittest module.", """
            No harm, but it is odd. If you want to send a message to
            rking@panoptic.com describing your system, he'd like to track down
            this condition.""")


    def register():
        bpy.utils.register_module(__name__)


    def unregister():
        bpy.utils.unregister_module(__name__)


    if __name__ == '__main__':
        register()

except:
    # OK, I totally don't get why this is necessary. But otherwise I am not
    # seeing error text. Causes the extra indent over all above code. =(
    import sys
    exc = sys.exc_info()
    print("MeshLint Oops: ", exc[1], exc[2])

# vim:ts=4 sw=4 sts=4
