import os
import tarfile


def make_tar_gz_from_release(kwargs):
    """
    Make tar.gz archive from release files
    :return:
    """
    WORK_DIR = kwargs["WORK_DIR"]
    BUILD_RELEASE_DIRNAME = kwargs["BUILD_RELEASE_DIRNAME"]
    BIN_RELEASE = kwargs["BIN_RELEASE"]
    OCVL_VERSION = kwargs["OCVL_VERSION"]

    source = os.path.join(WORK_DIR, BUILD_RELEASE_DIRNAME, BIN_RELEASE)
    destination = os.path.join(WORK_DIR, f"OCVL-{OCVL_VERSION}-linux.tar.gz")
    with tarfile.open(destination, "w:gz") as tar:
        tar.add(source, arcname=os.path.basename(source))
    print(f"Success. Artifact available on: {destination}")
