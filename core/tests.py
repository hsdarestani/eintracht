from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import (
    EVALUATION_CATEGORIES,
    Attendance,
    Match,
    Player,
    PlayerEvaluation,
    TeamEvent,
    TrainingSession,
)
from .views import seed_demo_data


class InitialSetupTests(TestCase):
    def test_setup_creates_first_coach_and_demo_data(self):
        response = self.client.post(
            reverse("setup"),
            {
                "first_name": "Test",
                "last_name": "Trainer",
                "username": "coach",
                "password": "SecureCoach!2026",
            },
        )
        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(get_user_model().objects.filter(username="coach").exists())
        self.assertGreater(Player.objects.count(), 0)


class AuthenticatedPagesTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            "coach",
            "coach@example.com",
            "SecureCoach!2026",
            first_name="Test",
        )
        seed_demo_data(self.user)
        self.client.force_login(self.user)

    def test_main_pages_render(self):
        urls = [
            reverse("dashboard"),
            reverse("players"),
            reverse("trainings"),
            reverse("calendar"),
            reverse("matches"),
            reverse("report"),
            reverse("player_detail", args=[Player.objects.first().pk]),
            reverse("evaluate_player", args=[Player.objects.first().pk]),
            reverse("training_detail", args=[TrainingSession.objects.first().pk]),
            reverse("match_detail", args=[Match.objects.first().pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_detailed_evaluation_page_contains_all_categories(self):
        player = Player.objects.first()
        response = self.client.get(reverse("evaluate_player", args=[player.pk]))
        self.assertContains(response, "Gesamtleistung")
        self.assertContains(response, "Spielintelligenz")
        self.assertContains(response, "Man of the Match")
        self.assertEqual(response.content.decode().count('type="range"'), len(EVALUATION_CATEGORIES))

    def test_detailed_evaluation_saves_scores_and_legacy_summary(self):
        player = Player.objects.first()
        payload = {
            key: 8 if key != "mentality" else 9
            for key, _label, _group_slug, _group_label in EVALUATION_CATEGORIES
        }
        payload["comment"] = "Sehr komplette Leistung."
        response = self.client.post(reverse("evaluate_player", args=[player.pk]), payload)

        self.assertRedirects(response, reverse("player_detail", args=[player.pk]))
        evaluation = PlayerEvaluation.objects.filter(player=player).latest("evaluated_at")
        self.assertEqual(len(evaluation.scores), len(EVALUATION_CATEGORIES))
        self.assertEqual(evaluation.performance, 8)
        self.assertEqual(evaluation.mentality, 9)
        self.assertEqual(evaluation.physicality, 8)
        self.assertEqual(evaluation.scores["decision_making"], 8)

    def test_attendance_updates_without_page_reload(self):
        attendance = Attendance.objects.first()
        response = self.client.post(
            reverse("training_detail", args=[attendance.training_id]),
            {
                "action": "attendance",
                "attendance_id": attendance.pk,
                "status": Attendance.Status.CANCELLED,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        attendance.refresh_from_db()
        self.assertEqual(attendance.status, Attendance.Status.CANCELLED)

    def test_create_event(self):
        before = TeamEvent.objects.count()
        response = self.client.post(
            reverse("event_create"),
            {
                "title": "Videoanalyse",
                "event_type": "meeting",
                "starts_at": "2026-08-01T10:00",
                "ends_at": "2026-08-01T11:00",
                "location": "Besprechungsraum",
                "notes": "Interne Analyse",
            },
        )
        self.assertRedirects(response, reverse("calendar"))
        self.assertEqual(TeamEvent.objects.count(), before + 1)
