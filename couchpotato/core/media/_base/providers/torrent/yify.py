from couchpotato.core.helpers.variable import tryInt
from couchpotato.core.logger import CPLog
import traceback
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider

log = CPLog(__name__)


class Base(TorrentProvider):

    urls = {
        'test': '%s/api',
        'search': '%s/api/list.json?keywords=%s&quality=%s',
        'detail': '%s/api/movie.json?id=%s'
    }

    http_time_between_calls = 1  #seconds

    proxy_list = [
        'http://yify.unlocktorrent.com',
        'http://yify-torrents.com.come.in',
        'http://yts.re',
        'http://yts.im'
        'https://yify-torrents.im',
    ]

    def search(self, movie, quality):

        if not quality.get('hd', False):
            return []

        return super(Base, self).search(movie, quality)

    def _search(self, movie, quality, results):

        search_url = self.urls['search'] % (self.getDomain(), movie['identifier'], quality['identifier'])

        data = self.getJsonData(search_url)

        if data and data.get('MovieList'):
            try:
                for result in data.get('MovieList'):

                    try:
                        title = result['TorrentUrl'].split('/')[-1][:-8].replace('_', '.').strip('._')
                        title = title.replace('.-.', '-')
                        title = title.replace('..', '.')
                    except:
                        continue

                    results.append({
                        'id': result['MovieID'],
                        'name': title,
                        'url': result['TorrentMagnetUrl'],
                        'detail_url': self.urls['detail'] % (self.getDomain(), result['MovieID']),
                        'size': self.parseSize(result['Size']),
                        'seeders': tryInt(result['TorrentSeeds']),
                        'leechers': tryInt(result['TorrentPeers'])
                    })

            except:
                log.error('Failed getting results from %s: %s', (self.getName(), traceback.format_exc()))

    def correctProxy(self, data):
        data = data.lower()
        return 'yify' in data and 'yts' in data


config = [{
    'name': 'yify',
    'groups': [
        {
            'tab': 'searcher',
            'list': 'torrent_providers',
            'name': 'Yify',
            'description': 'Free provider, less accurate. Small HD movies, encoded by <a href="https://yify-torrents.com/">Yify</a>.',
            'wizard': False,
            'options': [
                {
                    'name': 'enabled',
                    'type': 'enabler',
                    'default': 0
                },
                {
                    'name': 'domain',
                    'advanced': True,
                    'label': 'Proxy server',
                    'description': 'Domain for requests, keep empty to let CouchPotato pick.',
                },
                {
                    'name': 'seed_ratio',
                    'label': 'Seed ratio',
                    'type': 'float',
                    'default': 1,
                    'description': 'Will not be (re)moved until this seed ratio is met.',
                },
                {
                    'name': 'seed_time',
                    'label': 'Seed time',
                    'type': 'int',
                    'default': 40,
                    'description': 'Will not be (re)moved until this seed time (in hours) is met.',
                },
                {
                    'name': 'extra_score',
                    'advanced': True,
                    'label': 'Extra Score',
                    'type': 'int',
                    'default': 0,
                    'description': 'Starting score for each release found via this provider.',
                }
            ],
        }
    ]
}]