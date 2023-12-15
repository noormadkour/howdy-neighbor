UPDATE auth_user
SET is_superuser = 1
WHERE username = 'reem@email.com';

DELETE FROM auth_user WHERE email = 'dementorpoop';
DELETE FROM neighborapi_neighbor WHERE user_id = 20;