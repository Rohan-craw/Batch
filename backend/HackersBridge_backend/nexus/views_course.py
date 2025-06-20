import uuid
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from .models import Course, Book
from .serializer import CourseSerializer, BookSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from Student.models import StudentCourse, Student,BookAllotment
from Student.serializer import StudentSerializer
from nexus.serializer import BatchCreateSerializer
from nexus.models import Batch
from django.db.models import Prefetch
from rest_framework_simplejwt.authentication import JWTAuthentication
from collections import defaultdict
from django.utils.timezone import make_aware, datetime
from datetime import timedelta
from django.utils.timezone import localtime
from rest_framework.pagination import PageNumberPagination

class CourseListAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            course = serializer.save()  # Save the course and store it

            LogEntry.objects.create(
                content_type=ContentType.objects.get_for_model(Course),
                cid=str(uuid.uuid4()),  # Generate unique ID
                object_pk=course.id,
                object_id=course.id,
                object_repr=f"Course: {course.name}",  # Assuming `name` field exists
                action=LogEntry.Action.CREATE,
                changes=f"Created course: {course.name} by {request.user.username}",
                serialized_data=json.dumps(CourseSerializer(course).data, default=str),
                changes_text=f"Course '{course.name}' created by {request.user.username}.",
                additional_data="Course",
                actor=request.user,
                timestamp=now()
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseEditAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        try:
            course = Course.objects.get(id=id)
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            updated_course = serializer.save(last_update_user=request.user)

            LogEntry.objects.create(
                content_type=ContentType.objects.get_for_model(Course),
                cid=str(uuid.uuid4()),  # Generate unique ID
                object_pk=updated_course.id,
                object_id=updated_course.id,
                object_repr=f"Course: {updated_course.name}",
                action=LogEntry.Action.UPDATE,  # Corrected from CREATE to UPDATE
                changes=f"Updated course: {updated_course.name} by {request.user.username}",
                serialized_data=json.dumps(CourseSerializer(updated_course).data, default=str),
                changes_text=f"Course '{updated_course.name}' updated by {request.user.username}.",
                additional_data="Course",
                actor=request.user,
                timestamp=now()
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CourseDeleteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        try:
            course = Course.objects.get(id=id)
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        # Log the delete action before deleting the course
        LogEntry.objects.create(
            content_type=ContentType.objects.get_for_model(Course),
            cid=str(uuid.uuid4()),  # Generate unique ID
            object_pk=course.id,
            object_id=course.id,
            object_repr=f"Course: {course.name}",
            action=LogEntry.Action.DELETE,  # Correct action type
            changes=f"Deleted course: {course.name} by {request.user.username}",
            serialized_data=json.dumps(CourseSerializer(course).data, default=str),
            changes_text=f"Course '{course.name}' deleted by {request.user.username}.",
            additional_data="Course",
            actor=request.user,
            timestamp=now()
        )

        course.delete()
        return Response({'detail': 'Course deleted successfully'}, status=status.HTTP_204_NO_CONTENT)




class CourseinfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        # Step 1: Get the course
        course = get_object_or_404(Course, id=id)

        # Step 2: Get student IDs and prefetch full student data efficiently
        student_ids = StudentCourse.objects.filter(course=course).values_list('student_id', flat=True).distinct()
        students = Student.objects.filter(id__in=student_ids).select_related(
            'support_coordinator', 'course_counsellor', 'location'
        ).prefetch_related(
            'courses', 'notes', 'studentcourse_set'
        )

        Student_take_by = StudentSerializer(students, many=True).data

        # Step 3: Fetch related batch data efficiently
        batches = Batch.objects.filter(course=course).select_related(
            'course', 'trainer', 'batch_time', 'location', 'batch_coordinator'
        ).prefetch_related(
            Prefetch('student', queryset=Student.objects.only('id', 'name'))
        )

        Batch_take_by = []
        for batch in batches:
            Batch_take_by.append({
                "id": batch.id,
                "batch_id": batch.batch_id,
                "course": batch.course.name,
                "trainer": batch.trainer.name if batch.trainer else None,
                "mode": batch.mode,
                "status": batch.status,
                "start_date": batch.start_date,
                "end_date": batch.end_date,
                "preferred_week": batch.preferred_week,
                "batch_time": str(batch.batch_time) if batch.batch_time else None,
                "language": str(batch.language) if batch.language else None,
                "location": str(batch.location) if batch.location else None,
                "batch_coordinator": str(batch.batch_coordinator) if batch.batch_coordinator else None,
                "students": [
                    {"id": student.id, "name": student.name} for student in batch.student.all()
                ]
            })

        # Step 4: Final Response
        course_info = {
            'course': CourseSerializer(course).data,
            'Student_take_by': Student_take_by,
            'Batch_take_by': Batch_take_by
        }

        return Response({'course_info': course_info})




class CourseTakebyEdit(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, course_id):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        new_course_id = request.data.get("course")
        if not new_course_id:
            return Response({"error": "New course ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_course = Course.objects.get(id=new_course_id)
        except Course.DoesNotExist:
            return Response({"error": "New course not found."}, status=status.HTTP_404_NOT_FOUND)

        student_courses = StudentCourse.objects.filter(course_id=course_id)
        updated_instances = []
        skipped_instances = []

        for sc in student_courses:
            # Check for existing (student, new_course) pair
            if StudentCourse.objects.filter(student=sc.student, course=new_course).exists():
                skipped_instances.append(sc.id)
                continue

            sc.course = new_course

            sc.save()
            updated_instances.append(sc.id)


        return Response({
            "updated_student_course_ids": updated_instances,
            "skipped_due_to_duplicates": skipped_instances
        }, status=status.HTTP_200_OK)




class StudentCourseUpdate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, course_id):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
        new_course_id = request.data.get("course")
        student_list = request.data.get("student", [])

        if not new_course_id:
            return Response({"error": "New course ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_course = Course.objects.get(id=new_course_id)
        except Course.DoesNotExist:
            return Response({"error": "New course not found."}, status=status.HTTP_404_NOT_FOUND)

        updated_instances = []
        skipped_instances = []

        for student_id in student_list:
            student_courses = StudentCourse.objects.filter(student=student_id, course_id=course_id)

            for sc in student_courses:
                # Check for existing (student, new_course) pair
                if StudentCourse.objects.filter(student=sc.student, course=new_course).exists():
                    skipped_instances.append(sc.id)
                    continue

                sc.course = new_course
                sc.save()
                updated_instances.append(sc.id)

        return Response({
            "updated_student_course_ids": updated_instances,
            "skipped_due_to_duplicates": skipped_instances
        }, status=status.HTTP_200_OK)
    



class BatchCourseUpdate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, course_id):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        new_course_id = request.data.get("course")

        if not new_course_id:
            return Response({"error": "New Course ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_course = Course.objects.get(id=new_course_id)
        except Course.DoesNotExist:
            return Response({"error": "New course not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get all batches with the given course_id
        batches = Batch.objects.filter(course_id=course_id)
        if not batches.exists():
            return Response({"message": "No batches found for the given course."}, status=status.HTTP_404_NOT_FOUND)

        updated_batches = []

        for batch in batches:
            serializer = BatchCreateSerializer(instance=batch, data={"course": new_course.id}, partial=True)
            if serializer.is_valid():
                serializer.save()
                updated_batches.append(serializer.data)
            else:
                return Response({
                    "error": f"Error updating batch {batch.id}",
                    "details": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": f"{len(updated_batches)} batches updated successfully.",
            "updated_batches": updated_batches
        }, status=status.HTTP_200_OK)
    

    


class BookListAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        books = Book.objects.all()

        for book in books:
            if book.stock >= 1 and book.status != 'Available':
                book.status = 'Available'
                book.save(update_fields=['status'])
            elif book.stock == 0 and book.status != 'Not':
                book.status = 'Not'
                book.save(update_fields=['status'])

        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)



class BookCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.save(last_update_user=request.user)  # Save and get instance

            LogEntry.objects.create(
                content_type=ContentType.objects.get_for_model(Book),
                cid=str(uuid.uuid4()),  # Generate unique ID
                object_pk=book.id,
                object_id=book.id,
                object_repr=f"Book: {book.name}",  # Assuming `title` field exists
                action=LogEntry.Action.CREATE,
                changes=f"Created book: {book.name} by {request.user.username}",
                serialized_data=json.dumps(BookSerializer(book).data, default=str),
                changes_text=f"Book '{book.name}' created by {request.user.username}.",
                additional_data="Book",
                actor=request.user,
                timestamp=now()
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class BookUpdateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        try:
            book = Book.objects.get(id=id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            # Save the updated book first
            updated_book = serializer.save(last_update_user=request.user)

            # Now, create the log entry
            LogEntry.objects.create(
                content_type=ContentType.objects.get_for_model(Book),
                cid=str(uuid.uuid4()),  # Generate unique ID
                object_pk=updated_book.id,
                object_id=updated_book.id,
                object_repr=f"Book: {updated_book.name}",  # Use updated name
                action=LogEntry.Action.UPDATE,
                changes=f"Updated book: {updated_book.name} by {request.user.username}",
                serialized_data=json.dumps(BookSerializer(updated_book).data, default=str),
                changes_text=f"Book '{updated_book.name}' updated by {request.user.username}.",
                additional_data="Book",
                actor=request.user,
                timestamp=now()
            )

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    
class BookDeleteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        try:
            book = Book.objects.get(id=id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create the log entry before deleting the book
        LogEntry.objects.create(
            content_type=ContentType.objects.get_for_model(Book),
            cid=str(uuid.uuid4()),  # Generate unique ID
            object_pk=book.id,
            object_id=book.id,
            object_repr=f"Book: {book.name}",  # Use correct field if different
            action=LogEntry.Action.DELETE,
            changes=f"Deleted book: {book.name} by {request.user.username}",
            serialized_data=json.dumps(BookSerializer(book).data, default=str),
            changes_text=f"Book '{book.name}' deleted by {request.user.username}.",
            additional_data="Book",
            actor=request.user,
            timestamp=now()
        )

        # Delete the book after logging
        book.delete()
        return Response({'detail': 'Book deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


{
# class BookTakeByCountAPIView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         if request.user.role not in ['admin', 'coordinator']:
#             return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

#         # Get the start and end of the current month
#         today = now()
#         start_of_month = today.replace(day=1)
        
#         # Get all BookAllotment entries this month
#         allotments_this_month = BookAllotment.objects.filter(
#             allotment_datetime__date__gte=start_of_month
#         ).prefetch_related('book')

#         # Flat list of book IDs for this month
#         book_counts = {}

#         for allotment in allotments_this_month:
#             for book in allotment.book.all():
#                 if book.name in book_counts:
#                     book_counts[book.name] += 1
#                 else:
#                     book_counts[book.name] = 1

#         return Response(book_counts)
    



# class BookTakeByStudentListAPIView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         if request.user.role not in ['admin', 'coordinator']:
#             return Response({'error': 'Forbidden'}, status=403)

#         # Get Current Month
#         today = now()
#         start_of_month = today.replace(day=1)

#         # Get all BookAllotments for current month
#         allotments_this_month = BookAllotment.objects.filter(
#             allotment_datetime__date__gte=start_of_month
#         ).prefetch_related('student', 'book__course')

#         # Build response data
#         data = []
#         for allotment in allotments_this_month:
#             for student in allotment.student.all():
#                 for book in allotment.book.all():
#                     data.append({
#                         'student_name': student.name,
#                         'enrollment_no': student.enrollment_no,
#                         'book_name': book.name,
#                         'course_name': book.course.name,
#                     })

#         return Response({"data": data})
}


# This is for geting all info about book issue...
class BookTakeByAllDataAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        today = now()
        start_of_month = today.replace(day=1)

        # Fetch BookAllotments with related data
        allotments = BookAllotment.objects.filter(
            allotment_datetime__date__gte=start_of_month
        ).select_related('allot_by').prefetch_related(
            Prefetch('student'),
            Prefetch('book')
        )

        # Structure data
        book_data = defaultdict(lambda: {'count': 0, 'students_map': {}})

        for allotment in allotments:
            allot_by_name = getattr(allotment.allot_by, 'first_name', 'Unknown')
            issue_date = allotment.allotment_datetime

            for book in allotment.book.all():
                book_key = book.name.replace(" ", "_")

                for student in allotment.student.all():
                    key = student.enrollment_no

                    # Add count (total allotments)
                    book_data[book_key]['count'] += 1

                    # Add student info if not already added
                    if key not in book_data[book_key]['students_map']:
                        book_data[book_key]['students_map'][key] = {
                            'name': student.name,
                            'enrollment_no': student.enrollment_no,
                            'book_issue_date': issue_date,
                            'book_issue_by': allot_by_name,
                            'course':book.name,
                        }

        # Final formatted response
        response = {'all_book_tasks': {}}
        for book_key, info in book_data.items():
            response['all_book_tasks'][f"{book_key}_count"] = info['count']
            response['all_book_tasks'][f"{book_key}_book_take_by"] = list(info['students_map'].values())

        return Response(response)
    



# This is for apply filter on issue books...
class BookIssueFilterAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        filter_type = request.query_params.get('filter_type')
        today = now().date()

        try:
            match filter_type:
                case "today":
                    start_date = end_date = today

                case "yesterday":
                    start_date = end_date = today - timedelta(days=1)

                case "this_week":
                    start_date = today - timedelta(days=today.weekday())
                    end_date = today

                case "last_week":
                    end_date = today - timedelta(days=today.weekday() + 1)
                    start_date = end_date - timedelta(days=6)

                case "this_month":
                    start_date = today.replace(day=1)
                    end_date = today

                case "last_month":
                    first_day_this_month = today.replace(day=1)
                    last_month_end = first_day_this_month - timedelta(days=1)
                    start_date = last_month_end.replace(day=1)
                    end_date = last_month_end

                case "this_year":
                    start_date = today.replace(month=1, day=1)
                    end_date = today

                case "last_year":
                    start_date = today.replace(year=today.year - 1, month=1, day=1)
                    end_date = today.replace(year=today.year - 1, month=12, day=31)

                case "custom":
                    start_date_str = request.query_params.get('start_date')
                    end_date_str = request.query_params.get('end_date')
                    if not start_date_str or not end_date_str:
                        return Response({'error': 'Start and end dates are required for custom filter'}, status=400)
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

                case _:
                    return Response({'error': 'Invalid filter_type'}, status=400)

        except Exception as e:
            return Response({'error': 'Invalid date processing', 'details': str(e)}, status=400)

        try:
            start_date_aware = make_aware(datetime.combine(start_date, datetime.min.time()))
            end_date_aware = make_aware(datetime.combine(end_date + timedelta(days=1), datetime.min.time()))
        except Exception as e:
            return Response({'error': 'Date conversion failed', 'details': str(e)}, status=400)

        allotments = BookAllotment.objects.filter(
            allotment_datetime__range=(start_date_aware, end_date_aware)
        ).select_related('allot_by').prefetch_related(
            Prefetch('student'),
            Prefetch('book')
        )

        book_data = defaultdict(lambda: {'count': 0, 'students_map': {}})

        for allotment in allotments:
            allot_by_name = getattr(allotment.allot_by, 'first_name', 'Unknown')
            issue_date = allotment.allotment_datetime

            for book in allotment.book.all():
                book_key = book.name.replace(" ", "_")
                for student in allotment.student.all():
                    student_key = student.enrollment_no
                    book_data[book_key]['count'] += 1

                    if student_key not in book_data[book_key]['students_map']:
                        book_data[book_key]['students_map'][student_key] = {
                            'name': student.name,
                            'enrollment_no': student.enrollment_no,
                            'book_issue_date': issue_date,
                            'book_issue_by': allot_by_name,
                            'course':book.name,
                        }

        response = {'all_book_tasks': {}}
        for book_key, info in book_data.items():
            response['all_book_tasks'][f"{book_key}_count"] = info['count']
            response['all_book_tasks'][f"{book_key}_book_take_by"] = list(info['students_map'].values())

        return Response(response, status=200)



# This if for Book Info also send issued or not issued students..
class BookInfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'User is Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # Fetch the book with course
        book = Book.objects.select_related('course').filter(id=id).first()
        if not book:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

        # Extract optional date filter params
        start_date_str = request.query_params.get('allotment_datetime__date__gte')
        end_date_str = request.query_params.get('allotment_datetime__date__lte')
        start_date = None
        end_date = None

        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1)
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        # Build book info
        book_info = {
            'id': book.id,
            'book_id': book.book_id,
            'name': book.name,
            'version': book.version,
            'course': book.course.name if book.course else None,
            'stock': book.stock,
            'status': book.status,
            'last_update_user': str(book.last_update_user) if book.last_update_user else None
        }

        # Get active students for the book's course
        students_not_issued = StudentCourse.objects.select_related('student', 'course').filter(
            course=book.course,
            student_book_allotment=False,
            student__status='Active'
        )

        students_issued = StudentCourse.objects.select_related('student', 'course').filter(
            course=book.course,
            student_book_allotment=True,
            student__status='Active'
        )

        # Get all allotments related to this book
        issued_allotments = BookAllotment.objects.filter(book=book)
        if start_date and end_date:
            issued_allotments = issued_allotments.filter(
                allotment_datetime__range=(start_date, end_date)
            )

        issued_allotments = issued_allotments.prefetch_related('student', 'allot_by')

        # Map student.id → allotment info
        allotment_map = {}
        for allot in issued_allotments:
            for student in allot.student.all():
                allotment_map[student.id] = {
                    'issue_by': str(allot.allot_by.first_name) if allot.allot_by.first_name else None,
                    'allotment_datetime': localtime(allot.allotment_datetime).strftime('%Y-%m-%d %H:%M')
                }

        # Not Issued List (no date to sort by, so keep as-is)
        not_issued_students = sorted([
            {
                'student_id': sc.student.id,
                'name': sc.student.name,
                'enrollment_no': sc.student.enrollment_no,
                'course': sc.course.name,
                'issue_by': None,
                'allotment_datetime': None
            }
            for sc in students_not_issued
        ], key=lambda x: x['name'])  # Optional: sort alphabetically

        # Issued List (include only those with matching allotments, then sort by datetime)
        issued_students = sorted([
            {
                'student_id': sc.student.id,
                'name': sc.student.name,
                'enrollment_no': sc.student.enrollment_no,
                'course': sc.course.name,
                'book_status': 'Old' if sc.student_old_book_allotment else 'New',
                'issue_by': allotment_map.get(sc.student.id, {}).get('issue_by'),
                'allotment_datetime': allotment_map.get(sc.student.id, {}).get('allotment_datetime')
            }
            for sc in students_issued
            if sc.student.id in allotment_map
        ], key=lambda x: x['allotment_datetime'], reverse=True )  # ✅ Sort by allotment_datetime

        return Response({
            'book_info': book_info,
            'not_issued_students': not_issued_students,
            'issued_students': issued_students
        }, status=status.HTTP_200_OK)




# Custom paginator
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 50



# Giving all book student issued data...
class AllBookIssuedDataAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['admin', 'coordinator']:
            return Response({'error': 'User is Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        books = Book.objects.select_related('course').all()
        if not books.exists():
            return Response({'error': 'No books found.'}, status=status.HTTP_404_NOT_FOUND)

        filter_type = request.query_params.get('filter_type')
        today = now().date()
        start_dt = end_dt = None

        try:
            if filter_type:
                match filter_type:
                    case "today":
                        start_date = end_date = today
                    case "yesterday":
                        start_date = end_date = today - timedelta(days=1)
                    case "this_week":
                        start_date = today - timedelta(days=today.weekday())
                        end_date = today
                    case "last_week":
                        end_date = today - timedelta(days=today.weekday() + 1)
                        start_date = end_date - timedelta(days=6)
                    case "this_month":
                        start_date = today.replace(day=1)
                        end_date = today
                    case "last_month":
                        first_day_this_month = today.replace(day=1)
                        last_month_end = first_day_this_month - timedelta(days=1)
                        start_date = last_month_end.replace(day=1)
                        end_date = last_month_end
                    case "this_year":
                        start_date = today.replace(month=1, day=1)
                        end_date = today
                    case "last_year":
                        start_date = today.replace(year=today.year - 1, month=1, day=1)
                        end_date = today.replace(year=today.year - 1, month=12, day=31)
                    case "custom":
                        start_date_str = request.query_params.get('start_date')
                        end_date_str = request.query_params.get('end_date')
                        if not start_date_str or not end_date_str:
                            return Response({'error': 'Start and end dates are required for custom filter'}, status=400)
                        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                    case _:
                        return Response({'error': 'Invalid filter_type'}, status=400)

                start_dt = datetime.combine(start_date, datetime.min.time())
                end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
        except Exception as e:
            return Response({'error': 'Invalid date processing', 'details': str(e)}, status=400)

        issued_students = []

        for book in books:
            student_issued = StudentCourse.objects.select_related('student', 'course').filter(
                course=book.course,
                student_book_allotment=True,
                student__status='Active'
            )

            allotment_qs = BookAllotment.objects.filter(book=book)
            if start_dt and end_dt:
                allotment_qs = allotment_qs.filter(allotment_datetime__range=(start_dt, end_dt))

            issued_allotments = allotment_qs.prefetch_related('student', 'allot_by')

            allotment_map = {}
            for allot in issued_allotments:
                for student in allot.student.all():
                    allotment_map[student.id] = {
                        'issue_by': allot.allot_by.first_name if allot.allot_by else None,
                        'allotment_datetime': allot.allotment_datetime
                    }

            for sc in student_issued:
                if sc.student.id in allotment_map:
                    book_status = 'Old' if getattr(sc, 'student_old_book_allotment', False) else 'New'
                    issued_students.append({
                        'student_id': sc.student.id,
                        'name': sc.student.name,
                        'enrollment_no': sc.student.enrollment_no,
                        'course': sc.course.name,
                        'book_status': book_status,
                        'issue_by': allotment_map[sc.student.id]['issue_by'],
                        'allotment_datetime': localtime(allotment_map[sc.student.id]['allotment_datetime']).strftime('%Y-%m-%d %H:%M')
                    })

        # Search filter
        search_query = request.query_params.get('search', '').lower().strip()
        if search_query:
            issued_students = [
                s for s in issued_students
                if search_query in s['name'].lower()
                or search_query in s['enrollment_no'].lower()
                or search_query in s['course'].lower()
                or search_query == s['book_status'].lower()
                or search_query == s['issue_by'].lower()
            ]

        # Sort
        issued_students = sorted(
            issued_students,
            key=lambda x: datetime.strptime(x['allotment_datetime'], '%Y-%m-%d %H:%M'),
            reverse=True
        )

        # Apply pagination manually
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(issued_students, request)

        return paginator.get_paginated_response(page)