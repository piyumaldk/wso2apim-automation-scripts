// README
//
// Navigate to the WSO2 API Manager Publisher and manually create one sample API 
// with a random name that does not match any of the APIs being created by this script.
// Deploying the sample API is fine.
//
// Once the sample API is created, go to /publisher/apis and execute the following 
// script in the browser console to automatically create and publish multiple APIs.

// ==================== Configuration Variables ====================
const namePrefix = 'hey';
const startNumber = 2;
const count = 100;
// ================================================================

// Helper function to wait for specified milliseconds
const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Helper function to trigger all React events properly
const setReactValue = (element, value) => {
    // Get the native setter
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype,
        'value'
    ).set;
    nativeInputValueSetter.call(element, value);
    
    // Trigger all possible React events
    const events = [
        new Event('input', { bubbles: true }),
        new Event('change', { bubbles: true }),
        new Event('blur', { bubbles: true }),
        new KeyboardEvent('keydown', { bubbles: true, key: 'Enter' }),
        new KeyboardEvent('keyup', { bubbles: true, key: 'Enter' })
    ];
    
    events.forEach(event => element.dispatchEvent(event));
};

// Helper function to click an element
const clickElement = (element) => {
    if (element) {
        element.focus();
        element.click();
        return true;
    }
    return false;
};

// Helper function to wait for button to be enabled
const waitForButtonEnabled = async (buttonId, maxWaitTime = 10000) => {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWaitTime) {
        const button = document.getElementById(buttonId);
        if (button && !button.disabled) {
            return button;
        }
        await wait(100); // Check every 100ms
    }
    
    throw new Error(`Button ${buttonId} did not become enabled within ${maxWaitTime}ms`);
};

// Helper function to wait for element to appear
const waitForElement = async (selector, isId = false, maxWaitTime = 10000) => {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWaitTime) {
        const element = isId ? document.getElementById(selector) : document.querySelector(selector);
        if (element) {
            return element;
        }
        await wait(100); // Check every 100ms
    }
    
    throw new Error(`Element ${selector} not found within ${maxWaitTime}ms`);
};

// Main automation function for creating a single API
const createAPI = async (apiName) => {
    try {
        // Step 1: Click "Create API" button
        const createButton = await waitForElement('itest-create-api-menu-button', true);
        clickElement(createButton);
        await wait(2000);

        // Step 2: Click "Start From Scratch"
        const startFromScratchLink = await waitForElement('itest-id-landing-rest-create-default', true);
        clickElement(startFromScratchLink);
        await wait(2000);

        // Step 3: Fill in the form with delays between fields
        // Fill API Name
        const nameInput = await waitForElement('itest-id-apiname-input', true);
        nameInput.focus();
        await wait(100);
        setReactValue(nameInput, apiName);
        await wait(500); // Give React time to validate

        // Fill Context (same as name)
        const contextInput = await waitForElement('itest-id-apicontext-input', true);
        contextInput.focus();
        await wait(100);
        setReactValue(contextInput, apiName);
        await wait(500); // Give React time to validate

        // Fill Version
        const versionInput = await waitForElement('itest-id-apiversion-input', true);
        versionInput.focus();
        await wait(100);
        setReactValue(versionInput, '1');
        await wait(500); // Give React time to validate

        // Fill Endpoint
        const endpointInput = await waitForElement('itest-id-apiendpoint-input', true);
        endpointInput.focus();
        await wait(100);
        setReactValue(endpointInput, 'http://localhost:3000');
        await wait(500); // Give React time to validate

        // Step 4: Wait for "Create & Publish" button to be enabled
        const createPublishButton = await waitForButtonEnabled('itest-id-apicreatedefault-createnpublish', 15000);
        
        // Extra wait to ensure form is fully validated
        await wait(500);
        
        // Click the button
        clickElement(createPublishButton);
        await wait(5000);

        // Step 5: Click logo to go back to home
        const logoImg = await waitForElement('img[src="/publisher/site/public/images/logo.svg"]');
        clickElement(logoImg);
        await wait(2000);

        return true;
    } catch (error) {
        console.error(`Error creating API ${apiName}:`, error.message);
        return false;
    }
};

// Main execution function
const executeAutomation = async () => {
    console.log('='.repeat(50));
    console.log('API Creation Automation Started');
    console.log(`Name Prefix: ${namePrefix}`);
    console.log(`Start Number: ${startNumber}`);
    console.log(`Total Count: ${count}`);
    console.log('='.repeat(50));

    let successCount = 0;
    let failCount = 0;
    const startTime = Date.now();

    for (let i = 0; i < count; i++) {
        const currentNumber = startNumber + i;
        const apiName = `${namePrefix}${currentNumber}`;
        
        const iterationStartTime = Date.now();
        console.log(`${i + 1}/${count}`);

        const result = await createAPI(apiName);
        
        const iterationTime = ((Date.now() - iterationStartTime) / 1000).toFixed(2);
        
        if (result) {
            successCount++;
        } else {
            failCount++;
            console.warn(`⚠️ Failed: ${apiName}`);
        }
    }

    const totalTime = ((Date.now() - startTime) / 1000 / 60).toFixed(2);

    console.log('='.repeat(50));
    console.log('✅ Automation Completed!');
    console.log(`Total APIs: ${count}`);
    console.log(`Successful: ${successCount}`);
    console.log(`Failed: ${failCount}`);
    console.log(`Total Time: ${totalTime} minutes`);
    console.log('='.repeat(50));
};

// Start the automation
executeAutomation().catch(error => {
    console.error('❌ Fatal error during automation:', error);
});