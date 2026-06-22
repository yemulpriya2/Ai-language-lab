from django.db import models
from django.conf import settings


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Lesson(models.Model):
    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="lessons")
    step_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    content_target_language = models.TextField(default="", blank=True)
    content_english = models.TextField(default="", blank=True)
    funny_activity = models.TextField()
    funny_activity_target_language = models.TextField(default="", blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="beginner")

    class Meta:
        ordering = ["step_number"]
        unique_together = ("language", "step_number")

    def __str__(self):
        return f"{self.language.name} - Step {self.step_number}: {self.title}"


class QuizQuestion(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="question")
    prompt = models.CharField(max_length=255)
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")])

    def __str__(self):
        return self.prompt


class LearnerProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="learner_profiles")
    name = models.CharField(max_length=120)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="learners")
    completed_lessons = models.PositiveIntegerField(default=0)
    quiz_attempts = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("name", "language")
        constraints = [
            models.UniqueConstraint(fields=["user", "language"], name="unique_user_language_profile"),
        ]

    @property
    def accuracy(self):
        if self.quiz_attempts == 0:
            return 0
        return round((self.correct_answers / self.quiz_attempts) * 100, 1)

    @property
    def performance_score(self):
        lesson_part = min(self.completed_lessons * 20, 50)
        quiz_part = min(self.accuracy * 0.5, 50)
        return round(lesson_part + quiz_part, 1)

    @property
    def level(self):
        score = self.performance_score
        if score < 25:
            return "Starter"
        if score < 50:
            return "Explorer"
        if score < 75:
            return "Communicator"
        if score < 90:
            return "Speaker"
        return "Master"

    def __str__(self):
        return f"{self.name} ({self.language.name})"


class PerformanceLog(models.Model):
    learner = models.ForeignKey(LearnerProfile, on_delete=models.CASCADE, related_name="logs")
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)
    question = models.ForeignKey(QuizQuestion, on_delete=models.SET_NULL, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.learner.name} | {self.points} pts | correct={self.is_correct}"


class BadgeAward(models.Model):
    learner = models.ForeignKey(LearnerProfile, on_delete=models.CASCADE, related_name="badges")
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("learner", "title")

    def __str__(self):
        return f"{self.learner.name} - {self.title}"


class TutorInteraction(models.Model):
    learner = models.ForeignKey(LearnerProfile, on_delete=models.CASCADE, related_name="tutor_interactions")
    prompt = models.TextField()
    response = models.TextField()
    provider = models.CharField(max_length=100, default="local-ai")
    used_external_ai = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Tutor chat for {self.learner.name} ({self.provider})"
