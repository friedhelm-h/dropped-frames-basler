import traceback
import os
import pathlib

import pypylon.pylon as py
import cv2


class VideoWriter(py.ImageEventHandler):
    def __init__(self, path, fps, save_type='mp4'):
        super().__init__()

        storing_options = ['mp4', 'png']
        assert save_type in storing_options, \
            'save_type must be one of the following options;\n' \
            f'{storing_options}'

        self._save_type = save_type
        self.fps = fps

        if save_type == 'mp4':
            self._name = f'{path}/frames.mp4'
            self._fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            self._out = None
        elif save_type == 'png':
            self._name = f'{path}/frames'
            if not os.path.isdir(self._name):
                pathlib.Path(self._name).mkdir(parents=True)
            self.index = 0

    def __del__(self):
        self.stop_recording()

    def stop_recording(self):
        try:
            if self._save_type == 'mp4' and self._out is not None:
                self._out.release()
        except:
            RuntimeError('Error stopping video writer')

    def OnImageGrabbed(self, camera, grabResult):
        try:
            if grabResult.GrabSucceeded():
                if self._save_type == 'mp4':
                    if not self._out:
                        width = grabResult.GetWidth()
                        height = grabResult.GetHeight()
                        self._out = cv2.VideoWriter(self._name, self._fourcc,
                                                    self.fps, (width, height), 0)

                    self._out.write(grabResult.GetArray())
                elif self._save_type == 'png':
                    cv2.imwrite(f'{self._name}/{str(self.index).zfill(12)}.png',
                                grabResult.GetArray())
                    self.index += 1

            else:
                raise RuntimeError('Grab Failed')
        except RuntimeError:
            traceback.print_exc()
