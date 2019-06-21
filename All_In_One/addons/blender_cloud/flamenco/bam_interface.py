"""BAM packing interface for Flamenco."""

import logging
from pathlib import Path
import typing

# Timeout of the BAM subprocess, in seconds.
SUBPROC_READLINE_TIMEOUT = 600
log = logging.getLogger(__name__)


class CommandExecutionError(Exception):
    """Raised when there was an error executing a BAM command."""
    pass


def wheel_pythonpath_278() -> str:
    """Returns the value of a PYTHONPATH environment variable needed to run BAM from its wheel file.

    Workaround for Blender 2.78c not having io_blend_utils.pythonpath()
    """

    import os
    from ..wheels import wheel_filename

    # Find the wheel to run.
    wheelpath = wheel_filename('blender_bam')

    log.info('Using wheel %s to run BAM-Pack', wheelpath)

    # Update the PYTHONPATH to include that wheel.
    existing_pypath = os.environ.get('PYTHONPATH', '')
    if existing_pypath:
        return os.pathsep.join((existing_pypath, wheelpath))

    return wheelpath


async def bam_copy(base_blendfile: Path, target_blendfile: Path,
                   exclusion_filter: str) -> typing.List[Path]:
    """Uses BAM to copy the given file and dependencies to the target blendfile.

    Due to the way blendfile_pack.py is programmed/structured, we cannot import it
    and call a function; it has to be run in a subprocess.

    :raises: asyncio.CanceledError if the task was cancelled.
    :raises: asyncio.TimeoutError if reading a line from the BAM process timed out.
    :raises: CommandExecutionError if the subprocess failed or output invalid UTF-8.
    :returns: a list of missing sources; hopefully empty.
    """

    import asyncio
    import os
    import shlex
    import subprocess

    import bpy
    import io_blend_utils

    args = [
        bpy.app.binary_path_python,
        '-m', 'bam.pack',
        '--input', str(base_blendfile),
        '--output', str(target_blendfile),
        '--mode', 'FILE',
    ]

    if exclusion_filter:
        args.extend(['--exclude', exclusion_filter])

    cmd_to_log = ' '.join(shlex.quote(s) for s in args)
    log.info('Executing %s', cmd_to_log)

    # Workaround for Blender 2.78c not having io_blend_utils.pythonpath()
    if hasattr(io_blend_utils, 'pythonpath'):
        pythonpath = io_blend_utils.pythonpath()
    else:
        pythonpath = wheel_pythonpath_278()

    env = {
        'PYTHONPATH': pythonpath,
        # Needed on Windows because http://bugs.python.org/issue8557
        'PATH': os.environ['PATH'],
    }
    if 'SYSTEMROOT' in os.environ:  # Windows http://bugs.python.org/issue20614
        env['SYSTEMROOT'] = os.environ['SYSTEMROOT']

    proc = await asyncio.create_subprocess_exec(
        *args,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    missing_sources = []

    try:
        while not proc.stdout.at_eof():
            line = await asyncio.wait_for(proc.stdout.readline(),
                                          SUBPROC_READLINE_TIMEOUT)
            if not line:
                # EOF received, so let's bail.
                break

            try:
                line = line.decode('utf8')
            except UnicodeDecodeError as ex:
                raise CommandExecutionError('Command produced non-UTF8 output, '
                                            'aborting: %s' % ex)

            line = line.rstrip()
            if 'source missing:' in line:
                path = parse_missing_source(line)
                missing_sources.append(path)
                log.warning('Source is missing: %s', path)

            log.info('  %s', line)
    finally:
        if proc.returncode is None:
            # Always wait for the process, to avoid zombies.
            try:
                proc.kill()
            except ProcessLookupError:
                # The process is already stopped, so killing is impossible. That's ok.
                log.debug("The process was already stopped, aborting is impossible. That's ok.")
            await proc.wait()
        log.info('The process stopped with status code %i', proc.returncode)

    if proc.returncode:
        raise CommandExecutionError('Process stopped with status %i' % proc.returncode)

    return missing_sources


def parse_missing_source(line: str) -> Path:
    r"""Parses a "missing source" line into a pathlib.Path.

    >>> parse_missing_source(r"  source missing: b'D\xc3\xaffficult \xc3\x9cTF-8 filename'")
    PosixPath('Dïfficult ÜTF-8 filename')
    >>> parse_missing_source(r"  source missing: b'D\xfffficult Win1252 f\xeflen\xe6me'")
    PosixPath('D�fficult Win1252 f�len�me')
    """

    _, missing_source = line.split(': ', 1)
    missing_source_as_bytes = parse_byte_literal(missing_source.strip())

    # The file could originate from any platform, so UTF-8 and the current platform's
    # filesystem encodings are just guesses.
    try:
        missing_source = missing_source_as_bytes.decode('utf8')
    except UnicodeDecodeError:
        import sys
        try:
            missing_source = missing_source_as_bytes.decode(sys.getfilesystemencoding())
        except UnicodeDecodeError:
            missing_source = missing_source_as_bytes.decode('ascii', errors='replace')

    path = Path(missing_source)

    return path


def parse_byte_literal(bytes_literal: str) -> bytes:
    r"""Parses a repr(bytes) output into a bytes object.

    >>> parse_byte_literal(r"b'D\xc3\xaffficult \xc3\x9cTF-8 filename'")
    b'D\xc3\xaffficult \xc3\x9cTF-8 filename'
    >>> parse_byte_literal(r"b'D\xeffficult Win1252 f\xeflen\xe6me'")
    b'D\xeffficult Win1252 f\xeflen\xe6me'
    """

    # Some very basic assertions to make sure we have a proper bytes literal.
    assert bytes_literal[0] == "b"
    assert bytes_literal[1] in {'"', "'"}
    assert bytes_literal[-1] == bytes_literal[1]

    import ast
    return ast.literal_eval(bytes_literal)


if __name__ == '__main__':
    import doctest

    doctest.testmod()
