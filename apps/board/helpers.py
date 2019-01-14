import hashlib
import io
import json
import random
import subprocess

from PIL import Image
from django.core.files.images import get_image_dimensions
from django.utils import timezone

from . import constants


def resolve_save_path(instance, filename):
    """
    Вычисляем путь для сохранения нового файла
    :param instance: Инстанс сохраняемого объекта
    :param str filename: Первоначальное имя файла
    :return: Путь для сохранения файла
    :rtype: str
    """

    thread = instance.post.thread.thread_num
    board = instance.post.thread.board.board

    now = timezone.now()
    date = now.strftime('%Y/%m/%d')

    return f'{date}/{board}/src/{thread}/{filename}'


def resolve_thumb_path(instance, filename):
    thread = instance.post.thread.thread_num
    board = instance.post.thread.board.board

    now = timezone.now()
    date = now.strftime('%Y/%m/%d')

    return f'{date}/{board}/thumb/{thread}/{filename}'


def roulette(match):
    """
    Бросаем кости с указанным количеством граней n-раз
    Использование 1RL2, где 1 - число граней, 2 - количество раз
    :param match: Объект match регулярного выражения
    :return: форматированный в html результат броска костей
    :rtype: str
    """

    first_num = int(match.group(1))
    last_num = int(match.group(2))

    if 0 < first_num <= 100 and 0 < last_num <= 10:
        maximum = first_num * last_num
        result = 0
        result_line = ''

        for i in range(0, last_num):
            rand_int = random.randint(0, first_num)
            result += rand_int
            result_line = (
                rand_int if not result_line else f'{result_line} + {rand_int}'
            )

        full_line = (
            f'{first_num}x{last_num}: {result_line} = {result}({maximum})'
        )
        return f'<br><span class="roulette">{full_line}</span><br>'

    return f'{first_num}RL{last_num}'


def process_file(file_type, file):
    file.seek()
    temp_buffer = io.BytesIO(file.read())

    md5 = hashlib.md5()
    md5.update(temp_buffer.getvalue())
    md5 = md5.hexdigest()

    if file_type == constants.IMAGE_FILE:
        thumb = Image.open(temp_buffer)
        width, height = get_image_dimensions(thumb)

        if thumb.mode in ('RGBA', 'LA'):
            background = Image.new(thumb.mode[:-1], thumb.size,
                                   (255, 255, 255))
            background.paste(thumb, thumb.split()[-1])
            thumb = background

        size = thumb.size
        if size[0] > size[1]:
            scale_factor = 500 / size[0]
        else:
            scale_factor = 500 / size[1]

        new_width = int(thumb.width * scale_factor)
        new_height = int(thumb.height * scale_factor)

        thumb = thumb.resize((new_width, new_height), Image.LANCZOS)
        thumb = thumb.convert("RGB")

        temp_buffer = io.BytesIO()
        thumb.save(temp_buffer, "JPEG")

        return io.BytesIO(temp_buffer.getvalue()), md5, width, height

    elif file_type == constants.VIDEO_FILE:
        _FFMPEG_FLAGS = ' '.join([
            '-hide_banner',
            '-loglevel quiet',
            '-i pipe:0',
            '-f mjpeg',
            '-frames:v 1',
            '-q:v 2',
            '-vf scale=w=500:h=500:force_original_aspect_ratio=decrease',
            'pipe:1'
        ])
        _FFPROBE_FLAGS = ' '.join([
            '-hide_banner',
            '-loglevel quiet',
            '-i pipe:0',
            '-select_streams v:0',
            '-print_format json',
            '-show_entries format=duration',
            '-show_entries stream=width,height'
        ])

        ffmpeg_commandline = f'ffmpeg {_FFMPEG_FLAGS}'.split()
        ffprobe_commandline = f'ffprobe {_FFPROBE_FLAGS}'.split()

        ffmpeg_result = subprocess.run(ffmpeg_commandline,
                                       input=temp_buffer.getvalue(),
                                       stdout=subprocess.PIPE)
        ffprobe_result = subprocess.run(ffprobe_commandline,
                                        input=temp_buffer.getvalue(),
                                        stdout=subprocess.PIPE)

        ffprobe_result_json = json.loads(ffprobe_result.stdout)

        file_streams = ffprobe_result_json['streams']
        file_format = ffprobe_result_json['format']
        duration = int(float(file_format.get('duration', 0)))
        stream = file_streams[0]
        width = stream.get('width', 0)
        height = stream.get('height', 0)

        return io.BytesIO(ffmpeg_result.stdout), md5, duration, width, height
