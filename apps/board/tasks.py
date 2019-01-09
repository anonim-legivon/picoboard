from __future__ import absolute_import, unicode_literals

from apps.board.models import Post, Thread
from picoboard import celery_app


@celery_app.task()
def clear_db():
    _, threads_count = Thread.all_objects.filter(is_removed=True).delete()
    _, posts_count = Post.all_objects.filter(is_removed=True).delete()
    return {'deleted': [threads_count, posts_count]}

# @celery_app.task()
# def bump_limit_threads():
#     max_posts = Board.objects.filter(threads=OuterRef('pk')).values(
#         'bump_limit')
#     max_threads = Board.objects.filter(threads=OuterRef('pk')).values(
#         'thread_limit'
#     )
#     threads_in_bump_limit = Thread.objects.annotate(
#         p_count=Count('posts'), max_posts=Subquery(max_posts),
#     ).filter(p_count__gte=max_posts)
#
#     indexes = []
#
#     threads = Thread.objects.all().order_by('-lasthist')
#     for thread in threads_in_bump_limit:
#         index = threads.ind
