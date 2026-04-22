# Fire Compliance OS — Auth Testing Playbook

## 1. MongoDB Verification
```
mongosh
use fire_compliance_os
db.users.find({role: "super_admin"}).pretty()
db.users.getIndexes()   # expect unique index on email
db.login_attempts.getIndexes()
db.password_reset_tokens.getIndexes()  # TTL on expires_at
```
bcrypt hash must start with `$2b$`.

## 2. API Testing (localhost)
```
curl -c c.txt -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@sspl.in","password":"Sspl@12345"}'
cat c.txt        # must show access_token + refresh_token cookies
curl -b c.txt http://localhost:8001/api/auth/me
```

## 3. Credentials (see /app/memory/test_credentials.md)
