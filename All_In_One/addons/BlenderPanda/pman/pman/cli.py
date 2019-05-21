import argparse
import subprocess
import sys


import pman


def create(args):
    pman.create_project(args.dirname, args.extras)


def update(args):
    config = pman.get_config()
    pman.create_project(config['internal']['projectdir'], args.extras)


def build(_):
    pman.build()


def run(_):
    pman.run()


def test(_):
    config = pman.get_config()
    args = [
        pman.get_python_program(),
        'setup.py',
        'test',
    ]
    subprocess.call(args, cwd=config['internal']['projectdir'])


def dist(args):
    pman.get_python_program()

    try:
        import direct.dist.commands #pylint:disable=unused-import,unused-variable
    except ImportError:
        print('Setuptools-based distribution is not supported by this version of Panda3D')
        return

    platforms = args.platforms
    if platforms is not None:
        platforms = list(platforms)
    pman.dist(build_installers=not args.skip_installers, platforms=platforms)


def clean(_):
    pman.clean()


def main():
    parser = argparse.ArgumentParser(
        description='Tool for building and managing Panda3D applications'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=pman.__version__),
    )

    subparsers = parser.add_subparsers(
        title='commands',
    )

    create_parser = subparsers.add_parser(
        'create',
        help='Create a new project',
    )
    create_parser.add_argument(
        'dirname',
        action='store',
        nargs='?',
        default='.',
        help='Directory to create the project in (will be created if it does not exist)',
    )
    create_parser.add_argument(
        '--extras',
        action='store',
        nargs='+',
        help='Extra creation hooks to run',
    )
    create_parser.set_defaults(func=create)

    update_parser = subparsers.add_parser(
        'update',
        help='Re-run project creation logic on the project directory'
    )
    update_parser.add_argument(
        '--extras',
        action='store',
        nargs='+',
        help='Extra creation hooks to run',
    )
    update_parser.set_defaults(func=update)

    build_parser = subparsers.add_parser(
        'build',
        help='Build project',
    )
    build_parser.set_defaults(func=build)

    run_parser = subparsers.add_parser(
        'run',
        help='Run project',
    )
    run_parser.set_defaults(func=run)

    test_parser = subparsers.add_parser(
        'test',
        help='Run tests',
    )
    test_parser.set_defaults(func=test)

    dist_parser = subparsers.add_parser(
        'dist',
        help='Create binary distributions and installers'
    )
    dist_parser.add_argument(
        '--skip-installers',
        action='store_true',
        help='Do not build installers',
    )
    dist_parser.add_argument(
        '-p', '--platforms',
        action='store',
        nargs='+',
        help='Override list of platforms to build for',
    )
    dist_parser.set_defaults(func=dist)

    clean_parser = subparsers.add_parser(
        'clean',
        help='Remove built files',
    )
    clean_parser.set_defaults(func=clean)


    args = parser.parse_args()
    if not hasattr(args, 'func'):
        print('A command must be provided\n')
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
