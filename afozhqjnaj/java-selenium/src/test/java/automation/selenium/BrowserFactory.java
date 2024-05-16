package automation.selenium;

import automation.enums.Browsers;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;

public class BrowserFactory {

    public static WebDriver launch(Browsers browser) {
        if (browser.equals(Browsers.CHROME)) {
            return new ChromeDriver();
        } else if (browser.equals(Browsers.FIREFOX)) {
            return new FirefoxDriver();
        } else if (browser.equals(Browsers.EDGE)) {
            return new EdgeDriver();
        }

        // default
        return new ChromeDriver();
    }
}
