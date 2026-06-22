from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Language",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("code", models.CharField(max_length=10, unique=True)),
                ("description", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="LearnerProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("completed_lessons", models.PositiveIntegerField(default=0)),
                ("quiz_attempts", models.PositiveIntegerField(default=0)),
                ("correct_answers", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "language",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="learners", to="learning.language"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learner_profiles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("name", "language")},
            },
        ),
        migrations.CreateModel(
            name="Lesson",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("step_number", models.PositiveIntegerField()),
                ("title", models.CharField(max_length=200)),
                ("content", models.TextField()),
                ("funny_activity", models.TextField()),
                (
                    "difficulty",
                    models.CharField(
                        choices=[("beginner", "Beginner"), ("intermediate", "Intermediate"), ("advanced", "Advanced")],
                        default="beginner",
                        max_length=20,
                    ),
                ),
                (
                    "language",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lessons", to="learning.language"),
                ),
            ],
            options={
                "ordering": ["step_number"],
                "unique_together": {("language", "step_number")},
            },
        ),
        migrations.CreateModel(
            name="BadgeAward",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=80)),
                ("description", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "learner",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="badges", to="learning.learnerprofile"),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("learner", "title")},
            },
        ),
        migrations.CreateModel(
            name="QuizQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("prompt", models.CharField(max_length=255)),
                ("option_a", models.CharField(max_length=200)),
                ("option_b", models.CharField(max_length=200)),
                ("option_c", models.CharField(max_length=200)),
                ("option_d", models.CharField(max_length=200)),
                ("correct_option", models.CharField(choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")], max_length=1)),
                (
                    "lesson",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="question", to="learning.lesson"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PerformanceLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_correct", models.BooleanField(default=False)),
                ("points", models.IntegerField(default=0)),
                ("notes", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "learner",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="logs", to="learning.learnerprofile"),
                ),
                (
                    "lesson",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="learning.lesson"),
                ),
                (
                    "question",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="learning.quizquestion"),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="TutorInteraction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("prompt", models.TextField()),
                ("response", models.TextField()),
                ("provider", models.CharField(default="local-ai", max_length=100)),
                ("used_external_ai", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "learner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tutor_interactions",
                        to="learning.learnerprofile",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="learnerprofile",
            constraint=models.UniqueConstraint(fields=("user", "language"), name="unique_user_language_profile"),
        ),
    ]
