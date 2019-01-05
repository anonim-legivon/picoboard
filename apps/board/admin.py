from django.contrib import admin

from .models import Board, Category, Post, Thread


# Register your models here.

class PostsInline(admin.TabularInline):
    model = Post
    fields = ('is_op_post', 'date', 'topic', 'message', 'ip')
    readonly_fields = ('date', 'is_op_post')
    fk_name = 'thread'


class ThreadAdmin(admin.ModelAdmin):
    inlines = (PostsInline,)
    list_display = ('board', 'thread_id',)

    def save_related(self, request, form, formsets, change):
        op_post = formsets[0][0].instance
        if op_post:
            obj = op_post  # 1st formset 1st form values
            obj.is_op_post = True
            super(ThreadAdmin, self).save_related(request, form, formsets,
                                                  change)


class PostAdmin(admin.ModelAdmin):
    list_display = ('thread', 'message', 'date')


admin.site.register(Post, PostAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register([Category, Board])
