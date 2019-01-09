from __future__ import absolute_import, unicode_literals

# @celery_app.task()
# def clear_db():
#     _, threads_count = Thread.all_objects.filter(is_removed=True).delete()
#     _, posts_count = Post.all_objects.filter(is_removed=True).delete()
#     return {'deleted': [threads_count, posts_count]}
