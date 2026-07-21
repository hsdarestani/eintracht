from django import forms
from django.contrib.auth import get_user_model
from .models import Match, MatchPerformance, Player, PlayerEvaluation, ReportNote, TaskAssignment, TeamEvent, TrainingSession

DT_INPUT = forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M")

class StyledFormMixin:
    def apply_styles(self):
        for field in self.fields.values():
            cls = "form-control"
            if isinstance(field.widget, forms.CheckboxInput):
                cls = "form-check-input"
            field.widget.attrs["class"] = cls

class SetupForm(forms.Form, StyledFormMixin):
    first_name = forms.CharField(label="Vorname", max_length=80)
    last_name = forms.CharField(label="Nachname", max_length=80)
    username = forms.CharField(label="Benutzername", max_length=80)
    password = forms.CharField(label="Sicheres Passwort", widget=forms.PasswordInput, min_length=10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.apply_styles()

    def save(self):
        User = get_user_model()
        return User.objects.create_superuser(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )

class PlayerForm(forms.ModelForm, StyledFormMixin):
    class Meta:
        model = Player
        fields = ["first_name", "last_name", "shirt_number", "position", "status", "birth_date", "nationality", "notes"]
        labels = {"first_name":"Vorname","last_name":"Nachname","shirt_number":"Rückennummer","position":"Position","status":"Status","birth_date":"Geburtsdatum","nationality":"Nationalität","notes":"Interne Notiz"}
        widgets = {"birth_date": forms.DateInput(attrs={"type":"date"})}
    def __init__(self,*args,**kwargs): super().__init__(*args,**kwargs); self.apply_styles()

class EvaluationForm(forms.ModelForm, StyledFormMixin):
    class Meta:
        model = PlayerEvaluation
        fields = ["mentality", "physicality", "performance", "potential", "comment"]
        labels = {"mentality":"Mentalität","physicality":"Physis","performance":"Leistung","potential":"Potenzial","comment":"Kommentar des Trainers"}
        widgets = {k: forms.NumberInput(attrs={"type":"range","min":1,"max":10,"step":1}) for k in ["mentality","physicality","performance","potential"]} | {"comment": forms.Textarea(attrs={"rows":4})}
    def __init__(self,*args,**kwargs): super().__init__(*args,**kwargs); self.apply_styles()

class TrainingForm(forms.ModelForm, StyledFormMixin):
    class Meta:
        model = TrainingSession
        fields = ["title", "starts_at", "ends_at", "location", "focus", "status", "notes"]
        labels = {"title":"Titel","starts_at":"Start","ends_at":"Ende","location":"Ort","focus":"Trainingsfokus","status":"Status","notes":"Notizen"}
        widgets = {"starts_at": DT_INPUT, "ends_at": DT_INPUT, "notes": forms.Textarea(attrs={"rows":4})}
    def __init__(self,*args,**kwargs): super().__init__(*args,**kwargs); self.apply_styles(); self.fields["starts_at"].input_formats=["%Y-%m-%dT%H:%M"]; self.fields["ends_at"].input_formats=["%Y-%m-%dT%H:%M"]

class EventForm(forms.ModelForm, StyledFormMixin):
    class Meta:
        model = TeamEvent
        fields = ["title", "event_type", "starts_at", "ends_at", "location", "notes"]
        labels = {"title":"Titel","event_type":"Art","starts_at":"Start","ends_at":"Ende","location":"Ort","notes":"Notizen"}
        widgets = {"starts_at": DT_INPUT, "ends_at": DT_INPUT, "notes": forms.Textarea(attrs={"rows":4})}
    def __init__(self,*args,**kwargs): super().__init__(*args,**kwargs); self.apply_styles(); self.fields["starts_at"].input_formats=["%Y-%m-%dT%H:%M"]; self.fields["ends_at"].input_formats=["%Y-%m-%dT%H:%M"]

class MatchForm(forms.ModelForm, StyledFormMixin):
    class Meta:
        model = Match
        fields = ["opponent", "kickoff", "competition", "location", "venue", "goals_for", "goals_against", "notes"]
        labels = {"opponent":"Gegner","kickoff":"Anstoß","competition":"Wettbewerb","location":"Ort","venue":"Spielort","goals_for":"Eigene Tore","goals_against":"Gegentore","notes":"Spielnotizen"}
        widgets = {"kickoff": DT_INPUT, "notes": forms.Textarea(attrs={"rows":4})}
    def __init__(self,*args,**kwargs): super().__init__(*args,**kwargs); self.apply_styles(); self.fields["kickoff"].input_formats=["%Y-%m-%dT%H:%M"]

class MatchPerformanceForm(forms.ModelForm, StyledFormMixin):
    class Meta:
        model = MatchPerformance
        fields = ["player", "minutes_played", "mentality", "physicality", "performance", "comment"]
        labels = {"player":"Spieler","minutes_played":"Spielminuten","mentality":"Mentalität","physicality":"Physis","performance":"Leistung","comment":"Kurzkommentar"}
        widgets = {k: forms.NumberInput(attrs={"type":"range","min":1,"max":10,"step":1}) for k in ["mentality","physicality","performance"]}
    def __init__(self,*args,**kwargs): super().__init__(*args,**kwargs); self.apply_styles(); self.fields["player"].queryset=Player.objects.filter(active=True)

class TaskForm(forms.ModelForm, StyledFormMixin):
    class Meta:
        model = TaskAssignment
        fields = ["player", "task"]
        labels = {"player":"Spieler","task":"Aufgabe"}
    def __init__(self,*args,**kwargs): super().__init__(*args,**kwargs); self.apply_styles(); self.fields["player"].queryset=Player.objects.filter(active=True)

class ReportNoteForm(forms.ModelForm, StyledFormMixin):
    class Meta:
        model = ReportNote
        fields = ["note"]
        labels = {"note":"Kommentar zum Report"}
        widgets = {"note": forms.Textarea(attrs={"rows":4,"placeholder":"Interne Einschätzung oder Hinweise für den Ausdruck …"})}
    def __init__(self,*args,**kwargs): super().__init__(*args,**kwargs); self.apply_styles()
