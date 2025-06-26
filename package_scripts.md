
# ClassPoint Automation Setup Instructions

## Frontend Setup

The required dependencies are already installed. To run the application:

```bash
# Install Python dependencies (run this first)
pip install -r requirements.txt

# Start both frontend and backend together
npm run dev & python start_automation.py

# Or run them separately:
# Terminal 1 - Frontend
npm run dev

# Terminal 2 - Backend  
python start_automation.py
```

## Usage

1. **Start the backend**: Run `python start_automation.py`
2. **Start the frontend**: Run `npm run dev` 
3. **Open browser**: Navigate to `http://localhost:8080`
4. **Configure settings**: Enter your ClassPoint class code and student name
5. **Start automation**: Click the "Start Automation" button

## Troubleshooting

- Check `classpoint_automation.log` for detailed Python backend logs
- Use browser developer tools (F12) to check for frontend errors
- Ensure Chrome browser is installed for Selenium WebDriver
- Make sure both servers are running on their respective ports (8080 for frontend, 5000 for backend)

## Files Structure

- `automation_backend.py` - Python Flask API server
- `src/components/ClassPointAutomation.tsx` - React frontend component
- `requirements.txt` - Python dependencies
- `classpoint_automation.log` - Runtime logs
