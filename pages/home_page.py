from urllib.parse import urlparse

from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
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
        self.assert_condition(
            lambda _: self._try_open_consumer_loan(),
            'Consumer loan menu link remained hidden or covered after reopening the menu.')
        self.wait.until(lambda d: urlparse(d.current_url).path.rstrip('/') == '/ge/samomkhmareblo-seskhi')
        page = ConsumerLoanPage(self.driver, self.timeout)
        page.assert_loaded()
        return page

    def _try_open_consumer_loan(self):
        """Reopen the entire hover chain when animation or a banner intercepts it."""
        try:
            menus = self.visible_elements(self.PERSONAL_MENU)
            if not menus:
                return False
            ActionChains(self.driver).move_to_element(menus[0]).perform()
            loans = self.visible_elements(self.PERSONAL_LOANS)
            if not loans:
                return False
            ActionChains(self.driver).move_to_element(loans[0]).perform()
            links = self.visible_elements(self.CONSUMER_LOAN)
            for link in links:
                # Do not scroll a hover menu: scrolling can close it.
                ActionChains(self.driver).move_to_element(link).perform()
                uncovered = self.driver.execute_script("""
                    const e=arguments[0], r=e.getBoundingClientRect();
                    const top=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
                    return r.width > 0 && r.height > 0 && top && (top===e || e.contains(top));
                """, link)
                if uncovered and link.is_displayed() and link.is_enabled():
                    link.click()
                    return True
            return False
        except (ElementClickInterceptedException, StaleElementReferenceException):
            return False
