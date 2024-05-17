package web_saucedemo.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

public class LoginPage extends BasePage {

    private static final String ERR_LOCKED_OUT = "Epic sadface: Sorry, this user has been locked out.";

    By txtUsername = By.id("user-name");
    By txtPassword = By.id("password");
    By btnLogin = By.id("login-button");
    By lblErrMsg = By.xpath("//div[contains(@class,'error-message-container')]/h3");

    public LoginPage(WebDriver driver) {
        super(driver);
    }

    public boolean isAt() {
        return driver.findElement(txtUsername).isDisplayed();
    }

    public boolean isUserLockedOut() {
        String error = driver.findElement(lblErrMsg).getText();
        if(error.equals(ERR_LOCKED_OUT)) {
            return true;
        }
        return false;
    }

    public void login(String username, String password) {
        driver.findElement(txtUsername).sendKeys(username);
        driver.findElement(txtPassword).sendKeys(password);
        driver.findElement(btnLogin).click();
    }
}
