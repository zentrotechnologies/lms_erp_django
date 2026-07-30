from django.contrib import admin
from django.urls import path
from .import views as v


urlpatterns = [
    path('candidate-list',v.candidateList,name="Candidatelist"),
    path('add-candidate',v.addCandidate,name="addCandidate"),
    path('update-candidate/<uuid:id>',v.updateCandidate,name="updateCandidate"),
    path('view-candidate-profile/<uuid:id>',v.ViewCandidateProfile,name="ViewCandidateProfile"),
    path('candidates-results',v.CandidatesResults,name="CandidatesResults"),

]