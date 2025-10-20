// README
//
// Navigate to the WSO2 API Manager Publisher and manually create one sample API 
// with a random name that does not match any of the APIs being created by this script.
//
// Once the sample API is created, go to /publisher/apis and execute the following 
// script in the browser console to automatically create and publish multiple APIs.

(async () => {
  // ======= CONFIG =======
  const count = 100;             // total number of APIs to create
  const namePrefix = "hey";      // prefix for API name
  const startNumber = 1;         // starting number
  const endpoint = "http://localhost:3000"; // endpoint to use
  // =======================

  const wait = (ms) => new Promise(res => setTimeout(res, ms));

  for (let i = 0; i < count; i++) {
    const apiNumber = startNumber + i;
    const apiName = `${namePrefix}${apiNumber}`;
    console.log(`🚀 [${i + 1}/${count}] Creating API: ${apiName}`);

    // Step 1: Click "Create API ▼"
    document.querySelector('#itest-create-api-menu-button')?.click();
    console.log("➡️ Clicked 'Create API ▼'");
    await wait(2000);

    // Step 2: Click "Start From Scratch"
    document.querySelector('#itest-id-landing-rest-create-default')?.click();
    console.log("➡️ Clicked 'Start From Scratch'");
    await wait(2000);

    // Step 3: Fill API Name
    const nameInput = document.querySelector('#itest-id-apiname-input');
    if (nameInput) {
      nameInput.value = apiName;
      nameInput.dispatchEvent(new Event('input', { bubbles: true }));
      console.log(`✏️ Set API name: ${apiName}`);
    } else {
      console.warn("⚠️ Name input not found!");
    }

    // Step 4: Fill Context
    const contextInput = document.querySelector('#itest-id-apicontext-input');
    if (contextInput) {
      contextInput.value = `/${apiName}`;
      contextInput.dispatchEvent(new Event('input', { bubbles: true }));
      console.log(`✏️ Set context: /${apiName}`);
    } else {
      console.warn("⚠️ Context input not found!");
    }

    // Step 5: Fill Version
    const versionInput = document.querySelector('#itest-id-apiversion-input');
    if (versionInput) {
      versionInput.value = "1";
      versionInput.dispatchEvent(new Event('input', { bubbles: true }));
      console.log("✏️ Set version: 1");
    } else {
      console.warn("⚠️ Version input not found!");
    }

    // Step 6: Fill Endpoint
    const endpointInput = document.querySelector('#itest-id-apiendpoint-input');
    if (endpointInput) {
      endpointInput.value = endpoint;
      endpointInput.dispatchEvent(new Event('input', { bubbles: true }));
      console.log(`✏️ Set endpoint: ${endpoint}`);
    } else {
      console.warn("⚠️ Endpoint input not found!");
    }

    // Step 7: Click "Create & Publish"
    const publishButton = [...document.querySelectorAll('span')]
      .find(span => span.textContent.includes('Create & Publish'));
    publishButton?.click();
    console.log("🖱️ Clicked 'Create & Publish'");
    await wait(5000);

    // Step 8: Click logo to return home
    document.querySelector('img[alt="[Publisher] - WSO2 APIM"]')?.click();
    console.log("🏠 Clicked logo to return home");
    await wait(2000);

    console.log(`✅ Done creating ${apiName}\n`);
  }

  console.log("🎉 All APIs created successfully!");
})();
