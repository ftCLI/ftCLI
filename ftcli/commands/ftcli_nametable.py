import click
from ftcli.Lib.TTFontCLI import TTFontCLI
from ftcli.Lib.utils import getFontsList, makeOutputFileName


@click.group()
def printLanguageCodes():
    pass


@printLanguageCodes.command()
def lang_help():
    """Prints available languages that can be used with the 'setname' and 'delname' commands
    """
    from fontTools.ttLib.tables._n_a_m_e import (_MAC_LANGUAGES, _WINDOWS_LANGUAGES)
    print('\n[WINDOWS LANGUAGES]')
    winlist = []
    for v in _WINDOWS_LANGUAGES.values():
        winlist.append(v)
    winlist.sort()
    print(winlist)
    print('\n[MAC LANGUAGES]')
    maclist = []
    for v in _MAC_LANGUAGES.values():
        maclist.append(v)
    maclist.sort()
    print(maclist)


@click.group()
def winToMac():
    pass


@winToMac.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t '
                   'exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By '
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of file'
                   'name). By default, files are overwritten.')
def fill_mac_names(input_path, output_dir, recalc_timestamp, overwrite):
    """Copies namerecords from Windows table to Macintosh table.
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            font = TTFontCLI(f, recalcTimestamp=recalc_timestamp)
            font.win2mac()
            output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
            font.save(output_file)
            click.secho('%s saved' % f, fg='green')
        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')


@click.group()
def deleteMacNames():
    pass


@deleteMacNames.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-ex', '--exclude-namerecords', type=click.IntRange(0, 32767), multiple=True,
              help="Name IDs to ignore. The specified name IDs won't be deleted. This option can be repeated"
                   "(example: -ex 3 -ex 5 -ex 6...).")
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t '
                   'exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By '
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of file'
                   'name). By default, files are overwritten.')
def del_mac_names(input_path, exclude_namerecords, output_dir, recalc_timestamp, overwrite):
    """Deletes all namerecords in platformID 1.

    According to Apple (https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6name.html), "names with
    platformID 1 were required by earlier versions of macOS. Its use on modern platforms is discouraged. Use names with
    platformID 3 instead for maximum compatibility. Some legacy software, however, may still require names with
    platformID 1, platformSpecificID 0".

    USAGE:

        ftcli nametable del-mac-names INPUT_PATH [OPTIONS]

    Use the -ex / --exclude-namerecords option to prevent certain namerecords to be deleted:

        ftcli nametable del-mac-names INPUT_PATH -ex 1

    The -ex / --exclude-namerecords option can be repeated to exclude from deletion more than one namerecord:

        ftcli nametable del-mac-names INPUT_PATH -ex 1 -ex 3 -ex 6

    Input path can be a font or a folder with fonts.
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            font = TTFontCLI(f, recalcTimestamp=recalc_timestamp)
            font.delMacNames(exclude_namerecords=exclude_namerecords)
            output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
            font.save(output_file)
            click.secho('%s saved' % f, fg='green')
        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')

# set-name


@click.group()
def setNameRecord():
    pass


@setNameRecord.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-n', '--name-id', type=click.IntRange(0, 32767), help="nameID (Integer between 1 and 32767)")
@click.option("-p", "--platform", type=click.Choice(choices=["win", "mac"]),
              help="platform [win, mac]. If it's not specified, name will be written in both tables.")
@click.option('-l', '--language', default="en", show_default=True, help="language")
@click.option('-s', '--string', required=True, help='string')
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t'
                   'exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By'
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of file'
                   'name). By default, files are overwritten.')
def set_name(input_path, name_id, platform, language, string, output_dir, recalc_timestamp, overwrite):
    """Writes the specified namerecord in the name table.

    If the namerecord is not present, it will be created. If it already exists, will be overwritten.

    If name_id parameter is not specified, the first available nameID will be used.

    By default, the namerecord will be written both in platformID 1 (Macintosh) and platformID 3 (Windows) tables. Use
    -p/--platform-id [win|mac] option to write the namerecord only in the specified platform.

    Use the -l/--language option to write the namerecord in a language different than 'en'. Use 'ftcli nametable
    langhelp' to display available languages.
    """

    windows = False if platform == "mac" else True
    mac = False if platform == "win" else True

    files = getFontsList(input_path)

    for f in files:
        try:
            font = TTFontCLI(f, recalcTimestamp=recalc_timestamp)
            font.setMultilingualName(nameID=name_id, language=language, string=string, windows=windows, mac=mac)

            output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
            font.save(output_file)
            click.secho('%s saved' % output_file, fg='green')
        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')

# copy-name


@click.group()
def copyNameRecord():
    pass


@copyNameRecord.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-s', '--source-name', type=(click.Choice(choices=["win", "mac"]), click.IntRange(0, 32767)),
              required=True, help="source platformID [win|mac] and nameID (1-32767).")
@click.option("-d", "--dest-name", type=(click.Choice(choices=["win", "mac"]), click.IntRange(0, 32767)),
              required=True, help="destination platformID [win|mac] and nameID (1-32767)")
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t'
                   'exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By'
                   'default, original timestamp is kept.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of file'
                   'name). By default, files are overwritten.')
def copy_name(input_path, source_name, dest_name, output_dir, recalc_timestamp, overwrite):
    """Copies a namerecord string to another namerecord.

    Usage example:

    ftcli nametable copy-name INPUT_PATH --source-name win 6 --dest-name mac 6
    """

    # The program exits if we try to copy a namerecord on itself.
    if dest_name == source_name:
        click.secho('ERROR: source name and destination name are the same', fg='red')
        exit()

    source_platform = source_name[0]
    source_nameID = source_name[1]
    dest_platform = dest_name[0]
    dest_nameID = dest_name[1]

    source_platID, source_platEncID, source_langID = (1, 0, 0x0) if source_platform == 'mac' else (3, 1, 0x409)

    mac = True if dest_platform == 'mac' else False
    win = True if dest_platform == 'win' else False

    files = getFontsList(input_path)

    for f in files:
        try:
            font = TTFontCLI(f, recalcTimestamp=recalc_timestamp)
            name_string = font['name'].getName(source_nameID, source_platID, source_platEncID,
                                               source_langID).toUnicode()

            font.setMultilingualName(nameID=dest_nameID, string=name_string, windows=win, mac=mac)

            output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
            font.save(output_file)
            click.secho('%s saved' % output_file, fg='green')

        except AttributeError:
            click.secho('ERROR: nameID {} not found in {} table'.format(source_nameID, source_platform), fg='red')

        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')


# delname


@click.group()
def delNameRecord():
    pass


@delNameRecord.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option('-n', '--name-id', type=click.IntRange(0, 32767), required=True,
              help="nameID (Integer between 1 and 32767)")
@click.option("-p", "--platform", type=click.Choice(choices=["win", "mac"]),
              help="platform [win, mac]. If no platform is specified, the namerecord will be deleted from both tables.")
@click.option('-l', '--language', default="en", show_default=True,
              help="Specify the name ID language (eg: 'de'), or use 'ALL' to delete the name ID from all languages.")
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t'
                   'exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By'
                   'default, timestamp is not recalculated.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of file'
                   'name). By default, files are overwritten.')
def del_name(input_path, name_id, platform, language, output_dir, recalc_timestamp, overwrite):
    """Deletes the specified nemerecord from the name table.

    Use the -l/--language option to delete a namerecord in a language different than 'en'. Use 'ftcli nametable
    langhelp' to display available languages.

    Use '-l ALL' to delete the name ID from all languages.
    """
    windows = False if platform == "mac" else True
    mac = False if platform == "win" else True

    files = getFontsList(input_path)

    for f in files:
        try:
            font = TTFontCLI(f, recalcTimestamp=recalc_timestamp)
            font.delMultilingualName(name_id, language=language, windows=windows, mac=mac)
            output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
            font.save(output_file)
            click.secho('%s saved' % output_file, fg='green')
        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')


# findreplace


@click.group()
def findReplace():
    pass


@findReplace.command()
@click.argument('input_path', type=click.Path(exists=True, resolve_path=True))
@click.option("-os", "--old-string", required=True,
              help="old string")
@click.option('-ns', '--new-string', required=True,
              help="new string", show_default=True)
@click.option('-n', '--name-id', type=click.IntRange(0, 32767),
              help="nameID (Integer between 1 and 32767). If not specified, the string will be replaced in all"
                   "namerecords.")
@click.option("-p", "--platform", type=click.Choice(choices=["win", "mac"]),
              help="platform [win, mac]. If no platform is specified, the string will be replaced in both tables.")
@click.option('-cff', '--fix-cff', is_flag=True,
              help="Replaces the string in the CFF table.")
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help='Specify the output directory where the output files are to be saved. If output_directory doesn\'t'
                   'exist, will be created. If not specified, files are saved to the same folder.')
@click.option('--recalc-timestamp/--no-recalc-timestamp', default=False, show_default=True,
              help='Keep the original font \'modified\' timestamp (head.modified) or set it to current time. By'
                   'default, timestamp is not recalculated.')
@click.option('--overwrite/--no-overwrite', default=True, show_default=True,
              help='Overwrite existing output files or save them to a new file (numbers are appended at the end of file'
                   'name). By default, files are overwritten.')
def find_repl(input_path, old_string, new_string, name_id, platform, fix_cff, output_dir, recalc_timestamp, overwrite):
    """Replaces a string in the name table with a new string.

    If the '-cff' option is passed, the string will be replaced in the 'CFF' table too.

    ftcli nametable replace .\\fonts\\MyFont-Black.otf --os "Black" --ns "Heavy" --cff

    To simply remove a string, use an empty string as new string:

    ftcli nametable replace .\\fonts\\MyFont-Black.otf --os "RemoveMe" --ns ""
    """

    files = getFontsList(input_path)

    for f in files:
        try:
            font = TTFontCLI(f, recalcTimestamp=recalc_timestamp)
            fix_count = font.findReplace(
                old_string, new_string, fixCFF=fix_cff, nameID=name_id, platform=platform)

            if fix_count > 0:
                output_file = makeOutputFileName(f, outputDir=output_dir, overWrite=overwrite)
                font.save(output_file)
                click.secho('%s --> saved' % output_file, fg='green')
            else:
                click.secho('%s --> no changes made' % f, fg='yellow')
        except Exception as e:
            click.secho('ERROR: {}'.format(e), fg='red')


cli = click.CommandCollection(sources=[
    setNameRecord, delNameRecord, copyNameRecord, findReplace, winToMac, deleteMacNames, printLanguageCodes], help="""
A command line tool to add, delete and edit namerecords.
    """)
