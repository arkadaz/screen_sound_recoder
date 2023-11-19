import dxcam
import cv2
from time import time
import soundfile as sf
import soundcard as sc
from multiprocessing import Process, cpu_count
from moviepy.editor import *
from tqdm import tqdm

def record_sound(second, file_name_sound, sound_device):
    speakers = sc.all_speakers()
    default_speaker = sc.default_speaker()
    mics = sc.all_microphones(include_loopback=True)
    device_index = sound_device
    default_mic = mics[device_index]
    print("Recording sound")
    numframe_cal = int(44100 * second)
    with default_mic.recorder(samplerate=44100) as mic, \
                default_speaker.player(samplerate=44100) as sp:
        data = mic.record(numframes=numframe_cal)
        sf.write(f'{file_name_sound}.wav', data, 44100)
    print("Finished sound")

def record_video(second, file_name_video):    
    camera = dxcam.create(device_idx=0 ,output_color="BGR", output_idx=0, max_buffer_len=2048)
    width = 1920
    height = 1080
    fps = 30
    frame_delta = 1 / fps

    # open video writer
    video = cv2.VideoWriter(f'{file_name_video}.avi', cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))
    next_frame = time()
    camera.start(target_fps=120, video_mode=True)
    print("Recording video")
    for i in tqdm(range(fps*second)):
        next_frame += frame_delta
        video.write(camera.get_latest_frame())
        wait_ms = max(int((next_frame - time()) * 1000), 1)
        if cv2.waitKey(wait_ms) & 0xFF == ord('q'):
            break
    camera.stop()
    video.release()
    del camera
    print("Finished video")
    
if __name__ == '__main__':
    # multiprocessing.freeze_support()
    m = sc.all_microphones(include_loopback=True)
    for i in range(len(m)):
        try:
            print(f"{i}: {m[i].name}")
        except Exception as e:
            print(e)
    # print(dxcam.device_info())
    sound_device = int(input("Sound device: "))
    second = int(input("Second: "))
    file_name_sound = input("Sound file name: ").replace(' ', '').replace('\n', ' ').replace('\r', '')
    file_name_video = input("Video file name: ").replace(' ', '').replace('\n', ' ').replace('\r', '')
    output_file_name = input("Output file name: ").replace(' ', '').replace('\n', ' ').replace('\r', '')

    t1 = Process(target=record_sound, args=(second, file_name_sound, sound_device,))
    t2 = Process(target=record_video, args=(second, file_name_video,))
    t1.start()
    t2.start()

    t1.join()
    t2.join()
    videoclip = VideoFileClip(f"{file_name_video}.avi")
    audioclip = AudioFileClip(f"{file_name_sound}.wav")

    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip
    videoclip.write_videofile(f"{output_file_name}.mp4", audio_fps=44100, audio_nbytes=4, threads=cpu_count(), codec='libx264', bitrate="8500k")
    print("All Done!")
