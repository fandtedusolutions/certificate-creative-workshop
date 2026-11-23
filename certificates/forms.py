import re
from django import forms
from .models import StudentLead, format_student_name


class StudentLeadForm(forms.ModelForm):
    class Meta:
        model = StudentLead
        fields = ['name', 'student_class', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter your full name',
                'autocomplete': 'name',
                'required': 'required',
                'style': 'text-transform: capitalize;',
            }),
            'student_class': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'required': 'required',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter 10-digit WhatsApp / Phone number',
                'type': 'tel',
                'autocomplete': 'tel',
                'required': 'required',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add an empty choice at the beginning of the dropdown
        choices = [('', '-- Select your year / class --')] + list(StudentLead.CLASS_CHOICES)
        self.fields['student_class'].choices = choices
        self.fields['name'].label = "Full Name"
        self.fields['student_class'].label = "Class / Year"
        self.fields['phone_number'].label = "Phone / WhatsApp Number"

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your complete name.")
        # Ensure first letter of every word is capitalized
        return format_student_name(name)

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        # Clean up common phone formatting symbols
        cleaned_digits = re.sub(r'[\s\-\(\)\+]', '', phone)
        if len(cleaned_digits) < 10:
            raise forms.ValidationError("Please enter a valid phone number with at least 10 digits.")
        return phone

