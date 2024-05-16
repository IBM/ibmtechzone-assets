package web_saucedemo.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import web_saucedemo.contexts.CheckoutYourInfoData;

public class CheckoutPage extends BasePage {

    By txtFName = By.id("first-name");
    By txtLName = By.id("last-name");
    By txtZip = By.id("postal-code");
    By btnContinue = By.id("continue");
    By btnFinish = By.id("finish");

    protected CheckoutPage(WebDriver driver) {
        super(driver);
    }

    public boolean isCheckoutComplete() {
        return driver.findElement(By.id("checkout_complete_container")).isDisplayed();
    }

    public CheckoutPage setInformation(CheckoutYourInfoData data) {
        driver.findElement(txtFName).sendKeys(data.getFirstName());
        driver.findElement(txtLName).sendKeys(data.getLastName());
        driver.findElement(txtZip).sendKeys(data.getZip());
        driver.findElement(btnContinue).click();
        return this;
    }

    public CheckoutPage finish() {
        driver.findElement(btnFinish).click();
        return this;
    }
}
