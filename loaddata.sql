UPDATE auth_user
SET is_superuser = 1
WHERE username = 'reem@email.com';

DELETE FROM auth_user WHERE username = 'reem@email.com';