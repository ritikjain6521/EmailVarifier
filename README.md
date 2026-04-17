# Email Verifier System

A production-ready asynchronous email verification system built with Python (FastAPI), React (Next.js), and PostgreSQL (via Supabase).

## Features
- **Format Validation:** Regular expression checks for general syntax.
- **Disposable Detection:** Instantly drops known disposable email addresses.
- **Deep Deep SMTP Checks:** Concurrently verifies inbox existence on remote servers.
- **Full Frontend Dashboard:** Built with Next.js and Tailwind CSS v4. Easily upload JSON batches to process concurrently.
- **Postgres Database:** SQLAlchemy natively stores user registration and quotas asynchronously using Supabase.

---

## 🛠️ Requirements
Before you begin, ensure you have:
1. **Python 3.10+**
2. **Node.js 18+** & **npm**
3. A running PostgreSQL database (e.g., Supabase)

---

## 🚀 1. Setup the Backend (FastAPI Server)

The backend handles all heavy lifting, SMTP connections, and authorization rules.

### Open a new terminal from the root folder:

**(1) Install Dependencies**
```bash
pip install -r requirements.txt
pip install python-multipart requests pydantic-settings sqlalchemy asyncpg greenlet bcrypt==4.0.1
```

**(2) Configure Environment Variables**
A `.env` file should already be present in the root directory. If not, create one:
```env
DATABASE_URL="postgresql+asyncpg://postgres:[YOUR_PASSWORD]@db.[PROJECT].supabase.co:5432/postgres"
SECRET_KEY="your-super-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="1440"
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

**(3) Run the Server**
Start the FastAPI API using Uvicorn. The `--reload` flag enables auto-reloading on code changes.
```bash
python -m uvicorn app.main:app --reload
```
You should see: `Uvicorn running on http://127.0.0.1:8000`. Leave this terminal open.

---

## 💻 2. Setup the Frontend (Next.js React Server)

The interactive dashboard where you can log in and drop JSON files for verification.

### Open a SECOND new terminal and navigate to the frontend:
```bash
cd frontend
```

**(1) Install Dependencies**
```bash
npm install
```

**(2) Run the Development Server**
Launch the Next.js server locally:
```bash
npm run dev
```
You should see `Ready in ...` and `http://localhost:3000` inside your terminal. Leave this terminal open.

---

## 🏁 3. How to Use & Test

Now that both servers are running side-by-side:

1. **Visit the Dashboard:**
   Open your browser to [http://localhost:3000](http://localhost:3000).

2. **Sign Up:**
   Click "Get Started For Free" or manually head over to [http://localhost:3000/signup](http://localhost:3000/signup). Enter your details. The backend will automatically store your record into your PostgreSQL database.

3. **Verify Emails:**
   On the dashboard, locate the Drag & Drop area.
   Upload a `.json` file containing emails. Example structure for JSON:
   ```json
   ["test@example.com", "support@github.com", "fake@mailinator.com"]
   ```
   Click "Process Emails" and watch the table populate with detailed metrics immediately!

*Note: You can also explore the raw backend interactive Swagger documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).*
