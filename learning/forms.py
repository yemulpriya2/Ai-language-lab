from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Language


class StartLearningForm(forms.Form):
    name = forms.CharField(max_length=120, label="Your name")
    language = forms.ModelChoiceField(queryset=Language.objects.none(), empty_label="Choose a language")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["language"].queryset = Language.objects.all().order_by("name")


class QuizAnswerForm(forms.Form):
    question_id = forms.IntegerField(widget=forms.HiddenInput)
    selected_option = forms.ChoiceField(
        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
        widget=forms.RadioSelect,
        label="Choose the best answer",
    )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class TutorPromptForm(forms.Form):
    prompt = forms.CharField(
        label="Ask AI tutor",
        max_length=600,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Ask anything about your current language lesson..."}),
    )
