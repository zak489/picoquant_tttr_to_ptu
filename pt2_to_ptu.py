'''
This script includes functions to convert .pt2 file to .ptu file.
One needs to make sure the header file used (i.e. the .npz file) is the same mode
such that they are taken from the same device (e.g. both .pt2 and header .npz files 
are generated from PicoHarp 300).
Tested on .pt2 file generated from a PicoHarp 300.

Author:
Zhe Xian, Koong
Date: 8th of April 2023. Oxford, UK.
'''

import os
import datetime
from tttr_mode_to_ptu import write_ptuheader, combine_time_tags_header
import struct


def convert_pt2_to_ptu(originalfile, isprint=True, header='picoharp_ptu_header_parameter.npz'):
    '''
    Input:
    1. originalfile: .pt2 file to be converted to .ptu
    2. isprint: default: True. If true, print the header of the file.
    3. header: default: 'picoharp_ptu_header_parameter.npz' in the picoquant_tttr_to_ptu folder. Example header file to be modified.

    Output:
    Original file in .ptu format

    Algorithm:
    1. Read the original file and extract the header files and the time tags.
    2. Save the timetags file and create an appropriate header file for .ptu file based on the defined header.
    3. Combined the new header file with the time tags into a .ptu file. Tested with trattoria package. https://github.com/GCBallesteros/trattoria
    '''
    dataitem = ['Numberofcurves', 'Bitsperrecord', 'Routingchannels', 'Numberofboards',
                'Activecurve', 'Measurementmode', 'Submode', 'Rangeno', 'Offset', 'Acquisitiontime_ms',
                'Stopat', 'Stoponovfl', 'Restart', 'Displaylinlog', 'Displaytimeaxisfrom',
                'Displaytimeaxisto', 'Displaycountaxisfrom', 'Displaycountaxisto']
    dataitem_t2_header = ['Extdevices', 'Reserved', 'Reserved', 'Inprate0',
                          'Inprate1', 'Stopafter_ms', 'Stopreason', 'Numrecords',
                          'Imghdrsize']
    dataitem_boards = ['Hardwareident', 'Hardwareversion', 'Hardwareserial',
                       'Sync divider', 'CFDzerocross0', 'CFDlevel0',
                       'CFDzerocross1', 'CFDlevel1', 'Resolution_ns',
                       'Routermodelcode', 'Routermodelenabled']

    tagIdx = []
    header_description = {}
    headerfile = originalfile[:-4]+'_header.bin'
    timetagsfile = originalfile[:-4]+'_timetags.bin'
    processedfile = originalfile[:-4]+'.ptu'
    with open(originalfile, "rb") as inputfile:
        ident = inputfile.read(16).decode("utf-8").strip('\0')
        formatversion = inputfile.read(6).decode("utf-8").strip('\0')
        creatorname = inputfile.read(18).decode("utf-8").strip('\0')
        creatorversion = inputfile.read(12).decode("utf-8").strip('\0')
        filetime = inputfile.read(18).decode("utf-8").strip('\0')
        crlf = inputfile.read(2).decode("utf-8").strip('\0')
        comment = inputfile.read(256).decode("utf-8").strip('\0')
        header_description['File_CreatingTime'] = filetime
        if isprint:
            print(ident, formatversion, creatorname, creatorversion, filetime)
            print(comment)
        for j in range(len(dataitem)):
            tagIdx.append(struct.unpack("<i", inputfile.read(4))[0])
            header_description[dataitem[j]] = tagIdx[-1]
            if dataitem[j] == 'Numberofboards':
                numberofboards = tagIdx[-1]
            if isprint:
                print(dataitem[j], tagIdx[-1])
        for j in range(8):
            mapto = struct.unpack("<i", inputfile.read(4))[0]
            displaycurve = struct.unpack("<i", inputfile.read(4))[0]
        for j in range(3):
            start = struct.unpack("<f", inputfile.read(4))[0]
            step = struct.unpack("<f", inputfile.read(4))[0]
            end = struct.unpack("<f", inputfile.read(4))[0]
        repeatmode = struct.unpack("<i", inputfile.read(4))[0]
        repeatspercurve = struct.unpack("<i", inputfile.read(4))[0]
        repeattime = struct.unpack("<i", inputfile.read(4))[0]
        repeatwaittime = struct.unpack("<i", inputfile.read(4))[0]
        scriptname = inputfile.read(20).decode("utf-8").strip('\0')
        for j in range(numberofboards):
            tagIdx.append(inputfile.read(16).decode("utf-8").strip('\0'))
            tagIdx.append(inputfile.read(8).decode("utf-8").strip('\0'))
            tagIdx.append(struct.unpack("<i", inputfile.read(4))[0])
            tagIdx.append(struct.unpack("<i", inputfile.read(4))[0])
            tagIdx.append(struct.unpack("<i", inputfile.read(4))[0])
            tagIdx.append(struct.unpack("<i", inputfile.read(4))[0])
            tagIdx.append(struct.unpack("<i", inputfile.read(4))[0])
            tagIdx.append(struct.unpack("<i", inputfile.read(4))[0])
            tagIdx.append(struct.unpack("<f", inputfile.read(4))[0])
            tagIdx.append(struct.unpack("<i", inputfile.read(4))[0])
            tagIdx.append(struct.unpack("<i", inputfile.read(4))[0])
            header_description[dataitem_boards[0]] = tagIdx[-11]
            header_description[dataitem_boards[1]] = tagIdx[-10]
            header_description[dataitem_boards[2]] = tagIdx[-9]
            header_description[dataitem_boards[3]] = tagIdx[-8]
            header_description[dataitem_boards[4]] = tagIdx[-7]
            header_description[dataitem_boards[5]] = tagIdx[-6]
            header_description[dataitem_boards[6]] = tagIdx[-5]
            header_description[dataitem_boards[7]] = tagIdx[-4]
            header_description[dataitem_boards[8]] = tagIdx[-3]
            header_description[dataitem_boards[9]] = tagIdx[-2]
            header_description[dataitem_boards[10]] = tagIdx[-1]
            if isprint:
                print(dataitem_boards[0], tagIdx[-11])
                print(dataitem_boards[1], tagIdx[-10])
                print(dataitem_boards[2], tagIdx[-9])
                print(dataitem_boards[3], tagIdx[-8])
                print(dataitem_boards[4], tagIdx[-7])
                print(dataitem_boards[5], tagIdx[-6])
                print(dataitem_boards[6], tagIdx[-5])
                print(dataitem_boards[7], tagIdx[-4])
                print(dataitem_boards[8], tagIdx[-3])
                print(dataitem_boards[9], tagIdx[-2])
                print(dataitem_boards[10], tagIdx[-1])
            for j in range(4):
                inputtype = struct.unpack("<i", inputfile.read(4))[0]
                inputlevel = struct.unpack("<i", inputfile.read(4))[0]
                inputedge = struct.unpack("<i", inputfile.read(4))[0]
                cfdpresent = struct.unpack("<i", inputfile.read(4))[0]
                cfdlevel = struct.unpack("<i", inputfile.read(4))[0]
                cfdzcross = struct.unpack("<i", inputfile.read(4))[0]
        for j in range(len(dataitem_t2_header)):
            tagIdx.append(struct.unpack("<i", inputfile.read(4))[0])
            header_description[dataitem_t2_header[j]] = tagIdx[-1]
            if isprint:
                print(dataitem_t2_header[j], tagIdx[-1])
        for j in range(int(tagIdx[-1])):
            reserved = struct.unpack("<L", inputfile.read(4))[0]
        # time tags
        timetags = inputfile.read()
        with open(timetagsfile, "wb") as file:
            file.write(timetags)
    # write header
    write_ptuheader(inputfile=headerfile, acquisition_time_ms=header_description['Acquisitiontime_ms'],
                    timestamp=datetime.datetime.strptime(
                        header_description['File_CreatingTime'], "%d/%m/%y %H:%M:%S").timestamp(),
                    counts0=header_description['Inprate0'], counts1=header_description['Inprate1'],
                    total_records=header_description['Numrecords'], header=header)

    # combine the new header with timetags file
    combine_time_tags_header(headerfile=headerfile,
                             timetags=timetagsfile, outputfile=processedfile)
    os.remove(headerfile)
    os.remove(timetagsfile)
    print('Converted {0} to {1}'.format(originalfile, processedfile))


if __name__ == "__main__":
    originalfile = r'C:\Users\ZakKoong\Desktop\etp032023a_000.pt2'
    convert_pt2_to_ptu(originalfile, isprint=True,
                       header='picoharp_ptu_header_parameter.npz')
