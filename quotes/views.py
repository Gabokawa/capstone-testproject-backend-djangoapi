# === IMPORTS ===
# We're adding all the DRF bits and get_object_or_404
# We're removing JsonResponse, csrf_exempt, require_http_methods, and json
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404  # Replaces the try/except block

from .models import Quote, Booking, ServiceIssue
from .serializer import QuoteSerializer, BookingSerializer, ServiceIssueSerializer

# ============ QUOTE VIEWS ============

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def quote_list_create(request):
    """List all quotes or create a new quote"""
    
    if request.method == "GET":
        # Your filter logic is still good
        quotes = Quote.objects.all()
        request_id = request.GET.get('request_id')
        professional_id = request.GET.get('professional_id')
        status_filter = request.GET.get('status')
        
        if request_id:
            quotes = quotes.filter(request_id=request_id)
        if professional_id:
            quotes = quotes.filter(professional_id=professional_id)
        if status_filter:
            quotes = quotes.filter(status=status_filter)
        
        # This one line replaces your entire 20-line manual serialization
        serializer = QuoteSerializer(quotes, many=True)
        return Response({'quotes': serializer.data}, status=status.HTTP_200_OK)
    
    elif request.method == "POST":
        # This replaces all your manual validation and creation
        serializer = QuoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def quote_detail(request, quote_id):
    """Retrieve, update or delete a quote"""
    
    # This one line replaces your try/except block
    quote = get_object_or_404(Quote, quote_id=quote_id)
    
    if request.method == "GET":
        serializer = QuoteSerializer(quote)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == "PUT":
        # partial=True would make this a PATCH, but we'll follow your PUT logic
        serializer = QuoteSerializer(quote, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "DELETE":
        quote.delete()
        # 204 No Content is more standard for a successful DELETE
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============ BOOKING VIEWS ============
# We just repeat the same pattern...

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def booking_list_create(request):
    """List all bookings or create a new booking"""
    
    if request.method == "GET":
        bookings = Booking.objects.all()
        request_id = request.GET.get('request_id')
        quote_id = request.GET.get('quote_id')
        status_filter = request.GET.get('status')
        
        if request_id:
            bookings = bookings.filter(request_id=request_id)
        if quote_id:
            bookings = bookings.filter(quote_id=quote_id)
        if status_filter:
            bookings = bookings.filter(status=status_filter)
        
        serializer = BookingSerializer(bookings, many=True)
        return Response({'bookings': serializer.data}, status=status.HTTP_200_OK)
    
    elif request.method == "POST":
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def booking_detail(request, booking_id):
    """Retrieve, update or delete a booking"""
    
    booking = get_object_or_404(Booking, booking_id=booking_id)
    
    if request.method == "GET":
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == "PUT":
        serializer = BookingSerializer(booking, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "DELETE":
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============ SERVICE ISSUE VIEWS ============
# ...and again. So much cleaner.

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def service_issue_list_create(request):
    """List all service issues or create a new issue"""
    
    if request.method == "GET":
        issues = ServiceIssue.objects.all()
        booking_id = request.GET.get('booking_id')
        issue_type = request.GET.get('issue_type')
        status_filter = request.GET.get('status')
        
        if booking_id:
            issues = issues.filter(booking_id=booking_id)
        if issue_type:
            issues = issues.filter(issue_type=issue_type)
        if status_filter:
            issues = issues.filter(status=status_filter)
        
        serializer = ServiceIssueSerializer(issues, many=True)
        return Response({'issues': serializer.data}, status=status.HTTP_200_OK)
    
    elif request.method == "POST":
        serializer = ServiceIssueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def service_issue_detail(request, issue_id):
    """Retrieve, update or delete a service issue"""
    
    issue = get_object_or_404(ServiceIssue, issue_id=issue_id)
    
    if request.method == "GET":
        serializer = ServiceIssueSerializer(issue)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == "PUT":
        serializer = ServiceIssueSerializer(issue, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "DELETE":
        issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)