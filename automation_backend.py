
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import threading
import schedule
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('classpoint_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ClassPointAutomation:
    def __init__(self):
        self.driver = None
        self.is_running = False
        self.config = {}
        self.status = {
            'isRunning': False,
            'currentStep': 'Ready to start',
            'lastPollAnswered': 'None',
            'totalPollsAnswered': 0,
            'errors': []
        }
        self.polls_answered = 0
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with appropriate options"""
        try:
            logger.info("Setting up Chrome WebDriver...")
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Add more specific options for better stability
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-extensions')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Chrome WebDriver initialized successfully")
            return True
        except Exception as e:
            error_msg = f"Failed to initialize WebDriver: {str(e)}"
            logger.error(error_msg)
            self.add_error(error_msg)
            return False
    
    def add_error(self, error_msg: str):
        """Add error to status tracking"""
        self.status['errors'].append(f"{datetime.now().strftime('%H:%M:%S')} - {error_msg}")
        if len(self.status['errors']) > 10:  # Keep only last 10 errors
            self.status['errors'] = self.status['errors'][-10:]
        logger.error(error_msg)
    
    def update_status(self, step: str):
        """Update current status"""
        self.status['currentStep'] = step
        logger.info(f"Status update: {step}")
    
    def join_classpoint(self, class_code: str, student_name: str) -> bool:
        """Join ClassPoint session with provided credentials"""
        try:
            self.update_status("Opening ClassPoint website")
            logger.info(f"Navigating to ClassPoint with class code: {class_code}, student name: {student_name}")
            
            self.driver.get("https://www.classpoint.app/")
            time.sleep(3)  # Wait for page to load
            
            # Wait for and enter class code
            self.update_status("Looking for class code input field")
            
            # Try multiple selectors for class code input
            class_code_selectors = [
                "input[placeholder*='class code' i]",
                "input[type='text']",
                "input[name*='code']",
                ".class-code-input",
                "#classCode"
            ]
            
            class_code_input = None
            for selector in class_code_selectors:
                try:
                    class_code_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if class_code_input.is_displayed():
                        logger.info(f"Found class code input with selector: {selector}")
                        break
                except:
                    continue
            
            if not class_code_input:
                raise Exception("Could not find class code input field")
            
            self.update_status("Entering class code")
            class_code_input.clear()
            class_code_input.send_keys(class_code)
            logger.info(f"Entered class code: {class_code}")
            
            # Click the blue arrow button after class code
            self.update_status("Looking for submit button")
            
            button_selectors = [
                "button[type='submit']",
                ".btn",
                "button",
                "[role='button']",
                ".submit-btn"
            ]
            
            arrow_button = None
            for selector in button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            arrow_button = button
                            logger.info(f"Found submit button with selector: {selector}")
                            break
                    if arrow_button:
                        break
                except:
                    continue
            
            if not arrow_button:
                raise Exception("Could not find submit button for class code")
            
            arrow_button.click()
            logger.info("Clicked submit button for class code")
            time.sleep(3)
            
            # Wait for and enter student name
            self.update_status("Looking for student name input field")
            
            name_selectors = [
                "input[placeholder*='name' i]",
                "input[type='text']",
                "input[name*='name']",
                ".student-name-input",
                "#studentName"
            ]
            
            name_input = None
            for selector in name_selectors:
                try:
                    name_input = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if name_input.is_displayed():
                        logger.info(f"Found name input with selector: {selector}")
                        break
                except:
                    continue
            
            if not name_input:
                raise Exception("Could not find student name input field")
            
            self.update_status("Entering student name")
            name_input.clear()
            name_input.send_keys(student_name)
            logger.info(f"Entered student name: {student_name}")
            
            # Click the submit button for name
            submit_button = None
            for selector in button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            submit_button = button
                            break
                    if submit_button:
                        break
                except:
                    continue
            
            if not submit_button:
                raise Exception("Could not find submit button for student name")
            
            submit_button.click()
            logger.info("Clicked submit button for student name")
            
            self.update_status("Successfully joined ClassPoint session")
            time.sleep(5)  # Wait for session to fully load
            return True
            
        except TimeoutException as e:
            error_msg = f"Timeout while joining ClassPoint: {str(e)}"
            self.add_error(error_msg)
            return False
        except Exception as e:
            error_msg = f"Error joining ClassPoint: {str(e)}"
            self.add_error(error_msg)
            return False

    def detect_and_answer_poll(self) -> bool:
        """Detect if a poll is active and answer it"""
        try:
            logger.info("Checking for active polls...")
            
            # Multiple selectors to detect poll interface
            poll_selectors = [
                # Look for multiple choice options (A, B, C, D buttons)
                "button:contains('A'), button:contains('B'), button:contains('C'), button:contains('D')",
                "[data-testid*='option'], [data-testid*='choice']",
                ".poll-option, .choice-option, .answer-option",
                "button[class*='option'], button[class*='choice']",
                # Look for submit button which indicates an active poll
                "button:contains('Submit')",
                ".submit-btn, .poll-submit",
                # Generic poll indicators
                ".poll-container, .question-container, .multiple-choice",
                "[role='radiogroup'], [role='group']"
            ]
            
            poll_found = False
            poll_element = None
            
            # Check each selector to find active poll
            for selector in poll_selectors:
                try:
                    if ":contains(" in selector:
                        # Handle jQuery-style selectors
                        elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), 'A') or contains(text(), 'B') or contains(text(), 'C') or contains(text(), 'D') or contains(text(), 'Submit')]")
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            poll_element = element
                            poll_found = True
                            logger.info(f"Found poll element with selector: {selector}")
                            break
                    if poll_found:
                        break
                except:
                    continue
            
            if not poll_found:
                # Try to find poll by looking for specific text patterns
                try:
                    poll_indicators = [
                        "//*[contains(text(), 'choose') and contains(text(), 'answer')]",
                        "//*[contains(text(), 'Multiple Choice')]",
                        "//*[contains(text(), 'Select one')]",
                        "//*[contains(text(), 'question')]"
                    ]
                    
                    for indicator in poll_indicators:
                        elements = self.driver.find_elements(By.XPATH, indicator)
                        if elements and elements[0].is_displayed():
                            poll_found = True
                            logger.info(f"Found poll by text indicator: {indicator}")
                            break
                except:
                    pass
            
            if not poll_found:
                return False
            
            logger.info("Active poll detected! Attempting to answer...")
            self.update_status("Poll detected - selecting answer")
            
            # Find answer options (A, B, C, D)
            option_selectors = [
                # Look for buttons with text A, B, C, D
                "//button[text()='A' or text()='B' or text()='C' or text()='D']",
                "//div[text()='A' or text()='B' or text()='C' or text()='D']//parent::button",
                "//span[text()='A' or text()='B' or text()='C' or text()='D']//ancestor::button",
                # Look for clickable elements with option classes
                "button[class*='option'], div[class*='option'][role='button']",
                "[data-option], [data-choice]",
                ".poll-option, .choice-button, .answer-btn",
                # Look for radio buttons or checkboxes
                "input[type='radio'], input[type='checkbox']"
            ]
            
            answer_options = []
            
            for selector in option_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            answer_options.append(element)
                    
                    if len(answer_options) >= 2:  # Found multiple options
                        break
                except:
                    continue
            
            if len(answer_options) == 0:
                logger.warning("No answer options found")
                return False
            
            # Select answer based on strategy
            strategy = self.config.get('answerStrategy', 'random')
            selected_option = None
            
            if strategy == 'random':
                selected_option = random.choice(answer_options)
                selected_text = "Random"
            elif strategy == 'always_a' and len(answer_options) > 0:
                selected_option = answer_options[0]
                selected_text = "A"
            elif strategy == 'always_b' and len(answer_options) > 1:
                selected_option = answer_options[1]
                selected_text = "B"
            elif strategy == 'always_c' and len(answer_options) > 2:
                selected_option = answer_options[2]
                selected_text = "C"
            elif strategy == 'always_d' and len(answer_options) > 3:
                selected_option = answer_options[3]
                selected_text = "D"
            else:
                # Fallback to random if strategy option not available
                selected_option = random.choice(answer_options)
                selected_text = "Random (fallback)"
            
            if not selected_option:
                logger.warning("Could not select an option")
                return False
            
            # Click the selected option
            logger.info(f"Selecting option: {selected_text}")
            selected_option.click()
            time.sleep(1)
            
            # Find and click submit button
            submit_selectors = [
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'submit')]",
                "//input[@type='submit']",
                ".submit-btn, .poll-submit, .answer-submit",
                "button[type='submit']"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            submit_button = element
                            break
                    if submit_button:
                        break
                except:
                    continue
            
            if submit_button:
                logger.info("Clicking submit button")
                submit_button.click()
                time.sleep(2)
                
                # Update status
                self.polls_answered += 1
                self.status['totalPollsAnswered'] = self.polls_answered
                self.status['lastPollAnswered'] = f"Option {selected_text} at {datetime.now().strftime('%H:%M:%S')}"
                
                logger.info(f"Successfully answered poll #{self.polls_answered} with option {selected_text}")
                self.update_status(f"Poll #{self.polls_answered} answered - {selected_text}")
                return True
            else:
                logger.warning("Could not find submit button")
                return False
                
        except Exception as e:
            error_msg = f"Error while answering poll: {str(e)}"
            logger.error(error_msg)
            self.add_error(error_msg)
            return False

    def run_continuous_polling(self):
        """Run continuous poll detection and answering"""
        logger.info("Starting continuous poll monitoring...")
        self.update_status("Monitoring for polls...")
        
        poll_check_interval = 3  # Check every 3 seconds
        last_poll_time = 0
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # Only check for polls every few seconds to avoid overwhelming
                if current_time - last_poll_time >= poll_check_interval:
                    
                    # Check if we're still connected to ClassPoint
                    if not self.driver or not self.driver.current_url:
                        logger.error("Lost connection to ClassPoint")
                        self.add_error("Lost connection to ClassPoint")
                        break
                    
                    # Look for and answer polls
                    poll_answered = self.detect_and_answer_poll()
                    
                    if poll_answered:
                        logger.info("Poll answered successfully")
                        # Wait a bit longer after answering a poll
                        time.sleep(5)
                    
                    last_poll_time = current_time
                
                # Short sleep to prevent excessive CPU usage
                time.sleep(1)
                
            except Exception as e:
                error_msg = f"Error in polling loop: {str(e)}"
                logger.error(error_msg)
                self.add_error(error_msg)
                time.sleep(5)  # Wait before retrying
        
        logger.info("Continuous polling stopped")
        self.update_status("Poll monitoring stopped")
    
    def start_automation(self, config: Dict):
        """Start the automation process"""
        logger.info("Starting automation process...")
        logger.info(f"Configuration: {config}")
        
        self.config = config
        self.is_running = True
        self.status['isRunning'] = True
        self.polls_answered = 0
        self.status['totalPollsAnswered'] = 0
        self.status['errors'] = []
        
        try:
            if not self.setup_driver():
                self.stop_automation()
                return False
            
            if not self.join_classpoint(config['classCode'], config['studentName']):
                self.stop_automation()
                return False
            
            # Start continuous polling in a separate thread
            polling_thread = threading.Thread(target=self.run_continuous_polling)
            polling_thread.daemon = True
            polling_thread.start()
            
            logger.info("Automation started successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to start automation: {str(e)}"
            logger.error(error_msg)
            self.add_error(error_msg)
            self.stop_automation()
            return False
    
    def stop_automation(self):
        """Stop the automation process"""
        logger.info("Stopping automation...")
        self.is_running = False
        self.status['isRunning'] = False
        self.update_status("Stopping automation...")
        
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("WebDriver closed successfully")
        except Exception as e:
            logger.error(f"Error closing WebDriver: {str(e)}")
        
        self.update_status("Automation stopped")
        logger.info("Automation stopped successfully")

# Flask API
app = Flask(__name__)
CORS(app, origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:5173"])

automation = ClassPointAutomation()

@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    try:
        logger.info("Received start automation request")
        config = request.get_json()
        logger.info(f"Config received: {config}")
        
        if automation.is_running:
            logger.warning("Automation is already running")
            return jsonify({'error': 'Automation is already running'}), 400
        
        success = automation.start_automation(config)
        
        if success:
            logger.info("Automation started successfully")
            return jsonify({'message': 'Automation started successfully'})
        else:
            logger.error("Failed to start automation")
            return jsonify({'error': 'Failed to start automation'}), 500
            
    except Exception as e:
        logger.error(f"Error starting automation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/stop', methods=['POST'])
def stop_automation():
    try:
        logger.info("Received stop automation request")
        automation.stop_automation()
        return jsonify({'message': 'Automation stopped successfully'})
    except Exception as e:
        logger.error(f"Error stopping automation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/status', methods=['GET'])
def get_status():
    return jsonify(automation.status)

@app.route('/api/health', methods=['GET'])
def health_check():
    logger.info("Health check requested")
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    logger.info("Starting ClassPoint Automation API Server on http://127.0.0.1:5000")
    print("🚀 Backend server starting on http://127.0.0.1:5000")
    print("📝 Check 'classpoint_automation.log' for detailed logs")
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
