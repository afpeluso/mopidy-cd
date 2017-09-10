import pykka

from mopidy import backend
from mopidy.models import Ref, Track
from . import cdrom
import logging

logger = logging.getLogger(__name__)


class CdBackend(pykka.ThreadingActor, backend.Backend):
    uri_schemes = ['cd']

    def __init__(self, config, audio):
        super(CdBackend, self).__init__()
        self.audio = audio
        self.cdrom = cdrom.Cdrom()

        self.library = CdLibrary(backend=self)
        self.playback = CdPlaybackProvider(audio=audio, backend=self)

class CdLibrary(backend.LibraryProvider):

    def __init__(self, backend):
        self.backend = backend # be sure to assign it...
        self.refresh() # refreshes the CD and the title

    def browse(self, uri):
        self.refresh()

        results = []
        if not uri=='cd:root':
            return results
        logger.debug('Cdrom backend %s',self.backend)
        tracks = self.backend.cdrom.tracks
        logger.debug('Cdrom: in browse found %d tracks',len(tracks))
        for (seq,(number,name,duration)) in enumerate(tracks,1):
            results.append(Ref.track(uri='cd:/'+str(seq), name=name))
        return results

    def refresh(self, uri=None):
        self.backend.cdrom.refresh()
        if self.backend.cdrom.title is not None:
            self.root_directory = Ref.directory(uri='cd:root', name='CD: ' + self.backend.cdrom.title)
        else:
            self.root_directory = Ref.directory(uri='cd:root', name='CD: No Disc')

    def lookup(self, uri):
        logger.debug('Cdrom: track selected')
        i=int(uri.lstrip("cd:/"))-1
        logger.debug('Cdrom: track %s selected',i)
        (number,name,duration) = self.backend.cdrom.tracks[i]
        return [Track(uri=uri,
                      name=name,
                      length=int(duration)*1000)]

class CdPlaybackProvider(backend.PlaybackProvider):

    def change_track(self, track):
        logger.debug('Cdrom: playing track %s', track)
        return super(CdPlaybackProvider, self).change_track(track)

    def translate_uri(self, uri):
        return uri.replace('cd:/','cdda://')
