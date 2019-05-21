'''Audio System (aud)
   This module provides access to the audaspace audio library.
   
'''


AUD_DEVICE_JACK = 3 #constant value 

AUD_DEVICE_NULL = 0 #constant value 

AUD_DEVICE_OPENAL = 1 #constant value 

AUD_DEVICE_SDL = 2 #constant value 

AUD_DISTANCE_MODEL_EXPONENT = 5 #constant value 

AUD_DISTANCE_MODEL_EXPONENT_CLAMPED = 6 #constant value 

AUD_DISTANCE_MODEL_INVALID = 0 #constant value 

AUD_DISTANCE_MODEL_INVERSE = 1 #constant value 

AUD_DISTANCE_MODEL_INVERSE_CLAMPED = 2 #constant value 

AUD_DISTANCE_MODEL_LINEAR = 3 #constant value 

AUD_DISTANCE_MODEL_LINEAR_CLAMPED = 4 #constant value 

AUD_FORMAT_FLOAT32 = 36 #constant value 

AUD_FORMAT_FLOAT64 = 40 #constant value 

AUD_FORMAT_INVALID = 0 #constant value 

AUD_FORMAT_S16 = 18 #constant value 

AUD_FORMAT_S24 = 19 #constant value 

AUD_FORMAT_S32 = 20 #constant value 

AUD_FORMAT_U8 = 1 #constant value 

AUD_STATUS_INVALID = 0 #constant value 

AUD_STATUS_PAUSED = 2 #constant value 

AUD_STATUS_PLAYING = 1 #constant value 

AUD_STATUS_STOPPED = 3 #constant value 

def device(*argv):
   '''device()
      Returns the application's Device.
      
      @returns (Device): The application's Device.
   '''

   return Device

class Device:
   '''Device objects represent an audio output backend like OpenAL or SDL, but might also represent a file output or RAM buffer output.
      
   '''

   def lock(*argv):
      '''lock()
         Locks the device so that it's guaranteed, that no samples are read from the streams until :meth:unlock is called.
         This is useful if you want to do start/stop/pause/resume some sounds at the same time.
         
         Note: The device has to be unlocked as often as locked to be able to continue playback... warning:: Make sure the time between locking and unlocking is as short as possible to avoid clicks.
         
      '''
   
      pass
   

   def play(*argv):
      '''play(factory, keep=False)
         Plays a factory.
         
         Arguments:
         @factory (Factory): The factory to play.
         @keep (bool): See :attr:Handle.keep.
   
         @returns (Handle): The playback handle with which playback can be controlled with.
      '''
   
      return Handle
   

   def stopAll(*argv):
      '''stopAll()
         Stops all playing and paused sounds.
         
      '''
   
      pass
   

   def unlock(*argv):
      '''unlock()
         Unlocks the device after a lock call, see :meth:lock for details.
         
      '''
   
      pass
   

   channels = None
   '''The channel count of the device.
      
   '''
   

   distance_model = None
   '''The distance model of the device.
      
      (seealso OpenAL documentation <https://www.openal.org/documentation>)
      
   '''
   

   doppler_factor = None
   '''The doppler factor of the device.
      This factor is a scaling factor for the velocity vectors in doppler calculation. So a value bigger than 1 will exaggerate the effect as it raises the velocity.
      
   '''
   

   format = None
   '''The native sample format of the device.
      
   '''
   

   listener_location = None
   '''The listeners's location in 3D space, a 3D tuple of floats.
      
   '''
   

   listener_orientation = None
   '''The listener's orientation in 3D space as quaternion, a 4 float tuple.
      
   '''
   

   listener_velocity = None
   '''The listener's velocity in 3D space, a 3D tuple of floats.
      
   '''
   

   rate = None
   '''The sampling rate of the device in Hz.
      
   '''
   

   speed_of_sound = None
   '''The speed of sound of the device.
      The speed of sound in air is typically 343.3 m/s.
      
   '''
   

   volume = None
   '''The overall volume of the device.
      
   '''
   



class Factory:
   '''Factory objects are immutable and represent a sound that can be played simultaneously multiple times. They are called factories because they create reader objects internally that are used for playback.
      
   '''

   @classmethod
   def file(*argv):
      '''file(filename)
         Creates a factory object of a sound file.
         
         Arguments:
         @filename (string): Path of the file.
   
         @returns (Factory): The created Factory object... warning:: If the file doesn't exist or can't be read you will not get an exception immediately, but when you try to start playback of that factory.
         
      '''
   
      return Factory
   

   @classmethod
   def sine(*argv):
      '''sine(frequency, rate=48000)
         Creates a sine factory which plays a sine wave.
         
         Arguments:
         @frequency (float): The frequency of the sine wave in Hz.
         @rate (int): The sampling rate in Hz. It's recommended to set this value to the playback device's samling rate to avoid resamping.
   
         @returns (Factory): The created Factory object.
      '''
   
      return Factory
   

   def buffer(*argv):
      '''buffer()
         Buffers a factory into RAM.
         This saves CPU usage needed for decoding and file access if the underlying factory reads from a file on the harddisk, but it consumes a lot of memory.
         
         @returns (Factory): The created Factory object.
         Note: Only known-length factories can be buffered... warning:: Raw PCM data needs a lot of space, only buffer short factories.
         
      '''
   
      return Factory
   

   def delay(*argv):
      '''delay(time)
         Delays by playing adding silence in front of the other factory's data.
         
         Arguments:
         @time (float): How many seconds of silence should be added before the factory.
   
         @returns (Factory): The created Factory object.
      '''
   
      return Factory
   

   def fadein(*argv):
      '''fadein(start, length)
         Fades a factory in by raising the volume linearly in the given time interval.
         
         Arguments:
         @start (float): Time in seconds when the fading should start.
         @length (float): Time in seconds how long the fading should last.
   
         @returns (Factory): The created Factory object.
         Note: Before the fade starts it plays silence.
      '''
   
      return Factory
   

   def fadeout(*argv):
      '''fadeout(start, length)
         Fades a factory in by lowering the volume linearly in the given time interval.
         
         Arguments:
         @start (float): Time in seconds when the fading should start.
         @length (float): Time in seconds how long the fading should last.
   
         @returns (Factory): The created Factory object.
         Note: After the fade this factory plays silence, so that the length of the factory is not altered.
      '''
   
      return Factory
   

   def filter(*argv):
      '''filter(b, a = (1))
         Filters a factory with the supplied IIR filter coefficients.
         Without the second parameter you'll get a FIR filter.
         If the first value of the a sequence is 0 it will be set to 1 automatically.
         If the first value of the a sequence is neither 0 nor 1, all filter coefficients will be scaled by this value so that it is 1 in the end, you don't have to scale yourself.
         
         Arguments:
         @b (sequence of float): The nominator filter coefficients.
         @a (sequence of float): The denominator filter coefficients.
   
         @returns (Factory): The created Factory object.
      '''
   
      return Factory
   

   def highpass(*argv):
      '''highpass(frequency, Q=0.5)
         Creates a second order highpass filter based on the transfer function H(s) = s^2 / (s^2 + s/Q + 1)
         
         Arguments:
         @frequency (float): The cut off trequency of the highpass.
         @Q (float): Q factor of the lowpass.
   
         @returns (Factory): The created Factory object.
      '''
   
      return Factory
   

   def join(*argv):
      '''join(factory)
         Plays two factories in sequence.
         
         Arguments:
         @factory (Factory): The factory to play second.
   
         @returns (Factory): The created Factory object.
         Note: The two factories have to have the same specifications (channels and samplerate).
      '''
   
      return Factory
   

   def limit(*argv):
      '''limit(start, end)
         Limits a factory within a specific start and end time.
         
         Arguments:
         @start (float): Start time in seconds.
         @end (float): End time in seconds.
   
         @returns (Factory): The created Factory object.
      '''
   
      return Factory
   

   def loop(*argv):
      '''loop(count)
         Loops a factory.
         
         Arguments:
         @count (integer): How often the factory should be looped. Negative values mean endlessly.
   
         @returns (Factory): The created Factory object.
         Note: This is a filter function, you might consider using :attr:Handle.loop_count instead.
      '''
   
      return Factory
   

   def lowpass(*argv):
      '''lowpass(frequency, Q=0.5)
         Creates a second order lowpass filter based on the transfer function H(s) = 1 / (s^2 + s/Q + 1)
         
         Arguments:
         @frequency (float): The cut off trequency of the lowpass.
         @Q (float): Q factor of the lowpass.
   
         @returns (Factory): The created Factory object.
      '''
   
      return Factory
   

   def mix(*argv):
      '''mix(factory)
         Mixes two factories.
         
         Arguments:
         @factory (Factory): The factory to mix over the other.
   
         @returns (Factory): The created Factory object.
         Note: The two factories have to have the same specifications (channels and samplerate).
      '''
   
      return Factory
   

   def pingpong(*argv):
      '''pingpong()
         Plays a factory forward and then backward.
         This is like joining a factory with its reverse.
         
         @returns (Factory): The created Factory object.
      '''
   
      return Factory
   

   def pitch(*argv):
      '''pitch(factor)
         Changes the pitch of a factory with a specific factor.
         
         Arguments:
         @factor (float): The factor to change the pitch with.
   
         @returns (Factory): The created Factory object.
         Note: This is done by changing the sample rate of the underlying factory, which has to be an integer, so the factor value rounded and the factor may not be 100 % accurate.
      '''
   
      return Factory
   

   def reverse(*argv):
      '''reverse()
         Plays a factory reversed.
         
         @returns (Factory): The created Factory object.
         Note: The factory has to have a finite length and has to be seekable. It's recommended to use this only with factories	 with fast and accurate seeking, which is not true for encoded audio files, such ones should be buffered using :meth:buffer before being played reversed... warning:: If seeking is not accurate in the underlying factory you'll likely hear skips/jumps/cracks.
         
      '''
   
      return Factory
   

   def square(*argv):
      '''square(threshold = 0)
         Makes a square wave out of an audio wave by setting all samples with a amplitude >= threshold to 1, all <= -threshold to -1 and all between to 0.
         
         Arguments:
         @threshold (float): Threshold value over which an amplitude counts non-zero.
   
         @returns (Factory): The created Factory object.
      '''
   
      return Factory
   

   def volume(*argv):
      '''volume(volume)
         Changes the volume of a factory.
         
         Arguments:
         @volume (float): The new volume..
   
         @returns (Factory): The created Factory object.
         Note: Should be in the range [0, 1] to avoid clipping.
      '''
   
      return Factory
   



class Handle:
   '''Handle objects are playback handles that can be used to control playback of a sound. If a sound is played back multiple times then there are as many handles.
      
   '''

   def pause(*argv):
      '''pause()
         Pauses playback.
         
         @returns (bool): Whether the action succeeded.
      '''
   
      return bool
   

   def resume(*argv):
      '''resume()
         Resumes playback.
         
         @returns (bool): Whether the action succeeded.
      '''
   
      return bool
   

   def stop(*argv):
      '''stop()
         Stops playback.
         
         @returns (bool): Whether the action succeeded.
         Note: This makes the handle invalid.
      '''
   
      return bool
   

   attenuation = None
   '''This factor is used for distance based attenuation of the source.
      
      (seealso :attr:Device.distance_model)
      
   '''
   

   cone_angle_inner = None
   '''The opening angle of the inner cone of the source. If the cone values of a source are set there are two (audible) cones with the apex at the :attr:location of the source and with infinite height, heading in the direction of the source's :attr:orientation.
      In the inner cone the volume is normal. Outside the outer cone the volume will be :attr:cone_volume_outer and in the area between the volume will be interpolated linearly.
      
   '''
   

   cone_angle_outer = None
   '''The opening angle of the outer cone of the source.
      
      (seealso :attr:cone_angle_inner)
      
   '''
   

   cone_volume_outer = None
   '''The volume outside the outer cone of the source.
      
      (seealso :attr:cone_angle_inner)
      
   '''
   

   distance_maximum = None
   '''The maximum distance of the source.
      If the listener is further away the source volume will be 0.
      
      (seealso :attr:Device.distance_model)
      
   '''
   

   distance_reference = None
   '''The reference distance of the source.
      At this distance the volume will be exactly :attr:volume.
      
      (seealso :attr:Device.distance_model)
      
   '''
   

   keep = None
   '''Whether the sound should be kept paused in the device when its end is reached.
      This can be used to seek the sound to some position and start playback again.
      .. warning:: If this is set to true and you forget stopping this equals a memory leak as the handle exists until the device is destroyed.
      
   '''
   

   location = None
   '''The source's location in 3D space, a 3D tuple of floats.
      
   '''
   

   loop_count = None
   '''The (remaining) loop count of the sound. A negative value indicates infinity.
      
   '''
   

   orientation = None
   '''The source's orientation in 3D space as quaternion, a 4 float tuple.
      
   '''
   

   pitch = None
   '''The pitch of the sound.
      
   '''
   

   position = None
   '''The playback position of the sound in seconds.
      
   '''
   

   relative = None
   '''Whether the source's location, velocity and orientation is relative or absolute to the listener.
      
   '''
   

   status = None
   '''Whether the sound is playing, paused or stopped (=invalid).
      
   '''
   

   velocity = None
   '''The source's velocity in 3D space, a 3D tuple of floats.
      
   '''
   

   volume = None
   '''The volume of the sound.
      
   '''
   

   volume_maximum = None
   '''The maximum volume of the source.
      
      (seealso :attr:Device.distance_model)
      
   '''
   

   volume_minimum = None
   '''The minimum volume of the source.
      
      (seealso :attr:Device.distance_model)
      
   '''
   



class error:
   



