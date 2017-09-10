from __future__ import unicode_literals

import logging
import time
import discid

try:
    import musicbrainzngs
    musicbrainz = True
except:
    musicbrainz = False

logger = logging.getLogger(__name__)

class Cdrom(object):

    def __init__(self):
        self.refresh()

    def refresh(self):
        self.tracks=[]

        self.title = "No Disc" # blank title?

        try:
            self.disc = discid.read()
        except:
            logger.debug("Cdrom: Unable to read cd")
            return

        logger.debug("Cdrom: reading cd")
        self.n = len(self.disc.tracks)
        logger.debug('Cdrom: %d tracks found',self.n)

        if musicbrainz:
            musicbrainzngs.set_useragent("Audacious", "0.1", "https://github.com/jonnybarnes/audacious")
            try:
                result = musicbrainzngs.get_releases_by_discid(self.disc.id, includes=["artists", "recordings"])
            except musicbrainzngs.ResponseError:
                logger.debug("Disc not found on Musicbrainz")
            else:
                if 'disc' in result:
                    mbtracks = result["disc"]["release-list"][0]["medium-list"][0]["track-list"]
                    self.title = result["disc"]["release-list"][0]["title"]
                elif 'cdstub' in result:
                    mbtracks = result["cdstub"]["track-list"]
                    self.title = result["cdstub"]["title"]
                else:
                    mbtracks = []
                    logger.debug("Disc Lookup: No Compatible Result Found")

                if len(mbtracks) == len(self.disc.tracks):
                    for mbtrack, track in zip(mbtracks,self.disc.tracks):
                        number = track.number
                        duration = track.seconds
                        if 'title' in mbtrack:
                            name = '%s - %s (%s)' % (number, mbtrack['title'], time.strftime('%H:%M:%S', time.gmtime (duration)))
                        elif 'recording' in mbtrack:
                            name = '%s - %s (%s)' % (number, mbtrack['recording']['title'], time.strftime('%H:%M:%S', time.gmtime (duration)))
                        else:
                            name = '%s - %s (%s)' % (number, 'Title Unknown', time.strftime('%H:%M:%S', time.gmtime (duration)))

                        self.tracks.append((number,name,duration))

                    return

        for track in self.disc.tracks:
            number = track.number
            duration = track.seconds
            name = 'Cdrom Track %s (%s)' % (number, time.strftime('%H:%M:%S', time.gmtime (duration)))
            self.tracks.append((number,name,duration))
