from selenium import webdriver
import unittest
import HtmlTestRunner
from time import sleep

url = 'https://siya-diabetes-prediction.herokuapp.com'
#url = 'http://127.0.0.1:5000/'

class Prediction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Safari()
        cls.driver.implicitly_wait(10)
        cls.driver.maximize_window()

    def test_search_1(self):
        self.driver.get(url)
        sleep(4)
        self.driver.find_element_by_name("Glucose Level").send_keys('148')
        self.driver.find_element_by_name("Insulin").send_keys('0')
        self.driver.find_element_by_name("BMI").send_keys('33.6')
        self.driver.find_element_by_name("Age").send_keys('50')
        sleep(4)
        self.driver.find_element_by_id("a").click()
        sleep(6)

    def test_search_2(self):
        self.driver.get(url)
        self.driver.find_element_by_name("Glucose Level").send_keys('85')
        self.driver.find_element_by_name("Insulin").send_keys('0')
        self.driver.find_element_by_name("BMI").send_keys('26.6')
        self.driver.find_element_by_name("Age").send_keys('31')
        sleep(4)
        self.driver.find_element_by_id("b").click()
        sleep(6)

    def test_search_3(self):
        self.driver.get(url)
        self.driver.find_element_by_name("Glucose Level").send_keys('137')
        self.driver.find_element_by_name("Insulin").send_keys('168')
        self.driver.find_element_by_name("BMI").send_keys('43.1')
        self.driver.find_element_by_name("Age").send_keys('33')
        sleep(4)
        self.driver.find_element_by_id("a").click()
        sleep(4)

    # def test_search_4(self):
    #     self.driver.get(url)
    #     self.driver.find_element_by_name("Glucose Level").send_keys('93')
    #     self.driver.find_element_by_name("Insulin").send_keys('0')
    #     self.driver.find_element_by_name("BMI").send_keys('30.4')
    #     self.driver.find_element_by_name("Age").send_keys('23')
    #     sleep(4)
    #     self.driver.find_element_by_id("a").click()
    #     sleep(4)

    # def test_search_5(self):
    #     self.driver.get(url)
    #     self.driver.find_element_by_name("Glucose Level").send_keys('121')
    #     self.driver.find_element_by_name("Insulin").send_keys('112')
    #     self.driver.find_element_by_name("BMI").send_keys('26.2')
    #     self.driver.find_element_by_name("Age").send_keys('30')
    #     sleep(4)
    #     self.driver.find_element_by_id("b").click()
    #     sleep(4)

    # def test_search_6(self):
    #     self.driver.get(url)
    #     self.driver.find_element_by_name("Glucose Level").send_keys('71')
    #     self.driver.find_element_by_name("Insulin").send_keys('0')
    #     self.driver.find_element_by_name("BMI").send_keys('28')
    #     self.driver.find_element_by_name("Age").send_keys('22')
    #     sleep(4)
    #     self.driver.find_element_by_id("a").click()
    #     sleep(4)

    # def test_search_7(self):
    #     self.driver.get(url)
    #     self.driver.find_element_by_name("Glucose Level").send_keys('103')
    #     self.driver.find_element_by_name("Insulin").send_keys('0')
    #     self.driver.find_element_by_name("BMI").send_keys('39.1')
    #     self.driver.find_element_by_name("Age").send_keys('31')
    #     sleep(4)
    #     self.driver.find_element_by_id("b").click()
    #     sleep(4)

    # def test_search_8(self):
    #     self.driver.get(url)
    #     self.driver.find_element_by_name("Glucose Level").send_keys('197')
    #     self.driver.find_element_by_name("Insulin").send_keys('543')
    #     self.driver.find_element_by_name("BMI").send_keys('30.5')
    #     self.driver.find_element_by_name("Age").send_keys('53')
    #     sleep(4)
    #     self.driver.find_element_by_id("b").click()
    #     sleep(4)

    # def test_search_9(self):
    #     self.driver.get(url)
    #     self.driver.find_element_by_name("Glucose Level").send_keys('189')
    #     self.driver.find_element_by_name("Insulin").send_keys('846')
    #     self.driver.find_element_by_name("BMI").send_keys('30.1')
    #     self.driver.find_element_by_name("Age").send_keys('59')
    #     sleep(4)
    #     self.driver.find_element_by_id("a").click()
    #     sleep(4)        
        
    @classmethod
    def tearDownClass(cls):
        cls.driver.close()


if __name__ == '__main__':
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='reports'))