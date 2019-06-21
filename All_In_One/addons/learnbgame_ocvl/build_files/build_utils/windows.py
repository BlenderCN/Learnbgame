import os
import sys

import subprocess


def nsis_installer_build(version_display, build_blender_path, bf_build_dir, rel_dir, kwargs):

    VERSION = version_display[0:3]
    BF_INSTALLDIR = f"{bf_build_dir}/bin/Release"

    print("="*35)
    bitness = '64'
    bf_installdir = os.path.normpath(os.path.join(build_blender_path, BF_INSTALLDIR))

    doneroot = False
    rootdirconts = []
    datafiles = ''
    deldatafiles = ''
    deldatadirs = ''
    len_bf_installdir = len(bf_installdir)

    for dp, dn, df in os.walk(bf_installdir):
        # install
        if not doneroot:
            for f in df:
                rootdirconts.append(os.path.join(dp, f))
            doneroot = True
        else:
            if len(df) > 0:
                datafiles += "\n" + r'SetOutPath $INSTDIR' + dp[len_bf_installdir:] + "\n\n"

                for f in df:
                    outfile = os.path.join(dp, f)
                    if " " in outfile:
                        print(f"WARNING: filename with space character: {outfile}")
                        continue
                    datafiles += '  File '+outfile + "\n"

        # uninstall
        deldir = dp[len_bf_installdir+1:]

        if len(deldir) > 0:
            deldatadirs = "RMDir $INSTDIR\\" + deldir + "\n" + deldatadirs
            deldatadirs = "RMDir /r $INSTDIR\\" + deldir + "\\__pycache__\n" + deldatadirs

            for f in df:
                deldatafiles += 'Delete \"$INSTDIR\\' + os.path.join(deldir, f) + "\"\n"

    # change to suit install dir
    inst_dir = bf_installdir

    ns = open(os.path.join(rel_dir, "installer/00.sconsblender.nsi"), "r")
    ns_cnt = str(ns.read())
    ns.close()

    # var replacements
    ns_cnt = ns_cnt.replace("[DISTDIR]", os.path.normpath(inst_dir+os.sep))
    ns_cnt = ns_cnt.replace("[VERSION]", version_display)
    ns_cnt = ns_cnt.replace("[SHORTVERSION]", VERSION)
    ns_cnt = ns_cnt.replace("[RELDIR]", os.path.normpath(rel_dir))
    ns_cnt = ns_cnt.replace("[BITNESS]", bitness)

    # do root
    rootlist = []
    for rootitem in rootdirconts:
        rootlist.append("File \"" + rootitem + "\"")
    rootstring = "\n  ".join(rootlist)
    rootstring += "\n\n"
    ns_cnt = ns_cnt.replace("[ROOTDIRCONTS]", rootstring)

    # do delete items
    delrootlist = []
    for rootitem in rootdirconts:
        delrootlist.append("Delete $INSTDIR\\" + rootitem[len_bf_installdir+1:])
    del_root_string = "\n ".join(delrootlist)
    del_root_string += "\n"
    ns_cnt = ns_cnt.replace("[DELROOTDIRCONTS]", del_root_string)

    ns_cnt = ns_cnt.replace("[DODATAFILES]", datafiles)
    ns_cnt = ns_cnt.replace("[DELDATAFILES]", deldatafiles)
    ns_cnt = ns_cnt.replace("[DELDATADIRS]", deldatadirs)

    tmpnsi = os.path.normpath(build_blender_path + os.sep + bf_build_dir + os.sep + "00.blender_tmp.nsi")
    print(f"Temp nsi file: {tmpnsi}")
    new_nsis = open(tmpnsi, 'w')
    new_nsis.write(ns_cnt)
    new_nsis.close()
    print("NSIS Installer script created")


    print("Launching 'makensis'")

    cmdline = "makensis " + "\""+tmpnsi+"\""

    startupinfo = subprocess.STARTUPINFO()
    #  startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    proc = subprocess.Popen(
        cmdline,
        stdin=subprocess.PIPE,
        stdout=sys.stdout,
        stderr=sys.stderr,
        startupinfo=startupinfo,
        shell=True
    )
    data, err = proc.communicate()
    rv = proc.wait()

    if rv != 0:
        print(f"Data: {data}")
        print(f"Errors: {err}")

    print("Compilation Success!")
    print(f"Output file in {bf_installdir}")
    return rv