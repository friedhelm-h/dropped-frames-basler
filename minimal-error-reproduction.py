import argparse

from recording.recorder import Recorder


def parse_args():
    parser = argparse.ArgumentParser(description='minimal-error-reproduction',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--save_type_basler', dest='save_type_basler', default='mp4', help='')
    parser.add_argument('-f', '--fps', dest='fps', type=int, default=120, help='')
    parser.add_argument('-c', '--basler_config', dest='basler_config',
                        default='config/basler_0.yaml', help=''),
    return parser.parse_args()


def main():
    args = parse_args()

    basler_recorder = Recorder(args.basler_config, path, fps, save_type_basler)
    basler_recorder.run()


if __name__ == '__main__':
    main()