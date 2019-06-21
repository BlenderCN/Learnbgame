import f3b
import f3b.datas_pb2
import f3b.custom_params_pb2
import f3b.animations_kf_pb2
import f3b.physics_pb2
from . import Relations
from ..F3bContext import *
from ..Utils import *
from .. import Logger as log



def export_rbct(ctx: F3bContext,ob, phy_data, data):
    btct = ob.rigid_body_constraint

    if not btct or not ctx.checkUpdateNeededAndClear(btct):
        return

    if phy_data == None:
        phy_data = data.physics.add()
    ct_type = btct.type
    constraint = phy_data.constraint
    constraint.id = ctx.idOf(btct)

    o1 = btct.object1
    o2 = btct.object2

    o1_wp = o1.matrix_world.to_translation()
    o2_wp = o2.matrix_world.to_translation()

    constraint.a_ref = ctx.idOf(o1.rigid_body)
    constraint.b_ref = ctx.idOf(o2.rigid_body)

    if ct_type == "GENERIC":
        generic = constraint.generic
        cnv_vec3((0, 0, 0), generic.pivotA)
        cnv_vec3(cnv_toVec3ZupToYup(o1_wp-o2_wp), generic.pivotB)
        generic.disable_collisions = btct.disable_collisions

        if btct.use_limit_lin_x:
            limit_lin_x_upper = btct.limit_lin_x_upper
            limit_lin_x_lower = btct.limit_lin_x_lower
        else:
            limit_lin_x_upper = float('inf')
            limit_lin_x_lower = float('-inf')

        if btct.use_limit_lin_y:
            limit_lin_y_upper = btct.limit_lin_y_upper
            limit_lin_y_lower = btct.limit_lin_y_lower
        else:
            limit_lin_y_upper = float('inf')
            limit_lin_y_lower = float('-inf')

        if btct.use_limit_lin_z:
            limit_lin_z_upper = btct.limit_lin_z_upper
            limit_lin_z_lower = btct.limit_lin_z_lower
        else:
            limit_lin_z_upper = float('inf')
            limit_lin_z_lower = float('-inf')

        if btct.use_limit_ang_x:
            limit_ang_x_upper = btct.limit_ang_x_upper
            limit_ang_x_lower = btct.limit_ang_x_lower
        else:
            limit_ang_x_upper = float('inf')
            limit_ang_x_lower = float('-inf')

        if btct.use_limit_ang_y:
            limit_ang_y_upper = btct.limit_ang_y_upper
            limit_ang_y_lower = btct.limit_ang_y_lower
        else:
            limit_ang_y_upper = float('inf')
            limit_ang_y_lower = float('-inf')

        if btct.use_limit_ang_z:
            limit_ang_z_upper = btct.limit_ang_z_upper
            limit_ang_z_lower = btct.limit_ang_z_lower
        else:
            limit_ang_z_upper = float('inf')
            limit_ang_z_lower = float('-inf')

        cnv_vec3(cnv_toVec3ZupToYup((limit_lin_x_upper, limit_lin_y_upper, limit_lin_z_upper)), generic.upperLinearLimit)
        cnv_vec3(cnv_toVec3ZupToYup((limit_lin_x_lower, limit_lin_y_lower, limit_lin_z_lower)), generic.lowerLinearLimit)
        cnv_vec3(cnv_toVec3ZupToYup((limit_ang_x_upper, limit_ang_y_upper, limit_ang_z_upper)), generic.upperAngularLimit)
        cnv_vec3(cnv_toVec3ZupToYup((limit_ang_x_lower, limit_ang_y_lower, limit_ang_z_lower)), generic.lowerAngularLimit)


def export_rb(ctx: F3bContext,ob, phy_data, data):
    if not  ob.rigid_body or not ctx.checkUpdateNeededAndClear(ob.rigid_body):
        return

    if phy_data is None:
        phy_data = data.physics.add()

    rigidbody = phy_data.rigidbody
    rigidbody.id = ctx.idOf(ob.rigid_body)

    rbtype = ob.rigid_body.type
    dynamic = ob.rigid_body.enabled
    if rbtype == "PASSIVE" or not dynamic:
        rigidbody.type = f3b.datas_pb2.RigidBody.tstatic
    else:
        rigidbody.type = f3b.datas_pb2.RigidBody.tdynamic
    # Ghost?

    rigidbody.mass = ob.rigid_body.mass
    rigidbody.isKinematic = ob.rigid_body.kinematic
    rigidbody.friction = ob.rigid_body.friction
    rigidbody.restitution = ob.rigid_body.restitution
    if not ob.rigid_body.use_margin:
        rigidbody.margin = 0
    else:
        rigidbody.margin = ob.rigid_body.collision_margin

    rigidbody.linearDamping = ob.rigid_body.linear_damping
    rigidbody.angularDamping = ob.rigid_body.angular_damping
    cnv_vec3((1, 1, 1), rigidbody.angularFactor) #Not used
    cnv_vec3((1, 1, 1), rigidbody.linearFactor) #Not used

    shape = ob.rigid_body.collision_shape
    if shape == "MESH":
        shape = f3b.datas_pb2.PhysicsData.smesh
    elif shape == "SPHERE":
        shape = f3b.datas_pb2.PhysicsData.ssphere
    elif shape == "CONVEX_HULL":
        shape = f3b.datas_pb2.PhysicsData.shull
    elif shape == "BOX":
        shape = f3b.datas_pb2.PhysicsData.sbox
    elif shape == "CAPSULE":
        shape = f3b.datas_pb2.PhysicsData.scapsule
    elif shape == "CYLINDER":
        shape = f3b.datas_pb2.PhysicsData.scylinder
    elif shape == "CONE":
        shape = f3b.datas_pb2.PhysicsData.scone


    rigidbody.shape = shape

    collision_groups = ob.rigid_body.collision_collections
    collision_group = 0
    i = 0
    for g in collision_groups:
        if g:
            collision_group |= (g<<i)
        i += 1

    rigidbody.collisionGroup = collision_group
    rigidbody.collisionMask = collision_group

    Relations.add(ctx,data,rigidbody.id,ctx.idOf(ob))
    return phy_data


def export(ctx: F3bContext,data: f3b.datas_pb2.Data,scene: bpy.types.Scene):
    for obj in scene.objects:
        if not ctx.isExportable(obj):
            #sprint("Skip ",obj,"not selected/render disabled")
            continue
        phy_data = None
        phy_data = export_rb(ctx,obj, phy_data, data)
        export_rbct(ctx,obj, phy_data, data)