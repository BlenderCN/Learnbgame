import bpy, os, subprocess, time, threading


def run_proxy_gen_loop() :
  # check si le rendu proxy est actif dans les prefs
  if Conf.get_addon_conf().proxy_render :
    print("starting proxy gen loop...")
    new_thread = threading.Thread()
    new_thread.run = proxy_gen_loop
    new_thread.start() # the new thread is created and then is running.

def proxy_generate(strip,engine) :
	'''
	genere les proxy pour l'affichage dans le sequencer
	ça fonctionne en executant blender en subprocess avec un script qui fait la conversion
	'''
	debug = False
	name  = strip.bs_name
	if Conf.get_addon_conf().proxy_render :
		timer = time.time() # utilisé pour chronometrer l'export
		if debug : print("running subprocess for generating proxy :",strip.name , engine)
		inf=get_proxy_infos(strip,engine)
		#### creation de la commande
		cmd = (
			inf["blender"],
			"-b",
			"-s %s -e %s" % (strip.frame_file_start,strip.frame_file_end),
			"-P",
			inf["script"],
			"--",
			inf["image"],
			inf["proxy"],
			inf["stamp"],
		)
		t=1

		process = subprocess.Popen(" ".join(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
		try : strip.etacolor = 3
		except(AttributeError) : pass
		count=0 # un compteur qui evite de trop saturer l'interface
		while True :
			line = process.stdout.readline()
			if line :
				if debug : print(line)
				## Blender command line parser
				if line[:6] == b"Saved:":
					t+=1
					count += 1
					if debug : print(t,"/",inf["length"])
					if debug : print (strip.etapercent)
					if count >= 30 :
						count = 0
						try :
							strip.etapercent = t / inf["length"]
							Dsp.tag_redraw_all_sequencer_editors()
						except(AttributeError) :
							print("proxy : attribute error ")
							pass

				if line[:12] == b"Blender quit":
					try :
						strip.etapercent = 1.0
					except(AttributeError) :
						print("proxy : attribute error ")
						pass
					break
			else:
				break
		if debug : print("Done in : ",time.time()-timer," seconds")
		strip.etacolor = 5
		bpy.ops.sequencer.refresh_all()
