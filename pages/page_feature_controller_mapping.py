from playwright.sync_api import sync_playwright, expect
from basic_actions import BasicActions

class feature_controller_mapping_page(BasicActions):
    def __init__(self, page):
        super().__init__(page)
        self.page = page
        # Elements to interact
        self.loc_module_list = page.locator('#moduleList')
        self.loc_feature_list = page.locator('#featureList')
        self.loc_action_list = page.locator('#actionList')

        self.loc_add_controller_btn = page.locator('//input[@type="button" and @value="Add Controller"]')
        self.loc_save_controller_btn = page.locator('//input[@type="button" and @value="Save"]')

        self.loc_controller_list = lambda i: page.locator(f'#controllerList-{i}')
        self.loc_controller_search_box = lambda i: page.locator(f'//select[@id="controller-list[{i}]"]/following-sibling::div/descendant::input')
        self.loc_controller_item_add_btns = lambda i: page.locator(f'//select[@id="controller-list[{i}]"]/following-sibling::div/descendant::ul[@class="available connected-list"]/li[@style="display: list-item;"]/a')


    def set_module_feature_action_controller(self, module, feature, action, controller, ctrl_item):
        # Setting Module, Feature and Action
        self.loc_module_list.select_option(label=module)
        self.wait_for_timeout(500)
        self.loc_feature_list.select_option(label=feature)
        self.wait_for_timeout(500)
        self.loc_action_list.select_option(label=action)
        self.wait_for_timeout(500)
        flag = False

        # Check if the give controller mapping already exists
        all_controllers = self.page.locator('//div[text()="Controller"]')
        count = all_controllers.count()
        if count == 0:            
            # Click on Add Controller button
            self.loc_add_controller_btn.click()
            self.wait_for_timeout(500)
            # Set Controller value
            self.loc_controller_list(0).select_option(label=controller)
            self.wait_for_timeout(500)
            self.search_and_add_controllers(controller_item=ctrl_item, index=0)
            flag = True
        else:            
            for i in range(count):
                elem_text = self.page.locator(f'//select[@id="controllerList-{i}"]').inner_text()
                if elem_text == controller:
                    # Controller mapping already exists
                    self.search_and_add_controllers(controller_item=ctrl_item, index=i)
                    flag = True
                    break        
            if not flag:
                # Click on Add Controller button
                self.loc_add_controller_btn.click()
                self.wait_for_timeout(500)
                # Set Controller value
                self.loc_controller_list(count).select_option(label=controller)
                self.wait_for_timeout(500)
                self.search_and_add_controllers(controller_item=ctrl_item, index=count)
                flag = True

    def search_and_add_controllers(self, controller_item, index):
        # Input controller item to search box
        self.loc_controller_search_box(index).fill(controller_item)
        self.wait_for_timeout(500)
        self.page.keyboard.press('Enter')
        self.wait_for_timeout(500)
        count = self.loc_controller_item_add_btns(index).count()
        for _ in range(count):
            # Add all controllers one-by-one
            self.loc_controller_item_add_btns(index).locator("nth=0").click()
            self.wait_for_timeout(500)
        # Save the map
        self.loc_save_controller_btn.click()
        self.wait_for_timeout(500)


    def perform_action(self, data):
        self.set_module_feature_action_controller(module=data['Module'],feature=data['Feature'],action=data['Action'],controller=data['Parent Controller'],ctrl_item=data['Controllers'])
        # self.search_and_add_controllers(controller_item=data['ctrl_item'])