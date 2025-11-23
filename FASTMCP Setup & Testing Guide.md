# FASTMCP Setup & Testing Guide

This guide walks you through setting up and testing the FASTMCP Sales Team Automation ERP system.

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Git
- pip or conda

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
cd fastmcp_sales_erp
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Set Up Database

Create a PostgreSQL database:

```bash
# Using psql
createdb fastmcp_sales_erp

# Or using PostgreSQL client
psql -U postgres -c "CREATE DATABASE fastmcp_sales_erp;"
```

### Step 3: Initialize Database with Sample Data

```bash
source venv/bin/activate
python fastmcp/seed_db.py
```

You should see:
```
✓ Database initialized
✓ Cleared existing data
✓ Created 3 users
✓ Created 4 clients
✓ Created 4 projects
✓ Created 4 employees
✓ Created 5 project-employee assignments
✓ Created 6 payments

✅ Database seeded successfully!
```

### Step 4: Start the FastAPI Server

```bash
source venv/bin/activate
python fastmcp/server.py
```

You should see:
```
Starting FASTMCP Server...
Database initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 5: Test the API (in another terminal)

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}
```

### Step 6: Start Streamlit Client (in another terminal)

```bash
source venv/bin/activate
streamlit run streamlit_app.py
```

Navigate to `http://localhost:8501` in your browser.

---

## 🧪 Testing the System

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Test 2: Get Users

```bash
curl http://localhost:8000/api/users
```

Expected response:
```json
{
  "success": true,
  "count": 3,
  "users": [
    {
      "id": 1,
      "name": "Dharmendra",
      "email": "dharmendra@goldeneagle.com",
      "role": "manager",
      "active": true
    },
    ...
  ]
}
```

### Test 3: Process NLP Message (Payment)

```bash
curl -X POST http://localhost:8000/api/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Google ka iss week ka 1.2 lakh payment aa gaya",
    "user_id": 1
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Google ka iss week ka 1.2 lakh payment aa gaya",
  "parsed": {
    "intent": "payment",
    "action": "record_payment",
    "project": "Google",
    "amount": 120000,
    "week": 47,
    "status": "received",
    "confidence": 0.85
  },
  "execution": {
    "success": true,
    "action": "record_payment",
    "data": {
      "payment_id": 7,
      "project": "Google",
      "amount": 120000,
      "week": 47,
      "status": "received"
    }
  }
}
```

### Test 4: Process NLP Message (Employee Assignment)

```bash
curl -X POST http://localhost:8000/api/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Ramesh is assigned to Amazon project",
    "user_id": 1
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Ramesh is assigned to Amazon project",
  "parsed": {
    "intent": "employee",
    "action": "assign_employee",
    "employee": "Ramesh",
    "project": "Amazon",
    "confidence": 0.8
  },
  "execution": {
    "success": true,
    "action": "assign_employee",
    "data": {
      "assignment_id": 6,
      "employee": "Ramesh",
      "project": "Amazon AWS Integration",
      "start_date": "2024-11-22"
    }
  }
}
```

### Test 5: Manager Dashboard

```bash
curl http://localhost:8000/api/manager/dashboard/1
```

Expected response:
```json
{
  "success": true,
  "manager_id": 1,
  "statistics": {
    "total_projects": 2,
    "active_projects": 2,
    "total_revenue": 390000,
    "pending_payments_count": 1
  },
  "projects": [
    {
      "id": 1,
      "name": "Google Cloud Migration",
      "client": "Google",
      "status": "active",
      "estimated_value": 500000
    },
    ...
  ]
}
```

### Test 6: Executive Dashboard

```bash
curl http://localhost:8000/api/executive/dashboard/2
```

Expected response:
```json
{
  "success": true,
  "executive_id": 2,
  "statistics": {
    "total_projects": 1,
    "active_projects": 1,
    "total_revenue": 75000
  },
  "projects": [
    {
      "id": 3,
      "name": "Adobe Creative Suite Deployment",
      "client": "Adobe",
      "status": "active"
    }
  ]
}
```

---

## 🔍 Testing NLP Parser Directly

```bash
source venv/bin/activate
python fastmcp/tools/nlp_parser.py
```

This will test the NLP parser with sample messages:

```
Message: Google ka iss week ka 1.2 lakh payment aa gaya
Parsed: {
  "intent": "payment",
  "action": "record_payment",
  "project": "Google",
  "amount": 120000,
  "week": 47,
  "status": "received",
  "confidence": 0.85,
  ...
}
```

---

## 🎯 Testing Coordinator Agent

```bash
source venv/bin/activate
python fastmcp/coordinator_agent.py
```

This will test the full NLP → SQL execution flow with sample messages.

---

## 📊 Using Streamlit Client

1. Start the FastAPI server (see Step 4 above)
2. In another terminal, run:
   ```bash
   source venv/bin/activate
   streamlit run streamlit_app.py
   ```
3. Open `http://localhost:8501` in your browser
4. Select a user from the sidebar
5. Navigate between Dashboard and NLP Chat pages

### Streamlit Features

- **Dashboard Page**: View manager or executive dashboard based on selected user
- **NLP Chat Page**: Send natural language messages and see parsed intents and execution results
- **User Selection**: Switch between different users to see their respective dashboards
- **Server Status**: Check if the FastAPI backend is running

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to database"

**Solution:**
1. Ensure PostgreSQL is running
2. Check DATABASE_URL:
   ```bash
   echo $DATABASE_URL
   ```
3. Test connection:
   ```bash
   psql -h localhost -U postgres -d fastmcp_sales_erp
   ```

### Issue: "NLP Parser not recognizing messages"

**Solution:**
1. Check message format (should contain project name and amount)
2. Verify project names in database:
   ```bash
   python -c "from fastmcp.db.session import SessionLocal; from fastmcp.db.models import Project; db = SessionLocal(); print([p.project_name for p in db.query(Project).all()])"
   ```
3. Review confidence scores in parsed output

### Issue: "Streamlit cannot connect to API"

**Solution:**
1. Ensure FastAPI server is running on `http://localhost:8000`
2. Check firewall settings
3. Verify API_BASE_URL in `streamlit_app.py` is correct

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
PORT=8001 python fastmcp/server.py
```

---

## 📝 Sample Test Data

The seeding script creates:

**Users:**
- Dharmendra (Manager) - dharmendra@goldeneagle.com
- Priya (Executive) - priya@goldeneagle.com
- Amit (Executive) - amit@goldeneagle.com

**Clients:**
- Google (Mountain View, CA)
- Amazon (Seattle, WA)
- Adobe (San Jose, CA)
- Infosys (Bangalore, India)

**Projects:**
- Google Cloud Migration (Dharmendra)
- Amazon AWS Integration (Dharmendra)
- Adobe Creative Suite Deployment (Priya)
- Infosys Data Analytics (Amit)

**Employees:**
- Ramesh (Python, AWS, DevOps)
- Deepak (Java, Spring Boot, Microservices)
- Anita (Frontend, React, JavaScript)
- Vikram (Database, SQL, PostgreSQL)

**Payments:**
- Multiple payments across projects with different statuses

---

## 🚀 Next Steps

1. **Explore the Streamlit Client**: Test all features in the web interface
2. **Test NLP Commands**: Try various natural language messages
3. **Review Logs**: Check server logs for any errors
4. **Extend NLP Patterns**: Add more patterns to `nlp_parser.py` for additional commands
5. **Build React Dashboard**: Implement the React frontend in `client/` directory

---

## 📚 Documentation

- **FASTMCP_README.md** – Complete project documentation
- **fastmcp/db/models.py** – Database schema details
- **fastmcp/tools/nlp_parser.py** – NLP parser implementation
- **fastmcp/tools/sql_executor.py** – SQL executor implementation
- **fastmcp/server.py** – FastAPI application

---

## 💡 Tips

1. **Use curl for quick API testing**: Much faster than Postman for simple requests
2. **Check logs for debugging**: Server logs show detailed error messages
3. **Use Streamlit for interactive testing**: Great for exploring features
4. **Test with sample data first**: Easier to understand the system
5. **Review confidence scores**: Helps understand NLP parser accuracy

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs for error messages
3. Check database connectivity
4. Verify all dependencies are installed

---

**Version**: 1.0.0  
**Last Updated**: November 2024
