from django.shortcuts import render
from api.serializers import UserSearializer,ProfileSerializer,QuestionSerializer,AnswerSerializer,serializers
from rest_framework.response import Response
from rest_framework import mixins

from rest_framework.viewsets import ViewSet,ModelViewSet,GenericViewSet

from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import GenericAPIView
from django.contrib.auth.models import User
from rest_framework import authentication,permissions
from stack.models import UserProfile,Questions,Answers
from rest_framework.decorators import action


# Create your views here
class UsersView(GenericViewSet,CreateModelMixin):
    serializer_class=UserSearializer
    queryset=User.objects.all()

class ProfileView(ModelViewSet):
    serializer_class=ProfileSerializer
    queryset=UserProfile.objects.all()
    # authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # def get_queryset(self):
        # return UserProfile.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        prof=self.get_object()
        if prof.user != request.user:
            raise serializers.ValidationError("not allowed to perform")
        else:
            return super().destroy(request,*args,**kwargs)
    
    # localhost:8000/api/questions/

class QuestionView(ModelViewSet):
    serializer_class=QuestionSerializer
    queryset=Questions.objects.all()
    # authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["post"],detail=True)
    def add_answer(self,request,*args,**kwargs):
        serializer=AnswerSerializer(data=request.data)
        # id=kwargs.get("pk")
        # quest=Questions.objects.get(id=id)
        quest=self.get_object()
        user=request.user
        if serializer.is_valid():
            serializer.save(question=quest,user=user)
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)
    # def get_queryset(self):
    #     return Questions.objects.all().order_by("-created_date")

    # localhost:8000/api/questions/{id}/add_answer
    # method:post

class AnswersView(ModelViewSet):
    serializer_class=AnswerSerializer
    queryset=Answers.objects.all()
    # authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        raise serializers.ValidationError("method not allowed")
    
    # localhost:8000/api/answers/1/add_upvote/
    @action(methods=["post"],detail=True)
    def add_upvote(self,request,*args,**kwargs):
        answer=self.get_object()
        answer.upvote.add(request.user)
        answer.save()
        return Response(data="upvoted")

    @action(methods=["post"],detail=True)
    def down_upvote(self,request,*args,**kwargs):
        answer=self.get_object()
        answer.upvote.remove(request.user)
        answer.save()
        return Response(data="upvote removed") 