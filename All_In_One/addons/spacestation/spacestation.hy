; Generate procedural space stations

(import bpy)
(import math)
(import random)
(import [numpy :as np])

;;;;; Random number helpers

(defn rng_int [seed salt x] (do (random.seed (% (+ seed salt) 1024))
                      (random.randint 0 x)))

(defn rng_float [seed salt a b] (do (random.seed (% (+ seed salt) 1024))
                                    (random.uniform a b)))

;;;;; Mesh generators and blender helpers

(def obj_prefix "SpaceStation_")

(defn clear_scene [] (do (bpy.ops.object.select_all :action "DESELECT")
                         (for [o bpy.context.scene.objects]
                               (if (o.name.startswith "SpaceStation")
                                   (setv o.select true)))
                         (bpy.ops.object.delete :use_global false)))

(defn join_objects [] (do (bpy.ops.object.select_all :action "DESELECT")
                          ; Select all station parts
                          (for [o bpy.context.scene.objects]
                               (if (o.name.startswith obj_prefix)
                                   (setv o.select true)))
                          ; Activate Beam
                          (setv bpy.context.scene.objects.active (get bpy.context.scene.objects "SpaceStation_Beam"))
                          (bpy.ops.object.join)
                          (setv bpy.context.object.name "SpaceStation")))

(defn set_material [] (do (bpy.ops.object.editmode_toggle)
                          (bpy.ops.mesh.select_all :action "SELECT")
                          (bpy.ops.uv.smart_project)  ; Add a uv map
                          (bpy.ops.object.editmode_toggle)
                          (bpy.ops.object.material_slot_add)  ; Add a slot for the material
                          (setv (. (get bpy.context.object.material_slots 0) material) (get bpy.data.materials "SpaceStation"))))  ; Assign the material to that slot

(defn rename [] (do (setv bpy.context.object.name (+ obj_prefix bpy.context.object.name))))

(defn beam [n] (do (bpy.ops.mesh.primitive_cylinder_add :radius 0.1 :depth (+ 1 n) :location [0 0 0])  ; Center beam for the station
                   (setv bpy.context.object.name "SpaceStation_Beam")))

(defn part_torus [seed config z] (do (setv mrad (rng_float seed 1 (get config "torus_major_min")
                                                                  (get config "torus_major_max")))  ; Major radius
                              (setv zrot (rng_float seed 2 0.0 3.1415))  ; Z rotation
                              (bpy.ops.mesh.primitive_torus_add :major_radius mrad
                                                                :minor_radius (rng_float seed 3 (get config "torus_minor_min")
                                                                                                (get config "torus_minor_max"))
                                                                :location     [0 0 z])  ; The torus itself
                              (rename)
                              (bpy.ops.mesh.primitive_cylinder_add :radius   0.05
                                                                   :vertices 8
                                                                   :depth    (* mrad 2)
                                                                   :rotation [0 1.5708 zrot]
                                                                   :location [0 0 z])  ; Fist beam to hold the torus
                              (rename)
                              (bpy.ops.mesh.primitive_cylinder_add :radius   0.05
                                                                   :vertices 8
                                                                   :depth    (* mrad 2)
                                                                   :rotation [1.5708 0 zrot]
                                                                   :location [0 0 z])  ; Second beam to hold the torus
                              (rename)))

(defn part_bevelbox [seed config z] (do (bpy.ops.mesh.primitive_cube_add :radius   (rng_float seed 1 (get config "bevelbox_min")
                                                                                                     (get config "bevelbox_max"))
                                                                  :rotation [0 0 (rng_float seed 2 0.0 3.1415)]
                                                                  :location [0 0 z])  ; Add a cube
                                 (rename)
                                 (bpy.ops.object.modifier_add :type "BEVEL")  ; Add bevel
                                 (bpy.ops.object.modifier_apply :apply_as "DATA" :modifier "Bevel")))  ; Apply the bevel

(defn part_cylinder [seed config z] (do (bpy.ops.mesh.primitive_cylinder_add :radius   (rng_float seed 1 (get config "cylinder_min")
                                                                                                         (get config "cylinder_max"))
                                                                      :depth    (rng_float seed 2 (get config "cylinder_h_min") (get config "cylinder_h_max"))
                                                                      :location [0 0 z]
                                                                      :vertices 16)  ; Add a cylinder
                                 (rename)
                                 (bpy.ops.object.modifier_add :type "BEVEL")  ; Add bevel
                                 (bpy.ops.object.modifier_apply :apply_as "DATA" :modifier "Bevel")))  ; Apply the bevel

(defn part_storagering [seed config z] (do (bpy.ops.mesh.primitive_cube_add :location [1 0 z])  ; Add first cube
                                    (bpy.ops.transform.resize :value [0.5 0.5 (rng_float seed 1 (get config "storage_min") (get config "storage_max"))])  ; Scale it
                                    (bpy.ops.object.transform_apply :location false
                                                                    :rotation false
                                                                    :scale true)  ; Apply scaling to make the bevel look better
                                    (rename)
                                    (bpy.ops.object.modifier_add :type "BEVEL")  ; Add bevel
                                    (setv (. (get bpy.context.object.modifiers "Bevel") width) 0.3)  ; Make it the correct size
                                    (bpy.ops.object.modifier_apply :apply_as "DATA" :modifier "Bevel")
                                    ; Copy the cube 3 times
                                    (bpy.ops.object.duplicate)
                                    (rename)
                                    (setv bpy.context.object.location [-1 0 z])
                                    (bpy.ops.object.duplicate)
                                    (rename)
                                    (setv bpy.context.object.location [0 1 z])
                                    (bpy.ops.object.duplicate)
                                    (rename)
                                    (setv bpy.context.object.location [0 -1 z])
                                    ; Add 2 beams to hold the boxes
                                    (bpy.ops.mesh.primitive_cylinder_add :radius   0.05
                                                                         :vertices 8
                                                                         :depth    2
                                                                         :rotation [0 1.5708 0]
                                                                         :location [0 0 z])  ; Fist beam to hold the boxes
                                    (rename)
                                    (bpy.ops.mesh.primitive_cylinder_add :radius   0.05
                                                                         :vertices 8
                                                                         :depth    2
                                                                         :rotation [1.5708 0 0]
                                                                         :location [0 0 z])  ; Second beam to hold the boxes
                                    (rename)))

;;;;; Base generator

(defn generate_station [seed config] (do (setv n (+ (get config "min_parts") (rng_int seed 1 (- (get config "max_parts") (get config "min_parts")))))
                                  (print n "parts.")
                                  (beam n)
                                  (for [i (range n)]
                                       (do (setv part (rng_int seed i 3))  ; Select a random part
                                           (setv z (- i (/ n 2)))  ; Precalculate z coordinate
                                           (print "Part" i "is" part)
                                           (cond [(= part 0) (part_torus (+ seed i) config z)]
                                                 [(= part 1) (part_bevelbox (+ seed i) config z)]
                                                 [(= part 2) (part_cylinder (+ seed i) config z)]
                                                 [(= part 3) (part_storagering (+ seed i) config z)])))
                                  (join_objects)
                                  (if (= __name__ "__main__") (set_material))))  ; Only set material if this is the main script

(if (= __name__ "__main__") (do (clear_scene)
                                (setv conf {"min_parts"       3
                                            "max_parts"       8
                                            "torus_major_min" 2.0
                                            "torus_major_max" 5.0
                                            "torus_minor_min" 0.1
                                            "torus_minor_max" 0.5
                                            "bevelbox_min"    0.2
                                            "bevelbox_max"    0.5
                                            "cylinder_min"    0.5
                                            "cylinder_max"    3.0
                                            "cylinder_h_min"  0.3
                                            "cylinder_h_max"  1.0
                                            "storage_min"     0.5
                                            "storage_max"     1.0})
                                (generate_station 5 conf)))


; Good seeds:
; 80, 4, 5
