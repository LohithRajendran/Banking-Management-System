"""
Banking App — Test Suite
=========================
Tests every major logical flow in the banking application.

HOW TO RUN:
  cd backend
  python manage.py test banking --verbosity=2

WHAT IS TESTED:
  1. User signup — valid data, duplicate email, weak password (must return 400 not 500)
  2. User login  — correct/wrong credentials, inactive account
  3. Bank account creation — one per user, welcome bonus
  4. Bank transfer (account number) — success, insufficient funds, self-transfer, bad account
  5. Web ID transfer — success, invalid web id, no bank account on receiver
  6. Concurrent transfers — race condition safety (SELECT FOR UPDATE)
  7. Transaction history — filter by type, limit
  8. Lookup endpoints — by web id and account number
  9. Dashboard — with/without account, unauthenticated
"""

from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from threading import Thread

from .models import CustomUser, BankAccount, Transaction


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def make_user(email='user@test.com', password='StrongPass123!',
              first='Test', last='User'):
    """Create a CustomUser directly in the DB."""
    return CustomUser.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first,
        last_name=last,
    )


def make_account(user, balance=Decimal('1000.00')):
    """Create a BankAccount for the user and override the default balance."""
    acct = BankAccount.objects.create(user=user)
    acct.balance = balance
    acct.save(update_fields=['balance'])
    return acct


def auth_client(user, password='StrongPass123!'):
    """Return an APIClient authenticated as *user* via JWT."""
    client = APIClient()
    resp = client.post(reverse('login'), {'email': user.email, 'password': password})
    assert resp.status_code == 200, f"Auth failed: {resp.data}"
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['data']['access'])
    return client


# ─────────────────────────────────────────────
# 1. SIGNUP TESTS
# ─────────────────────────────────────────────

class SignupTests(TestCase):

    def test_signup_valid(self):
        """Valid signup creates a user and returns JWT tokens."""
        client = APIClient()
        payload = {
            'first_name': 'John',
            'last_name':  'Doe',
            'email':      'john@example.com',
            'password':   'StrongPass123!',
            'confirm_password': 'StrongPass123!',
        }
        resp = client.post(reverse('signup'), payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('access',  resp.data['data'])
        self.assertIn('refresh', resp.data['data'])
        self.assertTrue(CustomUser.objects.filter(email='john@example.com').exists())

    def test_signup_duplicate_email_returns_400(self):
        """Signing up twice with the same email returns 400."""
        make_user(email='dup@test.com')
        client = APIClient()
        resp = client.post(reverse('signup'), {
            'first_name': 'A', 'last_name': 'B',
            'email': 'dup@test.com',
            'password': 'StrongPass123!', 'confirm_password': 'StrongPass123!',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_password_mismatch_returns_400(self):
        """Mismatched passwords return 400."""
        client = APIClient()
        resp = client.post(reverse('signup'), {
            'first_name': 'A', 'last_name': 'B',
            'email': 'mismatch@test.com',
            'password': 'StrongPass123!', 'confirm_password': 'WrongPass456!',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_weak_password_returns_400_not_500(self):
        """
        BUG FIX: Django's validate_password raises a Django ValidationError,
        NOT a DRF ValidationError. Before the fix this caused a 500 server crash.
        After the fix it must return a clean 400 Bad Request response.
        """
        client = APIClient()
        resp = client.post(reverse('signup'), {
            'first_name': 'A', 'last_name': 'B',
            'email': 'weak@test.com',
            'password': '123',          # Too short and purely numeric
            'confirm_password': '123',
        })
        self.assertEqual(
            resp.status_code, status.HTTP_400_BAD_REQUEST,
            "Weak password must return 400, not a 500 internal server crash"
        )
        self.assertIn('errors', resp.data)

    def test_signup_missing_fields_returns_400(self):
        """Missing required fields return 400."""
        client = APIClient()
        resp = client.post(reverse('signup'), {'email': 'no@name.com'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
# 2. LOGIN TESTS
# ─────────────────────────────────────────────

class LoginTests(TestCase):

    def setUp(self):
        self.user   = make_user(email='login@test.com')
        self.client = APIClient()

    def test_login_valid(self):
        resp = self.client.post(reverse('login'), {
            'email': 'login@test.com', 'password': 'StrongPass123!'
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data['data'])

    def test_login_wrong_password(self):
        resp = self.client.post(reverse('login'), {
            'email': 'login@test.com', 'password': 'wrongpassword'
        })
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_unknown_email(self):
        resp = self.client.post(reverse('login'), {
            'email': 'ghost@test.com', 'password': 'anything'
        })
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        resp = self.client.post(reverse('login'), {
            'email': 'login@test.com', 'password': 'StrongPass123!'
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_has_bank_account_flag_false_when_no_account(self):
        """Login response includes has_bank_account=False when no account exists."""
        resp = self.client.post(reverse('login'), {
            'email': 'login@test.com', 'password': 'StrongPass123!'
        })
        self.assertIn('has_bank_account', resp.data['data'])
        self.assertFalse(resp.data['data']['has_bank_account'])

    def test_login_has_bank_account_flag_true_when_account_exists(self):
        """Login response includes has_bank_account=True when account exists."""
        make_account(self.user)
        resp = self.client.post(reverse('login'), {
            'email': 'login@test.com', 'password': 'StrongPass123!'
        })
        self.assertTrue(resp.data['data']['has_bank_account'])


# ─────────────────────────────────────────────
# 3. BANK ACCOUNT CREATION TESTS
# ─────────────────────────────────────────────

class CreateAccountTests(TestCase):

    def setUp(self):
        self.user   = make_user()
        self.client = auth_client(self.user)

    def test_create_account_success(self):
        resp = self.client.post(reverse('create_bank_account'))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.data['data']
        self.assertEqual(len(data['account_number']), 12)
        self.assertTrue(data['account_number'].isdigit())
        # Welcome bonus check
        self.assertEqual(Decimal(data['balance']), Decimal('1000.00'))

    def test_cannot_create_second_account(self):
        make_account(self.user)
        resp = self.client.post(reverse('create_bank_account'))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_cannot_create(self):
        unauth = APIClient()
        resp = unauth.post(reverse('create_bank_account'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


# ─────────────────────────────────────────────
# 4. BANK TRANSFER TESTS
# ─────────────────────────────────────────────

class BankTransferTests(TestCase):

    def setUp(self):
        self.sender_user = make_user(email='sender@test.com', first='Sender')
        self.recv_user   = make_user(email='recv@test.com',   first='Receiver')
        self.sender_acct = make_account(self.sender_user, Decimal('5000.00'))
        self.recv_acct   = make_account(self.recv_user,   Decimal('1000.00'))
        self.client      = auth_client(self.sender_user)

    def _transfer(self, amount, account_number=None, description='Test'):
        return self.client.post(reverse('bank_transfer'), {
            'recipient_account_number': account_number or self.recv_acct.account_number,
            'amount': str(amount),
            'description': description,
        })

    def test_successful_transfer(self):
        resp = self._transfer(500)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.sender_acct.refresh_from_db()
        self.recv_acct.refresh_from_db()
        self.assertEqual(self.sender_acct.balance, Decimal('4500.00'))
        self.assertEqual(self.recv_acct.balance,   Decimal('1500.00'))
        # Returned new_balance must reflect the deduction
        self.assertEqual(Decimal(resp.data['data']['new_balance']), Decimal('4500.00'))

    def test_insufficient_funds_returns_400(self):
        resp = self._transfer(99999)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Balances must be unchanged
        self.sender_acct.refresh_from_db()
        self.assertEqual(self.sender_acct.balance, Decimal('5000.00'))

    def test_self_transfer_rejected(self):
        resp = self._transfer(100, account_number=self.sender_acct.account_number)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('yourself', resp.data['message'].lower())

    def test_unknown_account_number_returns_400(self):
        resp = self._transfer(100, account_number='000000000000')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_amount_rejected(self):
        resp = self._transfer(0)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_amount_rejected(self):
        resp = self._transfer(-50)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_digit_account_number_rejected(self):
        resp = self.client.post(reverse('bank_transfer'), {
            'recipient_account_number': 'ABCDEFGHIJKL',
            'amount': '100',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transfer_creates_transaction_record(self):
        self._transfer(200, description='Lunch money')
        txn = Transaction.objects.filter(
            sender=self.sender_acct, receiver=self.recv_acct
        ).first()
        self.assertIsNotNone(txn)
        self.assertEqual(txn.amount,        Decimal('200.00'))
        self.assertEqual(txn.description,   'Lunch money')
        self.assertEqual(txn.status,        'completed')
        self.assertEqual(txn.transfer_type, 'bank')
        self.assertTrue(txn.reference_number.startswith('TXN'))

    def test_user_without_bank_account_cannot_transfer(self):
        new_user   = make_user(email='noact@test.com')
        new_client = auth_client(new_user)
        resp = new_client.post(reverse('bank_transfer'), {
            'recipient_account_number': self.recv_acct.account_number,
            'amount': '100',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_cannot_transfer(self):
        unauth = APIClient()
        resp = unauth.post(reverse('bank_transfer'), {
            'recipient_account_number': self.recv_acct.account_number,
            'amount': '100',
        })
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


# ─────────────────────────────────────────────
# 5. WEB ID TRANSFER TESTS
# ─────────────────────────────────────────────

class WebIDTransferTests(TestCase):

    def setUp(self):
        self.sender_user = make_user(email='s@test.com', first='Sender')
        self.recv_user   = make_user(email='r@test.com', first='Receiver')
        self.sender_acct = make_account(self.sender_user, Decimal('3000.00'))
        self.recv_acct   = make_account(self.recv_user,   Decimal('500.00'))
        self.client      = auth_client(self.sender_user)

    def _transfer(self, web_id, amount):
        return self.client.post(reverse('webid_transfer'), {
            'recipient_web_id': web_id,
            'amount': str(amount),
        })

    def test_successful_webid_transfer(self):
        resp = self._transfer(self.recv_user.web_id, 300)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.sender_acct.refresh_from_db()
        self.recv_acct.refresh_from_db()
        self.assertEqual(self.sender_acct.balance, Decimal('2700.00'))
        self.assertEqual(self.recv_acct.balance,   Decimal('800.00'))

    def test_invalid_web_id_returns_400(self):
        resp = self._transfer('nonexistentwid', 100)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_self_transfer_via_webid_rejected(self):
        resp = self._transfer(self.sender_user.web_id, 100)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_receiver_without_bank_account_rejected(self):
        no_acct_user = make_user(email='noaccount@test.com')
        resp = self._transfer(no_acct_user.web_id, 100)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('bank account', resp.data['message'].lower())

    def test_insufficient_funds_webid_returns_400(self):
        resp = self._transfer(self.recv_user.web_id, 99999)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
# 6. RACE CONDITION / CONCURRENCY TESTS
# ─────────────────────────────────────────────

class ConcurrentTransferTests(TransactionTestCase):
    """
    TransactionTestCase (not TestCase) is required here because:
      - TestCase wraps every test in a transaction and rolls it back (no real commits).
      - TransactionTestCase actually commits to the DB, letting threads see each other's writes.
      - This is necessary to test SELECT FOR UPDATE behaviour across threads.
    """

    def test_concurrent_transfers_do_not_overdraft(self):
        """
        BUG FIX (race condition): Without SELECT FOR UPDATE, two concurrent
        transfers can both read the same stale balance, both pass the check,
        and both succeed — resulting in a negative balance (overdraft).

        With SELECT FOR UPDATE + consistent lock ordering, only one should
        succeed and the final balance must remain >= 0.
        """
        sender = make_user(email='concurrent_sender@test.com')
        recvA  = make_user(email='concurrent_recvA@test.com')
        recvB  = make_user(email='concurrent_recvB@test.com')

        sender_acct = make_account(sender, Decimal('500.00'))
        acctA       = make_account(recvA,  Decimal('0.00'))
        acctB       = make_account(recvB,  Decimal('0.00'))

        from .utils import perform_transfer
        results = []

        def do_transfer(receiver_acct, result_list):
            # Each thread fetches a fresh copy of the sender account from DB.
            # This simulates real concurrent web requests.
            fresh_sender = BankAccount.objects.get(pk=sender_acct.pk)
            fresh_recv   = BankAccount.objects.get(pk=receiver_acct.pk)
            txn, err = perform_transfer(
                fresh_sender, fresh_recv, Decimal('400.00'), 'bank', 'concurrent test'
            )
            result_list.append((txn, err))

        t1 = Thread(target=do_transfer, args=(acctA, results))
        t2 = Thread(target=do_transfer, args=(acctB, results))
        t1.start(); t2.start()
        t1.join();  t2.join()

        sender_acct.refresh_from_db()

        # The balance must NEVER go below zero
        self.assertGreaterEqual(
            sender_acct.balance, Decimal('0.00'),
            f"Overdraft occurred! Final balance: {sender_acct.balance}"
        )

        # Exactly one of the two concurrent transfers must have succeeded
        successes = sum(1 for txn, err in results if txn is not None)
        self.assertEqual(
            successes, 1,
            f"Expected exactly 1 success but got {successes}. Results: {results}"
        )


# ─────────────────────────────────────────────
# 7. TRANSACTION HISTORY TESTS
# ─────────────────────────────────────────────

class TransactionHistoryTests(TestCase):

    def setUp(self):
        self.user  = make_user(email='hist@test.com')
        self.other = make_user(email='other@test.com')
        self.acct  = make_account(self.user,  Decimal('5000.00'))
        self.oacct = make_account(self.other, Decimal('5000.00'))
        self.client = auth_client(self.user)

    def _make_transfer(self, amount, ttype='bank'):
        from .utils import perform_transfer
        fresh_sender = BankAccount.objects.get(pk=self.acct.pk)
        fresh_recv   = BankAccount.objects.get(pk=self.oacct.pk)
        perform_transfer(fresh_sender, fresh_recv, Decimal(str(amount)), ttype)

    def test_history_returns_transactions(self):
        self._make_transfer(100)
        resp = self.client.get(reverse('transaction_history'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data['data']['transactions']), 1)

    def test_history_filter_by_type_bank(self):
        self._make_transfer(100, 'bank')
        self._make_transfer(50,  'webid')
        resp = self.client.get(reverse('transaction_history') + '?type=bank')
        for txn in resp.data['data']['transactions']:
            self.assertEqual(txn['transfer_type'], 'bank')

    def test_history_filter_by_type_webid(self):
        self._make_transfer(100, 'bank')
        self._make_transfer(50,  'webid')
        resp = self.client.get(reverse('transaction_history') + '?type=webid')
        for txn in resp.data['data']['transactions']:
            self.assertEqual(txn['transfer_type'], 'webid')

    def test_history_limit_parameter(self):
        for _ in range(5):
            self._make_transfer(10)
        resp = self.client.get(reverse('transaction_history') + '?limit=2')
        self.assertEqual(len(resp.data['data']['transactions']), 2)

    def test_history_no_account_returns_empty_list(self):
        new_user = make_user(email='noact2@test.com')
        c = auth_client(new_user)
        resp = c.get(reverse('transaction_history'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['data']['transactions'], [])

    def test_history_includes_received_transactions(self):
        """History must show transactions where user is the RECEIVER too."""
        from .utils import perform_transfer
        fresh_other  = BankAccount.objects.get(pk=self.oacct.pk)
        fresh_self   = BankAccount.objects.get(pk=self.acct.pk)
        perform_transfer(fresh_other, fresh_self, Decimal('50'), 'bank')
        resp = self.client.get(reverse('transaction_history'))
        self.assertGreaterEqual(len(resp.data['data']['transactions']), 1)


# ─────────────────────────────────────────────
# 8. LOOKUP ENDPOINT TESTS
# ─────────────────────────────────────────────

class LookupTests(TestCase):

    def setUp(self):
        self.user        = make_user(email='lookup@test.com')
        self.acct        = make_account(self.user)
        self.user_noact  = make_user(email='noacct@lookup.com')
        self.client      = auth_client(self.user)

    def test_lookup_by_webid_success(self):
        resp = self.client.get(
            reverse('lookup_by_webid', kwargs={'web_id': self.user.web_id})
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['data']['web_id'], self.user.web_id)

    def test_lookup_by_webid_not_found(self):
        resp = self.client.get(
            reverse('lookup_by_webid', kwargs={'web_id': 'doesntexist'})
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_lookup_by_webid_user_has_no_bank_account(self):
        resp = self.client.get(
            reverse('lookup_by_webid', kwargs={'web_id': self.user_noact.web_id})
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lookup_by_account_success(self):
        resp = self.client.get(
            reverse('lookup_by_account',
                    kwargs={'account_number': self.acct.account_number})
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['data']['account_number'], self.acct.account_number)

    def test_lookup_by_account_not_found(self):
        resp = self.client.get(
            reverse('lookup_by_account', kwargs={'account_number': '000000000000'})
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_lookup_requires_authentication(self):
        unauth = APIClient()
        resp = unauth.get(
            reverse('lookup_by_webid', kwargs={'web_id': self.user.web_id})
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


# ─────────────────────────────────────────────
# 9. DASHBOARD TESTS
# ─────────────────────────────────────────────

class DashboardTests(TestCase):

    def setUp(self):
        self.user   = make_user(email='dash@test.com')
        self.acct   = make_account(self.user)
        self.client = auth_client(self.user)

    def test_dashboard_with_account(self):
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['data']['has_bank_account'])
        self.assertIn('account', resp.data['data'])
        self.assertIn('recent_transactions', resp.data['data'])

    def test_dashboard_without_account(self):
        new_user   = make_user(email='nodash@test.com')
        new_client = auth_client(new_user)
        resp = new_client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(resp.data['data']['has_bank_account'])
        self.assertIsNone(resp.data['data']['account'])

    def test_dashboard_unauthenticated(self):
        unauth = APIClient()
        resp = unauth.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_balance_is_accurate(self):
        """Balance shown on dashboard matches the actual DB value."""
        self.acct.refresh_from_db()
        resp = self.client.get(reverse('dashboard'))
        dash_balance = Decimal(resp.data['data']['account']['balance'])
        self.assertEqual(dash_balance, self.acct.balance)
