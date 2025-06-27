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
        """Detect and answer a poll using robust, multi-strategy methods. Fallback to mouse automation if needed."""
        import importlib
        import sys
        logger.info("Checking for active polls (multi-strategy)...")
        driver = self.driver
        poll_found = False
        poll_header = None
        poll_header_xpaths = [
            # Most specific to least specific
            "//div[contains(@class, 'active_title_head')]//h4[contains(text(), 'Multiple Choice')]",
            "//h4[contains(text(), 'Multiple Choice')]",
            "//div[contains(@class, 'active_title_head')]//h4",
            "//h4",
            "//*[contains(text(), 'Multiple Choice')]",
            "//*[contains(text(), 'Poll')]",
            "//*[contains(text(), 'Question')]",
        ]
        for xpath in poll_header_xpaths:
            try:
                elem = driver.find_element(By.XPATH, xpath)
                if elem.is_displayed():
                    poll_header = elem
                    poll_found = True
                    logger.info(f"Poll header found with xpath: {xpath}")
                    break
            except Exception:
                continue
        if not poll_found:
            logger.info("No poll header found (all strategies). Trying to find answer area anyway.")
        # Try to find the answer area (custom_sheck or similar)
        answer_area = None
        answer_area_xpaths = [
            "//div[contains(@class, 'custom_sheck')]",
            "//div[contains(@class, 'MuiBox-root') and .//input]",
            "//div[contains(@class, 'MuiFormGroup-root')]",
            "//form//div[.//input]",
            "//div[.//input]",
        ]
        for xpath in answer_area_xpaths:
            try:
                elem = driver.find_element(By.XPATH, xpath)
                if elem.is_displayed():
                    answer_area = elem
                    logger.info(f"Answer area found with xpath: {xpath}")
                    break
            except Exception:
                continue
        if not answer_area:
            logger.warning("No answer area found. Will try global search for options.")
        # Find all answer options (A/B/C/D) by multiple strategies
        answer_inputs = []
        option_letters = ["A", "B", "C", "D"]
        # 1. Try by input id and label for
        search_contexts = [answer_area] if answer_area else [driver]
        for context in search_contexts:
            for letter in option_letters:
                try:
                    input_elem = context.find_element(By.XPATH, f".//input[@id='{letter}' or @value='{letter}' or @aria-label='{letter}' or @type='radio' or @type='checkbox']")
                    label_elem = context.find_element(By.XPATH, f".//label[@for='{letter}']")
                    if input_elem.is_displayed() or label_elem.is_displayed():
                        answer_inputs.append((input_elem, label_elem, letter))
                except Exception:
                    continue
        # 2. Try by visible text (span or div with A/B/C/D)
        if not answer_inputs:
            for context in search_contexts:
                for letter in option_letters:
                    try:
                        span_elem = context.find_element(By.XPATH, f".//*[text()='{letter}']")
                        parent = span_elem.find_element(By.XPATH, "..")
                        input_elem = None
                        try:
                            input_elem = parent.find_element(By.XPATH, ".//input")
                        except Exception:
                            pass
                        if input_elem and (input_elem.is_displayed() or span_elem.is_displayed()):
                            answer_inputs.append((input_elem, span_elem, letter))
                    except Exception:
                        continue
        # 3. Try all visible radio/checkbox inputs in the area
        if not answer_inputs and answer_area:
            try:
                inputs = answer_area.find_elements(By.XPATH, ".//input[@type='radio' or @type='checkbox']")
                for idx, input_elem in enumerate(inputs):
                    if input_elem.is_displayed():
                        label = None
                        try:
                            label = answer_area.find_element(By.XPATH, f".//label[@for='{input_elem.get_attribute('id')}']")
                        except Exception:
                            pass
                        letter = input_elem.get_attribute('id') or chr(65+idx)
                        answer_inputs.append((input_elem, label, letter))
            except Exception:
                pass
        # 4. As a last resort, try all visible radio/checkbox inputs globally
        if not answer_inputs:
            try:
                inputs = driver.find_elements(By.XPATH, "//input[@type='radio' or @type='checkbox']")
                for idx, input_elem in enumerate(inputs):
                    if input_elem.is_displayed():
                        label = None
                        try:
                            label = driver.find_element(By.XPATH, f"//label[@for='{input_elem.get_attribute('id')}']")
                        except Exception:
                            pass
                        letter = input_elem.get_attribute('id') or chr(65+idx)
                        answer_inputs.append((input_elem, label, letter))
            except Exception:
                pass
        if not answer_inputs:
            # Debug: log the HTML of the answer area for troubleshooting
            try:
                html = answer_area.get_attribute('outerHTML') if answer_area else driver.page_source
                logger.warning(f"No answer options found. Answer area HTML: {html[:2000]}")
            except Exception as e:
                logger.warning(f"No answer options found and could not get answer area HTML: {str(e)}")
            # Failsafe: try mouse automation
            logger.warning("Trying mouse automation as failsafe for answer selection.")
            return self._mouse_failsafe_answer()
        # Choose answer based on strategy
        strategy = self.config.get('answerStrategy', 'random')
        selected = None
        if strategy == 'random':
            selected = random.choice(answer_inputs)
        elif strategy == 'always_a':
            selected = next((x for x in answer_inputs if x[2].upper() == 'A'), answer_inputs[0])
        elif strategy == 'always_b':
            selected = next((x for x in answer_inputs if x[2].upper() == 'B'), answer_inputs[0])
        elif strategy == 'always_c':
            selected = next((x for x in answer_inputs if x[2].upper() == 'C'), answer_inputs[0])
        elif strategy == 'always_d':
            selected = next((x for x in answer_inputs if x[2].upper() == 'D'), answer_inputs[0])
        else:
            selected = random.choice(answer_inputs)
        selected_input, selected_label, selected_letter = selected
        # Try to click the label, then input, then JS click
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_label or selected_input)
            time.sleep(0.1)
            try:
                if selected_label:
                    selected_label.click()
                else:
                    selected_input.click()
            except Exception:
                try:
                    driver.execute_script("arguments[0].click();", selected_label or selected_input)
                except Exception:
                    selected_input.click()
            logger.info(f"Clicked answer for {selected_letter}")
            time.sleep(0.2)
        except Exception as e:
            logger.error(f"Failed to click answer: {str(e)}. Trying mouse failsafe.")
            return self._mouse_failsafe_answer()
        # Find the submit button by multiple strategies
        submit_btn = None
        submit_xpaths = [
            ".//button[span[text()='Submit'] or text()='Submit']",
            ".//div[contains(@class, 'sh_btn')]//button[contains(., 'Submit')]",
            ".//button[contains(@class, 'MuiButton-containedPrimary') and (span[text()='Submit'] or text()='Submit')]",
            ".//button[contains(text(), 'Submit')]",
            ".//button",
        ]
        for context in search_contexts:
            for xpath in submit_xpaths:
                try:
                    btn = context.find_element(By.XPATH, xpath)
                    if btn.is_displayed() and btn.is_enabled():
                        submit_btn = btn
                        break
                except Exception:
                    continue
            if submit_btn:
                break
        # Fallback: try global
        if not submit_btn:
            try:
                btns = driver.find_elements(By.XPATH, "//button")
                for btn in btns:
                    if btn.is_displayed() and btn.is_enabled() and ('submit' in btn.text.lower() or btn.get_attribute('type') == 'submit'):
                        submit_btn = btn
                        break
            except Exception:
                pass
        if not submit_btn:
            logger.warning("Submit button not found. Trying mouse failsafe for submit.")
            return self._mouse_failsafe_answer(answer=True)
        try:
            submit_btn.click()
        except Exception:
            try:
                driver.execute_script("arguments[0].click();", submit_btn)
            except Exception:
                logger.error("Failed to click submit button. Trying mouse failsafe.")
                return self._mouse_failsafe_answer(answer=False, submit=True)
        logger.info("Clicked submit button")
        self.polls_answered += 1
        self.status['totalPollsAnswered'] = self.polls_answered
        self.status['lastPollAnswered'] = f"Poll answered at {datetime.now().strftime('%H:%M:%S')}"
        self.update_status(f"Poll #{self.polls_answered} answered")
        time.sleep(1.5)
        return True

    def _mouse_failsafe_answer(self, answer=True, submit=True):
        """Move mouse to hardcoded coordinates for A and submit as a last resort."""
        try:
            import pyautogui
        except ImportError:
            logger.error("pyautogui not installed. Please install it for mouse failsafe.")
            return False
        logger.warning("Using pyautogui mouse failsafe. Move your mouse away if you want to abort.")
        # These coordinates may need to be adjusted for your screen/browser
        # You can use pyautogui.displayMousePosition() to calibrate
        # Default: (x, y) for A option and submit button
        # You may want to expose these as config in the future
        a_option_coords = (600, 400)  # Example: center of browser where A is expected
        submit_btn_coords = (600, 600)  # Example: below A, where submit is expected
        if answer:
            logger.warning(f"Moving mouse to {a_option_coords} and clicking for A option.")
            pyautogui.moveTo(*a_option_coords, duration=0.3)
            pyautogui.click()
            time.sleep(0.2)
        if submit:
            logger.warning(f"Moving mouse to {submit_btn_coords} and clicking for submit button.")
            pyautogui.moveTo(*submit_btn_coords, duration=0.3)
            pyautogui.click()
            time.sleep(0.2)
        self.polls_answered += 1
        self.status['totalPollsAnswered'] = self.polls_answered
        self.status['lastPollAnswered'] = f"Poll answered at {datetime.now().strftime('%H:%M:%S')} (mouse failsafe)"
        self.update_status(f"Poll #{self.polls_answered} answered (mouse failsafe)")
        return True

    def run_continuous_polling(self):
        """Continuously check for and answer polls every 5 seconds"""
        self.is_running = True
        self.status['isRunning'] = True
        
        logger.info("Starting continuous poll monitoring...")
        self.update_status("Monitoring for polls")
        
        while self.is_running:
            try:
                if self.detect_and_answer_poll():
                    # Successfully answered a poll, wait 5 seconds before checking again
                    time.sleep(5)
                else:
                    # No poll found, wait 5 seconds before checking again
                    time.sleep(5)
            except Exception as e:
                error_msg = f"Error in poll monitoring loop: {str(e)}"
                logger.error(error_msg)
                self.add_error(error_msg)
                time.sleep(5)  # Wait before retrying even if there's an error
        
        logger.info("Stopped poll monitoring")
        self.status['isRunning'] = False
    
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
