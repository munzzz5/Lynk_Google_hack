from django import forms
from .models import Feedback

# Step 1: Category Selection


class FeedbackCategoryForm(forms.Form):
    CATEGORY_CHOICES = [
        ('work_related', 'Work Related'),
        ('culture_related', 'Culture Related'),
    ]
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=True)

# Step 2: Topic and Department (shown if category is 'work')


class FeedbackWorkForm(forms.Form):
    DEPARTMENT_CHOICES = [
        ('it', 'IT'),
        ('hr', 'Human Resources'),
        ('finance', 'Finance'),
        ('marketing', 'Marketing'),
        ('office supplies', 'Office Supplies'),
        ('sales', 'Sales'),
        ('other', 'Other'),
    ]
    topic = forms.CharField(max_length=255, required=True)
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, required=True)

# Step 3: Additional Details


class FeedbackDetailsForm(forms.Form):
    suggestions = forms.CharField(widget=forms.Textarea, required=False)
    effect = forms.CharField(widget=forms.Textarea, required=True)
    description = forms.CharField(
        widget=forms.Textarea, required=True)  # For problem/pain point
    tools = forms.CharField(max_length=255, required=False)
    affected_areas = forms.CharField(widget=forms.Textarea, required=False)
    anonymous = forms.BooleanField(required=False)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = '__all__'
        exclude = ['tags']
        widgets = {
            'suggestions': forms.Textarea(attrs={'rows': 2}),
            'effect': forms.Textarea(attrs={'rows': 2}),
            'description': forms.Textarea(attrs={'rows': 2}),
            'affected_areas': forms.Textarea(attrs={'rows': 2}),
        }
