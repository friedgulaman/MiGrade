from django import forms
from .models import ProcessedDocument
from .models import Subject
from .models import GradeScores, SchoolInformation
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
        fields = ['name', 'written_works_percentage', 'performance_task_percentage', 'quarterly_assessment_percentage']


class GradeScoresForm(forms.ModelForm):
    class Meta:
        model = GradeScores
        fields = ['written_works_scores', 'performance_task_scores', 'initial_grades', 'transmuted_grades']


class SchoolInformationForm(forms.ModelForm):
    class Meta:
        model = SchoolInformation
        fields = '__all__'

class DocumentBatchUploadForm(forms.Form):
    documents = MultiFileField(min_num=1, max_num=None, max_file_size=1024*1024*5)