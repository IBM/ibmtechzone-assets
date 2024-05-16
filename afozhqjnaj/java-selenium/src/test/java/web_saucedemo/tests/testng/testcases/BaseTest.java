package web_saucedemo.tests.testng.testcases;

import automation.enums.Browsers;
import automation.selenium.BrowserFactory;
import org.openqa.selenium.WebDriver;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import web_saucedemo.config.EnvironmentVariables;

import java.time.Duration;

public abstract class BaseTest {

    // TODO: Externalise config data
    protected WebDriver driver;
    private Browsers browser = Browsers.CHROME;
    private String url = "https://www.saucedemo.com/";

    @BeforeMethod
    public void setup() {
        driver = BrowserFactory.launch(browser);
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(EnvironmentVariables.WAIT_IMPLICIT));
        driver.manage().window().maximize();
        driver.get(url);
    }

    @AfterMethod
    public void tearDown() {
        driver.quit();
    }
}