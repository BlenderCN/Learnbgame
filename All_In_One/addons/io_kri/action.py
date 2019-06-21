__author__ = ['Dzmitry Malyshau']
__bpydoc__ = 'Action module of KRI exporter.'

import bpy
from io_kri.common	import *


###  ANIMATION CURVES   ###

def gather_anim(ob,log):
	ad = ob.animation_data
	if not ad: return []
	all = [ns.action for nt in ad.nla_tracks for ns in nt.strips]
	if ad.action not in ([None]+all):
		log.log(1,'w','current action (%s) is not finalized' % (ad.action.name))
		all.append( ad.action )
	return all

def save_action(out,act,prefix,log):
	import re
	offset,nf = act.frame_range
	rnas = {} # [attrib_name][sub_id]
	indexator,n_empty = None,0
	# gather all
	for f in act.fcurves:
		attrib = f.data_path
		if not len(attrib):
			n_empty += 1
			continue
		pos_dot		= attrib.find('.')
		pos_array	= attrib.find('[')
		domain = None
		if pos_dot>=0 and pos_dot<pos_array:
			domain = attrib[:pos_dot]
		if domain != prefix:
			continue
		#log.logu(2, 'passed [%d].%s.%d' %(bid,attrib,f.array_index) )
		if not attrib in rnas:
			rnas[attrib] = []
		lis = rnas[attrib]
		if len(lis)<=f.array_index:
			while len(lis)<f.array_index:
				lis.append(None)
			lis.append(f)
		else:	lis[f.array_index] = f
	# write header or exit
	if not len(rnas):
		return None
	if not out:
		return act.name
	out.begin( 'action' )
	out.text( act.name )
	out.pack('f', nf / bpy.context.scene.render.fps )
	log.logu(1,'+anim: %s, %d frames, %d groups' % ( act.name,nf,len(act.groups) ))
	if n_empty:
		log.log(2,'w','%d empty curves detected' % (n_empty))
	# write in packs
	curves = set()
	for attrib,sub in rnas.items():
		str = re.sub(r'\".+\"','*',attrib)
		curves.add( '%s[%d]' % (str,len(sub)) )
		out.begin('curve')
		out.text( attrib )
		out.pack('B', len(sub) )
		save_curve_pack( out, sub, offset, log )
		out.end()
	log.logu(2, ', '.join(curves))
	out.end()	#action
	return act.name

def save_actions_int(out,ob,prefix,log):
	if not ob: return []
	anilist = []
	for act in gather_anim(ob,log):
		name = save_action(out,act,prefix,log)
		if name != None:
			anilist.append(name)
	return anilist

def save_actions_ext(path,ob,prefix,log):
	if not ob: return []
	all_actions = gather_anim(ob,log)
	if len(all_actions)==0: return []
	anilist = []
	out = None
	if path:
		out = Writer(path + '.k3act')
		out.begin('*action')
	for act in all_actions:
		name = save_action(out,act,prefix,log)
		if name != None:
			anilist.append(name)
	if out:
		out.end()
		out.close()
	return anilist


###  ACTION:CURVES   ###

def save_curve_pack(out,orig_curves,offset,log):
	curves = [c for c in orig_curves if c!=None]
	if len(curves)!=len(orig_curves):
		log.log(2,'w','null curves detected')
	if len(curves)==0:
		log.log(2,'w','zero length curve pack')
		out.pack('H',0)
		return
	num = len( curves[0].keyframe_points )
	extra = curves[0].extrapolation
	#log.log(2,'i', '%s, keys %d' %(curves,num))
	for c in curves:
		assert c.extrapolation == extra
		if len(c.keyframe_points) != num:
			log.log(2,'w','unmatched keyframes detected')
			out.pack('H',0)
			return
	out.pack('HBB', num, (extra == 'LINEAR'), Settings.keyBezier)
	for i in range(num):
		kp = tuple((c if c else curves[0]).keyframe_points[i] for c in orig_curves)
		frame = kp[0].co[0]
		out.pack('f', (frame-offset) / bpy.context.scene.render.fps)
		#print ('Time', x, i, data)
		out.array('f', (k.co[1] for k in kp))
		if not Settings.keyBezier:
			continue
		# ignoring handlers time
		out.array('f', (k.handle_left[1] for k in kp))
		out.array('f', (k.handle_right[1] for k in kp))
