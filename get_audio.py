import whisper
import wave
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

# convert audio content into text
def whisper_wav_to_text(audio_name, model=[], model_name=False):
    if isinstance(model_name, str):
        print('loading model ', model_name)
        model = whisper.load_model(model_name)

    if model == []:
        raise Exception("model cannot be unspecified")

    print('listening to ',audio_name,'...')
    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(audio_name)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    # detect the spoken language
    try:
        _, probs = model.detect_language(mel)
        print(f"Detected language: {max(probs, key=probs.get)}")
        detected_lang = str(max(probs, key=probs.get))
        options = whisper.DecodingOptions()
        result = whisper.decode(model, mel, options)
    except:
        # model does not support multiple languages, default to English
        print('language: en')
        detected_lang = 'en'
        options = whisper.DecodingOptions(language='en')
        result = whisper.decode(model, mel,options)
    

    # print the recognized text
    print(result.text)
    return result.text, detected_lang

def record():
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Start recording")
    frames = []

    try:
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
            

    except KeyboardInterrupt:
        print("Done recording")
    except Exception as e:
        print(str(e))

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    return sample_width, frames

def record_to_file(file_path):
	wf = wave.open(file_path, 'wb')
	wf.setnchannels(CHANNELS)
	sample_width, frames = record()
	wf.setsampwidth(sample_width)
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()


def demo():
    model = whisper.load_model("base.en")
    print('#' * 80)
    print("Please speak word(s) into the microphone")
    print('Press Ctrl+C to stop the recording')
    
    # record
    record_to_file('audio.wav')

    print("Result written to output.wav")
    print("\n## transcirbing ##")

    # transcribe
    text = whisper_wav_to_text('output.wav',model)
    print('#' * 80)