
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
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
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
    
    def update_status(self, step: str):
        """Update current status"""
        self.status['currentStep'] = step
        logger.info(f"Status update: {step}")
    
    def join_classpoint(self, class_code: str, student_name: str) -> bool:
        """Join ClassPoint session with provided credentials"""
        try:
            self.update_status("Opening ClassPoint website")
            self.driver.get("https://www.classpoint.app/")
            
            # Wait for and enter class code
            self.update_status("Entering class code")
            class_code_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='class code' i], input[type='text']"))
            )
            class_code_input.clear()
            class_code_input.send_keys(class_code)
            
            # Click the blue arrow button after class code
            arrow_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], .btn, button"))
            )
            arrow_button.click()
            
            time.sleep(2)
            
            # Wait for and enter student name
            self.update_status("Entering student name")
            name_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='name' i], input[type='text']"))
            )
            name_input.clear()
            name_input.send_keys(student_name)
            
            # Click the submit button for name
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], .btn, button"))
            )
            submit_button.click()
            
            self.update_status("Successfully joined ClassPoint session")
            time.sleep(3)
            return True
            
        except TimeoutException as e:
            error_msg = f"Timeout while joining ClassPoint: {str(e)}"
            logger.error(error_msg)
            self.add_error(error_msg)
            return False
        except Exception as e:
            error_msg = f"Error joining ClassPoint: {str(e)}"
            logger.error(error_msg)
            self.add_error(error_msg)
            return False
    
    def detect_and_answer_poll(self, answer_strategy: str = 'random') -> bool:
        """Detect if a poll is active and answer it"""
        try:
            # Look for poll questions and answer options
            poll_selectors = [
                "div[class*='poll']",
                "div[class*='question']",
                "div[class*='multiple-choice']",
                ".poll-container",
                ".question-container"
            ]
            
            poll_found = False
            for selector in poll_selectors:
                try:
                    poll_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if poll_element.is_displayed():
                        poll_found = True
                        break
                except NoSuchElementException:
                    continue
            
            if not poll_found:
                return False
            
            # Look for answer options (A, B, C, D, E)
            option_selectors = [
                "button[data-option]",
                ".option-button",
                "button[class*='option']",
                "div[class*='choice'] button",
                "button:contains('A'), button:contains('B'), button:contains('C'), button:contains('D'), button:contains('E')"
            ]
            
            options = []
            for selector in option_selectors:
                try:
                    found_options = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if found_options:
                        options = found_options
                        break
                except:
                    continue
            
            if not options:
                # Alternative approach - look for clickable elements with text A, B, C, D, E
                potential_options = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'A') or contains(text(), 'B') or contains(text(), 'C') or contains(text(), 'D') or contains(text(), 'E')]")
                if potential_options:
                    options = potential_options
            
            if not options:
                logger.warning("Poll detected but no answer options found")
                return False
            
            # Select answer based on strategy
            selected_option = None
            if answer_strategy == 'random':
                selected_option = random.choice(options)
                answer_text = "Random"
            elif answer_strategy == 'always_a' and len(options) > 0:
                selected_option = options[0]
                answer_text = "A"
            elif answer_strategy == 'always_b' and len(options) > 1:
                selected_option = options[1]
                answer_text = "B"
            elif answer_strategy == 'always_c' and len(options) > 2:
                selected_option = options[2]
                answer_text = "C"
            elif answer_strategy == 'always_d' and len(options) > 3:
                selected_option = options[3]
                answer_text = "D"
            else:
                selected_option = options[0]  # Default to first option
                answer_text = "A (default)"
            
            # Click the selected option
            selected_option.click()
            time.sleep(1)
            
            # Look for and click submit button
            submit_selectors = [
                "button[type='submit']",
                "button:contains('Submit')",
                "button:contains('Send')",
                ".submit-btn",
                "button[class*='submit']"
            ]
            
            submit_clicked = False
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        submit_button.click()
                        submit_clicked = True
                        break
                except:
                    continue
            
            if not submit_clicked:
                # Try XPath approach for submit button
                try:
                    submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Submit') or contains(text(), 'Send')]")
                    submit_button.click()
                    submit_clicked = True
                except:
                    logger.warning("Could not find submit button, answer may have been auto-submitted")
            
            self.polls_answered += 1
            self.status['totalPollsAnswered'] = self.polls_answered
            self.status['lastPollAnswered'] = answer_text
            
            self.update_status(f"Answered poll #{self.polls_answered} with option {answer_text}")
            logger.info(f"Successfully answered poll with option: {answer_text}")
            
            time.sleep(2)  # Wait before looking for next poll
            return True
            
        except Exception as e:
            error_msg = f"Error detecting/answering poll: {str(e)}"
            logger.error(error_msg)
            self.add_error(error_msg)
            return False
    
    def run_continuous_polling(self):
        """Continuously check for and answer polls"""
        self.update_status("Starting continuous poll monitoring")
        
        while self.is_running:
            try:
                if self.detect_and_answer_poll(self.config.get('answerStrategy', 'random')):
                    self.update_status(f"Monitoring for polls... (Answered: {self.polls_answered})")
                else:
                    self.update_status(f"Monitoring for polls... (Answered: {self.polls_answered})")
                
                time.sleep(3)  # Check every 3 seconds
                
            except Exception as e:
                error_msg = f"Error in continuous polling: {str(e)}"
                logger.error(error_msg)
                self.add_error(error_msg)
                time.sleep(5)  # Wait longer after error
    
    def start_automation(self, config: Dict):
        """Start the automation process"""
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
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to start automation: {str(e)}"
            logger.error(error_msg)
            self.add_error(error_msg)
            self.stop_automation()
            return False
    
    def stop_automation(self):
        """Stop the automation process"""
        self.is_running = False
        self.status['isRunning'] = False
        self.update_status("Automation stopped")
        
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")
        
        self.driver = None

# Flask API
app = Flask(__name__)
CORS(app, origins=["http://localhost:8080"])

automation = ClassPointAutomation()

@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    try:
        config = request.get_json()
        
        if automation.is_running:
            return jsonify({'error': 'Automation is already running'}), 400
        
        success = automation.start_automation(config)
        
        if success:
            return jsonify({'message': 'Automation started successfully'})
        else:
            return jsonify({'error': 'Failed to start automation'}), 500
            
    except Exception as e:
        logger.error(f"Error starting automation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/stop', methods=['POST'])
def stop_automation():
    try:
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
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    logger.info("Starting ClassPoint Automation API Server")
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
