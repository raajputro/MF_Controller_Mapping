from playwright.sync_api import sync_playwright, expect
from basic_actions import BasicActions


class utility_page(BasicActions):
    def __init__(self, page, base_url):
        super().__init__(page)
        page = self.page
        self.base = base_url

    def perform_utility_action(self):
        # click on resolve from requestmap resolve
        url_ext = '/myDashboard#!/requestmap/resolve'
        task_url = self.base + url_ext
        self.page.goto(task_url)
        self.wait_for_timeout(5000)
        for _ in range(3):
             self.page.locator('//input[@type="button" and @value="Resolve"]').click()
             self.wait_for_timeout(2000)
        self.wait_for_timeout(5000)
        # navigate to microfinance>programme admin>MF Cache update>MF Cache Update
        # click on update button
        url_ext = '/node/mfDashboard#!/mfCacheManager/index'
        task_url = self.base + url_ext
        self.page.goto(task_url)
        self.wait_for_timeout(5000)
        self.page.locator('//input[@type="button" and @value="Update"]').click()        
        self.wait_for_timeout(5000)
        # navigate to settings>menu>update application cache>
        # click on update button
        url_ext = '/myDashboard#!/applicationCacheManager/updateCache'
        task_url = self.base + url_ext
        self.page.goto(task_url)
        self.wait_for_timeout(5000)
        self.page.locator('//input[@type="button" and @value="Update"]').click()        
        self.wait_for_timeout(5000)