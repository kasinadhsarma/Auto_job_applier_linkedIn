"""Smart question handling for job applications"""

from typing import Dict, List, Optional, Union
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from config.questions import (
    years_of_experience,
    require_visa,
    notice_period,
    expected_salary,
    current_salary,
    summary,
    cover_letter
)

class QuestionHandler:
    def __init__(self):
        self.previous_answers = {}
        
    def handle_select_question(self, element: WebElement, label: str) -> bool:
        """Handle dropdown select questions"""
        try:
            select = Select(element.find_element(By.TAG_NAME, "select"))
            
            # Handle common select questions
            if "experience" in label.lower():
                select.select_by_visible_text(years_of_experience)
            elif "notice" in label.lower():
                select.select_by_visible_text(notice_period)
            elif any(word in label.lower() for word in ["salary", "compensation"]):
                select.select_by_visible_text(expected_salary)
            else:
                # Use previous answer if available
                prev_answer = self.previous_answers.get(label)
                if prev_answer:
                    select.select_by_visible_text(prev_answer)
                else:
                    # Default to first non-empty option
                    options = select.options
                    for option in options:
                        if option.text.strip():
                            select.select_by_visible_text(option.text)
                            self.previous_answers[label] = option.text
                            break
            return True
            
        except Exception as e:
            print(f"Error handling select question: {e}")
            return False
            
    def handle_text_question(self, element: WebElement, label: str) -> bool:
        """Handle text input questions"""
        try:
            input_field = element.find_element(By.TAG_NAME, "input")
            
            # Handle common text questions
            if "salary" in label.lower():
                input_field.send_keys(current_salary)
            elif "visa" in label.lower():
                input_field.send_keys(require_visa)
            else:
                # Use previous answer if available
                prev_answer = self.previous_answers.get(label)
                if prev_answer:
                    input_field.send_keys(prev_answer)
                else:
                    # Default empty
                    return False
                    
            return True
            
        except Exception as e:
            print(f"Error handling text question: {e}")
            return False
            
    def handle_textarea_question(self, element: WebElement, label: str) -> bool:
        """Handle textarea questions like summary and cover letter"""
        try:
            textarea = element.find_element(By.TAG_NAME, "textarea")
            
            if "summary" in label.lower():
                textarea.send_keys(summary)
            elif "cover letter" in label.lower():
                textarea.send_keys(cover_letter) 
            else:
                # Use previous answer if available
                prev_answer = self.previous_answers.get(label)
                if prev_answer:
                    textarea.send_keys(prev_answer)
                else:
                    return False
                    
            return True
            
        except Exception as e:
            print(f"Error handling textarea question: {e}")
            return False
            
    def handle_radio_question(self, element: WebElement, label: str) -> bool:
        """Handle radio button questions"""
        try:
            options = element.find_elements(By.TAG_NAME, "input[type='radio']")
            
            # Handle common radio questions
            if "sponsorship" in label.lower():
                for option in options:
                    if require_visa.lower() in option.get_attribute("value").lower():
                        option.click()
                        return True
                        
            # Use previous answer if available
            prev_answer = self.previous_answers.get(label)
            if prev_answer:
                for option in options:
                    if prev_answer.lower() in option.get_attribute("value").lower():
                        option.click()
                        return True
                        
            # Default to first option
            if options:
                options[0].click()
                self.previous_answers[label] = options[0].get_attribute("value")
                return True
                
            return False
            
        except Exception as e:
            print(f"Error handling radio question: {e}")
            return False
