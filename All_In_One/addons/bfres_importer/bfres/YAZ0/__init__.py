import logging; log = logging.getLogger(__name__)
from .Decoder import Decoder

def decompressFile(infile, outfile):
    """Decompress from `infile` to `outfile`."""
    decoder = Decoder(infile)
    for data in decoder.bytes():
        outfile.write(data)
