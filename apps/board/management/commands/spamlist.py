import json
from os.path import join

from django.conf import settings
from django.core.management import BaseCommand

from board.models import SpamWord


class Command(BaseCommand):
    help = 'Загрузка спам листа из json файла'

    DATA_FILE_PATH = settings.BASE_DIR

    def add_arguments(self, parser):
        parser.add_argument('spamlist', nargs='+', type=str)

    def handle(self, *args, **options):
        spamword_instances = []
        for spamlist in options['spamlist']:
            with open(join(self.DATA_FILE_PATH, spamlist), 'r') as json_file:
                data = json.loads(json_file.read())

            for spamword in data:
                spamword_instances.append(self._import_spamword(spamword))

        SpamWord.objects.bulk_create(spamword_instances)

    def _import_spamword(self, spamword_data):
        spamword = SpamWord(
            expression=spamword_data['expression'],
            for_all_boards=spamword_data['for_all_boards'],
        )
        return spamword
