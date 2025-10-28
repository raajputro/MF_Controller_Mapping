from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
from basic_actions import BasicActions
import re

class user_access_control_page(BasicActions):
    def __init__(self, page):
        super().__init__(page)
        self.page = page       

        
    def set_user_access_for_feature_action(self, role, module, feature, action):
        # try:            
        #     self.page.locator('#roleList').select_option(label=role)            
        #     self.page.locator('#moduleList').select_option(label=module)        
            
        #     self.page.locator('#request-map-table').wait_for(state='visible') #, timeout=10000)

        #     print(f'Clicking on {action}')
        #     action_locator = self.page.locator(f'//table[@id="request-map-table"]/tbody/tr/td/input[@value="{feature}"]/parent::td/following-sibling::td/input[@value="{action}"]')
        #     action_locator.click()            
        #     self.page.locator('//input[@type="button" and @value="Save"]').click()    
        #     self.wait_for_timeout(5000)

        #     success_elem = self.page.locator('div.jGrowl-notification.ui-state-highlight.ui-corner-all.success')
        #     success_elem.wait_for(state='visible', timeout=10000)

        #     # Optional: Verify the message content
        #     if "success" in success_elem.text_content().lower():
        #         print(f'User access for Role: {role}, Module: {module}, Feature: {feature}, Action: {action} set successfully.')
        #     else:
        #         print('Action completed but success message content unexpected')                
        #     self.get_full_page_screenshot('Mapping Done')
        # except PlaywrightTimeoutError:
        #     print(f'User access for Role: {role}, Module: {module}, Feature: {feature}, Action: {action} set successfully.')
        #     raise
        # except Exception as e:
        #     print(f'Error in setting user access for feature action: {e}')
        #     raise
        try:
            # Step 1: Select role and module with retry logic
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    print(f'Selecting Role: {role} (attempt {retry_count + 1}/{max_retries})')
                    self.page.locator('#roleList').select_option(label=role)
                    
                    print(f'Selecting Module: {module} (attempt {retry_count + 1}/{max_retries})')
                    self.page.locator('#moduleList').select_option(label=module)
                    
                    # Wait for the table to load and be stable
                    print('Waiting for request map table to load...')
                    self.page.locator('#request-map-table').wait_for(state='visible', timeout=15000)
                    
                    # Additional check to ensure table has content
                    table_rows = self.page.locator('#request-map-table tbody tr')
                    table_rows.first.wait_for(state='visible', timeout=10000)
                    break
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise Exception(f"Failed to select role/module after {max_retries} attempts: {str(e)}")
                    print(f"Retry {retry_count} for role/module selection...")
                    self.wait_for_timeout(2000)
                    continue

            # Step 2: Click on the action with robust waiting
            print(f'Clicking on action: {action} for feature: {feature}')
            
            # Multiple selector strategies for the action locator
            action_locators = [
                f'//table[@id="request-map-table"]/tbody/tr/td/input[@value="{feature}"]/parent::td/following-sibling::td/input[@value="{action}"]',
                # f'//input[@value="{feature}"]/ancestor::tr//input[@value="{action}"]',
                # f'//table[@id="request-map-table"]//input[@value="{action}"]'
            ]
            
            action_element = None
            for locator_strategy in action_locators:
                try:
                    action_element = self.page.locator(locator_strategy)
                    if action_element.count() > 0:
                        action_element.first.wait_for(state='visible', timeout=5000)
                        break
                except:
                    continue
            
            if not action_element or action_element.count() == 0:
                raise Exception(f"Could not find action element for feature '{feature}' and action '{action}'")
            
            # Verify element is enabled before clicking
            if not action_element.is_enabled():
                raise Exception(f"Action element for '{action}' is not enabled")
            
            action_element.click()
            
            # Step 3: Save with multiple verification strategies
            print('Clicking Save button...')
            save_button = self.page.locator('//input[@type="button" and @value="Save"]')
            save_button.wait_for(state='visible', timeout=5000)
            
            if not save_button.is_enabled():
                raise Exception("Save button is not enabled")
            
            save_button.click()
            
            # Step 4: Wait for operation to complete with multiple verification methods
            print('Waiting for save operation to complete...')
            
            # Method 1: Wait for success message
            success_indicators = [
                'div.jGrowl-notification.ui-state-highlight.ui-corner-all.success',
                # '.jGrowl-notification.success',
                # 'div.ui-state-highlight',  # More generic highlight
                # 'div.alert-success',       # Alternative success class
            ]
            
            success_element = None
            for selector in success_indicators:
                try:
                    success_element = self.page.locator(selector)
                    success_element.first.wait_for(state='visible', timeout=30000)  # 30 second timeout
                    print(f'Success indicator found using selector: {selector}')
                    break
                except:
                    continue
            
            if not success_element:
                # Method 2: Check for any visible success indicators using regex
                try:
                    success_element = self.page.get_by_text(re.compile(r'success|saved|completed|successfully', re.IGNORECASE))
                    success_element.first.wait_for(state='visible', timeout=30000)
                    print('Success indicator found using text regex match')
                except:
                    pass
            
            # Method 3: Wait for loading indicators to disappear (if any)
            try:
                self.page.locator('.loading, .spinner, .progress-bar').wait_for(state='hidden', timeout=15000)
            except:
                pass  # No loading indicator found, that's fine
            
            # Step 5: Verify the success
            if success_element:
                success_text = success_element.text_content().lower()
                print(f'Success message detected: {success_text[:100]}...')
                
            #     if any(word in success_text for word in ['success', 'saved', 'completed', 'updated']):
            #         print(f'✓ User access for Role: {role}, Module: {module}, Feature: {feature}, Action: {action} set successfully.')
            #     else:
            #         print(f'⚠ Action completed but success message content unexpected: {success_text[:100]}...')
            #         # Don't raise error here, as the operation might have succeeded
            else:
                print('⚠ No explicit success message detected, but operation may have completed')
            #     # Check if we're still on the same page and form is stable
            #     try:
            #         self.page.locator('#request-map-table').wait_for(state='visible', timeout=5000)
            #         print('✓ Form is still accessible, operation likely completed')
            #     except:
            #         print('⚠ Form not accessible, operation status uncertain')
            
            # Step 6: Take screenshot for documentation
            self.get_full_page_screenshot('Mapping_Done')
            
            # Optional: Small delay to ensure everything is settled
            self.wait_for_timeout(2000)

        except PlaywrightTimeoutError as e:
            print(f'⏰ Timeout occurred during access setting for Role: {role}, Module: {module}, Feature: {feature}, Action: {action}')
            print(f'Timeout error details: {str(e)}')
            
            # Take screenshot on timeout for debugging
            self.get_full_page_screenshot('Timeout_Error')
            
            # Check if the operation might have succeeded despite timeout
            try:
                self.page.locator('#request-map-table').wait_for(state='visible', timeout=5000)
                print('✓ Form is still accessible after timeout, operation might have succeeded')
            except:
                print('❌ Form not accessible after timeout, operation likely failed')
            
            raise Exception(f"Timeout setting user access: {str(e)}")

        except Exception as e:
            print(f'❌ Error in setting user access for Role: {role}, Module: {module}, Feature: {feature}, Action: {action}')
            print(f'Error details: {str(e)}')
            
            # Take screenshot on error for debugging
            self.get_full_page_screenshot('Error_State')
            
            # Additional debug information
            try:
                current_url = self.page.url
                print(f'Current URL: {current_url}')
                
                # Check if page has any error messages
                error_elements = self.page.locator('.error, .alert-danger, .ui-state-error')
                if error_elements.count() > 0:
                    error_text = error_elements.first.text_content()
                    print(f'Page error message: {error_text}')
            except Exception as debug_error:
                print(f'Debug information unavailable: {str(debug_error)}')
            
            raise Exception(f"Failed to set user access: {str(e)}")