from django.contrib import admin
from .models import BadgeAward, Language, LearnerProfile, Lesson, PerformanceLog, QuizQuestion, TutorInteraction


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "code")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "language", "step_number", "difficulty")
    list_filter = ("language", "difficulty")
    ordering = ("language", "step_number")


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("lesson", "prompt", "correct_option")
    list_filter = ("lesson__language",)


@admin.register(LearnerProfile)
class LearnerProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "language", "completed_lessons", "quiz_attempts", "correct_answers")
    list_filter = ("language",)


@admin.register(PerformanceLog)
class PerformanceLogAdmin(admin.ModelAdmin):
    list_display = ("learner", "lesson", "question", "is_correct", "points", "created_at")
    list_filter = ("is_correct", "lesson__language")


@admin.register(BadgeAward)
class BadgeAwardAdmin(admin.ModelAdmin):
    list_display = ("learner", "title", "created_at")
    list_filter = ("title", "learner__language")


@admin.register(TutorInteraction)
class TutorInteractionAdmin(admin.ModelAdmin):
    list_display = ("learner", "provider", "used_external_ai", "created_at")
    list_filter = ("provider", "used_external_ai", "learner__language")
