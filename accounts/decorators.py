from django.contrib.auth.decorators import user_passes_test


def role_required(*roles):
    def check(user):
        if not user.is_authenticated:
            return False
        profile = getattr(user, "profile", None)
        if not profile:
            return False
        return profile.role in roles

    return user_passes_test(check)
