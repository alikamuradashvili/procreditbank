from urllib.parse import urlparse

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from pages.consumer_loan_page import ConsumerLoanPage


class HomePage(BasePage):
    CONSUMER_LOAN = (By.CSS_SELECTOR, 'a[href*="/ge/samomkhmareblo-seskhi"]')
    PERSONAL_MENU = (By.CSS_SELECTOR, 'li.level-0 > a[href="/ge?mid=1078"]')
    PERSONAL_LOANS = (By.CSS_SELECTOR, 'li.level-1 > a[href="/ge/sesxi?mid=1568"]')

    def open(self, url):
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        if 'Request Rejected' in self.driver.title:
            raise AssertionError('Bank firewall rejected the homepage; navigation cannot be verified.')
        expected = urlparse(url)
        self.assert_route(expected.hostname, expected.path)
        self.visible(self.PERSONAL_MENU)
        return self

    def open_consumer_loan(self):
        # Desktop menus reveal submenus on hover. The bank uses mid=1571 here;
        # list=3589 is another valid context for the same product path.
        ActionChains(self.driver).move_to_element(self.visible(self.PERSONAL_MENU)).perform()
        # Hover must finish before moving into the nested loans column.
        loans = self.wait.until(lambda _: self.visible_elements(self.PERSONAL_LOANS))[0]
        assert loans.is_displayed(), 'Personal loans submenu did not open.'
        ActionChains(self.driver).move_to_element(loans).perform()
        link = self.wait.until(lambda _: next(iter(self.visible_elements(self.CONSUMER_LOAN)), False))
        assert link.is_displayed(), 'Consumer loan product link is not visible.'
        link.click()
        self.wait.until(lambda d: urlparse(d.current_url).path.rstrip('/') == '/ge/samomkhmareblo-seskhi')
        page = ConsumerLoanPage(self.driver, self.timeout)
        page.assert_loaded()
        return page
