import qrcode
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import wave
import struct

def qr2specgram(qr_data, start_freq, end_freq, freq_step, step_scale, char_speed, fs, version, error_correction):
    try:
        qr = qrcode.QRCode(
            version=version,
            error_correction=error_correction,
            box_size=5,
            border=0,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        qr_img = qr_img.convert("L")

        # Inverting the image
        qr_img = qr_img.point(lambda x: 255 - x)

        # Saving QR code image
        qr_img.save("qrcode.png")

        # Converting to numpy array
        qr_array = np.array(qr_img)

        # Resizing the image
        image_length = qr_array.shape[1]
        image_length_fit = int(image_length * char_speed * fs)
        im = np.array(qr_img.resize((image_length_fit, freq_step)))

        # Generating the waveform
        wav = np.zeros(len(im.T))
        for m in range(freq_step):
            freq = start_freq * (end_freq / start_freq) ** (m / freq_step) if step_scale else start_freq + (
                        end_freq - start_freq) * (m / freq_step)
            print("%dHz" % (freq), end=", ")
            wav1 = np.sin(2 * np.pi * freq * np.arange(len(im.T)) / fs + m)
            wav += im[freq_step - m - 1, :] * wav1
            wav += wav1

        # Writing the waveform to a WAV file
        wav = wav / max(wav) * 24000
        wav = [int(x) for x in wav]
        wav_bin = struct.pack("h" * len(wav), *wav)

        w = wave.open("qrcode.wav", "w")
        p = (1, 2, fs, len(wav_bin), 'NONE', 'not compressed')
        w.setparams(p)
        w.writeframes(wav_bin)
        w.close

    except Exception as e:
        print("An error occurred:", e)

start_freq = 20
end_freq = 96000
freq_step = 1000
step_scale = False
fs = end_freq * 2
version = 4
char_speed = 1300 / end_freq
error_correction = qrcode.constants.ERROR_CORRECT_M

qr_data = input('text:')
qr2specgram(qr_data, start_freq, end_freq, freq_step, step_scale, char_speed, fs,version, error_correction)