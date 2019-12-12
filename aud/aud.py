#!/usr/bin/python3

from os.path import join, abspath, exists, isdir
from os import listdir, mkdir
from shutil import copy2, move
from zipfile import ZipFile
import datetime
from random import randrange

from colorama import Fore, Back

# import ffmpeg
from pydub import AudioSegment
from pydub.utils import mediainfo
from pydub.effects import (
    normalize,
    strip_silence,
    invert_phase,
    low_pass_filter,
    high_pass_filter,
    apply_gain_stereo,
)


class Dir(object):

    ########################################
    ##         UNDERSCORE METHODS         ##
    ########################################

    def __init__(
        self, _directory_path, _extensions=[], _logfile="", _blacklist=[], _whitelist=[]
    ):
        self.verbose = False
        self.verbose_log("Instantiating: " + abspath(_directory_path))
        self.all_files = []
        self.filtered_files = []
        self.extensions = _extensions
        self.blacklist = _blacklist
        self.whitelist = _whitelist
        self.logfile = _logfile
        self.directory_path = abspath(_directory_path)

        self.update()
        return

    def __str__(self):
        return self.directory_path

    def __len__(self):
        return len(self.filtered_files)

    def __iter__(self):
        self.cur = 0
        return self

    def __next__(self):
        if self.cur >= len(self.filtered_files):
            raise StopIteration
        else:
            self.cur += 1
            return self.filtered_files[self.cur - 1]

    ########################################
    ##              HELPERS               ##
    ########################################

    def get_all(self):
        self.verbose_log("Getting all filtered files")
        return self.filtered_files

    def get_single(self, num):
        self.verbose_log("Getting a single filtered file by number")
        return self.filtered_files[num]

    def log(self, message):
        self.verbose_log("Logging: " + message)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")
        if not self.logfile:
            return False
        try:
            with open(self.logfile, "a") as file:
                file.write("{}: {}\n".format(timestamp, message))
        except:
            return False
        return True

    def update(self):
        self.verbose_log("Updating filtered selection")
        self.all_files = listdir(self.directory_path)
        # sort if you want
        self.all_files = sorted(self.all_files)
        self.filtered_files = []
        for file in self.all_files:
            for ext in self.extensions:
                if str(file).lower().endswith(ext.lower()):
                    if file not in self.blacklist:
                        self.filtered_files.append(file)
            if file in self.whitelist and file not in self.filtered_files:
                self.filtered_files.append(file)
        return True

    def split_filename(self, file):
        split_at = file.find(".")
        filename = file[:split_at]
        ext = file[split_at + 1 :]
        return filename, ext

    def checkdir(self, target_directory):
        self.verbose_log("Checking if a directory already exists")
        target_directory = abspath(target_directory)
        if not (exists(target_directory)):
            try:
                mkdir(target_directory)
            except:
                self.verbose_log(
                    Fore.RED + "CHECKDIR Failed to Create A New Dir" + Fore.RESET
                )
        return True

    ########################################
    ##          GENERAL  METHODS          ##
    ########################################

    def backup(self, target_directory):
        self.verbose_log("Backing Up Selection In: " + target_directory)
        self.checkdir(abspath(target_directory))
        try:
            for file in self.filtered_files:
                copy2(join(self.directory_path, file), join(target_directory, file))
        except:
            self.verbose_log(Fore.RED + "Backing Up Dir Failed" + Fore.RESET)
            return False
        return True

    def move(self, target_directory):
        self.verbose_log("Moving Selection To: " + target_directory)
        self.checkdir(abspath(target_directory))
        try:
            for file in self.filtered_files:
                move(join(self.directory_path, file), join(target_directory, file))
        except:
            self.verbose_log(Fore.RED + "Moving Dir Failed" + Fore.RESET)
            return False
        self.directory_path = target_directory
        self.update()
        return True

    def copy(self, target_directory):
        self.verbose_log("Copying Selection To: " + target_directory)
        self.checkdir(abspath(target_directory))
        try:
            for file in self.filtered_files:
                copy2(join(self.directory_path, file), join(target_directory, file))
        except:
            self.verbose_log(Fore.RED + "Copying Dir Failed" + Fore.RESET)
            return False
        self.directory_path = target_directory
        self.update()
        return True

    def zip(self, file_location):
        self.verbose_log("Zipping up filtered files")
        try:
            zip = ZipFile(file_location, "w")
            [
                zip.write(join(self.directory_path, item), item)
                for item in self.filtered_files
            ]
            zip.close()
        except:
            return False
        return True

    def verbose_log(self, msg):
        if self.verbose:
            print(msg)
        return True

    ########################################
    ##           CONFIG METHODS           ##
    ########################################

    def config_get_whitelist(self):
        self.verbose_log("Retreive Whitelist")
        return self.whitelist

    def config_set_whitelist(self, _list):
        self.verbose_log("Set Whitelist")
        self.whitelist = _list
        self.update()
        return True

    def config_get_blacklist(self):
        self.verbose_log("Retreive Blacklist")
        return self.blacklist

    def config_set_blacklist(self, _list):
        self.verbose_log("Set Blacklist")
        self.blacklist = _list
        self.update()
        return True

    def config_set_log_file(self, filename="main.log"):
        self.verbose_log("Setting Log File To: " + filename)
        self.logfile = abspath(filename)
        self.log("Log created and set to: " + filename)
        self.update()
        return True

    def config_set_extensions(self, _extensions):
        self.verbose_log("Setting Extensions To: " + ", ".join(_extensions))
        exts = []
        for ext in _extensions:
            if not ext.startswith("."):
                exts.append("." + ext)
            else:
                exts.append(ext)
        self.extensions = exts
        self.update()
        return True

    def config_get_extensions(self):
        self.verbose_log("Retreive extensions")
        return self.extensions

    ########################################
    ##            NAME METHODS            ##
    ########################################

    def name_upper(self):
        self.verbose_log("Changing file names to uppercase")
        try:
            for file in self.filtered_files:
                name, ext = self.split_filename(file)
                new_file = name.upper() + "." + ext
                move(
                    join(self.directory_path, file), join(self.directory_path, new_file)
                )
        except:
            self.verbose_log(
                Fore.RED + "Changing Filename To Uppercase Failed" + Fore.RESET
            )
            return False
        self.update()
        return True

    def name_lower(self):
        self.verbose_log("Changing file names to lowercase")
        try:
            for file in self.filtered_files:
                name, ext = self.split_filename(file)
                new_file = name.lower() + "." + ext
                move(
                    join(self.directory_path, file), join(self.directory_path, new_file)
                )
        except:
            self.verbose_log(
                Fore.RED + "Changing Filename To Lowercase Failed" + Fore.RESET
            )
            return False
        self.update()
        return True

    def name_iterate(self, zerofill=0, separator="_"):
        self.verbose_log("Changing file names to be iterated")
        num = 0
        try:
            for file in self.filtered_files:
                num += 1
                new_file = str(num).zfill(zerofill) + separator + file
                move(
                    join(self.directory_path, file), join(self.directory_path, new_file)
                )
        except:
            self.verbose_log(Fore.RED + "Iterating Filename Failed" + Fore.RESET)
            return False
        self.update()
        return True

    def name_prepend(self, str):
        self.verbose_log("Changing names to prepend: " + str)
        try:
            for file in self.filtered_files:
                name, ext = self.split_filename(file)
                new_file = str + name + "." + ext
                move(
                    join(self.directory_path, file), join(self.directory_path, new_file)
                )
        except:
            self.verbose_log(Fore.RED + "Prepending Filename Failed" + Fore.RESET)
            return False
        self.update()
        return True

    def name_append(self, str):
        self.verbose_log("Changing names to append: " + str)
        try:
            for file in self.filtered_files:
                name, ext = self.split_filename(file)
                new_file = name + str + "." + ext
                move(
                    join(self.directory_path, file), join(self.directory_path, new_file)
                )
        except:
            self.verbose_log(Fore.RED + "Appending Filename Failed" + Fore.RESET)
            return False
        self.update()
        return True

    def name_replace(self, target, replacement):
        self.verbose_log("Replacing " + target + " with " + replacement)
        try:
            for file in self.filtered_files:
                name, ext = self.split_filename(file)
                new_file = name.replace(target, replacement) + "." + ext
                move(
                    join(self.directory_path, file), join(self.directory_path, new_file)
                )
        except:
            self.verbose_log(Fore.RED + "Replacing Characters Failed" + Fore.RESET)
            return False
        self.update()
        return True

    def name_replace_spaces(self, replacement="_"):
        self.verbose_log("Replacing spaces in files")
        try:
            self.name_replace(" ", replacement)
        except:
            self.verbose_log(Fore.RED + "Replacing Spaces Failed" + Fore.RESET)
            return False
        self.update()
        return True

    ########################################
    ##            AFX  METHODS            ##
    ########################################

    def afx_normalize(self, target_level=0.1, passes=1):
        self.verbose_log(
            "Normalizing files to "
            + str(target_level)
            + "dB at "
            + str(passes)
            + " passes"
        )
        for file in self.filtered_files:
            name, ext = self.split_filename(file)
            try:
                audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                for i in range(passes):
                    normalize(audio, headroom=target_level)
                audio.export(join(self.directory_path, file), ext)
            except:
                self.verbose_log(
                    Fore.RED
                    + "NORMALIZING FAILED: "
                    + join(self.directory_path, file)
                    + Fore.RESET
                )
                return False
        return True

    def afx_fade(self, in_fade=0, out_fade=0):
        self.verbose_log("Fading files in: " + str(in_fade) + " out: " + str(out_fade))
        for file in self.filtered_files:
            name, ext = self.split_filename(file)
            try:
                duration = mediainfo(join(self.directory_path, file)).get("duration")
                if float(duration) > (in_fade + out_fade):
                    audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                    if in_fade > 0:
                        audio = audio.fade_in(in_fade * 1000)
                    if out_fade > 0:
                        audio = audio.fade_out(out_fade * 1000)
                    audio.export(join(self.directory_path, file), format=ext)
            except:
                self.verbose_log(
                    Fore.RED
                    + "FADING FAILED: "
                    + join(self.directory_path, file)
                    + Fore.RESET
                )
                return False
        return True

    def afx_pad(self, in_pad=0, out_pad=0):
        self.verbose_log("Padding files in: " + str(in_pad) + " out: " + str(out_pad))
        leading_segment = AudioSegment.silent(duration=(1000 * in_pad))
        trailing_segment = AudioSegment.silent(duration=(1000 * out_pad))
        for file in self.filtered_files:
            name, ext = self.split_filename(file)
            try:
                audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                if in_pad > 0:
                    audio = leading_segment + audio
                if out_pad > 0:
                    audio = audio + trailing_segment
                audio.export(join(self.directory_path, file), format=ext)
            except:
                self.verbose_log(
                    Fore.RED
                    + "PADDING FAILED: "
                    + join(self.directory_path, file)
                    + Fore.RESET
                )
                return False
        return True

    def afx_watermark(self, watermark_file, frequency_min, frequency_max):
        self.verbose_log(
            "Adding watermarks between "
            + str(frequency_min)
            + " and "
            + str(frequency_max)
            + " seconds"
        )
        min = frequency_min * 1000
        max = frequency_max * 1000
        try:
            name, ext = self.split_filename(watermark_file)
            watermark = AudioSegment.from_file(abspath(watermark_file), ext)
        except:
            self.verbose_log(
                Fore.RED + "WATERMARKING FAILED TO FIND WATERMARK" + Fore.RESET
            )
            return False
        for file in self.filtered_files:
            name, ext = self.split_filename(file)
            try:
                audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                if len(audio) > len(watermark) + max:
                    cur = 0
                    next_step = 0
                    while True:
                        rng = randrange(min, max) + len(watermark)
                        cur += rng
                        if (cur + max + len(watermark)) < len(audio):
                            audio.overlay(watermark, rng, gain_during_overlay=-2)
                        else:
                            break
                    audio.export(join(self.directory_path, file), format=ext)
            except:
                self.verbose_log(
                    Fore.RED + "WATERMARKING FAILED TO EXPORT" + Fore.RESET
                )
                return False
        return True

    def afx_join(self, target_location, format="wav"):
        self.verbose_log("Joining all files into one file")
        try:
            audio = AudioSegment.silent(duration=1)
            for file in self.filtered_files:
                name, ext = self.split_filename(file)
                new_audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                audio = audio + new_audio
            audio.export(target_location, format=format)
        except:
            self.verbose_log(
                Fore.RED + "JOINING FAILED: " + target_location + Fore.RESET
            )
            return False
        self.update()
        return True

    def afx_prepend(self, file):
        self.verbose_log("Prepending " + file)
        file = abspath(file)
        name, ext = self.split_filename(file)
        try:
            segment = AudioSegment.from_file(file, ext)
            for f in self.filtered_files:
                name, ext = self.split_filename(f)
                audio = AudioSegment.from_file(join(self.directory_path, f), ext)
                audio = segment + audio
                audio.export(join(self.directory_path, f), format=ext)
        except:
            self.verbose_log(Fore.RED + "Prepending Audio FAILED" + Fore.RESET)
            return False
        return True

    def afx_append(self, file):
        self.verbose_log("Appending " + file)
        file = abspath(file)
        name, ext = self.split_filename(file)
        try:
            segment = AudioSegment.from_file(file, ext)
            for f in self.filtered_files:
                name, ext = self.split_filename(f)
                audio = AudioSegment.from_file(join(self.directory_path, f), ext)
                audio = audio + segment
                audio.export(join(self.directory_path, f), format=ext)
        except:
            self.verbose_log(Fore.RED + "Appending Audio FAILED" + Fore.RESET)
            return False
        return True

    def afx_strip_silence(
        self, silence_length=1000, silence_threshold=-16, padding=100
    ):
        self.verbose_log("Stripping Silence")
        for file in self.filtered_files:
            name, ext = self.split_filename(file)
            try:
                audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                strip_silence(audio, silence_length, silence_threshold, padding)
                audio.export(join(self.directory_path, file), format=ext)
            except:
                self.verbose_log(Fore.RED + "Stripping Silence FAILED" + Fore.RESET)
                return False
        return True

    def afx_invert_stereo_phase(self, channel="both"):
        self.verbose_log("Inverting phase")
        ## LEFT, RIGHT, or BOTH
        both = (1, 1)
        left = (1, 0)
        right = (0, 1)
        sel = None
        if channel.lower() == "left":
            sel = left
        elif channel.lower() == "right":
            sel = right
        elif channel.lower() == "both":
            sel = both

        for file in self.filtered_files:
            name, ext = self.split_filename(file)
            try:
                audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                invert_phase(audio, sel)
                audio.export(join(self.directory_path, file), format=ext)
            except:
                self.verbose_log(Fore.RED + "Inverting Phase FAILED" + Fore.RESET)
                return False
        return True

    def afx_lpf(self, cutoff=None):
        self.verbose_log("Appling Low Pass Filter")
        if cutoff:
            for file in self.filtered_files:
                name, ext = self.split_filename(file)
                try:
                    audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                    low_pass_filter(audio, cutoff)
                    audio.export(join(self.directory_path, file), format=ext)
                except:
                    self.verbose_log(Fore.RED + "Low Pass Filter FAILED" + Fore.RESET)
                    return False
        return True

    def afx_hpf(self, cutoff=None):
        self.verbose_log("Applying High Pass Filter")
        if cutoff:
            for file in self.filtered_files:
                name, ext = self.split_filename(file)
                try:
                    audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                    high_pass_filter(audio, cutoff)
                    audio.export(join(self.directory_path, file), format=ext)
                except:
                    self.verbose_log(Fore.RED + "High PAss Filter FAILED" + Fore.RESET)
                    return False
        return True

    def afx_stereo_gain(self, amount=0):
        self.verbose_log("Applying {}db gain".format(str(amount)))
        if amount != 0:
            for file in self.filtered_files:
                name, ext = self.split_filename(file)
                try:
                    audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                    apply_gain_stereo(audio, amount, amount)
                    audio.export(join(self.directory_path, file), format=ext)
                except:
                    self.verbose_log(Fore.RED + "Applying Gain FAILED" + Fore.RESET)
                    return False
        return True

    def afx_mono_gain(self, amount=0):
        self.verbose_log("Applying {}db gain".format(str(amount)))
        if amount != 0:
            for file in self.filtered_files:
                name, ext = self.split_filename(file)
                try:
                    audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                    apply_gain_stereo(audio, amount, amount)
                    audio.set_channels(1)
                    audio.export(join(self.directory_path, file), format=ext)
                except:
                    self.verbose_log(Fore.RED + "Applying Gain FAILED" + Fore.RESET)
                    return False
        return True

    ########################################
    ##          CONVERT  METHODS          ##
    ########################################

    def convert_to_mono(self):
        self.verbose_log("Converting to mono")
        for file in self.filtered_files:
            name, ext = self.split_filename(file)
            try:
                audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                audio.set_channels(1)
                audio.export(join(self.directory_path, file), format=ext)
            except:
                self.verbose_log(Fore.RED + "Converting To Mono FAILED" + Fore.RESET)
                return False
        return True

    def convert_to_stereo(self):
        self.verbose_log("Converting to stereo")
        for file in self.filtered_files:
            name, ext = self.split_filename(file)
            try:
                audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                apply_gain_stereo(audio, 0, 0)
                audio.export(join(self.directory_path, file), format=ext)
            except:
                self.verbose_log(Fore.RED + "Converting To Stereo FAILED" + Fore.RESET)
                return False
        return True

    def convert_to_wav(self, sample_rate=None, bit_depth=None, cover=None):
        self.verbose_log("Converting files to WAV")
        for file in self.filtered_files:
            name, ext = self.split_filename(file)
            try:
                audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                if sample_rate:
                    audio.set_frame_rate(sample_rate)
                if bit_depth:
                    if bit_depth == 8:
                        bit_depth = 1
                    elif bit_depth == 16:
                        bit_depth = 2
                    # pydub doesn't support 24 bit audio yet, always converts to 32
                    elif bit_depth == 24 or bit_depth == 32:
                        bit_depth = 4
                    audio.set_sample_width(bit_depth)

                audio.export(
                    join(self.directory_path, name + ".wav"), format="wav", cover=cover,
                )
            except:
                self.verbose_log(
                    Fore.RED
                    + "CONVERTING TO WAV FAILED: "
                    + join(self.directory_path, file)
                    + Fore.RESET
                )
                return False
        self.update()
        return True

    def convert_to_mp3(self, bit_rate=None, bit_depth=None, cover=None, tags=None):
        self.verbose_log("Converting files to MP3")
        for file in self.filtered_files:
            name, ext = self.split_filename(file)
            try:
                audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                if bit_rate:
                    audio.set_frame_rate(bit_rate)
                if bit_depth:
                    if bit_depth == 8:
                        bit_depth = 1
                    elif bit_depth == 16:
                        bit_depth = 2
                    # pydub doesn't support 24 bit audio yet, always converts to 32
                    elif bit_depth == 24 or bit_depth == 32:
                        bit_depth = 4
                    audio.set_sample_width(bit_depth)

                audio.export(
                    join(self.directory_path, name + ".mp3"),
                    format="mp3",
                    cover=cover,
                    tags=tags,
                )
            except:
                self.verbose_log(
                    Fore.RED
                    + "CONVERTING TO MP3 FAILED: "
                    + join(self.directory_path, file)
                    + Fore.RESET
                )
                return False
        self.update()
        return True

    def convert_to_raw(self, sample_rate=None, bit_depth=None, cover=None):
        self.verbose_log("Converting files to a RAW format")
        for file in self.filtered_files:
            name, ext = self.split_filename(file)
            try:
                audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                if sample_rate:
                    audio.set_frame_rate(sample_rate)
                if bit_depth:
                    if bit_depth == 8:
                        bit_depth = 1
                    elif bit_depth == 16:
                        bit_depth = 2
                    # pydub doesn't support 24 bit audio yet, always converts to 32
                    elif bit_depth == 24 or bit_depth == 32:
                        bit_depth = 4
                    audio.set_sample_width(bit_depth)
                audio.export(
                    join(self.directory_path, name + ".raw"), format="raw", cover=cover,
                )
            except:
                self.verbose_log(
                    Fore.RED
                    + "CONVERTING TO RAW FAILED: "
                    + join(self.directory_path, file)
                    + Fore.RESET
                )
                return False
        return True

    def convert_to_flac(self, sample_rate=None, bit_depth=None, cover=None, tags=None):
        self.verbose_log("Converting files to a FLAC format")
        for file in self.filtered_files:
            name, ext = self.split_filename(file)
            try:
                audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                if sample_rate:
                    audio.set_frame_rate(sample_rate)
                if bit_depth:
                    if bit_depth == 8:
                        bit_depth = 1
                    elif bit_depth == 16:
                        bit_depth = 2
                    # pydub doesn't support 24 bit audio yet, always converts to 32
                    elif bit_depth == 24 or bit_depth == 32:
                        bit_depth = 4
                    audio.set_sample_width(bit_depth)
                audio.export(join(self.directory_path, name + ".flac"), format="flac")
            except:
                self.verbose_log(
                    Fore.RED
                    + "CONVERTING TO FLAC FAILED: "
                    + join(self.directory_path, file)
                    + Fore.RESET
                )
                return False
        return True

    def convert_to(
        self, format="wav", sample_rate=None, bit_depth=None, cover=None, tags=None
    ):
        self.verbose_log("Converting files to {}")
        format = format.replace(".", "")
        for file in self.filtered_files:
            name, ext = self.split_filename(file)
            try:
                audio = AudioSegment.from_file(join(self.directory_path, file), ext)
                if sample_rate:
                    audio.set_frame_rate(sample_rate)
                if bit_depth:
                    if bit_depth == 8:
                        bit_depth = 1
                    elif bit_depth == 16:
                        bit_depth = 2
                    # pydub doesn't support 24 bit audio yet, always converts to 32
                    elif bit_depth == 24 or bit_depth == 32:
                        bit_depth = 4
                    audio.set_sample_width(bit_depth)
                audio.export(
                    join(self.directory_path, name + "." + format),
                    format=format,
                    cover=cover,
                    tags=tags,
                )
            except:
                self.verbose_log(
                    Fore.RED
                    + "CONVERTING TO {} FAILED: ".format(format)
                    + join(self.directory_path, file)
                    + Fore.RESET
                )
                return False
        return True
