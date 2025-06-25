
# ClassPoint Automation System

A comprehensive automation system for participating in ClassPoint online lectures. This system automatically joins classes, detects polls, and submits answers based on your preferences.

## 🎯 Features

- **Automated Class Joining**: Enters class code and student name automatically
- **Real-time Poll Detection**: Continuously monitors for new polls during lectures
- **Multiple Answer Strategies**: Random, fixed options, or custom strategies
- **Scheduled Execution**: Auto-start at 9:02 AM with 9:10 AM fallback
- **Modern Web Interface**: Easy-to-use React frontend for configuration
- **Real-time Status Monitoring**: Track polls answered, current status, and errors
- **Comprehensive Logging**: Detailed logs for troubleshooting

## 🛠️ Technology Stack

### Frontend
- React 18 with TypeScript
- Tailwind CSS for styling
- shadcn/ui components
- Real-time status updates

### Backend
- Python 3.8+
- Selenium WebDriver for browser automation
- Flask API for frontend communication
- Chrome browser automation

## 📋 Prerequisites

1. **Chrome Browser**: Must be installed and accessible
2. **Node.js**: Version 16+ for the React frontend
3. **Python**: Version 3.8+ for the automation backend
4. **Internet Connection**: Required for ClassPoint access

## 🚀 Quick Start

### Step 1: Clone and Setup Frontend
```bash
# The frontend is already set up in this Lovable project
# Just run the development server
npm run dev
```

### Step 2: Setup Python Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the automation backend
python start_automation.py
```

### Step 3: Open Web Interface
1. Open http://localhost:8080 in your browser
2. Configure your settings:
   - Class Code: `PHYS1E03` (or your specific code)
   - Student Name: Your name
   - Answer Strategy: Choose your preferred method
   - Schedule: Enable for automatic start times

### Step 4: Start Automation
1. Click "Start Automation" in the web interface
2. A new Chrome window will open and navigate to ClassPoint
3. The system will automatically:
   - Enter your class code
   - Enter your name  
   - Monitor for polls
   - Answer polls based on your strategy
   - Continue until stopped

## ⚙️ Configuration Options

### Answer Strategies
- **Random Selection**: Randomly chooses from available options
- **Always Answer A/B/C/D**: Always selects the specified option
- **Custom Logic**: Extend the code for more complex strategies

### Scheduling
- **Primary Time**: 9:02 AM (default for morning lectures)
- **Fallback Time**: 9:10 AM (if class hasn't started yet)
- **Manual Start**: Start immediately regardless of time

### Monitoring
- **Real-time Status**: Current step and progress
- **Poll Counter**: Total polls answered in session
- **Error Tracking**: Recent errors and issues
- **Detailed Logs**: Check `classpoint_automation.log`

## 🔧 Troubleshooting

### Common Issues

1. **Chrome Driver Not Found**
   ```bash
   # Install webdriver-manager
   pip install webdriver-manager
   ```

2. **ClassPoint Elements Not Found**
   - Check if ClassPoint has updated their interface
   - Update the CSS selectors in `automation_backend.py`
   - Enable debug mode for more detailed logging

3. **Connection Issues**
   - Ensure stable internet connection
   - Check if ClassPoint website is accessible
   - Verify class code is correct and active

4. **Frontend Not Loading**
   ```bash
   # Restart the React development server
   npm run dev
   ```

5. **Backend API Errors**
   ```bash
   # Restart the Python backend
   python automation_backend.py
   ```

### Debug Mode
Enable debug logging by modifying the logging level in `automation_backend.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📊 System Architecture

```
┌─────────────────┐    HTTP API    ┌──────────────────┐
│  React Frontend │ ◄─────────────► │  Python Backend  │
│                 │                │                  │
│ - Configuration │                │ - Selenium       │
│ - Status Display│                │ - ClassPoint API │
│ - Control Panel │                │ - Poll Detection │
└─────────────────┘                └──────────────────┘
                                           │
                                           ▼
                                   ┌──────────────┐
                                   │   Chrome     │
                                   │   Browser    │
                                   │              │
                                   └──────────────┘
```

## 🔒 Security & Ethics

### Responsible Use
- This tool is designed for legitimate educational participation
- Use only for your own accounts and classes
- Respect your institution's academic integrity policies
- Do not use for unauthorized access or fraudulent purposes

### Privacy
- No data is stored permanently
- All credentials remain local to your machine
- No external services receive your personal information

## 📝 File Structure

```
classpoint-automation/
├── src/
│   ├── components/
│   │   └── ClassPointAutomation.tsx    # Main React component
│   └── pages/
│       └── Index.tsx                   # Main page
├── automation_backend.py               # Python automation logic
├── start_automation.py                # Startup script
├── requirements.txt                   # Python dependencies
├── classpoint_automation.log          # Runtime logs
└── README.md                         # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please use responsibly and in accordance with your institution's policies.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the log files for detailed error messages
3. Ensure all prerequisites are properly installed
4. Verify ClassPoint is accessible and your class is active

## 🔄 Updates

### Version 1.0.0
- Initial release with core automation features
- React frontend with real-time monitoring
- Python backend with Selenium automation
- Scheduled execution capabilities
- Comprehensive error handling and logging

---

**Happy Learning! 🎓**
