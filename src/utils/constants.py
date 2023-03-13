__resolutions: dict[str, tuple] = {
    '1080P': (1920, 1080),
    '720P': (1280, 720),
    '480P': (854, 480),
    '360P': (640, 360),
    '240P': (426, 240),
    '144P': (256, 144)
}

videos_quality_list: dict[tuple, list[tuple]] = {
    __resolutions['1080P']: [__resolutions['720P'], __resolutions['480P'], __resolutions['360P'], __resolutions['240P'], __resolutions['144P']],
    __resolutions['720P']: [__resolutions['480P'], __resolutions['360P'], __resolutions['240P'], __resolutions['144P']],
    __resolutions['480P']: [__resolutions['360P'], __resolutions['240P'], __resolutions['144P']],
    __resolutions['360P']: [__resolutions['240P'], __resolutions['144P']],
    __resolutions['240P']: [__resolutions['144P']],
    __resolutions['144P']: [],
}

quality = {
    __resolutions['1080P']: '1080P',
    __resolutions['720P']: '720P',
    __resolutions['480P']: '480P',
    __resolutions['360P']: '360P',
    __resolutions['240P']: '240P',
    __resolutions['144P']: '144P',
}
