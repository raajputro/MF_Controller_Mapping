
# this page contains all the common actions to be performed in this project
from playwright.sync_api import expect
from datetime import datetime, timedelta
import os, re, random, sys, pandas as pd
from typing import Optional
# from db_query.check_db import db_query_execution


class BasicActions:
    def __init__(self, page):
        self.page = page
        # Login buttons
        self.userName = page.get_by_label('Username')
        self.passWord = page.get_by_label('Password')
        self.signBtn = page.locator('xpath=//input[@id="kc-login"]')
        # For branch selection
        self.officeDropdown = page.locator('#officeIdDiv_arrow')
        self.goBtn = page.locator('//input[@type="button" and @value="Go"]')
        # Navigation Locators
        # Top navigation
        self.main_nav = self.page.locator('//*[@class="top_nav_container"]')
        # Sub navigation
        self.menu_nav = self.page.locator('xpath=//*[@class="main_top_navigation nav navbar-nav"]')
        # Exit and Logout buttons
        self.exit_button = page.locator("a#btn_login.btn_user")
        self.logout_button = self.page.locator('a:has-text("Logout")')


    # def get_query_data(self, db_server, mobile):
    #     db = db_query_execution(db_server)
    #     result = db.otp_query(mobile_number=mobile)
    #     return result

    def perform_login(
            self,
            given_url: str,
            user_name: str,
            pass_word: str,
            branch_code: Optional[str] = "0",
            timeout: Optional[int] = 30_000,
            post_login_selector: Optional[str] = None,  # fallback dashboard shell
    ) -> bool: # type: ignore
        """Log in robustly; handle post-login overlay; verify success."""
        user_name = (user_name or "").strip()
        pass_word = (pass_word or "").strip()

        # 1) Navigate and wait for form
        self.page.goto(given_url, wait_until="domcontentloaded", timeout=timeout)
        self.userName.wait_for(state="visible", timeout=timeout)
        self.userName.clear()
        self.userName.fill(user_name, timeout=timeout)
        self.passWord.clear()
        self.passWord.fill(pass_word, timeout=timeout)

        # 2) Click login
        self.signBtn.click(timeout=timeout)
        # self.page.reload()
        
        # 3) If branch code given, then select branch code
        if branch_code != "0":
            self.wait_to_load_element(self.officeDropdown)            
            self.officeDropdown.click()
            self.page.get_by_text(branch_code).click()            
            self.click_on_btn(self.goBtn) # type: ignore

        # # After selecting branch code, we expected an overlay should be seen
        # # But this overlay is not available in all Test Environments or have
        # # different loading time in different network speed or environment
        # # therefore, a reload is being introduced, just to bypass it........

        # # 6) Reload the page
        self.page.wait_for_timeout(2000)
        self.page.reload()
        self.page.wait_for_timeout(2000)


    def perform_logout(self):
        self.wait_to_load_element(self.exit_button)
        self.exit_button.click()
        self.wait_to_load_element(self.logout_button)
        self.logout_button.click()
        

    def navigate_to_page(self, main_nav_val, sub_nav_val):
        # Navigate via Main Nav
        if main_nav_val != '':
            self.main_nav.get_by_text(main_nav_val).click()
            self.wait_for_timeout(5000)

        '''Sub menu level is 2, then we go from parent to first child'''
        try:
            # Navigate to Parent Sub Menu
            parent_item = self.page.locator(
                f'xpath=//li[@class="menu-parent"]/div[contains(text(),"{sub_nav_val[0]}")]')
            self.wait_to_load_element(parent_item)
            parent_item.click()
            if len(sub_nav_val) == 3:
                sub_item_1 = self.page.locator(
                    #f'xpath=//li[@class="sub_arrow"]//child::div/span[text()="{sub_nav_val[1]}"]').first
                    f'xpath=//li[@class="sub_arrow"]//child::div/span[contains(text(),"{sub_nav_val[1]}")]').first
                sub_item_2 = self.page.get_by_role("link", name=sub_nav_val[2],exact=True)                
                self.wait_to_load_element(sub_item_1)
                sub_item_1.hover()
                self.wait_to_load_element(sub_item_2)
                sub_item_2.click()
            elif len(sub_nav_val) == 2:
                sub_item_1 = self.page.get_by_role("link", name=sub_nav_val[1])
                self.wait_to_load_element(sub_item_1)
                sub_item_1.click()
            else:
                print(f"Please check your sec_menu list and update it properly!")

            self.wait_for_timeout(2000)
            # self.get_full_page_screenshot(f"{main_nav_val} Navigation Success")
            print(f"{main_nav_val} Navigation Success!!")
        except Exception as e:
            print(f"Missing {e}")


    def extract_integer_value(self, text):
        num = re.findall(r'\d+', text)[0]
        return int(num)

    def wait_to_load_element(self, elem):
        elem.wait_for(state='visible')

    def wait_for_timeout(self, timeout):
        self.page.wait_for_timeout(timeout)

    def get_screen_shot(self, name):
        self.page.screenshot(path=os.getcwd() + "/screenshots/" + name + ".png")

    def get_full_page_screenshot(self, name):
        self.page.screenshot(path=os.getcwd() + "/screenshots_taken/" + name + ".png", full_page=True)

    def navigate_to_url(self, given_url):
        self.page.goto(given_url)#, wait_until="networkidle")

    def verify_by_title(self, title):
        expect(self.page).to_have_title(title)

    def press_button(self, btnName):
        self.page.keyboard.press(btnName)

    # datePicker = 'xpath=//*[@id="ui-datepicker-div"]'
    def date_select_from_datepicker(self, date, datePicker):
        day = int(date.split("-")[0])
        month = int(date.split("-")[1])
        year = date.split("-")[2]

        self.page.locator(datePicker).click()
        # setting the month
        self.page.select_option('.ui-datepicker-month', value=str(month - 1))
        # setting the year
        self.page.select_option('.ui-datepicker-year', value=year)
        # setting the day
        day_locator = f'//*[@id="ui-datepicker-div"]//child::a[text()="{day}"]'
        self.page.locator(day_locator).click()


    def random_working_day_info(self, start_date: str) -> tuple[str, str, str]:
        """
        Takes a date in DD-MM-YYYY format and returns a random working date (Sunday–Thursday)
        within the next 20 days, not exceeding the 28th of the month,
        along with the day name and human-readable week number of that month.

        Returns:
            (date_str, day_name, week_number_str)
        """
        DATE_FMT = "%d-%m-%Y"
        WORKING_WEEKDAYS = {0, 1, 2, 3, 6}  # Mon(0), Tue(1), Wed(2), Thu(3), Sun(6)

        def week_of_month_sunday_start(d: datetime.date) -> int: # type: ignore
            """Calculate week of month, Sunday as week start."""
            to_sun0 = lambda wk: (wk + 1) % 7  # Mon=0..Sun=6 -> Sun=0..Sat=6
            first = d.replace(day=1)
            offset = to_sun0(first.weekday())
            day_index = d.day + offset - 1
            return day_index // 7 + 1

        def ordinal(n: int) -> str:
            """Convert integer to ordinal string (1 -> '1st')."""
            return f"{n}{'tsnrhtdd'[(n//10%10!=1)*(n%10<4)*n%10::4]}"

        base_date = datetime.strptime(start_date, DATE_FMT).date()

        # Collect valid working days in next 20 days, but not past 28th
        candidates = []
        for i in range(1, 21):
            cand = base_date + timedelta(days=i)
            if cand.day <= 28 and cand.weekday() in WORKING_WEEKDAYS:
                candidates.append(cand)

        if not candidates:
            raise ValueError("No working days found in the next 20 days (<=28th).")

        chosen = random.choice(candidates)
        week_num = week_of_month_sunday_start(chosen)
        print(f"Chosen Week: {ordinal(week_num)}")
        wk =self.extract_integer_value(f"{ordinal(week_num)}")

        return (
            chosen.strftime(DATE_FMT),     # Date in DD-MM-YYYY
            chosen.strftime("%A"),         # Day name
            str(wk) #f"{ordinal(week_num)}"    # Human-readable week number
        )

   

    def select_from_options(self, elem, option):
        self.page.select_option(elem, value=option)


    def select_from_options_label(self, elem, label):
        self.page.select_option(elem, label=label)


    def extract_toast_message_content(self, elem):
        #elem = self.page.locator('//div[@id="jGrowl"]//child::div[@class="message"]')
        return elem.inner_text()
    

    def select_from_dropdown_selector(self, elem, text):
        elem.fill(text)
        self.page.keyboard.press(" ")
        self.page.get_by_text(text, exact=True).click()
        self.wait_for_timeout(2000)


    def select_from_options_index(self, elem, index):
        if hasattr(elem, "select_option"):
            elem.wait_for(state="visible")
            elem.select_option(index=index)
        else:
            self.page.select_option(elem, index=index)


    def double_click(self, element):
        """Perform double click on an element"""
        element.click()
        element.click()

    
    def read_excel_file(self, file_path='./feature_excel/feature_map.xlsx'):
        """
        Check if file exists and return dataframe dictionary
        """
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            return None
        
        """
        Reads an Excel file and returns its content as a pandas DataFrame.
        """
        try:
            all_dfs = pd.read_excel(file_path, sheet_name=None)
            return all_dfs
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None


    # def query_data(self, db_server, query):
        
        
