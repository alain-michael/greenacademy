from rest_framework import viewsets, status
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer, UserRegistrationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from django.db.models.query import QuerySet

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        cached_data: QuerySet = cache.get("courses")
        if not cached_data:
            data: QuerySet = self.queryset
            cache.set("courses", data)
            return data
        return cached_data
    
    def perform_create(self, serializer) -> None:
        cache.delete("courses")
        super().perform_create(serializer)
    
    def perform_update(self, serializer) -> None:
        super().perform_update(serializer)
        cache.delete("courses")

    def perform_destroy(self, instance) -> None:
        cache.delete("courses")
        super().perform_destroy(instance)


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        cached_data: QuerySet = cache.get(f"enrollments_{self.request.user.id}")
        if cached_data:
            return cached_data
        data = self.queryset.filter(student=self.request.user)
        cache.set(f"enrollments_{self.request.user.id}", data)
        return data
    
    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data={**request.data, "student": request.user.id})
        if serializer.is_valid():
            serializer.save(student=request.user)
            
            cache.delete(f"enrollments_{request.user.id}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer) -> None:
        super().perform_update(serializer)
        cache.delete(f"enrollments_{self.request.user.id}")

    def perform_destroy(self, instance) -> None:
        cache.delete(f"enrollments_{self.request.user.id}")
        super().perform_destroy(instance)

    
class RegisterUserView(APIView):
    permission_classes: list = []

    def post(self, request, *args, **kwargs) -> Response:
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
