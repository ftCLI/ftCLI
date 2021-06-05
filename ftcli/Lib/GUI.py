import os
import sys
from shutil import get_terminal_size

import click
from fontTools.misc.fixedTools import floatToFixedToStr
from fontTools.misc.textTools import num2binary
from fontTools.misc.timeTools import timestampToString
from fontTools.ttLib import TTFont

from ftcli.Lib.TTFontCLI import TTFontCLI
from ftcli.Lib.configHandler import (DEFAULT_WEIGHTS, DEFAULT_WIDTHS, configHandler)
from ftcli.Lib.csvHandler import csvHandler
from ftcli.Lib.utils import (getFontsList, wrapString)


class GUI(object):

    def csvEditor(self, config_file, csv_file):

        data = csvHandler(csv_file).getData()

        click.clear()

        print("\nCURRENT FILE:", csv_file, '\n')

        commands = {
            'c': 'Edit configuration file',
            'i': 'Init CSV data',
            'r': 'Recalc CSV data',
            'f': 'Set family name',
            'l': 'Edit single line',
            'p': 'Print names',
            'x': 'Exit'
        }

        if len(data) == 0:
            del commands['l']
            del commands['p']
            click.secho("{} contains no data".format(
                csv_file), fg='yellow')
        else:
            self.printCsv(csv_file)

        print('\nAVAILABLE COMMANDS:\n')

        choices = []
        for key, value in commands.items():
            print('{} : {}'.format(key, value))
            choices.append(key)

        message = "\nYour selection"
        choice = click.prompt(
            message, type=click.Choice(choices), show_choices=True)

        if choice == 'c':
            self.cfgEditor(config_file)
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'f':
            family_name = click.prompt("\nFamily name")
            for row in data:
                row['family_name'] = family_name
            csvHandler(csv_file).writeCSV(data)
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'r':
            source_string = click.prompt("\nSource string", type=click.Choice(
                choices=('fname', '1_1_2', '1_4', '1_6', '1_16_17', '1_18', '3_1_2', '3_4', '3_6', '3_16_17', 'cff_1',
                         'cff_2')), default='fname', show_choices=True, show_default=True)

            confirm = click.confirm(
                '\nDo you want to continue', default=True)
            if confirm:
                csvHandler(csv_file).recalcCSV(
                    config_file=config_file, family_name=None, source_string=source_string)
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'l':
            line_to_edit = click.prompt(
                "\nEnter line number", type=click.IntRange(1, len(data))) - 1
            line_data = data[line_to_edit]

            print('\nSelected file:', data[line_to_edit]['file_name'])

            is_bold = int(click.prompt(
                "\nIs bold", type=click.BOOL, default=line_data['is_bold']))
            is_italic = int(click.prompt(
                "\nIs italic", type=click.BOOL, default=line_data['is_italic']))
            is_oblique = int(click.prompt(
                "\nIs oblique", type=click.BOOL, default=line_data['is_oblique']))
            uswidthclass = click.prompt("\nusWidthClass", type=click.IntRange(
                1, 9), default=line_data['uswidthclass'])
            wdt = click.prompt("\nWidth (short word)",
                               default=line_data['wdt'])
            width = click.prompt("\nWidth (long word)",
                                 default=line_data['width'])
            usweightclass = click.prompt("\nusWeightClass", type=click.IntRange(
                1, 1000), default=line_data['usweightclass'])
            wgt = click.prompt("\nWeight (short word)",
                               default=line_data['wgt'])
            weight = click.prompt("\nWeight (long word)",
                                  default=line_data['weight'])
            family_name = click.prompt(
                "\nFamily name", default=line_data['family_name'])

            data[line_to_edit]['is_bold'] = is_bold
            data[line_to_edit]['is_italic'] = is_italic
            data[line_to_edit]['is_oblique'] = is_oblique
            data[line_to_edit]['uswidthclass'] = uswidthclass
            data[line_to_edit]['wdt'] = wdt
            data[line_to_edit]['width'] = width
            data[line_to_edit]['usweightclass'] = usweightclass
            data[line_to_edit]['wgt'] = wgt
            data[line_to_edit]['weight'] = weight
            data[line_to_edit]['family_name'] = family_name

            csvHandler(csv_file).writeCSV(data)
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'p':
            selected_line = click.prompt(
                "\nEnter line number", type=click.IntRange(1, len(data))) - 1
            selected_filename = data[selected_line]['file_name']
            selected_file = os.path.join(os.path.split(
                csv_file)[0], selected_filename)

            click.clear()
            self.printFtNames(selected_file, minimal=True)
            print()
            click.pause()
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'i':
            confirm = click.confirm(
                '\nAll changes will be lost. Do you want to continue', default=True)
            if confirm:
                csvHandler(csv_file).resetCSV(config_file=config_file)
            self.csvEditor(config_file=config_file, csv_file=csv_file)

        if choice == 'x':
            sys.exit()

    def cfgEditor(self, config_file):
        config = configHandler(config_file).getConfig()

        click.clear()
        print("\nCURRENT FILE:", config_file, '\n')
        self.printCfg(config_file)

        commands = {
            '1': 'Edit Weights',
            '2': 'Edit Widths',
            '3': 'Edit Italics',
            '4': 'Edit Obliques',
            'r': 'Reset default values',
            'x': 'Exit'}

        print('\nAVAILABLE COMMANDS:\n')
        choices = []
        message = "\nYour selection"
        for key, value in commands.items():
            print('{} : {}'.format(key, value))
            choices.append(key)

        choice = click.prompt(message, type=click.Choice(choices), show_choices=True)

        # Weights editor
        if choice == '1':
            self.__dictEditor(config_file, 'weights', 'usWeightClass', 1, 1000, DEFAULT_WEIGHTS)

        # Widths editor
        if choice == '2':
            self.__dictEditor(config_file, 'widths', 'usWidthClass', 1, 9, DEFAULT_WIDTHS)

        # Italics editor
        if choice == '3':
            print('\n[ITALICS]')
            v1 = click.prompt("\nShort word", default=config['italics'][0])
            v2 = click.prompt("\nLong word", default=config['italics'][1])
            lst = [v1, v2]
            lst.sort(key=len)
            config['italics'] = lst
            configHandler(config_file).saveConfig(config)
            self.cfgEditor(config_file)

        # Obliques editor
        if choice == '4':
            print('\n[OBLIQUES]')
            v1 = click.prompt("\nShort word", default=config['obliques'][0])
            v2 = click.prompt("\nLong word", default=config['obliques'][1])
            lst = [v1, v2]
            lst.sort(key=len)
            config['obliques'] = lst
            configHandler(config_file).saveConfig(config)
            self.cfgEditor(config_file)

        if choice == 'r':
            confirmation_message = "\nWARNING: values will be replaced with default ones. All changes will be lost." \
                                   "\n\nDo you want continue?"
            confirm = click.confirm(confirmation_message, default=True)
            if confirm is True:
                configHandler(config_file).resetConfig()
            self.cfgEditor(config_file)

        # Exit GUI
        if choice == 'x':
            return

    def printCfg(self, config_file):

        config = configHandler(config_file).getConfig()

        max_line_len = 40  # minimum len

        for k, v in config['widths'].items():
            current_line_len = len(f'{k} : {v[0]}, {v[1]}')
            if current_line_len > max_line_len:
                max_line_len = current_line_len

        for k, v in config['weights'].items():
            current_line_len = len(f'{k} : {v[0]}, {v[1]}')
            if current_line_len > max_line_len:
                max_line_len = current_line_len

        for v in config['italics']:
            current_line_len = max(
                len(f'Short word : {v}'), len(f'Long word : {v}')
            )
            if current_line_len > max_line_len:
                max_line_len = current_line_len

        for v in config['obliques']:
            current_line_len = max(
                len(f'Short word : {v}'), len(f'Long word : {v}')
            )
            if current_line_len > max_line_len:
                max_line_len = current_line_len

        # Add the 2 spaces needed to place "|" at the beginning of the strings
        max_line_len += 2
        sep_line = '+' + '-' * max_line_len + '+'

        print(sep_line)
        print("| WEIGHTS".ljust(max_line_len, ' '), '|')
        print(sep_line)
        for k, v in config['weights'].items():
            print(f'| {k} : {v[0]}, {v[1]}'.ljust(max_line_len, ' '), '|')
        print(sep_line)

        print("| WIDTHS".ljust(max_line_len, ' '), '|')
        print(sep_line)
        for k, v in config['widths'].items():
            print(f'| {k} : {v[0]}, {v[1]}'.ljust(max_line_len, ' '), '|')
        print(sep_line)

        print('| ITALICS'.ljust(max_line_len, ' '), '|')
        print(sep_line)
        print(f'| Short word : {config["italics"][0]}'.ljust(max_line_len, ' '), '|')
        print(f'| Long word  : {config["italics"][1]}'.ljust(max_line_len, ' '), '|')
        print(sep_line)

        print('| OBLIQUES'.ljust(max_line_len, ' '), '|')
        print(sep_line)
        print(f'| Short word : {config["obliques"][0]}'.ljust(max_line_len, ' '), '|')
        print(f'| Long word  : {config["obliques"][1]}'.ljust(max_line_len, ' '), '|')
        print(sep_line)

    def printCsv(self, csv_file):

        data = csvHandler(csv_file).getData()

        # Get the maximum field len
        count = 0
        max_filename_len = 9  # length of the "File Name" string
        max_family_len = 11  # length of the "Family Name" string
        max_width_len = 5  # length of the "Width" string
        max_weight_len = 6  # length of the "Weight" string
        max_slope_len = 5  # length of the "Slope" string

        for row in data:

            count += 1

            current_filename_len = len(row['file_name'])
            if current_filename_len > max_filename_len:
                max_filename_len = current_filename_len

            current_family_len = len(f'{row["family_name"]}')
            if current_family_len > max_family_len:
                max_family_len = current_family_len

            current_width_len = len(f'{row["uswidthclass"]}: {row["wdt"]}, {row["width"]}')
            if current_width_len > max_width_len:
                max_width_len = current_width_len

            current_weight_len = len(f'{row["usweightclass"]}: {row["wgt"]}, {row["weight"]}')
            if current_weight_len > max_weight_len:
                max_weight_len = current_weight_len

            current_slope_len = len(f'{row["slp"]}, {row["slope"]}')
            if current_slope_len > max_slope_len:
                max_slope_len = current_slope_len

        count_len = len(str(count))
        max_filename_len = min(max_filename_len, 40)
        max_family_len = min(max_family_len, 30)
        max_width_len = min(max_width_len, 30)
        max_weight_len = min(max_weight_len, 30)
        max_slope_len = min(max_slope_len, 20)

        # Set the sep line
        sep_line = ('+' + '-' * (count_len + 2) + '+' +
                    '-' * (max_filename_len + 2) + '+' +
                    3 * ('-' * 3 + '+') +
                    '-' * (max_family_len + 2) + '+' +
                    '-' * (max_width_len + 2) + '+' +
                    '-' * (max_weight_len + 2) + '+' +
                    '-' * (max_slope_len + 2) + '+'
                    )

        print(sep_line)

        count = 0

        # Print the header
        print(
            '|', "#".rjust(count_len, ' '), '|',
            "File Name".ljust(max_filename_len, ' '), '|',
            'B | I | O | ',
            "Family Name".ljust(max_family_len, ' '), '|',
            "Width".ljust(max_width_len, ' '), '|',
            "Weight".ljust(max_weight_len, ' '), '|',
            "Slope".ljust(max_slope_len, ' '), '|',
        )

        print(sep_line)

        # Print formatted data
        for row in data:
            count += 1
            print(
                '|', str(count).rjust(count_len, ' '), '|',
                row['file_name'].ljust(max_filename_len, ' ')[0:max_filename_len], '|',
                row['is_bold'], '|', row['is_italic'], '|', row['is_oblique'], '|',
                row['family_name'].ljust(max_family_len, ' ')[0:max_family_len], '|',
                f'{row["uswidthclass"]}: {row["wdt"]}, {row["width"]}'.ljust(max_width_len, ' ')[0:max_width_len], '|',
                f'{row["usweightclass"]}: {row["wgt"]}, {row["weight"]}'.ljust(
                    max_weight_len, ' ')[0:max_weight_len], '|',
                f'{row["slp"]}, {row["slope"]}'.ljust(
                    max_slope_len, ' ') if len(row['slope']) > 0 else ' '.ljust(max_slope_len), '|',
            )

        print(sep_line)

    def printFtInfo(self, input_path):

        terminal_width = min(90, get_terminal_size()[0] - 1)
        files = getFontsList(input_path)
        length = 17

        for f in files:

            try:
                font = TTFontCLI(f)
                print("-" * terminal_width)
                print("BASIC INFORMATION:")
                print("-" * terminal_width)

                print("Flavor".ljust(length), end=" : ")
                if 'CFF ' in font:
                    print("PostScript")
                else:
                    print("TrueType")

                print("Glyphs number".ljust(length), ":", font['maxp'].numGlyphs)
                print("Date created".ljust(length), ":", timestampToString(font['head'].created))
                print("Date modified".ljust(length), ":", timestampToString(font['head'].modified))
                print("usWeightClass".ljust(length), ":", str(font['OS/2'].usWeightClass))
                print("usWidthClass".ljust(length), ":", str(font['OS/2'].usWidthClass))
                print("Font is bold".ljust(length), ":", str(font.isBold()))
                print("Font is italic".ljust(length), ":", str(font.isItalic()))
                print("Font is oblique".ljust(length), ":", str(font.isOblique()))
                print("Italic angle".ljust(length), ":", str(font['post'].italicAngle))

                embedLevel = font['OS/2'].fsType
                if embedLevel == 0:
                    string = "Everything is allowed"
                elif embedLevel == 2:
                    string = "Embedding of this font is not allowed"
                elif embedLevel == 4:
                    string = "Only printing and previewing of the document is allowed"
                elif embedLevel == 8:
                    string = "Editing of the document is allowed"
                else:
                    string = "Unknown"

                print("Embedding".ljust(length), ":", str(
                    font['OS/2'].fsType), "(" + string + ")")

                print("-" * terminal_width)
                print("VERSION AND IDENTIFICATION")
                print("-" * terminal_width)
                print("Version".ljust(length), ":", floatToFixedToStr(font['head'].fontRevision, precisionBits=12))
                print("Unique identifier".ljust(length), ":", font['name'].getName(3, 3, 1, 0x409))
                print("Vendor code".ljust(length), ":", font['OS/2'].achVendID)

                print("-" * terminal_width)
                print("METRICS AND DIMENSIONS")
                print("-" * terminal_width)
                print("unitsPerEm".ljust(length), ":", font['head'].unitsPerEm)
                print("Font BBox".ljust(length), ":", "(" + str(font['head'].xMin) + ", " + str(
                    font['head'].yMin) + ")", "(" + str(font['head'].xMax) + ", " + str(font['head'].yMax) + ")")

                print("\n[OS/2] table")
                print((" " * 4 + "TypoAscender").ljust(length), ":", font['OS/2'].sTypoAscender)
                print((" " * 4 + "TypoDescender").ljust(length), ":", font['OS/2'].sTypoDescender)
                print((" " * 4 + "TypoLineGap").ljust(length), ":", font['OS/2'].sTypoLineGap)
                print((" " * 4 + "WinAscent").ljust(length), ":", font['OS/2'].usWinAscent)
                print((" " * 4 + "WinDescent").ljust(length), ":", font['OS/2'].usWinDescent)
                print()

                try:
                    print((" " * 4 + "x height").ljust(length), ":", font['OS/2'].sxHeight)
                except Exception as e:
                    click.secho('ERROR: {}'.format(e), fg='red')

                try:
                    print((" " * 4 + "Caps height").ljust(length),
                          ":", font['OS/2'].sCapHeight)
                except Exception as e:
                    click.secho('ERROR: {}'.format(e), fg='red')

                try:
                    print((" " * 4 + "Subscript").ljust(length), ":",
                          "X pos = " +
                          str(font['OS/2'].ySubscriptXOffset) + ",",
                          "Y pos = " +
                          str(font['OS/2'].ySubscriptYOffset) + ",",
                          "X size = " +
                          str(font['OS/2'].ySubscriptXSize) + ",",
                          "Y size = " + str(font['OS/2'].ySubscriptYSize)
                          )
                except Exception as e:
                    click.secho('ERROR: {}'.format(e), fg='red')

                try:
                    print((" " * 4 + "Superscript").ljust(length), ":",
                          "X pos = " +
                          str(font['OS/2'].ySuperscriptXOffset) + ",",
                          "Y pos = " +
                          str(font['OS/2'].ySuperscriptYOffset) + ",",
                          "X size = " +
                          str(font['OS/2'].ySuperscriptXSize) + ",",
                          "Y size = " + str(font['OS/2'].ySuperscriptYSize)
                          )
                except Exception as e:
                    click.secho('ERROR: {}'.format(e), fg='red')

                print("\n[hhea] table")
                print((" " * 4 + "Ascent").ljust(length), ":", font['hhea'].ascent)
                print((" " * 4 + "Descent").ljust(length), ":", font['hhea'].descent)
                print((" " * 4 + "LineGap").ljust(length), ":", font['hhea'].lineGap)

                print("\n[head] table")

                print((" " * 4 + "xMin").ljust(length), ":", font['head'].xMin)
                print((" " * 4 + "yMin").ljust(length), ":", font['head'].yMin)
                print((" " * 4 + "xMax").ljust(length), ":", font['head'].xMax)
                print((" " * 4 + "yMax").ljust(length), ":", font['head'].yMax)

                print("-" * terminal_width)
                print('FONT TABLES')
                print("-" * terminal_width)
                print(", ".join([k.strip() for k in font.keys()]))
                print("-" * terminal_width)

            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

    def printFtList(self, input_path):

        files = getFontsList(input_path)

        max_filename_len = 9  # length of the string "File Name"

        for f in files:
            current_filename_len = len(os.path.basename(f))
            if current_filename_len > max_filename_len:
                max_filename_len = current_filename_len

        max_filename_len = min(max_filename_len, 60)  # Limit the printed file name string to 60 characters

        sep_line = '+' + '-' * (max_filename_len + 2) + '+' + '-' * 14 + '+' + '-' * 15 + '+' + '-' * 8 + '+' +\
                   '-' * 10 + '+' + '-' * 11 + '+'

        print(sep_line)
        print('|', 'File Name'.ljust(max_filename_len, ' '),
              '|', 'usWidthClass', '|', 'usWeightClass', '|', 'isBold', '|', 'isItalic', '|', 'isOblique', '|')
        print(sep_line)

        usWidthClassList = []
        usWeightClassList = []

        for f in files:
            try:
                font = TTFontCLI(f, recalcTimestamp=False)
                filename = os.path.basename(f)
                usWeightClass = font['OS/2'].usWeightClass
                usWidthClass = font['OS/2'].usWidthClass
                isBold = font.isBold()
                isItalic = font.isItalic()
                isOblique = font.isOblique()
                print('|', filename.ljust(max_filename_len, ' ')[0:max_filename_len], '|',
                      str(usWidthClass).rjust(12), '|',
                      str(usWeightClass).rjust(13), '|',
                      str(int(isBold)).rjust(6), '|',
                      str(int(isItalic)).rjust(8), '|',
                      str(int(isOblique)).rjust(9), '|',
                      )

                if usWeightClass not in usWeightClassList:
                    usWeightClassList.append(usWeightClass)
                if usWidthClass not in usWidthClassList:
                    usWidthClassList.append(usWidthClass)
            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

        usWidthClassList.sort()
        usWeightClassList.sort()
        print(sep_line)

        print()
        print(" Widths  :", str(usWidthClassList)[1:-1])
        print(" Weights :", str(usWeightClassList)[1:-1])

    def printFtName(self, input_path, name_id, indent=32, max_lines=None):

        terminal_width = min(90, get_terminal_size()[0] - 1)

        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                names = font['name'].names
                platform_specs = []
                for name in names:
                    platform_spec = [name.platformID,
                                     name.platEncID, name.langID]
                    if platform_spec not in platform_specs:
                        platform_specs.append(platform_spec)

                print('-' * terminal_width)
                print('FILE NAME: {}'.format(os.path.basename(f)))
                print('-' * terminal_width)

                for platform_spec in platform_specs:
                    platformID = platform_spec[0]
                    platEncID = platform_spec[1]
                    langID = platform_spec[2]

                    for name in names:
                        if name.nameID == name_id and name.platformID == platformID and name.platEncID == platEncID \
                                and name.langID == langID:
                            string = "platform: ({}, {}, {}),  nameID{} : {}".format(
                                platformID, platEncID, langID, name.nameID, name.toUnicode())

                            string = wrapString(string, indent, max_lines, terminal_width)
                            print(string)
                print()
            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

    def printFtNames(self, input_path, minimal=False, indent=32, max_lines=None):

        terminal_width = min(90, get_terminal_size()[0] - 1)

        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                names = font['name'].names
                platform_specs = []
                for name in names:
                    platform_spec = [name.platformID,
                                     name.platEncID, name.langID]
                    if platform_spec not in platform_specs:
                        platform_specs.append(platform_spec)

                print('\nCURRENT FILE: {}\n'.format(f))
                print('-' * terminal_width)

                # NAME TABLE
                print('NAME TABLE')
                print('-' * terminal_width)

                for platform_spec in platform_specs:

                    platformID = platform_spec[0]
                    platEncID = platform_spec[1]
                    langID = platform_spec[2]

                    print(
                        'platformID: {} ({}) | platEncID: {} | langID: {}'.format(platformID, PLATFORMS.get(platformID),
                                                                                  platEncID, langID)
                    )
                    print('-' * terminal_width)

                    for name in names:
                        try:
                            if name.platformID == platformID and name.platEncID == platEncID and name.langID == langID:
                                if name.nameID in NAMEIDS:
                                    string = "{:5d}".format(
                                        name.nameID) + " : " + "{0:<21}".format(
                                        NAMEIDS[name.nameID]) + " : " + name.toUnicode()
                                else:
                                    string = "{:5d}".format(
                                        name.nameID) + " : " + "{0:<21}".format(name.nameID) + " : " + name.toUnicode()

                                string = wrapString(
                                    string, indent, max_lines, terminal_width)

                                if minimal is False:
                                    print(string)
                                else:
                                    if name.nameID in [1, 2, 3, 4, 5, 6, 16, 17, 18, 21, 22]:
                                        print(string)
                        except Exception as e:
                            click.secho('nameID {} ERROR: {}'.format(name.nameID, e), fg='red')

                    print('-' * terminal_width)

                # CFF NAMES
                if 'CFF ' in font:
                    print('CFF NAMES')
                    print('-' * terminal_width)

                    otFont = font['CFF '].cff

                    try:
                        string = "{0:<29}".format(' CFFFont name') + ' : ' + str(font['CFF '].cff.fontNames[0])
                        string = wrapString(string, indent, max_lines, terminal_width)
                        print(string)
                    except:
                        pass

                    if minimal is False:
                        try:
                            string = "{0:<29}".format(' version') + ' : ' + str(otFont.topDictIndex[0].version)
                            string = wrapString(string, indent, max_lines, terminal_width)
                            print(string)
                        except:
                            pass

                        try:
                            string = "{0:<29}".format(' Notice') + ' : ' + str(otFont.topDictIndex[0].Notice)
                            string = wrapString(string, indent, max_lines, terminal_width)
                            print(string)
                        except:
                            pass

                        try:
                            string = "{0:<29}".format(' Copyright') + ' : ' + str(otFont.topDictIndex[0].Copyright)
                            string = wrapString(string, indent, max_lines, terminal_width)
                            print(string)
                        except:
                            pass

                    try:
                        string = "{0:<29}".format(' FullName') + ' : ' + str(otFont.topDictIndex[0].FullName)
                        string = wrapString(string, indent, max_lines, terminal_width)
                        print(string)
                    except:
                        pass

                    try:
                        string = "{0:<29}".format(' FamilyName') + ' : ' + str(otFont.topDictIndex[0].FamilyName)
                        string = wrapString(string, indent, max_lines, terminal_width)
                        print(string)
                    except:
                        pass

                    try:
                        string = "{0:<29}".format(' Weight') + ' : ' + str(otFont.topDictIndex[0].Weight)
                        string = wrapString(string, indent, max_lines, terminal_width)
                        print(string)
                    except:
                        pass

                    print("-" * terminal_width)
            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

    def printTableHead(self, input_path):

        terminal_width = get_terminal_size()[0] - 1
        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                print('\nCURRENT FILE: {}'.format(f))
                print('-' * terminal_width)

                for name, value in font['head'].__dict__.items():
                    if name == 'tableTag':
                        print(name, value)
                        print("-" * terminal_width)
                        print()
                    elif name in ("created", "modified"):
                        print('    <{} value="{}"/>'.format(name, timestampToString(value)))
                    elif name in ("magicNumber", "checkSumAdjustment"):
                        if value < 0:
                            value = value + 0x100000000
                        value = hex(value)
                        if value[-1:] == "L":
                            value = value[:-1]
                        print('    <{} value="{}"/>'.format(name, str(value)))
                    elif value in ("macStyle", "flags"):
                        print('    <{} value="{}"/>'.format(name, num2binary(value)))
                    else:
                        print('    <{} value="{}"/>'.format(name, value))
                print()
                print("-" * terminal_width)
            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

    def printTableOS2(self, input_path):

        terminal_width = get_terminal_size()[0] - 1
        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                print('\nCURRENT FILE: {}'.format(f))
                print('-' * terminal_width)
                for name, value in font['OS/2'].__dict__.items():
                    if name == 'tableTag':
                        print(name, value)
                        print("-" * terminal_width)
                        print()
                    elif name == 'panose':
                        print('    <' + name + '>')
                        for panosename, v in font['OS/2'].panose.__dict__.items():
                            print('        <' + panosename + ' value="' + str(v) + '"/>')
                        print('    </' + name + '>')
                    elif name in ("ulUnicodeRange1", "ulUnicodeRange2", "ulUnicodeRange3", "ulUnicodeRange4",
                                  "ulCodePageRange1", "ulCodePageRange2"):
                        print('    <' + name + ' value="' + num2binary(value) + '"/>')
                    elif name in ("fsType", "fsSelection"):
                        print('    <' + name + ' value="' + num2binary(value, 16) + '"/>')
                    elif name == "achVendID":
                        print('    <' + name + ' value="' + repr(value)[1:-1] + '"/>')
                    else:
                        print('    <' + name + ' value="' + str(value) + '"/>')
                print()
                print("-" * terminal_width)
            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

    def listTables(self, input_path):

        terminal_width = get_terminal_size()[0] - 1
        files = getFontsList(input_path)

        for f in files:
            try:
                font = TTFont(f)
                print('-' * terminal_width)
                print('CURRENT FILE: {}'.format(os.path.basename(f)))
                print('-' * terminal_width)
                print(", ".join([k.strip() for k in font.keys()]))
                print()
            except Exception as e:
                click.secho('ERROR: {}'.format(e), fg='red')

    def __dictEditor(self, config_file, input_dict, key_name, min_key, max_key, default_dict):

        config = configHandler(config_file).getConfig()

        max_line_len = 40
        for k, v in config[input_dict].items():
            current_line_len = len(f'{k} : {v[0]}, {v[1]}')
            if current_line_len > max_line_len:
                max_line_len = current_line_len

        max_line_len += 2

        sep_line = ('+' + '-' * max_line_len + '+')

        keys_list = []
        keys_list = [k for k in config[input_dict] if k not in keys_list]

        click.clear()
        print("\nCURRENT FILE:", config_file, "\n")
        print(sep_line)
        print(f'| {input_dict.upper()}'.ljust(max_line_len, ' '), '|')
        print(sep_line)
        for k, v in config[input_dict].items():
            print(f'| {k} : {v[0]}, {v[1]}'.ljust(max_line_len, ' '), '|')
        print(sep_line)

        print('\nAVAILABLE COMMANDS:\n')

        commands = {
            'a': 'Add/Edit item',
            'd': 'Delete item',
            'r': 'Reset default values',
            'x': 'Main menu'
        }
        message = "\nYour selection"
        choices = []
        for key, value in commands.items():
            print('[{}] : {}'.format(key, value))
            choices.append(key)

        choice = click.prompt(
            message, type=click.Choice(choices), show_choices=True)

        if choice == 'a':

            print()
            k = click.prompt(key_name, type=click.IntRange(min_key, max_key))

            if str(k) in keys_list:
                old_key = k
                old_v1 = config[input_dict][str(k)][0]
                old_v2 = config[input_dict][str(k)][1]
                new_key = click.prompt("\nnew {} value".format(key_name), type=click.IntRange(min_key, max_key),
                                       default=old_key)
                v1 = str(click.prompt("\nShort word", default=old_v1))
                v2 = str(click.prompt("\nLong word", default=old_v2))
                del config[input_dict][str(k)]
            else:
                new_key = k
                v1 = str(click.prompt("\nShort word"))
                v2 = str(click.prompt("\nLong word"))

            lst = [v1, v2]
            lst.sort(key=len)
            config[input_dict][str(new_key)] = lst
            configHandler(config_file).saveConfig(config)
            self.__dictEditor(config_file, input_dict, key_name, min_key,
                              max_key, default_dict)

        if choice == 'd':

            print()
            k = click.prompt("{} value".format(key_name), type=click.IntRange(min_key, max_key))

            if str(k) in keys_list:
                confirmation_message = "\nDo you want continue?"
                confirm = click.confirm(confirmation_message, default=True)
                if confirm is True:
                    del config[input_dict][str(k)]
                    configHandler(config_file).saveConfig(config)
            else:
                print()
                click.pause(key_name + str(k) +
                            ' value not found. Press any key to continue')

            self.__dictEditor(config_file, input_dict, key_name, min_key,
                              max_key, default_dict)

        if choice == 'r':
            confirmation_message = "\nWARNING: values will be replaced with default ones. All changes will be lost." \
                                   "\n\nDo you want continue?"
            confirm = click.confirm(confirmation_message, default=True)

            if confirm is True:
                config[input_dict] = default_dict
                configHandler(config_file).saveConfig(config)

            self.__dictEditor(config_file, input_dict, key_name, min_key,
                              max_key, default_dict)

        if choice == 'x':
            self.cfgEditor(config_file)


NAMEIDS = {
    0: 'Copyright Notice',
    1: 'Family name',
    2: 'Subfamily name',
    3: 'Unique identifier',
    4: 'Full font name',
    5: 'Version string',
    6: 'PostScript name',
    7: 'Trademark',
    8: 'Manufacturer Name',
    9: 'Designer',
    10: 'Description',
    11: 'URL Vendor',
    12: 'URL Designer',
    13: 'License Description',
    14: 'License Info URL',
    15: 'Reserved',
    16: 'Typographic Family',
    17: 'Typographic Subfamily',
    18: 'Compatible Full (Mac)',
    19: 'Sample text',
    20: 'PS CID findfont name',
    21: 'WWS Family Name',
    22: 'WWS Subfamily Name',
    23: 'Light Backgr Palette',
    24: 'Dark Backgr Palette',
    25: 'Variations PSName Pref'}

PLATFORMS = {
    0: 'Unicode',
    1: 'Macintosh',
    2: 'ISO (deprecated)',
    3: 'Windows',
    4: 'Custom'}
