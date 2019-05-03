#!/usr/bin/env python3

import gevent.monkey
gevent.monkey.patch_all()

import os
import sys
import re
import gevent
import gevent.pool
import requests
import m3u8
import logging
import urllib.parse
import json


class M3U8Downloader:
    def __init__(self, config, pool_size, retry = 1):
        self._config = config
        self.set_pool(pool_size, retry)

    def set_pool(self, pool_size, retry = None):
        self._pool_size = pool_size
        if retry:
            self._retry = retry
        self._pool = gevent.pool.Pool(self._pool_size)
        self._session = self._get_http_session(self._pool_size, self._retry)

    def run(self, uri = None):
        self._output_dir = self._config.get('output_dir', '')
        self._timeout = self._config.get('timeout', 20)
        self._headers = self._config.get('headers', {})

        if not uri:
            uri = self._config.get('uri', None)
            if not uri:
                raise ValueError('Uri should not be empty.')

        if not self._output_dir:
            raise ValueError('Output Dir should not be empty.')
        if os.path.isfile(self._output_dir):
            raise ValueError('File {0} has already existed.'.format(self._output_dir))
        os.makedirs(self._output_dir, exist_ok = True)

        self._m3u8_content = self._download_m3u8(uri, self._timeout, self._headers)
        assert(self._m3u8_content.is_variant is False)

        self._failed = []
        self._pool.map(self._download_ts, self._m3u8_content.segments)

        if self._failed:
            logging.error('[Run Finish] Some files fail to download. Please check the configure and run again.')
            return
        else:
            logging.info('[Finish Download]')

        input_file = self._dump_m3u8(uri)
        if self._config.get('concat', True):
            output_file = self._config.get('output_file', None)
            if not output_file:
                logging.error('[Concat] Can\'t get output file name')
                logging.error('[Help] "cancat_file" should be set if "concat" is True or default')
                logging.error('[Help] "cancat_file" is relative to "output_dir"')
                return
            output_file = os.path.abspath(os.path.join(self._output_dir, output_file))
            #self.concat_with_ffmpeg(input_file, output_file)

    def concat_with_ffmpeg(self, input_file, output_file):
        ffmpeg_path = self._config.get('ffmpeg_path', 'ffmpeg')
        ffmpeg_loglevel = self._config.get('ffmpeg_loglevel', 'quiet')
        ffmpeg_cmd = '{0} -y -loglevel {1} -i {2} -c copy {3}'.format(ffmpeg_path, ffmpeg_loglevel, input_file, output_file)
        logging.info('[concat cmd] {0}'.format(ffmpeg_cmd))
        os.system(ffmpeg_cmd)

    def _dump_m3u8(self, uri):
        for index, segment in enumerate(self._m3u8_content.segments):
            self._m3u8_content.segments[index].uri = self._get_filename(segment.uri, self._output_dir)

        filename = self._get_filename(uri, self._output_dir)
        self._m3u8_content.dump(filename)
        return filename

    def _download_m3u8(self, uri, timeout, headers):
        content = m3u8.load(uri, timeout, headers)
        if content.is_variant:
            print('\nThere are various m3u8 files. Please select one of them.\n')
            for index, playlist in enumerate(content.playlists):
                self._print_stream_info(index, playlist)

            try:
                chosen_idx = int(input('INDEX > '))
                chosen_uri = content.playlists[chosen_idx].uri
                return self._download_m3u8(chosen_uri, timeout, headers)

            except (ValueError, IndexError):
                print('Invalid Index! Try Again.')

        return content

    def _download_ts(self, m3u8_segments):
        uri = urllib.parse.urljoin(m3u8_segments.base_uri, m3u8_segments.uri)
        if not self._is_url(uri):
            logging.error('[Not Uri] {0} Skip.'.format(uri))
            self._failed.append(uri)
            return

        filename = self._get_filename(uri, self._output_dir)
        if os.path.exists(filename):
            logging.info('[Exists file] {0} Skip.'.format(filename))
            return

        retry = self._retry
        while retry:
            try:
                response = self._session.get(uri, timeout = self._timeout, headers = self._headers)
                if response.ok:
                    if len(response.content) < self._config.get('ignore_small_file_size', 10 * 1024):
                        logging.error('[File too small] {0}'.format(uri))
                        logging.info('[Help] If you want to download small files, set "ignore_small_file_size" to 0')
                        self._failed.append(uri)
                    else:
                        with open(filename, 'wb') as fout:
                            fout.write(response.content)
                    return
            except:
                retry -= 1
        logging.error('[Download Failed] {0}'.format(uri))
        self._failed.append(uri)

    @staticmethod
    def _print_stream_info(index, playlist):
        print('INDEX: ' + str(index))
        stream_info = playlist.stream_info
        if stream_info.bandwidth:
            print('\tBandwidth: {0}'.format(stream_info.bandwidth))
        if stream_info.average_bandwidth:
            print('\tAverage bandwidth: {0}'.format(stream_info.average_bandwidth))
        if stream_info.program_id:
            print('\tProgram ID: {0}'.format(stream_info.program_id))
        if stream_info.resolution:
            print('\tResolution: {0}'.format(stream_info.resolution))
        if stream_info.codecs:
            print('\tCodecs: {0}'.format(stream_info.codecs))
        print()

    @staticmethod
    def _get_http_session(pool_size, retry):
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_size, pool_size, retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @staticmethod
    def _is_url(uri):
        return re.match(r'https?://', uri) is not None

    @staticmethod
    def _get_filename(uri, dir):
        basename = urllib.parse.urlparse(uri).path.split('/')[-1]
        filename = os.path.abspath(os.path.join(dir, basename))
        return filename

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, 
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    config_file = open('config.json', 'r')
    config = json.load(config_file)
    pool_size = config.get("pool size")
    #process_number = input("Process Number: ")
    x = M3U8Downloader(config, pool_size)
    x.run()