"""
Banking App — Views (API Endpoints)
======================================
Views are the functions that handle incoming HTTP requests and return responses.
Think of each view as a specific "action" your server can perform.

Each view:
  1. Receives a request (with data from the frontend)
  2. Validates the data
  3. Performs some logic (read from / write to database)
  4. Returns a response (JSON data)

OUR ENDPOINTS:
  POST   /api/signup/           → Create a new user account
  POST   /api/login/            → Login, get JWT tokens
  POST   /api/token/refresh/    → Get new access token using refresh token
  POST   /api/create-account/   → Create a bank account for the logged-in user
  GET    /api/dashboard/        → Get current user's account info and balance
  POST   /api/transfer/bank/    → Transfer money by account number
  POST   /api/transfer/webid/   → Transfer money by Web ID
  GET    /api/transactions/     → Get transaction history
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, BankAccount, Transaction
from .serializers import (
    UserSignupSerializer,
    UserProfileSerializer,
    BankAccountSerializer,
    TransactionSerializer,
    BankTransferSerializer,
    WebIDTransferSerializer,
)
from .utils import get_dashboard_data_cached, perform_transfer
from decimal import Decimal


# ============================================
# HELPER: Build standard API response
# ============================================
def success_response(data, message='Success', status_code=status.HTTP_200_OK):
    """
    Returns a standard successful JSON response.
    Format: { "success": true, "message": "...", "data": {...} }
    """
    return Response({
        'success': True,
        'message': message,
        'data': data,
    }, status=status_code)


def error_response(message, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Returns a standard error JSON response.
    Format: { "success": false, "message": "...", "errors": {...} }
    """
    return Response({
        'success': False,
        'message': message,
        'errors': errors or {},
    }, status=status_code)


# ============================================
# ENDPOINT 1: SIGNUP
# POST /api/signup/
# ============================================
@api_view(['POST'])
@permission_classes([AllowAny])  # Anyone can sign up (no auth token needed)
def signup(request):
    """
    Register a new user.
    
    Request body:
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    
    Response:
    {
        "success": true,
        "message": "Account created successfully!",
        "data": {
            "user": { ... },
            "access": "eyJ...",   <- JWT access token
            "refresh": "eyJ..."   <- JWT refresh token
        }
    }
    """
    serializer = UserSignupSerializer(data=request.data)

    if not serializer.is_valid():
        return error_response(
            message="Please fix the errors below.",
            errors=serializer.errors,
        )

    # Create the user
    user = serializer.save()

    # Generate JWT tokens for the new user (so they're logged in immediately after signup)
    refresh = RefreshToken.for_user(user)

    return success_response(
        data={
            'user': UserProfileSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        },
        message="Account created successfully! Welcome to SecureBank.",
        status_code=status.HTTP_201_CREATED,
    )


# ============================================
# ENDPOINT 2: LOGIN
# POST /api/login/
# ============================================
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login with email and password.
    Returns JWT tokens on success.
    
    Request body:
    {
        "email": "john@example.com",
        "password": "SecurePass123!"
    }
    """
    email = request.data.get('email', '').lower().strip()
    password = request.data.get('password', '')

    # Check required fields
    if not email or not password:
        return error_response("Email and password are required.")

    # Find the user
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return error_response("No account found with this email address.", status_code=status.HTTP_401_UNAUTHORIZED)

    # Check password
    if not user.check_password(password):
        return error_response("Incorrect password. Please try again.", status_code=status.HTTP_401_UNAUTHORIZED)

    # Check if account is active
    if not user.is_active:
        return error_response("Your account has been deactivated. Contact support.", status_code=status.HTTP_403_FORBIDDEN)

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    # Check if user has a bank account
    has_bank_account = hasattr(user, 'bank_account')

    return success_response(
        data={
            'user': UserProfileSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'has_bank_account': has_bank_account,
        },
        message=f"Welcome back, {user.first_name}!",
    )


# ============================================
# ENDPOINT 3: CREATE BANK ACCOUNT
# POST /api/create-account/
# ============================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Must be logged in
def create_bank_account(request):
    """
    Create a bank account for the currently logged-in user.
    A user can only have one bank account.
    
    No request body needed — we know who the user is from their JWT token.
    New accounts start with ₹1000 welcome bonus.
    """
    user = request.user  # Django gets this from the JWT token automatically

    # Check if user already has a bank account
    if hasattr(user, 'bank_account'):
        return error_response(
            "You already have a bank account.",
            errors={'account_number': user.bank_account.account_number},
        )

    # Create the bank account
    account = BankAccount.objects.create(user=user)

    return success_response(
        data=BankAccountSerializer(account).data,
        message=f"Bank account created! Your account number is {account.account_number}. Starting balance: ₹1000.",
        status_code=status.HTTP_201_CREATED,
    )


# ============================================
# ENDPOINT 4: DASHBOARD
# GET /api/dashboard/
# ============================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """
    Get the current user's dashboard data.
    Returns: user info + account info + recent transactions.
    
    Uses Redis cache to speed up repeated requests.
    """
    user = request.user

    # Check if user has a bank account
    if not hasattr(user, 'bank_account'):
        return success_response(
            data={
                'user': UserProfileSerializer(user).data,
                'account': None,
                'has_bank_account': False,
            },
            message="Please create a bank account to get started."
        )

    account = user.bank_account

    # Get recent transactions (last 5)
    from django.db.models import Q
    recent_txns = Transaction.objects.filter(
        Q(sender=account) | Q(receiver=account)
    ).order_by('-timestamp')[:5]

    return success_response(
        data={
            'user': UserProfileSerializer(user).data,
            'account': BankAccountSerializer(account).data,
            'has_bank_account': True,
            'recent_transactions': TransactionSerializer(recent_txns, many=True).data,
        },
        message="Dashboard loaded."
    )


# ============================================
# ENDPOINT 5: BANK TRANSFER
# POST /api/transfer/bank/
# ============================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bank_transfer(request):
    """
    Transfer money using the recipient's account number.
    
    Request body:
    {
        "recipient_account_number": "481927364850",
        "amount": 500.00,
        "description": "Paying for dinner"
    }
    """
    user = request.user

    # Check if sender has a bank account
    if not hasattr(user, 'bank_account'):
        return error_response("You need to create a bank account first.")

    sender_account = user.bank_account

    # Validate input data
    serializer = BankTransferSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response("Invalid transfer data.", errors=serializer.errors)

    data = serializer.validated_data
    recipient_account_number = data['recipient_account_number']
    amount = Decimal(str(data['amount']))
    description = data.get('description', '')

    # Find the recipient's account
    try:
        receiver_account = BankAccount.objects.get(account_number=recipient_account_number)
    except BankAccount.DoesNotExist:
        return error_response(
            f"No account found with number '{recipient_account_number}'. Please check the account number."
        )

    # Perform the transfer
    txn, error = perform_transfer(
        sender_account=sender_account,
        receiver_account=receiver_account,
        amount=amount,
        transfer_type='bank',
        description=description,
    )

    if error:
        return error_response(error)

    return success_response(
        data={
            'transaction': TransactionSerializer(txn).data,
            'new_balance': str(sender_account.balance),
        },
        message=f"Successfully transferred ₹{amount} to account {recipient_account_number}.",
        status_code=status.HTTP_201_CREATED,
    )


# ============================================
# ENDPOINT 6: WEB ID TRANSFER
# POST /api/transfer/webid/
# ============================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webid_transfer(request):
    """
    Transfer money using the recipient's Web ID.
    Web ID is like a UPI ID — a short, memorable identifier.
    
    Request body:
    {
        "recipient_web_id": "john1abc",
        "amount": 250.00,
        "description": "Split the bill"
    }
    """
    user = request.user

    if not hasattr(user, 'bank_account'):
        return error_response("You need to create a bank account first.")

    sender_account = user.bank_account

    # Validate input
    serializer = WebIDTransferSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response("Invalid transfer data.", errors=serializer.errors)

    data = serializer.validated_data
    recipient_web_id = data['recipient_web_id'].strip().lower()
    amount = Decimal(str(data['amount']))
    description = data.get('description', '')

    # Find the recipient user by Web ID
    try:
        recipient_user = CustomUser.objects.get(web_id=recipient_web_id)
    except CustomUser.DoesNotExist:
        return error_response(
            f"No user found with Web ID '{recipient_web_id}'. Please check the Web ID."
        )

    # Check if recipient has a bank account
    if not hasattr(recipient_user, 'bank_account'):
        return error_response(
            f"The user with Web ID '{recipient_web_id}' does not have a bank account yet."
        )

    receiver_account = recipient_user.bank_account

    # Perform the transfer
    txn, error = perform_transfer(
        sender_account=sender_account,
        receiver_account=receiver_account,
        amount=amount,
        transfer_type='webid',
        description=description,
    )

    if error:
        return error_response(error)

    return success_response(
        data={
            'transaction': TransactionSerializer(txn).data,
            'new_balance': str(sender_account.balance),
        },
        message=f"Successfully transferred ₹{amount} to @{recipient_web_id}.",
        status_code=status.HTTP_201_CREATED,
    )


# ============================================
# ENDPOINT 7: TRANSACTION HISTORY
# GET /api/transactions/
# ============================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request):
    """
    Get the full transaction history for the current user.
    Shows all sent AND received transactions.
    
    Optional query parameters:
    - ?type=bank   → only bank transfers
    - ?type=webid  → only Web ID transfers
    - ?limit=20    → number of results (default 50)
    """
    user = request.user

    if not hasattr(user, 'bank_account'):
        return success_response(
            data={'transactions': [], 'total': 0},
            message="No bank account found."
        )

    account = user.bank_account

    # Filter by type if specified
    from django.db.models import Q
    queryset = Transaction.objects.filter(
        Q(sender=account) | Q(receiver=account)
    ).order_by('-timestamp')

    # Filter by transfer type
    transfer_type = request.query_params.get('type')
    if transfer_type in ('bank', 'webid'):
        queryset = queryset.filter(transfer_type=transfer_type)

    # Limit results
    try:
        limit = int(request.query_params.get('limit', 50))
        limit = min(limit, 200)  # Max 200 results
    except ValueError:
        limit = 50

    transactions = queryset[:limit]

    return success_response(
        data={
            'transactions': TransactionSerializer(transactions, many=True).data,
            'total': queryset.count(),
            'account_number': account.account_number,
        },
        message=f"Found {queryset.count()} transactions."
    )


# ============================================
# ENDPOINT 8: GET PROFILE
# GET /api/profile/
# ============================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get the current user's profile info."""
    return success_response(
        data=UserProfileSerializer(request.user).data,
        message="Profile loaded."
    )


# ============================================
# ENDPOINT 9: LOOKUP USER BY WEB ID (before transfer)
# GET /api/lookup/webid/<web_id>/
# ============================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lookup_by_webid(request, web_id):
    """
    Look up a user by their Web ID.
    Used to show "sending to: John Doe" before confirming a Web ID transfer.
    """
    try:
        user = CustomUser.objects.get(web_id=web_id.lower().strip())
        if not hasattr(user, 'bank_account'):
            return error_response("This user does not have a bank account.")
        return success_response(
            data={
                'full_name': user.get_full_name(),
                'web_id': user.web_id,
                'has_account': True,
            },
            message="User found."
        )
    except CustomUser.DoesNotExist:
        return error_response(f"No user found with Web ID '{web_id}'.", status_code=status.HTTP_404_NOT_FOUND)


# ============================================
# ENDPOINT 10: LOOKUP USER BY ACCOUNT NUMBER
# GET /api/lookup/account/<account_number>/
# ============================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lookup_by_account(request, account_number):
    """
    Look up a user by their account number.
    Used to show "sending to: John Doe" before confirming a bank transfer.
    """
    try:
        account = BankAccount.objects.get(account_number=account_number)
        return success_response(
            data={
                'full_name': account.user.get_full_name(),
                'account_number': account.account_number,
                'web_id': account.user.web_id,
            },
            message="Account found."
        )
    except BankAccount.DoesNotExist:
        return error_response(f"No account found with number '{account_number}'.", status_code=status.HTTP_404_NOT_FOUND)
