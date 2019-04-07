import os
from AudLib import setupLogger, createFolder
from pydub import AudioSegment

logger = setupLogger()

class AudFile:
    '''
    A wrapper for a file path to ease use
    '''
    filepath = ""
    name = ""
    extension = ""
    base = ""
    input_file = ""
    output_directory = "_Processed"

    def __init__(self, _input_file, _output_directory="_Processed"):
        try:
            path = os.path.abspath(_input_file)
            self.output_directory = _output_directory
            self.filepath = path
            self.name = os.path.basename(path)
            self.base = path.rstrip(self.name)
            self.extension = str('.' + self.name.split('.')[1].lower())
        except:
            del self

    ### override string and print
    def __repr__(self):
        return str(self.filepath)

    def __str__(self):
        return str(self.filepath)

    ### OS IO METHODS ###
    def renameUpper(self):
        '''
        Rename file to UPPERCASE
        '''
        logger.info("renameUpper:" + self.filepath)
        os.rename(self.filepath, self.base + '\\' + self.name.upper())

    def renameLower(self):
        '''
        Rename file to lowercase
        '''
        logger.info("renameLower:" + self.filepath)
        os.rename(self.filepath, self.base + '\\' + self.name.lower())

    def renameReplaceSpaces(self):
        '''
        Rename file to replace_all_spaces_with_underscored
        '''
        logger.info("renameReplaceSpaces:" + self.filepath)
        os.rename(self.filepath, self.base + '\\' + self.name.replace(" ", "_"))

    def renamePrepend(self, _prefix):
        '''
        Add a prefix for the filename
        '''
        logger.info("renamePrepend:" + self.filepath)
        os.rename(self.filepath, self.base + '\\' + _prefix + self.name)

    ### UNORGANIZED METHODS ###
    def convertTo(self, _target_samplerate=44100, _target_bitdepth=16):
        logger.info("convertTo:" + self.filepath)

    def pad(self, _in=0.0, _out=0.0):
        '''
        Add leading and trailing blank audio to an audio file
        '''
        #logger.info("pad:" + self.filepath)

        # create processed folder
        createFolder(self.base + self.output_directory)

        leading_segment = AudioSegment.silent(duration=(1000*_in))
        trailing_segment = AudioSegment.silent(duration=(1000*_out))

        if self.extension ==".mp3":
            logger.info("Processing mp3: " + self.filepath)
            #read wav file to an audio segment
            audio = AudioSegment.from_mp3(self.filepath)

            # Add above two audio segments
            final_song = leading_segment + audio + trailing_segment

            #Either save modified audio
            final_song.export(self.base + '/' + self.output_directory + '/' + self.name, format="mp3")

        if self.extension ==".wav":
            logger.info("Processing wav: " + self.filepath)
            #read wav file to an audio segment
            audio = AudioSegment.from_wav(self.filepath)

            # Add above two audio segments
            final_song = leading_segment + audio + trailing_segment

            #Either save modified audio
            final_song.export(self.base + '/' + self.output_directory + '/' + self.name, format="wav")

        if self.extension ==".ogg":
            logger.info("Processing ogg: " + self.filepath)
            #read wav file to an audio segment
            audio = AudioSegment.from_ogg(self.filepath)

            # Add above two audio segments
            final_song = leading_segment + audio + trailing_segment

            #Either save modified audio
            final_song.export(self.base + '/' + self.output_directory + '/' + self.name, format="ogg")

        if self.extension ==".flv":
            logger.info("Processing flv: " + self.filepath)
            #read wav file to an audio segment
            audio = AudioSegment.from_flv(self.filepath)

            # Add above two audio segments
            final_song = leading_segment + audio + trailing_segment

            #Either save modified audio
            final_song.export(self.base + '/' + self.output_directory + '/' + self.name, format="flv")

        ## This works with ogg or flv too

    def fade(self, _in=0.0, out=0.0, _type='log|lin', _ratio=0.0):
        '''
        Add fades to an audio file
        '''
        logger.info("fade:" + self.filepath)

    def move(self, _target_directory):
        '''
        Move file to another folder
        '''
        logger.info("moving:" + self.filepath)

    def metadata(self, _tags={}):
        '''
        add tags to a file like tags={"Artist": "Nobukazu Takemura", "Type": "Sfx"}
        You can add any tag you like but if you want them to come up in a particular
        application you will need to lookup what they use
        '''
        logger.info("metadata: " + self.filepath)

        if self.extension ==".mp3":
            audio = AudioSegment.from_mp3(self.filepath)
            audio.export(self.base + '/' + self.output_directory + '/' + self.name, format="mp3", tags=_tags)
            pass
        if self.extension ==".wav":
            audio = AudioSegment.from_wav(self.filepath)
            audio.export(self.base + '/' + self.output_directory + '/' + self.name, format="wav", tags=_tags)
            pass
        if self.extension ==".ogg":
            audio = AudioSegment.from_ogg(self.filepath)
            audio.export(self.base + '/' + self.output_directory + '/' + self.name, format="ogg", tags=_tags)
            pass
        if self.extension ==".flv":
            audio = AudioSegment.from_flv(self.filepath)
            audio.export(self.base + '/' + self.output_directory + '/' + self.name, format="flv", tags=_tags)
            pass

        #read wav file to an audio segment
        audio = AudioSegment.from_flv(self.filepath)

        # Add above two audio segments
        final_song = leading_segment + audio + trailing_segment

        #Either save modified audio
        final_song.export(self.base + '/' + self.output_directory + '/' + self.name, format="flv")
        pass
