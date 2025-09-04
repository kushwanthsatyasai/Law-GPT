# Create default user for Law-GPT local development

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..."
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "Virtual environment not found. Please create it first."
    Write-Host "Run: python -m venv .venv"
    exit 1
}

# Change to backend directory
Set-Location -Path "./backend"

# Create a Python script to add a default user
$pythonScript = @"
from app.database import Base, engine, SessionLocal
from app.models import User
from app.auth import hash_password

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create a default user
db = SessionLocal()
default_user = db.query(User).filter(User.email == "user@example.com").first()
if not default_user:
    user = User(
        email="user@example.com",
        password_hash=hash_password("password"),
        role="lawyer"
    )
    db.add(user)
    db.commit()
    print("Default user created: user@example.com / password")
else:
    print("Default user already exists")

db.close()
"@

# Write the Python script to a temporary file
$tempFile = "temp_create_user.py"
Set-Content -Path $tempFile -Value $pythonScript

# Run the Python script
Write-Host "Creating default user..."
python $tempFile

# Clean up
Remove-Item $tempFile

# Return to the original directory
Set-Location -Path ".."

Write-Host "Default user setup completed."
Write-Host "You can now log in with: user@example.com / password"