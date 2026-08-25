from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # Gestion utilisateurs (RG-06 : admin only)
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/create/", views.UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/edit/", views.UserUpdateView.as_view(), name="user_edit"),
    path("users/<int:pk>/toggle-active/", views.UserToggleActiveView.as_view(), name="user_toggle_active"),
    path("users/<int:pk>/reset-password/", views.UserResetPasswordView.as_view(), name="user_reset_password"),
]
