#!/bin/env python

import os, sys, shutil, logging, optparse

LOG = logging.getLogger('io_scene_cgf:setup')
CURDIR = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))

def run(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = optparse.OptionParser(
            version='1.0.0',
            usage="%prog [OPTIONS] ...",
            description='',
            )

    parser.add_option('-v', '--verbose',
            default=False,
            action='store_true',
            help='Verbose trace output')

    keywords, positional = parser.parse_args(argv)

    LOGGING_FMT = "%(message)s"
    logging.basicConfig(format=LOGGING_FMT)

    if keywords.verbose:
        LOG.setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.INFO)

    # Make build directory silentily
    build_dir = os.path.join(CURDIR, 'build')
    build_root = os.path.join(build_dir, 'io_scene_cgf')
    try:
        shutil.rmtree(build_dir)
    except OSError:
        pass

    try:
        os.mkdir(build_dir)
        LOG.debug("Make build directory if not exists ...")
    except OSError:
        pass

    try:
        os.mkdir(build_root)
        LOG.debug("Make build root directory if not exists ...")
    except OSError:
        pass

    LOG.debug("archive root dir: %s" % build_root)

    curlist = os.listdir(CURDIR)
    for f in curlist:
        if os.path.isfile(f) and f.endswith('.py') and f != os.path.basename(__file__):
            shutil.copyfile(f, os.path.join(build_root, f))
            LOG.debug('[COPY] %s => %s' % (f, os.path.join(build_root, f)))
        elif os.path.isdir(f) and f == 'pyffi':
            shutil.copytree(os.path.join(f, 'pyffi'), os.path.join(build_root, f), ignore=lambda  srcs, names: '__pycache__')
            LOG.debug('[COPY] %s => %s' % (os.path.join(f, 'pyffi'), os.path.join(build_root, f)))

    shutil.make_archive('io_scene_cgf', 'zip', root_dir=build_dir)
    LOG.info("Created archive io_scene_cgf.zip.")

    shutil.rmtree(build_dir)
    LOG.debug("Removes build dir: %s" % build_dir)
    LOG.info('Done.')

if __name__ == '__main__':
    run()

