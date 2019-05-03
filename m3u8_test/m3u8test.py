import m3u8


url = "http://videofile-hls-ko-record-cf.afreecatv.com/video/_definst_/smil:vod/20190421/945/92240BC9_213347945_1.smil/playlist.m3u8"
url1 = "http://videofile-hls-ko-record-cf.afreecatv.com/video/_definst_/vod/20190421/945/92240BC9_213347945_1.smil/chunklist_b2000000_t64aGQyaw==.m3u8"
m3u8_obj = m3u8.load(url)
variant_info_dict = {}
bandwidth_list = []
if m3u8_obj.is_variant:
    for playlist in m3u8_obj.playlists:
        variant_info_dict[playlist.stream_info.bandwidth] = playlist.uri
        bandwidth_list.append(playlist.stream_info.bandwidth)

final_bandwidth = max(bandwidth_list)
print(final_bandwidth, variant_info_dict[final_bandwidth])