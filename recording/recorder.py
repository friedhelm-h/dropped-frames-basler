from datetime import datetime
import os
import pathlib
import shutil
import yaml

import pypylon.pylon as py

from cocapture.basler.video_writer import VideoWriter


class Recorder:
    def __init__(self, configs, out_path, fps, save_type='mp4'):
        self.time = None
        assert isinstance(configs, (str, list)), \
            'configs is path to the yaml config file' \
            'and should be of type string or list of ' \
            'strings'
        if isinstance(configs, str):
            configs = [configs]
        parameters = []
        for config in configs:
            with open(config, 'r') as f:
                camera_parameters = yaml.safe_load(f)['Parameter']
                # Workaround because YAML reads 'On' as Boolean True
                if 'TriggerMode' in camera_parameters:
                    if camera_parameters['TriggerMode']:
                        camera_parameters['TriggerMode'] = 'On'
                    else:
                        camera_parameters['TriggerMode'] = 'Off'
                parameters.append(camera_parameters)

        self.num_cameras = len(configs)
        tlf = py.TlFactory.GetInstance()
        devices = tlf.EnumerateDevices()

        print('Found the following Basler cameras:')
        for d in devices:
            print(f'model: {d.GetModelName()}, serial: {d.GetSerialNumber()}')
        print()

        assert self.num_cameras <= len(devices), \
            'more config files given than cameras available'

        self.camera_array = py.InstantCameraArray(self.num_cameras)

        for i, cam in enumerate(self.camera_array):
            cam.Attach(tlf.CreateDevice(devices[i]))
        self.camera_array.Open()

        self.video_writers = []
        for i, cam in enumerate(self.camera_array):
            camera_serial = cam.DeviceInfo.GetSerialNumber()
            print(f"for camera {camera_serial} setting properties:")
            cam.SetCameraContext(i)
            print(f'CameraContext: {i}')

            camera_parameters = parameters[i]
            for p in camera_parameters:
                setattr(cam, p, camera_parameters[p])
                print(f'{p}: {camera_parameters[p]}')
            print()

            cam_path = f'{out_path}/basler_{i}'
            if not os.path.isdir(cam_path):
                pathlib.Path(cam_path).mkdir(parents=True)

            shutil.copy(configs[i], f'{cam_path}/config.yaml')

            self.video_writers.append(
                VideoWriter(cam_path, fps, save_type)
            )

            cam.RegisterImageEventHandler(self.video_writers[i],
                                          py.RegistrationMode_ReplaceAll,
                                          py.Cleanup_None)

    def __del__(self):
        self.camera_array.Close()
        del self.video_writers

    def run(self):
        self.time = datetime.now()
        print(f'Start recording with {self.num_cameras} Basler cameras')
        self.camera_array.StartGrabbing(py.GrabStrategy_OneByOne,
                                        py.GrabLoop_ProvidedByInstantCamera)

    def is_grabbing(self):
        return self.camera_array.IsGrabbing()

    def stop(self):
        print(f'Stop recording after {(datetime.now() - self.time).total_seconds()} seconds')
        self.camera_array.StopGrabbing()
        for writer in self.video_writers:
            writer.stop_recording()
