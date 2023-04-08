'''
This script includes functions to read and write header files for Picoquant devices, 
along with a function to combine the header file with the raw time tags file. 
They serve to modify the header files, with the most important variables 
include the acquisition time and the total number of time tags/ records. 
The other 3 variables (timestamp, counts0, and counts1) are optional 
and they are served to add more details to the header files.
The script is tested with the time tags acquired 
from PicoHarp 300 and Hydraharp 400 (in both T2 and T3 modes).
The header_parameter.npz files attached in this repo 
are header files for data taken in the T2 mode.
For data saved in the T3 mode, one can use the GUI 
provided by the company to generate a working T3 file.
After that, one can rip the header from the file. With that, one can modify it.

Author:
Zhe Xian, Koong
Date: 8th of April 2023. Oxford, UK.
'''

import struct
import time
import sys
import numpy as np

# Tag Types
tyEmpty8 = struct.unpack(">i", bytes.fromhex("FFFF0008"))[0]
tyBool8 = struct.unpack(">i", bytes.fromhex("00000008"))[0]
tyInt8 = struct.unpack(">i", bytes.fromhex("10000008"))[0]
tyBitSet64 = struct.unpack(">i", bytes.fromhex("11000008"))[0]
tyColor8 = struct.unpack(">i", bytes.fromhex("12000008"))[0]
tyFloat8 = struct.unpack(">i", bytes.fromhex("20000008"))[0]
tyTDateTime = struct.unpack(">i", bytes.fromhex("21000008"))[0]
tyFloat8Array = struct.unpack(">i", bytes.fromhex("2001FFFF"))[0]
tyAnsiString = struct.unpack(">i", bytes.fromhex("4001FFFF"))[0]
tyWideString = struct.unpack(">i", bytes.fromhex("4002FFFF"))[0]
tyBinaryBlob = struct.unpack(">i", bytes.fromhex("FFFFFFFF"))[0]

# Record types
rtPicoHarpT3 = struct.unpack(">i", bytes.fromhex("00010303"))[0]
rtPicoHarpT2 = struct.unpack(">i", bytes.fromhex("00010203"))[0]
rtHydraHarpT3 = struct.unpack(">i", bytes.fromhex("00010304"))[0]
rtHydraHarpT2 = struct.unpack(">i", bytes.fromhex("00010204"))[0]
rtHydraHarp2T3 = struct.unpack(">i", bytes.fromhex("01010304"))[0]
rtHydraHarp2T2 = struct.unpack(">i", bytes.fromhex("01010204"))[0]
rtTimeHarp260NT3 = struct.unpack(">i", bytes.fromhex("00010305"))[0]
rtTimeHarp260NT2 = struct.unpack(">i", bytes.fromhex("00010205"))[0]
rtTimeHarp260PT3 = struct.unpack(">i", bytes.fromhex("00010306"))[0]
rtTimeHarp260PT2 = struct.unpack(">i", bytes.fromhex("00010206"))[0]
rtMultiHarpNT3 = struct.unpack(">i", bytes.fromhex("00010307"))[0]
rtMultiHarpNT2 = struct.unpack(">i", bytes.fromhex("00010207"))[0]


def read_ptuheader(originalfile, isprint=True, npz_savedfile=None):
    """
    Read header from ptu file. It will work on a suitably formated binary file. Add option to output the headers to a .npz file compatible with the writing function.
    """
    _ident = []
    _tagIdx = []
    _tagTyp = []
    _val = []

    with open(originalfile, "rb") as inputfile:
        magic = inputfile.read(8).decode("utf-8").strip('\0')
        version = inputfile.read(8).decode("utf-8").strip('\0')
        if isprint:
            print(magic, version)
        while True:
            tagIdent = inputfile.read(32).decode("utf-8").strip('\0')
            tagIdx = struct.unpack("<i", inputfile.read(4))[0]
            tagTyp = struct.unpack("<i", inputfile.read(4))[0]
            _ident.append(tagIdent)
            _tagIdx.append(tagIdx)
            _tagTyp.append(tagTyp)
            if tagIdx > -1:
                evalName = tagIdent + '(' + str(tagIdx) + ')'
            else:
                evalName = tagIdent
            if tagTyp == tyEmpty8:
                inputfile.read(8)
                _val.append(' ')
                if isprint:
                    print((evalName, "<empty Tag>"))
            elif tagTyp == tyBool8:
                tagInt = struct.unpack("<q", inputfile.read(8))[0]
                _val.append(int(tagInt))
                if tagInt == 0:
                    if isprint:
                        print((evalName, "False"))
                else:
                    if isprint:
                        print((evalName, "True"))
            elif tagTyp == tyInt8:
                tagInt = struct.unpack("<q", inputfile.read(8))[0]
                _val.append(int(tagInt))
                if isprint:
                    print((evalName, tagInt))
            elif tagTyp == tyBitSet64:
                tagInt = struct.unpack("<q", inputfile.read(8))[0]
                _val.append(int(tagInt))
                if isprint:
                    print((evalName, tagInt))
            elif tagTyp == tyColor8:
                tagInt = struct.unpack("<q", inputfile.read(8))[0]
                _val.append(int(tagInt))
                if isprint:
                    print((evalName, tagInt))
            elif tagTyp == tyFloat8:
                tagFloat = struct.unpack("<d", inputfile.read(8))[0]
                _val.append(float(tagFloat))
                if isprint:
                    print((evalName, tagFloat))
            elif tagTyp == tyFloat8Array:
                tagInt = struct.unpack("<q", inputfile.read(8))[0]
                _val.append(int(tagInt))
                if isprint:
                    print((evalName, tagInt))
            elif tagTyp == tyTDateTime:
                tagFloat = struct.unpack("<d", inputfile.read(8))[0]
                _val.append(float(tagFloat))
                tagTime = int((tagFloat - 25569) * 86400)
                tagTime = time.gmtime(tagTime)
                if isprint:
                    print((evalName, tagTime))
            elif tagTyp == tyAnsiString:
                tagInt = struct.unpack("<q", inputfile.read(8))[0]
                tagString = inputfile.read(tagInt).decode("utf-8").strip("\0")
                _val.append(list([int(tagInt), tagString]))
                if isprint:
                    print((evalName, tagString))
            elif tagTyp == tyWideString:
                tagInt = struct.unpack("<q", inputfile.read(8))[0]
                tagString = inputfile.read(tagInt).decode(
                    "utf-16le", errors="ignore").strip("\0")
                _val.append(list([int(tagInt), tagString]))
                if isprint:
                    print((evalName, tagString))
            elif tagTyp == tyBinaryBlob:
                tagInt = struct.unpack("<q", inputfile.read(8))[0]
                _val.append(int(tagInt))
                if isprint:
                    print((evalName, tagInt))
            else:
                print("ERROR: Unknown tag type")
                sys.exit(0)
            if tagIdent == "Header_End":
                break
    if npz_savedfile is not None:
        np.savez(npz_savedfile, ident=_ident, tagIdx=_tagIdx,
                 tagTyp=_tagTyp, tagValues=np.array(_val, dtype=object))


def write_ptuheader(inputfile, acquisition_time_ms=None, total_records=None,
                    timestamp=None, counts0=None, counts1=None,
                    header='picoharp_ptu_header_parameter.npz'):
    """
    Create a blank file : inputfile
    Write the ptuheader from the npz file, with the only major changes being 
    the acquisition time in ms and the total records.
    Output :
    inputfile containing the header.
    """
    def timestamp_to_unix(t): return t / 86400 + 25569
    data = np.load(header, allow_pickle=True)
    _ident = data["ident"]
    _tagIdx = data["tagIdx"]
    _tagTyp = data["tagTyp"]
    _val = data["tagValues"]
    magic = "PQTTTR"
    empty = ""
    version = "1.0.00"
    with open(inputfile, "wb") as file:
        file.write(struct.pack("<8s", magic.encode("ascii")))
        file.write(struct.pack("<8s", version.encode("ascii")))
        for j in range(len(_ident)):
            file.write(struct.pack("<32s", _ident[j].encode("ascii")))
            file.write(struct.pack("<i", _tagIdx[j]))
            file.write(struct.pack("<i", _tagTyp[j]))

            if _tagTyp[j] == tyEmpty8:
                file.write(struct.pack("<8s", empty.encode("ascii")))
            elif _tagTyp[j] == tyBool8:
                file.write(struct.pack("<q", _val[j]))
            elif _tagTyp[j] == tyInt8:
                if _ident[j] == "MeasDesc_AcquisitionTime" and acquisition_time_ms is not None:
                    file.write(struct.pack("<q", acquisition_time_ms))
                elif (
                    _ident[j] == "TTResult_StopAfter"
                    and acquisition_time_ms is not None
                ):
                    file.write(struct.pack("<q", acquisition_time_ms))
                elif (
                    _ident[j] == "TTResult_SyncRate"
                    and counts0 is not None
                ):
                    file.write(struct.pack("<q", counts0))
                elif (
                    _ident[j] == "TTResult_InputRate"
                    and counts1 is not None
                ):
                    file.write(struct.pack("<q", counts1))
                elif (
                    _ident[j] == "TTResult_NumberOfRecords"
                    and total_records is not None
                ):
                    file.write(struct.pack("<q", total_records))
                else:
                    file.write(struct.pack("<q", _val[j]))
            elif _tagTyp[j] == tyBitSet64:
                file.write(struct.pack("<q", _val[j]))
            elif _tagTyp[j] == tyColor8:
                file.write(struct.pack("<q", _val[j]))
            elif _tagTyp[j] == tyFloat8:
                file.write(struct.pack("<d", _val[j]))
            elif _tagTyp[j] == tyFloat8Array:
                file.write(struct.pack("<q", _val[j]))
            elif _tagTyp[j] == tyTDateTime:
                if timestamp is None:
                    cur_time = timestamp_to_unix(time.time())
                else:
                    cur_time = timestamp_to_unix(timestamp)
                file.write(struct.pack("<d", cur_time))
            elif _tagTyp[j] == tyAnsiString:
                file.write(struct.pack("<q", _val[j][0]))
                file.write(
                    struct.pack(
                        "<{0:.0f}s".format(
                            _val[j][0]), _val[j][1].encode("ascii")
                    )
                )
            elif _tagTyp[j] == tyWideString:
                file.write(struct.pack("<q", _val[j][0]))
                file.write(
                    struct.pack(
                        "<{0:.0f}s".format(
                            _val[j][0]), _val[j][1].encode("ascii")
                    )
                )
            elif _tagTyp[j] == tyBinaryBlob:
                file.write(struct.pack("<q", _val[j]))
            else:
                print("ERROR: Unknown tag type")


def combine_time_tags_header(headerfile, timetags, outputfile):
    """
    Add the proper header to the saved timetags file so that the output (outputfile) can be used to be analyzed later.
    Ideally, you can name the outputfile in the .ptu file format.
    Tested on 
    device :PicoHarp 300  : 2 channels.
    timetag analysis software : readPTU library : https://github.com/QuantumPhotonicsLab/readPTU
    """

    with open(headerfile, "rb") as original, open(timetags, "rb") as _timetags, open(
        outputfile, "wb+"
    ) as _output:
        header = original.read()
        _output.write(header)
        tags = _timetags.read()
        _output.write(tags)


if __name__ == "__main__":
    filename1 = r'hydraharp_ptu_header_parameter.npz'
    filename2 = r'picoharp_ptu_header_parameter.npz'
    write_ptuheader("test.bin", acquisition_time_ms=600000,
                    total_records=6567632, header=filename1)
    read_ptuheader(originalfile="test.bin", isprint=True, npz_savedfile=None)
