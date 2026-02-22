"""
====================================================================
 JIRA: SVC-1890 — Fix Flaky Integration Test
====================================================================
 P1 | Points: 2 | Labels: testing, python

 Integration test for user service fails intermittently. Race
 condition in shared test state — tests modify same DB rows.
 Also missing test cleanup (teardown).

 ACCEPTANCE CRITERIA:
 - [ ] Each test gets isolated test data (unique per test)
 - [ ] Proper setUp/tearDown with cleanup
 - [ ] No shared mutable state between tests
====================================================================
"""

import unittest
import random

# Simulated shared database
shared_db = {}

class UserServiceTest(unittest.TestCase):
    # BUG: No setUp/tearDown — tests share state from previous runs
    # Should initialize fresh test data in setUp and clean up in tearDown

    def test_create_user(self):
        # BUG: Uses fixed key — conflicts with other test methods
        user_id = "test-user-1"
        shared_db[user_id] = {"name": "Test User", "active": True}
        self.assertIn(user_id, shared_db)

    def test_deactivate_user(self):
        # BUG: Depends on test_create_user running first
        # Tests should be independent — this fails if run in isolation
        user_id = "test-user-1"
        if user_id in shared_db:
            shared_db[user_id]["active"] = False
        self.assertFalse(shared_db.get(user_id, {}).get("active", True))

    def test_delete_user(self):
        # BUG: Modifies shared state — affects test_deactivate_user if run after
        user_id = "test-user-1"
        shared_db.pop(user_id, None)
        self.assertNotIn(user_id, shared_db)

    def test_list_users(self):
        # BUG: Result depends on which other tests have run
        # Could be 0, 1, or more users depending on execution order
        count = len(shared_db)
        self.assertGreaterEqual(count, 0)  # BUG: Useless assertion — always passes


if __name__ == '__main__':
    unittest.main()
