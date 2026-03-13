from rest_framework.permissions import BasePermission
from .models import Role


class IsUP(BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.roles.filter(id=Role.RoleType.UP).exists()


class IsSuper(BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.roles.filter(id=Role.RoleType.SUPER).exists()


class IsResponsabile(BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.roles.filter(id=Role.RoleType.RESPONSABILE).exists()


class IsResponsabileCons(BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.roles.filter(
            id=Role.RoleType.RESPONSABILE_CONS
        ).exists()
