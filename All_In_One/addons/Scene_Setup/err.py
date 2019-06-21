import sys

from . import log

class MeshPathError(TypeError):
    pass

class MeshLabelError(ValueError):
    pass

class ListParseError(ValueError):
    pass

class TempPathError(OSError):
    pass

def wrap(parser, main, *args, **kwargs):
    # Parse all arguments after double dash
    argv = []
    if 'ez' not in kwargs:
        try:
            arg0 = sys.argv.index('--')
            argv = list(sys.argv)[arg0+1:]
        except ValueError as e:
            log.yaml('Usage Error', {
                'Missing -- in': ' '.join(sys.argv),
                'Usage': parser.format_usage(),
            })
    else:
        argv = sys.argv[1:]
    try:
        parsed = parser.parse_args(argv)
        main(parsed, *args)
        print('Done')
    except SystemExit as e:
        helped = '-h' in argv or '--help' in argv
        usage = parser.format_usage().split(' ')
        log.yaml('EXIT', {
            'Cannot parse': ' '.join(argv),
            'Usage': ' '.join(usage[1:]),
        }, helped)
    # Cannot format paths without giving integers
    except MeshPathError as e:
        error, k, v = e.args
        log.yaml('Error', {
            'Error': error,
            'No ID in --list': {
                '--list': helps['list'],
            },
            'Need ID to format "{}" argument'.format(k): v,
        })
    # Cannot infer ID from file path
    except MeshLabelError as e:
        search, path = e.args
        log.yaml('Error', {
            'Error': 'Cannot infer ID label from path',
            'Search Path': search,
            'Real Path': path,
        })
    # Cannot link temp file needed
    except TempPathError as e:
        error, real, symbol = e.args
        log.yaml('Error', {
            'Error': error,
            'Cannot link': {
                'From': real,
                'To': symbol,
            }
        })
    # Cannot read list
    except ListParseError as e:
        error, k, v = e.args
        log.yaml('Error', {
            helps.get(k,'error'): v,
            k: error,
        })
