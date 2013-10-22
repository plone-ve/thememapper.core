from flask.ext.babel import gettext
import copy

class _NavigationModel:

    def __init__(self):
        self.nav_items = [
            {'slug':'home','text':      gettext('Home'),                 'url':'/',              'class':'',     'target':'_self'},
            {'slug':'editor',     'text': gettext('Editor'), 'url':'/editor/',        'class':'' ,'target':'_self'},
            {'slug':'settings',    'text': gettext('Settings'),'url':'/settings/', 'class':'',     'target':'_self'},
        ]

    def get_items(self,active='home',extra_items=None):
        items = copy.deepcopy(self.nav_items)
        if extra_items is not None:
            items.extend(extra_items)
        for item in items:
            if item['slug'] == active:
                item['class'] += ' active'
        return items
