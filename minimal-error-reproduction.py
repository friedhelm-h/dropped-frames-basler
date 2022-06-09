import argparse
from datetime import datetime
import time

from recording.recorder import Recorder


def parse_args():
    parser = argparse.ArgumentParser(description='minimal-error-reproduction',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--save_type_basler', dest='save_type_basler', default='mp4', help='')
    parser.add_argument('-f', '--fps', dest='fps', type=int, default=120, help='')
    parser.add_argument('-c', '--basler_config', dest='basler_config',
                        default='config/basler_0.yaml', help=''),
    parser.add_argument('-o', '--out_path', dest='out_path', default='data', help='')
    return parser.parse_args()


def main():
    args = parse_args()

    out_path = f'{args.out_path}/min-error-demo_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'

    recorder = Recorder(args.basler_config, out_path, args.fps, args.save_type_basler)
    recorder.run()

    cnt = 0
    while recorder.is_grabbing():
        if cnt < 10:
            time.sleep(1)
            cnt += 1
        else:
            break

    recorder.stop()


if __name__ == '__main__':
    main()
