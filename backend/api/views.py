from .models import MeUser, MeFollow
from .serializers import (
    MeFollowSerializer, 
    MeUserRegistrationSerializer, 
    MeUserSerializer, 
    PasswordChangeSerializer)
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class MeUserViewSet(viewsets.ModelViewSet):
    """ Вью для пользователя """
    queryset = MeUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return MeUserRegistrationSerializer
        return MeUserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получение текущего пользователя"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Изменение пароля"""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data.get('current_password')):
                return Response(
                    {"current_password": ["Неверный пароль"]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({"status": "Пароль успешно изменен"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk=None):
        """Подписка или отписка на пользователя"""
        author = get_object_or_404(MeUser, id=pk)
        
        if request.method == 'POST':
            data = {'user': request.user.id, 'author': author.id}
            serializer = MeFollowSerializer(
                data=data,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        elif request.method == 'DELETE':
            subscription = get_object_or_404(
                MeFollow,
                user=request.user,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def follower(self, request):
        """Список подписок пользователя"""
        subscribed_users = MeUser.objects.filter(
            following__user=request.user
        )
        page = self.paginate_queryset(subscribed_users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(subscribed_users, many=True)
        return Response(serializer.data)