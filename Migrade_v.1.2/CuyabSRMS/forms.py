from django import forms
from .models import ProcessedDocument
from .models import Subject
from .models import GradeScores, SchoolInformation, CoreValues, BehaviorStatement, LearnersObservation
from multiupload.fields import MultiFileField


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = ProcessedDocument
        fields = ('document',)  

class ExtractedDataForm(forms.Form):
    # Define form fields based on the keys in the extracted_data dictionary
    def __init__(self, extracted_data, *args, **kwargs):
        super(ExtractedDataForm, self).__init__(*args, **kwargs)
        for key, value in extracted_data.items():
            self.fields[key] = forms.CharField(initial=value, label=key, required=True)

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'assessment']


class GradeScoresForm(forms.ModelForm):
    class Meta:
        model = GradeScores
        fields = ['initial_grades', 'transmuted_grades']


class SchoolInformationForm(forms.ModelForm):
    class Meta:
        model = SchoolInformation
        fields = '__all__'

class DocumentBatchUploadForm(forms.Form):
    documents = MultiFileField(min_num=1, max_num=None, max_file_size=1024*1024*5)

class CoreValuesForm(forms.ModelForm):
    class Meta:
        model = CoreValues
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter core value name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter description'}),
        }
        def __init__(self, *args, **kwargs):
            super(CoreValuesForm, self).__init__(*args, **kwargs)
            self.fields['description'].required = False

class BehaviorStatementForm(forms.ModelForm):
    class Meta:
        model = BehaviorStatement
        fields = ['core_value', 'statement']
        widgets = {
            'core_value': forms.Select(attrs={'class': 'form-select'}),
            'statement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter behavior statement'}),
        }

class LearnersObservationForm(forms.Form):
    def __init__(self, students, behavior_statements, *args, **kwargs):
        super(LearnersObservationForm, self).__init__(*args, **kwargs)
        
        for student in students:
            for quarter in range(1, 5):  # Four quarters
                for behavior_statement in behavior_statements:
                    field_name = f'student_{student.id}_quarter_{quarter}_behavior_{behavior_statement.id}'
                    self.fields[field_name] = forms.ChoiceField(
                        label=behavior_statement.statement,
                        choices=[
                            ('AO', 'Always Observed'),
                            ('SO', 'Sometimes Observed'),
                            ('RO', 'Rarely Observed'),
                            ('NO', 'Not Observed'),
                        ],
                        widget=forms.RadioSelect
                    )