#!/bin/bash

# Copy the python code to the Blender scripts folder.

homedir=$HOME

if [ -n "$(uname -s | grep -i 'MINGW\|CYGWIN\|MSYS')" ]; then
  # We're using Bash on Windows!
  homedir="$HOME/Documents"
fi

usage(){
  cat <<'USAGE'
Wing Blender - Build script - Usage

./build.sh -[dpz]

-d    Build development version (Copy to BlenderScriptsDev)
-p    Build production version (Copy to BlenderScripts)
-z    Make release zip. Requires either -d or -p to be set, and zip to be in your PATH.
USAGE
}

if [[ $# -eq 0 ]]; then usage; exit 1; fi

pyfs=({__init__,{import,export}_iff,iff,iff_{mesh,read},mat_read}.py)

vers=''
gvers=''
zip=0

# Parse script options. Special thanks to the getopts tutorial on the Bash Hackers wiki:
# http://wiki.bash-hackers.org/howto/getopts_tutorial

while getopts ':dpz' build_option; do
  case $build_option in
    d)
      if [[ -n "$vers" ]]; then
        echo 'You cannot use -d and -p together!' >&2
        exit 1
      fi
      vers='development'
      gvers="$(git log -n 1 --format=%h)"
      blender_scripts_folder="$homedir/BlenderScriptsDev/addons/io_scene_wcp" # Development script folder
      ;;
    p)
      if [[ -n "$vers" ]]; then
        echo 'You cannot use -d and -p together!' >&2
        exit 1
      fi
      vers='production'
      blender_scripts_folder="$homedir/BlenderScripts/addons/io_scene_wcp" # Production script folder
      ;;
    z)
      if [[ -z "$vers" ]]; then
        usage; exit 1
      fi
      if [[ -z "$(which zip)" ]]; then
        echo 'zip is not in your PATH!' >&2; exit 1
      fi
      zip=1
      ;;
    \?)
      echo "Invalid option: $OPTARG" >&2
      usage; exit 1
      ;;
  esac
done

if [[ $zip -eq 0 ]]; then
  # Copy scripts to Blender scripts folder
  if [[ -d "$blender_scripts_folder" ]]; then
    for pyf in ${pyfs[@]}; do
      if [[ -f "$blender_scripts_folder/$pyf" ]]; then rm "$blender_scripts_folder/$pyf"; fi
    done
  else
    mkdir -p "$blender_scripts_folder"
  fi

  cp -t "$blender_scripts_folder" ${pyfs[@]}
  sed -i -e "s/%\\x7BGIT_COMMIT\\x7D/commit $gvers/g" "$blender_scripts_folder/__init__.py"

  build_success=0
  for pyf in ${pyfs[@]}; do
    if [[ -f "$blender_scripts_folder/$pyf" ]]; then ((++build_success)); fi
  done

  if [[ "$build_success" -eq "${#pyfs[@]}" ]]; then
    echo "Scripts copied to $vers folder."
    build_success=0  # From now on, this variable is the exit status.
  else
    echo "Failed to copy scripts to $vers folder."
    build_success=1
  fi

  if [[ -d "$blender_scripts_folder/__pycache__" ]]; then
    rm -r "$blender_scripts_folder/__pycache__"
  fi
else
  # Make installable Blender plugin zip file.
  mkdir io_scene_wcp
  cp -t io_scene_wcp ${pyfs[@]}
  sed -i -e "s/%\\x7BGIT_COMMIT\\x7D/commit $gvers/g" io_scene_wcp/__init__.py
  zipname="Wing_Blender"
  if [[ "$vers" = 'production' ]]; then
    zipname="${zipname}_$(git describe --tags)"
  else
    zipname="${zipname}_${gvers}"
  fi
  zip -r $zipname.zip io_scene_wcp
  rm -r io_scene_wcp
  if [[ -f "$zipname.zip" ]]; then
    echo "Created $zipname.zip."
    build_success=0
  else
    echo "Failed to create $zipname.zip."
    build_success=1
  fi
fi

exit $build_success
