# aud

## Quick tools for an audio studio environment

### Functionality:
> from aud import AudFile, AudDir
>
>> file = AudFile(filepath)
>> dir = AudDir(filepath, extensions=['wav', 'mp3'])
>
>> file.help()
>> dir.help()
>>   Prints out examples of all commands
>
>> dir.setExtensions(['wav', 'mp3', 'ogg'])
>>   select which extensions to apply commands to within a directory
>
>> file.convert()
>> dir.convert()
>>   converts all audio files to a specific file type, sample rate, and bit depth
>>   uses FFMPEG for high quality conversions
