from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.hashers import check_password

from .jwt_claim_serializer import CustomTokenObtainPairSerializer
from .serializers import UserSerializer, ChangePasswordSerializer, ProfileViewSerializer
from .models import User

class UserView(APIView):
    #프로필 정보
    def get(self, request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = ProfileViewSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #회원가입
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"가입성공"}, status=status.HTTP_201_CREATED )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST )
    
    #회원정보 수정
    def put(self, request):
        user = get_object_or_404(User, id=request.user.id)
        if user == request.user:
            serializer = UserSerializer(user, data=request.data, partial=True)#partial 부분 수정 가능
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"회원정보 수정 성공"} , status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN)

    #회원탈퇴
    def delete(self, request):
        user = get_object_or_404(User, id=request.user.id)
        if user:
            user.delete()
            return Response({"message":"회원탈퇴 성공"}, status=status.HTTP_200_OK)
        return Response({"message":"회원탈퇴 실패"}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    #비밀번호 인증
    def post(self, request):
        user = get_object_or_404(User, id=request.user.id)
        password = user.password
        if check_password(request.data, password):
            return Response({"message":"인증이 완료되었습니다."}, status=status.HTTP_200_OK)        
        return Response({"message":"맞는 비밀번호를 적어주세요."}, status=status.HTTP_400_BAD_REQUEST)

    #비밀번호 변경
    def put(self, request):
        user = get_object_or_404(User, id=request.user.id)
        if user == request.user:
            serializer = ChangePasswordSerializer(user, data=request.data, context={'request': request}) #request를 serializer로 넘김
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"비밀번호 변경이 완료되었습니다! 다시 로그인해주세요."} , status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"접근 권한 없음"}, status=status.HTTP_403_FORBIDDEN)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer