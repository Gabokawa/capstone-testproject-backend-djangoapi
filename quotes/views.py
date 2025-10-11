from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import json
from .models import Quote, Booking, ServiceIssue
from requests.models import ServiceRequest
from professionals.models import Professional

# Create your views here.

@csrf_exempt
@require_http_methods(["GET", "POST"])
def quote_list_create(request):
    """List all quotes or create a new quote"""
    
    if request.method == "GET":
        # Get query parameters for filtering
        request_id = request.GET.get('request_id')
        professional_id = request.GET.get('professional_id')
        status = request.GET.get('status')
        
        quotes = Quote.objects.all()
        
        # Apply filters
        if request_id:
            quotes = quotes.filter(request_id=request_id)
        if professional_id:
            quotes = quotes.filter(professional_id=professional_id)
        if status:
            quotes = quotes.filter(status=status)
        
        # Serialize data
        data = [{
            'quote_id': q.quote_id,
            'request_id': q.request_id,
            'professional_id': q.professional_id,
            'parts_needed': q.parts_needed,
            'parts_price': str(q.parts_price),
            'labor_cost': str(q.labor_cost),
            'total_quote_amount': str(q.total_quote_amount),
            'service_date': q.service_date.isoformat(),
            'start_time': q.start_time.isoformat(),
            'end_time': q.end_time.isoformat(),
            'quote_description': q.quote_description,
            'additional_notes': q.additional_notes,
            'valid_until': q.valid_until.isoformat(),
            'status': q.status,
            'created_at': q.created_at.isoformat(),
        } for q in quotes]
        
        return JsonResponse({'quotes': data}, status=200)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['request_id', 'professional_id', 'parts_price', 
                             'labor_cost', 'total_quote_amount', 'service_date',
                             'start_time', 'end_time', 'quote_description', 'valid_until']
            
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            
            # Create quote
            quote = Quote.objects.create(
                request_id=data['request_id'],
                professional_id=data['professional_id'],
                parts_needed=data.get('parts_needed'),
                parts_price=data['parts_price'],
                labor_cost=data['labor_cost'],
                total_quote_amount=data['total_quote_amount'],
                service_date=data['service_date'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                quote_description=data['quote_description'],
                additional_notes=data.get('additional_notes'),
                valid_until=data['valid_until'],
                status=data.get('status', 'pending')
            )
            
            return JsonResponse({
                'message': 'Quote created successfully',
                'quote_id': quote.quote_id
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def quote_detail(request, quote_id):
    """Retrieve, update or delete a quote"""
    
    try:
        quote = Quote.objects.get(quote_id=quote_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Quote not found'}, status=404)
    
    if request.method == "GET":
        data = {
            'quote_id': quote.quote_id,
            'request_id': quote.request_id,
            'professional_id': quote.professional_id,
            'parts_needed': quote.parts_needed,
            'parts_price': str(quote.parts_price),
            'labor_cost': str(quote.labor_cost),
            'total_quote_amount': str(quote.total_quote_amount),
            'service_date': quote.service_date.isoformat(),
            'start_time': quote.start_time.isoformat(),
            'end_time': quote.end_time.isoformat(),
            'quote_description': quote.quote_description,
            'additional_notes': quote.additional_notes,
            'valid_until': quote.valid_until.isoformat(),
            'status': quote.status,
            'created_at': quote.created_at.isoformat(),
        }
        return JsonResponse(data, status=200)
    
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            
            # Update fields
            for field in ['parts_needed', 'parts_price', 'labor_cost', 'total_quote_amount',
                         'service_date', 'start_time', 'end_time', 'quote_description',
                         'additional_notes', 'valid_until', 'status']:
                if field in data:
                    setattr(quote, field, data[field])
            
            quote.save()
            
            return JsonResponse({'message': 'Quote updated successfully'}, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == "DELETE":
        quote.delete()
        return JsonResponse({'message': 'Quote deleted successfully'}, status=200)


# ============ BOOKING VIEWS ============

@csrf_exempt
@require_http_methods(["GET", "POST"])
def booking_list_create(request):
    """List all bookings or create a new booking"""
    
    if request.method == "GET":
        # Get query parameters for filtering
        request_id = request.GET.get('request_id')
        quote_id = request.GET.get('quote_id')
        status = request.GET.get('status')
        
        bookings = Booking.objects.all()
        
        # Apply filters
        if request_id:
            bookings = bookings.filter(request_id=request_id)
        if quote_id:
            bookings = bookings.filter(quote_id=quote_id)
        if status:
            bookings = bookings.filter(status=status)
        
        # Serialize data
        data = [{
            'booking_id': b.booking_id,
            'request_id': b.request_id,
            'quote_id': b.quote_id,
            'booking_date': b.booking_date.isoformat(),
            'start_time': b.start_time.isoformat(),
            'end_time': b.end_time.isoformat(),
            'status': b.status,
            'final_price': str(b.final_price),
            'completion_notes': b.completion_notes,
            'cancellation_reason': b.cancellation_reason,
            'created_at': b.created_at.isoformat(),
            'completed_at': b.completed_at.isoformat() if b.completed_at else None,
        } for b in bookings]
        
        return JsonResponse({'bookings': data}, status=200)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['request_id', 'quote_id', 'booking_date', 
                             'start_time', 'end_time', 'final_price']
            
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            
            # Create booking
            booking = Booking.objects.create(
                request_id=data['request_id'],
                quote_id=data['quote_id'],
                booking_date=data['booking_date'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                status=data.get('status', 'confirmed'),
                final_price=data['final_price'],
                completion_notes=data.get('completion_notes'),
                cancellation_reason=data.get('cancellation_reason')
            )
            
            return JsonResponse({
                'message': 'Booking created successfully',
                'booking_id': booking.booking_id
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def booking_detail(request, booking_id):
    """Retrieve, update or delete a booking"""
    
    try:
        booking = Booking.objects.get(booking_id=booking_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)
    
    if request.method == "GET":
        data = {
            'booking_id': booking.booking_id,
            'request_id': booking.request_id,
            'quote_id': booking.quote_id,
            'booking_date': booking.booking_date.isoformat(),
            'start_time': booking.start_time.isoformat(),
            'end_time': booking.end_time.isoformat(),
            'status': booking.status,
            'final_price': str(booking.final_price),
            'completion_notes': booking.completion_notes,
            'cancellation_reason': booking.cancellation_reason,
            'created_at': booking.created_at.isoformat(),
            'completed_at': booking.completed_at.isoformat() if booking.completed_at else None,
        }
        return JsonResponse(data, status=200)
    
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            
            # Update fields
            for field in ['booking_date', 'start_time', 'end_time', 'status', 
                         'final_price', 'completion_notes', 'cancellation_reason', 'completed_at']:
                if field in data:
                    setattr(booking, field, data[field])
            
            booking.save()
            
            return JsonResponse({'message': 'Booking updated successfully'}, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == "DELETE":
        booking.delete()
        return JsonResponse({'message': 'Booking deleted successfully'}, status=200)


# ============ SERVICE ISSUE VIEWS ============

@csrf_exempt
@require_http_methods(["GET", "POST"])
def service_issue_list_create(request):
    """List all service issues or create a new issue"""
    
    if request.method == "GET":
        # Get query parameters for filtering
        booking_id = request.GET.get('booking_id')
        issue_type = request.GET.get('issue_type')
        status = request.GET.get('status')
        
        issues = ServiceIssue.objects.all()
        
        # Apply filters
        if booking_id:
            issues = issues.filter(booking_id=booking_id)
        if issue_type:
            issues = issues.filter(issue_type=issue_type)
        if status:
            issues = issues.filter(status=status)
        
        # Serialize data
        data = [{
            'issue_id': i.issue_id,
            'booking_id': i.booking_id,
            'issue_type': i.issue_type,
            'description': i.description,
            'status': i.status,
            'reported_at': i.reported_at.isoformat(),
            'resolved_at': i.resolved_at.isoformat() if i.resolved_at else None,
            'resolved_by_admin_id': i.resolved_by_admin_id,
            'resolution_notes': i.resolution_notes,
        } for i in issues]
        
        return JsonResponse({'issues': data}, status=200)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['booking_id', 'issue_type', 'description']
            
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            
            # Create service issue
            issue = ServiceIssue.objects.create(
                booking_id=data['booking_id'],
                issue_type=data['issue_type'],
                description=data['description'],
                status=data.get('status', 'reported')
            )
            
            return JsonResponse({
                'message': 'Service issue created successfully',
                'issue_id': issue.issue_id
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def service_issue_detail(request, issue_id):
    """Retrieve, update or delete a service issue"""
    
    try:
        issue = ServiceIssue.objects.get(issue_id=issue_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Service issue not found'}, status=404)
    
    if request.method == "GET":
        data = {
            'issue_id': issue.issue_id,
            'booking_id': issue.booking_id,
            'issue_type': issue.issue_type,
            'description': issue.description,
            'status': issue.status,
            'reported_at': issue.reported_at.isoformat(),
            'resolved_at': issue.resolved_at.isoformat() if issue.resolved_at else None,
            'resolved_by_admin_id': issue.resolved_by_admin_id,
            'resolution_notes': issue.resolution_notes,
        }
        return JsonResponse(data, status=200)
    
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            
            # Update fields
            for field in ['issue_type', 'description', 'status', 'resolved_at',
                         'resolved_by_admin_id', 'resolution_notes']:
                if field in data:
                    setattr(issue, field, data[field])
            
            issue.save()
            
            return JsonResponse({'message': 'Service issue updated successfully'}, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == "DELETE":
        issue.delete()
        return JsonResponse({'message': 'Service issue deleted successfully'}, status=200)