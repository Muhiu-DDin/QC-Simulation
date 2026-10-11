# ForeverMart Software Quality Assurance Report

Software Testing Portfolio Part 3 | 9 October 2026 | Version 1.0

70 supported defects and 20 separately labelled improvement observations. The requested target of 100 defects was not established. No fixes are claimed.

Reference: William E. Lewis, Software Testing and Continuous Quality Improvement, second edition, Auerbach / CRC Press, 2005. Detailed records adapt E12 and E27.

## Scope

Public storefront, browser/DOM checks, public client-code review and own disposable-account API tests. Eight authorised COD orders; no real payment. Admin functions, other-user data, load tests and card settlement were excluded.

## FM-001 Shop Now does not open the catalogue

**Defect | Medium | P2 | Open**

Module: Home  
Test: TC-001  
Location: https://forevermart.vercel.app/  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open the home page.
2. Click SHOP NOW in the hero.

**Expected:** The call to action opens the collection or another defined shopping destination.

**Actual:** The URL and page remain unchanged; SHOP NOW is rendered as a paragraph without an action.

**Impact:** The primary shopping invitation cannot be used.

**Recommended remedy:** Render a real link to /collection with a visible focus state.

**Retest acceptance:** Mouse click and Enter on the focused link both open Collection.

**Evidence:** evidence/shop-now-no-action.json, evidence/shop-now-no-action.jpg, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-002 Best Seller section has no products despite flagged catalogue items

**Defect | Medium | P2 | Open**

Module: Home  
Test: TC-002  
Location: https://forevermart.vercel.app/  
Method: Browser test and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Allow the catalogue to finish loading.
2. Inspect BEST SELLER and compare the public product flags.

**Expected:** Products marked bestSeller are displayed in the section.

**Actual:** The section is empty although five catalogue records have bestSeller=true. The public bundle filters the different key bestseller.

**Impact:** Merchandising content disappears and an empty section occupies the home page.

**Recommended remedy:** Use the product contract key bestSeller and map productName consistently. Add a populated-fixture component check.

**Retest acceptance:** The five flagged records render with names and prices; an empty source has a deliberate empty state.

**Evidence:** evidence/home-desktop.jpg, raw/products.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-003 Latest Collection is not ordered by creation date

**Observation | Low | P3 | Review required**

Module: Home  
Test: TC-003  
Location: https://forevermart.vercel.app/  
Method: Public data and code review  
Proposed owner: Content owner (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect the ten Latest Collection items.
2. Compare their createdAt values with the full public catalogue.

**Expected:** A section labelled Latest Collection presents the newest products first, or explains its curation.

**Actual:** The list takes the first ten API records. An October 14 record leads the list while newer October 22 records are available.

**Impact:** The section title does not describe its actual selection.

**Recommended remedy:** Sort a copy of products by createdAt descending before taking ten, or rename the section Featured Collection.

**Retest acceptance:** A fixture containing older and newer products displays the declared ordering.

**Evidence:** raw/products.json, raw/app.js, evidence/home-desktop.jpg

Audit note: Latest is an inferred merchandising criterion; confirm with the owner.

Developer/client comments: not supplied. Close date: not closed.

## FM-004 Reviews tab does not display reviews

**Defect | Medium | P2 | Open**

Module: Product  
Test: TC-004  
Location: https://forevermart.vercel.app/product/68ee7c73675d613eba9e96c6  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open the product and allow its data to load.
2. Click Reviews (122).

**Expected:** The selected tab displays the reviews or an honest unavailable state.

**Actual:** The displayed content does not change; the tab is a paragraph without a click handler.

**Impact:** Customers cannot inspect the reviews advertised by the page.

**Recommended remedy:** Implement accessible tabs backed by review data, or remove the inactive review tab and count.

**Retest acceptance:** Selecting Reviews changes the panel; keyboard selection works and the empty state is truthful.

**Evidence:** evidence/reviews-no-change.jpg, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-005 Product rating and review count are hard coded

**Defect | Medium | P2 | Open**

Module: Product  
Test: TC-005  
Location: https://forevermart.vercel.app/product/68ee7c73675d613eba9e96c6  
Method: Browser test and public code review  
Proposed owner: Content owner (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open the cotton T-shirt.
2. Open the Women Zip-Front Jacket and compare the rating area with the public data and bundle.

**Expected:** Rating and count derive from actual product reviews, or are clearly identified as sample content.

**Actual:** Both display the same stars and (122); these values are fixed in the public component and not derived from review data.

**Impact:** The storefront presents unsupported customer-feedback claims.

**Recommended remedy:** Aggregate approved reviews by product. Hide ratings when no verified review source exists; label demo fixtures explicitly.

**Retest acceptance:** Products with zero, one and several reviews show the correct counts and calculated ratings.

**Evidence:** evidence/product-details.json, evidence/second-product-loaded.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-006 Jacket description describes a short sleeved T-shirt

**Defect | Medium | P2 | Open**

Module: Product  
Test: TC-006  
Location: https://forevermart.vercel.app/product/68f38f15f780484273055b41  
Method: Browser test  
Proposed owner: Content owner (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open Women Zip-Front Relaxed Fit Jacket priced $399.
2. Read the short product description.

**Expected:** The description explains the jacket actually offered.

**Actual:** The jacket uses a generic round-neck, short-sleeved pullover shirt description. The same text is reused across different apparel types.

**Impact:** Customers receive incorrect information about the item.

**Recommended remedy:** Replace copied descriptions with product-specific material, fit, closure and care details; validate catalogue content before publishing.

**Retest acceptance:** Jackets, trousers and tops each have accurate descriptions matching their records and images.

**Evidence:** evidence/second-product-loaded.json, evidence/second-product-loaded.jpg, raw/products.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-007 Detailed Description panel explains ecommerce instead of the product

**Defect | Low | P3 | Open**

Module: Product  
Test: TC-007  
Location: https://forevermart.vercel.app/product/68ee7c73675d613eba9e96c6  
Method: Browser test  
Proposed owner: Content owner (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open the product.
2. Read the Description panel below the purchase controls.

**Expected:** The panel contains useful details about this product.

**Actual:** The text explains what an ecommerce website is rather than describing the selected apparel.

**Impact:** A prominent information panel gives customers no product details.

**Recommended remedy:** Populate the panel from a product detail field; remove template instructional copy.

**Retest acceptance:** Changing product changes the details and no ecommerce-definition template text remains.

**Evidence:** evidence/product-details.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-008 Product image and title describe different garment styles

**Defect | Medium | P2 | Open**

Module: Product  
Test: TC-008  
Location: https://forevermart.vercel.app/product/68ee7c73675d613eba9e96c6  
Method: Browser test  
Proposed owner: Content owner (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open Men Round Neck Pure Cotton T-shirt priced $200.
2. Compare the main photo with the title and description.

**Expected:** The images depict the named round-neck, short-sleeved T-shirt.

**Actual:** The main photo depicts a pink collared, long-sleeved shirt while the title and description describe a round-neck T-shirt.

**Impact:** The shopper cannot reliably determine which garment will be delivered.

**Recommended remedy:** Correct the product-to-image association or the product text after checking the intended inventory item.

**Retest acceptance:** All gallery images match the approved product identity and garment characteristics.

**Evidence:** evidence/product-details.jpg, evidence/product-details.json, raw/products.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-009 Related Products includes the product already being viewed

**Defect | Low | P3 | Open**

Module: Product  
Test: TC-009  
Location: https://forevermart.vercel.app/product/68ee7c73675d613eba9e96c6  
Method: Browser test and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open the $200 T-shirt.
2. Inspect Related Products.

**Expected:** Recommendations provide other relevant items.

**Actual:** The current product appears in its own related-product list; the filter does not exclude the current ID.

**Impact:** A recommendation slot is wasted on an item already open.

**Recommended remedy:** Exclude the current product ID before limiting related results.

**Retest acceptance:** No related result has the current ID, including after navigation between related items.

**Evidence:** evidence/product-details.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-010 Selected size carries over when navigating to a related product

**Defect | Medium | P2 | Open**

Module: Product  
Test: TC-010  
Location: https://forevermart.vercel.app/product/68ee7c73675d613eba9e96c6  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Choose size M on the $200 T-shirt.
2. Open a related product priced $280.
3. Inspect the size selection before choosing a size again.

**Expected:** The new product starts with no selection, or explicitly asks the customer to confirm its variant.

**Actual:** M remains selected on the new product even though it was selected for the previous item.

**Impact:** A shopper can add the next item using an unintended variant.

**Recommended remedy:** Reset variant and gallery state whenever productId changes; validate the selected size against the new product.

**Retest acceptance:** Navigate between products with different size lists; adding requires a valid selection for the new item.

**Evidence:** evidence/related-size-carryover.json, evidence/related-size-carryover.jpg

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-011 Unknown product leaves an incomplete purchase page

**Defect | Medium | P2 | Open**

Module: Product  
Test: TC-011  
Location: https://forevermart.vercel.app/product/000000000000000000000000  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open the stated non-existent product ID.
2. Allow the request to complete.

**Expected:** A Product not found state replaces purchase controls and offers a route back to the collection.

**Actual:** The page shows an empty title, a currency symbol without a price, hard-coded review content and ADD TO CART.

**Impact:** A broken URL looks like a purchasable item rather than a handled missing record.

**Recommended remedy:** Track loading, found, missing and failed states; render purchase controls only for a valid product.

**Retest acceptance:** Missing and malformed IDs have a clear recovery page; valid products still load normally.

**Evidence:** evidence/missing-product.json, evidence/missing-product.jpg

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-012 Search with no matches displays an unexplained empty grid

**Defect | Medium | P2 | Open**

Module: Collection  
Test: TC-012  
Location: https://forevermart.vercel.app/collection  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open search on Collection.
2. Enter zzqa-no-such-product.

**Expected:** A no-results message identifies the search and offers a clear or reset action.

**Actual:** No product cards appear and no no-results explanation is displayed.

**Impact:** Users cannot distinguish an empty result from a failed load.

**Recommended remedy:** Render a no-results state after loading completes, with a clear-search action.

**Retest acceptance:** An impossible query shows the message; clearing it restores products.

**Evidence:** evidence/search-no-results.json, evidence/search-no-results.jpg

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-013 Leading and trailing spaces prevent otherwise valid search matches

**Defect | Medium | P2 | Open**

Module: Collection  
Test: TC-013  
Location: https://forevermart.vercel.app/collection  
Method: Browser test and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Search for cotton.
2. Replace it with two leading spaces, cotton, and two trailing spaces.

**Expected:** Incidental outside whitespace does not change the meaningful query.

**Actual:** cotton finds 22 items, while the padded query finds none. The filter lowercases text but does not trim it.

**Impact:** Pasted or casually typed queries produce false empty results.

**Recommended remedy:** Normalize the search with trim and consistent case handling before filtering.

**Retest acceptance:** cotton, Cotton and padded cotton return the same matching IDs.

**Evidence:** evidence/search-spaces.json, evidence/search-spaces.jpg, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-014 Collection filters and sorting are lost after returning from a product

**Defect | Medium | P2 | Open**

Module: Collection  
Test: TC-014  
Location: https://forevermart.vercel.app/collection  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Select Men and Sort by Low to High.
2. Open a product.
3. Use browser Back.

**Expected:** The previous collection criteria are restored.

**Actual:** Men is unchecked and sorting returns to Relevant; all products are shown.

**Impact:** Customers must repeat their selection after every product inspection.

**Recommended remedy:** Store search, category and sort criteria in URL parameters or durable route state.

**Retest acceptance:** Back restores the same criteria and results, and a shared filtered URL opens the same view.

**Evidence:** evidence/collection-criteria.json, evidence/collection-after-back.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-015 Footer navigation labels cannot be opened

**Defect | Medium | P2 | Open**

Module: Shared layout  
Test: TC-015  
Location: https://forevermart.vercel.app/  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Go to the footer.
2. Attempt Home, About Us, Delivery and Privacy Policy.

**Expected:** Each advertised navigation destination is an operable link.

**Actual:** All four labels are static list items with no href or action.

**Impact:** Customers cannot reach the pages promised by the footer.

**Recommended remedy:** Create valid links and publish the intended delivery and privacy content. Grouped here because the same footer implementation affects all four labels.

**Retest acceptance:** All four destinations work with mouse and keyboard and have meaningful URLs.

**Evidence:** evidence/home-mobile.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-016 Forgot your password has no recovery action

**Defect | Medium | P2 | Open**

Module: Account  
Test: TC-016  
Location: https://forevermart.vercel.app/login  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open the account form.
2. Click Forgot your password?

**Expected:** A recovery flow or a clearly explained support alternative opens.

**Actual:** The page stays unchanged; the text has a pointer cursor but no handler.

**Impact:** A user who has forgotten a password has no advertised recovery path.

**Recommended remedy:** Implement a verified recovery process, or replace the inactive control with an accurate support instruction.

**Retest acceptance:** The control opens recovery; account existence is not disclosed by recovery responses.

**Evidence:** evidence/forgot-password-no-action.json, evidence/forgot-password-no-action.jpg, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-017 My Profile menu item has no destination

**Defect | Medium | P2 | Open**

Module: Account  
Test: TC-017  
Location: https://forevermart.vercel.app/  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Sign in with the disposable account.
2. Open the profile menu and click My Profile.

**Expected:** The profile page opens or the unavailable feature is not presented as an action.

**Actual:** No page or panel opens; My Profile is static text.

**Impact:** The account menu advertises a function users cannot use.

**Recommended remedy:** Link to an implemented profile page or remove the inactive menu item until available.

**Retest acceptance:** Selecting My Profile opens a working destination with the authenticated demo profile.

**Evidence:** evidence/profile-no-action.json, evidence/profile-no-action.jpg

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-018 Explore Jobs does not open career information

**Defect | Low | P3 | Open**

Module: Contact  
Test: TC-018  
Location: https://forevermart.vercel.app/contact  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open Contact.
2. Click Explore Jobs.

**Expected:** The button opens career details or a supported application destination.

**Actual:** The page and URL remain unchanged.

**Impact:** The careers call to action is nonfunctional.

**Recommended remedy:** Provide an actual careers link, or remove the button when no vacancies or careers page exist.

**Retest acceptance:** Mouse and keyboard activation open the declared destination.

**Evidence:** evidence/jobs-no-action.json, evidence/jobs-no-action.jpg, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-019 Newsletter subscription produces no result

**Defect | Medium | P2 | Open**

Module: Home  
Test: TC-019  
Location: https://forevermart.vercel.app/  
Method: Browser test and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Enter a syntactically valid synthetic email in Subscribe now.
2. Click SUBSCRIBE.

**Expected:** The form records the request and shows success or a useful error.

**Actual:** There is no feedback or subscription action. The handler only prevents the default form submission.

**Impact:** The advertised 20 percent offer has no usable subscription path.

**Recommended remedy:** Connect the form to the intended subscription service and show a result; remove the offer until its fulfilment works.

**Retest acceptance:** Valid, duplicate and invalid requests produce truthful, accessible feedback without unintended subscriptions.

**Evidence:** evidence/subscribe-no-feedback.json, evidence/subscribe-no-feedback.jpg, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-020 Product names are absent from cart and order rows

**Defect | Medium | P2 | Open**

Module: Cart  
Test: TC-020  
Location: https://forevermart.vercel.app/cart  
Method: Browser test and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Add the $200 T-shirt in size M.
2. Inspect its cart row, then the own demo order history.

**Expected:** Each row identifies the product by its stored productName.

**Actual:** Images, price and size appear but the product name is blank. These views read name while records contain productName.

**Impact:** Customers cannot clearly identify line items; the same data-contract mismatch affects both views.

**Recommended remedy:** Use one typed product contract and read productName in cart and order components.

**Retest acceptance:** Names appear for all line items in both cart and order history.

**Evidence:** evidence/cart-one-item.json, evidence/orders-validation-tests.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-021 Guest cart is overwritten after account creation

**Defect | High | P1 | Open**

Module: Cart  
Test: TC-021  
Location: https://forevermart.vercel.app/cart  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. As a guest, add one item.
2. Create the disposable account.
3. Inspect the cart after authentication.

**Expected:** The guest selection survives or is merged with the account cart.

**Actual:** The badge changes from one item to zero and the guest item disappears when the empty account cart is loaded.

**Impact:** A customer loses the prepared purchase at the authentication step.

**Recommended remedy:** Merge validated guest items with the account cart on authentication and reconcile the result before replacing local state.

**Retest acceptance:** Guest-only and existing-account carts merge without loss or duplicate quantities.

**Evidence:** evidence/cart-one-item.json, evidence/signup-outcome.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-022 An empty cart can be submitted as an order

**Defect | High | P1 | Open**

Module: Checkout  
Test: TC-022  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Use the authenticated demo account with an empty cart.
2. Proceed to checkout, complete the delivery form and submit cash on delivery.

**Expected:** Checkout is blocked when there are no valid line items; the server rejects an empty items array.

**Actual:** Order creation succeeds and the own-orders response contains an order with items=[] and amount=10.

**Impact:** Invalid transactions are stored and can enter fulfilment workflows. Empty orders are also invisible in the flattened history.

**Recommended remedy:** Enforce non-empty validated items on the server and block the empty-cart checkout path in the UI.

**Retest acceptance:** An empty order returns a validation error and creates no record; one valid item succeeds.

**Evidence:** evidence/cart-empty.json, evidence/empty-order-outcome.json, raw/demo-orders.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-023 Empty-cart total does not agree with displayed shipping

**Defect | Medium | P2 | Open**

Module: Cart  
Test: TC-023  
Location: https://forevermart.vercel.app/cart  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open an empty cart.
2. Compare Subtotal, Shipping Fee and Total.

**Expected:** Displayed amounts reconcile, and no charge applies to an order that cannot be placed.

**Actual:** Subtotal is $0.00 and shipping $10.00, but Total is $0.00. An empty submitted order instead stores $10.

**Impact:** The stated payable amount is internally inconsistent.

**Recommended remedy:** Use one totals function across display and submission; hide or zero shipping for an empty cart.

**Retest acceptance:** Empty and populated carts reconcile; submission and receipt equal the final displayed total.

**Evidence:** evidence/cart-empty.json, evidence/cart-empty.jpg, raw/demo-orders.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-024 Whitespace-only delivery information is accepted

**Defect | High | P1 | Open**

Module: Checkout  
Test: TC-024  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Enter three spaces in first name, last name, street, city, state and country; use a valid synthetic email.
2. Submit a demo COD order.

**Expected:** Required address strings remain non-empty after trimming and are rejected otherwise.

**Actual:** The order is accepted; the persisted address contains whitespace-only values.

**Impact:** The stored order has no deliverable recipient or address.

**Recommended remedy:** Trim and validate required strings on both client and server; show errors beside the fields.

**Retest acceptance:** Each whitespace-only required field rejects the order without persistence; a valid address succeeds.

**Evidence:** evidence/checkout-invalid-values.jpg, raw/demo-orders.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-025 Negative phone number is accepted at checkout

**Defect | High | P1 | Open**

Module: Checkout  
Test: TC-025  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Complete other delivery fields and enter -1 for Phone number.
2. Submit the authorized demo COD test order.

**Expected:** The contact field accepts a valid telephone string and rejects an impossible negative number.

**Actual:** The server stores phoneNumber="-1".

**Impact:** The fulfilment team has no usable delivery contact.

**Recommended remedy:** Use type=tel and server-side phone validation appropriate to the supported countries; do not treat phone numbers as arithmetic quantities.

**Retest acceptance:** -1 and malformed phones are rejected; supported formatted numbers remain intact.

**Evidence:** evidence/checkout-invalid-values.jpg, raw/demo-orders.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-026 Negative postal code is accepted at checkout

**Defect | Medium | P2 | Open**

Module: Checkout  
Test: TC-026  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Complete the other delivery fields and enter -1 for Zipcode.
2. Submit the authorized demo COD order.

**Expected:** Postal codes are validated as country-appropriate identifiers.

**Actual:** The persisted order contains zipCode="-1".

**Impact:** The order can contain unusable delivery routing data.

**Recommended remedy:** Use a text postal-code field and validate it against the selected supported country on the server.

**Retest acceptance:** Negative values fail; valid supported numeric and alphanumeric codes pass.

**Evidence:** evidence/checkout-invalid-values.jpg, raw/demo-orders.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-027 Order endpoint accepts a malformed delivery email

**Defect | Medium | P2 | Open**

Module: Order API  
Test: TC-027  
Location: https://foreverbackend-k8zm.onrender.com/api/order/placeOrder  
Method: Authenticated API test  
Proposed owner: Backend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Authenticate as the disposable account.
2. Submit one valid COD line item with address.email=not-an-email.
3. Fetch own orders.

**Expected:** The server rejects a malformed email independently of browser validation.

**Actual:** HTTP 200 success is returned and the malformed email persists in the order.

**Impact:** API clients can create orders with unusable notification addresses.

**Recommended remedy:** Apply the same validated address schema at the API boundary; return a field-specific 4xx error.

**Retest acceptance:** Malformed email creates no order; a valid synthetic email passes.

**Evidence:** raw/api-validation.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-028 Order endpoint accepts a negative fractional quantity

**Defect | High | P1 | Open**

Module: Order API  
Test: TC-028  
Location: https://foreverbackend-k8zm.onrender.com/api/order/placeOrder  
Method: Authenticated API test  
Proposed owner: Backend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Use the demo account and a valid product ID.
2. Submit quantity=-0.5 in a COD order.
3. Read back own orders.

**Expected:** Every apparel quantity is a positive integer within the allowed limit.

**Actual:** The endpoint returns success and persists -0.5; the history displays that quantity.

**Impact:** Invalid units corrupt order and fulfilment calculations.

**Recommended remedy:** Validate Number.isSafeInteger(quantity), quantity>=1 and a documented maximum before any write.

**Retest acceptance:** -0.5, 0, fractional and excessive values fail; 1 and a valid upper bound pass.

**Evidence:** raw/api-validation.json, evidence/orders-validation-tests.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-029 Order endpoint accepts a size not sold for the product

**Defect | High | P1 | Open**

Module: Order API  
Test: TC-029  
Location: https://foreverbackend-k8zm.onrender.com/api/order/placeOrder  
Method: Authenticated API test  
Proposed owner: Backend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Submit the valid T-shirt ID with size=QA-NOT-A-SIZE.
2. Fetch the resulting own order.

**Expected:** The chosen size belongs to the server-side product variant list.

**Actual:** HTTP 200 success is returned and QA-NOT-A-SIZE is stored and displayed.

**Impact:** The order requests an impossible product variant.

**Recommended remedy:** Resolve the product from the database and validate the requested variant against its current size list.

**Retest acceptance:** Unknown sizes fail without persistence; supported sizes succeed.

**Evidence:** raw/api-validation.json, evidence/orders-validation-tests.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-030 Order endpoint accepts a non-existent product ID

**Defect | High | P1 | Open**

Module: Order API  
Test: TC-030  
Location: https://foreverbackend-k8zm.onrender.com/api/order/placeOrder  
Method: Authenticated API test  
Proposed owner: Backend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Submit item ID 000000000000000000000000 with a copied valid product snapshot.
2. Fetch own orders.

**Expected:** Every order line references an existing saleable server-side product.

**Actual:** The fabricated ID is accepted and persisted.

**Impact:** An order can reference inventory that does not exist.

**Recommended remedy:** Look up every product and variant on the server; reject missing or unavailable records before writing the order.

**Retest acceptance:** Non-existent IDs fail; existing allowed IDs succeed without trusting copied metadata.

**Evidence:** raw/api-validation.json, raw/products.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-031 Order endpoint trusts an altered client line-item price

**Defect | High | P1 | Open**

Module: Order API  
Test: TC-031  
Location: https://foreverbackend-k8zm.onrender.com/api/order/placeOrder  
Method: Authenticated API test  
Proposed owner: Backend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Copy the valid $200 T-shirt line.
2. Change its client price to 1 and submit amount=11.
3. Fetch own orders.

**Expected:** The server uses its own catalogue price, ignoring a submitted client price.

**Actual:** The order stores the altered $1 price and $11 amount.

**Impact:** Price manipulation can create underpriced orders. No real payment or fraud was performed.

**Recommended remedy:** Accept only product ID, variant and quantity; derive immutable line prices and discounts from server rules.

**Retest acceptance:** Tampered prices are rejected or ignored and the stored price remains $200.

**Evidence:** raw/api-validation.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-032 Order endpoint trusts the submitted total amount

**Defect | High | P1 | Open**

Module: Order API  
Test: TC-032  
Location: https://foreverbackend-k8zm.onrender.com/api/order/placeOrder  
Method: Authenticated API test  
Proposed owner: Backend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Keep one valid line priced $200 with quantity 1.
2. Submit amount=1 rather than the displayed $210.
3. Fetch own orders.

**Expected:** The server calculates the payable total from validated lines and shipping.

**Actual:** The amount of 1 is persisted despite the unchanged $200 item.

**Impact:** Totals can be manipulated independently of line-item prices.

**Recommended remedy:** Recalculate all monetary values on the server with an explicit currency and rounding policy.

**Retest acceptance:** Altered totals cannot be stored; valid item $200 plus $10 shipping yields $210.

**Evidence:** raw/api-validation.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-033 Cart endpoint stores a negative fractional quantity

**Defect | High | P1 | Open**

Module: Cart API  
Test: TC-033  
Location: https://foreverbackend-k8zm.onrender.com/api/cart/update  
Method: Authenticated API test  
Proposed owner: Backend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Use only the demo account cart.
2. Update an item quantity to -0.5.
3. Fetch the cart and reload its page.

**Expected:** Cart quantities remain positive integers; removal uses an explicit operation.

**Actual:** The update succeeds and -0.5 persists. The invalid fixture produced a fractional badge and negative totals.

**Impact:** Cart arithmetic and checkout readiness become invalid.

**Recommended remedy:** Validate integer bounds server-side and sanitize existing invalid entries before computing totals.

**Retest acceptance:** Invalid quantities fail and the cart remains unchanged; valid increments and removal still work.

**Evidence:** raw/cart-validation.json, evidence/session-log.json

Audit note: Only the invalid demo entries created for this test were subsequently removed.

Developer/client comments: not supplied. Close date: not closed.

## FM-034 Cart endpoint accepts an unsupported size

**Defect | High | P1 | Open**

Module: Cart API  
Test: TC-034  
Location: https://foreverbackend-k8zm.onrender.com/api/cart/add  
Method: Authenticated API test  
Proposed owner: Backend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Authenticate as the disposable account.
2. Add the valid product with size=QA-NOT-A-SIZE.
3. Fetch its cart.

**Expected:** The server rejects a variant not listed for that product.

**Actual:** The unsupported size is stored in cartData.

**Impact:** The cart holds a selection the storefront cannot legitimately fulfil.

**Recommended remedy:** Resolve the product variant before writing cart state and return a validation error for unknown sizes.

**Retest acceptance:** Unsupported size is rejected with no cart change; valid size M is accepted.

**Evidence:** raw/cart-validation.json

Audit note: The test entry was removed after evidence capture.

Developer/client comments: not supplied. Close date: not closed.

## FM-035 Cart endpoint accepts a non-existent product

**Defect | High | P1 | Open**

Module: Cart API  
Test: TC-035  
Location: https://foreverbackend-k8zm.onrender.com/api/cart/add  
Method: Authenticated API test  
Proposed owner: Backend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Add ID 000000000000000000000000, size M to the demo cart.
2. Fetch the cart and reload it.

**Expected:** The cart accepts only existing saleable products.

**Actual:** The fabricated ID is stored but cannot be resolved into a visible valid product row.

**Impact:** Hidden invalid entries create inconsistent cart state and can break order construction.

**Recommended remedy:** Validate product existence on write and safely flag or remove stale references on read.

**Retest acceptance:** Unknown IDs are rejected; deletion or unavailability of a previously valid product has a clear recovery state.

**Evidence:** raw/cart-validation.json, evidence/session-log.json

Audit note: The fabricated test entry was removed after capture.

Developer/client comments: not supplied. Close date: not closed.

## FM-036 Guest checkout loses the address when authentication is required

**Defect | Medium | P2 | Open**

Module: Checkout  
Test: TC-036  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. As a guest with an item, complete the delivery form.
2. Press PLACE ORDER.
3. Follow the authentication flow.

**Expected:** Authentication is requested before data entry, or the draft and checkout destination are preserved.

**Actual:** Login is requested only on submission; the entered address is lost and successful signup returns to Home.

**Impact:** A customer must repeat delivery entry and navigate back to checkout.

**Recommended remedy:** Guard checkout earlier or preserve a draft and returnTo destination across authentication.

**Retest acceptance:** Guest-to-login and guest-to-signup flows return to checkout with the valid draft and cart intact.

**Evidence:** evidence/checkout-fields.json, evidence/signup-outcome.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-037 Postal field strips letters from an alphanumeric code

**Defect | Medium | P2 | Open**

Module: Checkout  
Test: TC-037  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Type SW1A 1AA into Zipcode using normal keystrokes.
2. Read the resulting field value.

**Expected:** A postal identifier is preserved for a supported destination; unsupported countries are explicitly excluded.

**Actual:** The number input retains only 11 from SW1A 1AA. Country remains unrestricted free text.

**Impact:** A legitimate alphanumeric postal code cannot be entered accurately.

**Recommended remedy:** Use type=text, preserve spaces and letters, and validate against the supported-country policy.

**Retest acceptance:** SW1A 1AA is preserved when the UK is supported; otherwise the UI clearly restricts destination selection.

**Evidence:** evidence/checkout-form-limitations.json, evidence/checkout-form-limitations.jpg

Audit note: Supported-country requirements were not supplied; unrestricted country entry makes the current constraint ambiguous.

Developer/client comments: not supplied. Close date: not closed.

## FM-038 Phone field rejects a normally formatted telephone string

**Defect | Medium | P2 | Open**

Module: Checkout  
Test: TC-038  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Type +1 (415) 555-0321 into Phone number.
2. Inspect the resulting value.

**Expected:** A telephone string can be entered and normalized without corrupting its meaning.

**Actual:** The type=number control does not retain the entered formatted phone; the recorded value is empty.

**Impact:** Customers cannot paste a commonly formatted contact number.

**Recommended remedy:** Use type=tel and appropriate inputmode, retaining the original string until validated and normalized.

**Retest acceptance:** Formatted supported phone numbers work; invalid values receive a field-specific error.

**Evidence:** evidence/checkout-form-limitations.json, evidence/checkout-form-limitations.jpg

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-039 Unknown route has no not-found message or recovery

**Defect | Medium | P2 | Open**

Module: Routing  
Test: TC-039  
Location: https://forevermart.vercel.app/qa-route-does-not-exist  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open the stated unknown URL.
2. Allow the application to settle.

**Expected:** A not-found view explains the invalid route and links to a valid destination.

**Actual:** Only the shared header and footer appear; the route receives the SPA HTML with HTTP 200.

**Impact:** Broken links leave users in an unexplained page and are difficult to diagnose.

**Recommended remedy:** Add a catch-all route with a clear message and recovery link; use an appropriate status when the hosting architecture permits.

**Retest acceptance:** Unknown routes show Not found; known deep links still load on refresh.

**Evidence:** evidence/unknown-route.json, evidence/unknown-route.jpg, raw/route-responses.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-040 Profile response includes password and refresh-token fields

**Defect | High | P1 | Open**

Module: Account API  
Test: TC-040  
Location: https://foreverbackend-k8zm.onrender.com/api/user/getUser  
Method: Authenticated API response inspection  
Proposed owner: Backend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Sign in only as the disposable account.
2. Inspect the field names returned by the own-profile endpoint.

**Expected:** The response contains only client-required profile data and excludes authentication internals.

**Actual:** The field list includes password and refreshToken, as well as internal persistence metadata. Secret values were not copied into this report.

**Impact:** Authentication material is unnecessarily exposed to client code. This is not evidence of access to other users.

**Recommended remedy:** Return an explicit safe profile DTO and exclude password hashes, refresh tokens and internal metadata from serialization.

**Retest acceptance:** Own-profile and login responses omit these fields while authorised profile functions still work.

**Evidence:** raw/api-validation.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-041 Search opener cannot be activated with the keyboard

**Defect | Medium | P2 | Open**

Module: Shared layout  
Test: TC-041  
Location: https://forevermart.vercel.app/  
Method: DOM and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect the search icon.
2. Traverse the header with Tab and attempt keyboard activation.

**Expected:** The search opener is a named keyboard-operable button.

**Actual:** The clickable image has no button role or tabindex and is absent from the normal interactive sequence.

**Impact:** Keyboard-only shoppers cannot open search.

**Recommended remedy:** Use a button with an accessible name such as Open search, preserving the icon as decorative.

**Retest acceptance:** Tab reaches the opener and Enter or Space opens the search form.

**Evidence:** evidence/home-mobile.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-042 Search close icon lacks a keyboard action and name

**Defect | Medium | P2 | Open**

Module: Collection  
Test: TC-042  
Location: https://forevermart.vercel.app/collection  
Method: DOM and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open the search bar.
2. Inspect its close icon and try keyboard traversal.

**Expected:** Close search is a named button reachable with Tab.

**Actual:** The close affordance is a clickable image with empty alternative text and no button semantics.

**Impact:** The visible closing action is unavailable to keyboard and screen-reader users.

**Recommended remedy:** Wrap the icon in a button labelled Close search and restore focus to the opener when it closes.

**Retest acceptance:** The action is announced by name and closes the bar with Enter or Space.

**Evidence:** evidence/search-no-results.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-043 Authenticated account menu is not keyboard operable

**Defect | Medium | P2 | Open**

Module: Account  
Test: TC-043  
Location: https://forevermart.vercel.app/  
Method: DOM and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Sign in and inspect the profile opener.
2. Inspect Orders and Logout in its menu.

**Expected:** The opener and menu actions have suitable keyboard behaviour and semantic roles.

**Actual:** The opener is a clickable div and image; menu actions are clickable paragraphs without normal keyboard semantics.

**Impact:** Keyboard users cannot reliably open or use the account menu, including logout.

**Recommended remedy:** Use a named disclosure button, a link for Orders and a button for Logout with proper focus handling.

**Retest acceptance:** The entire account menu can be opened, traversed, activated and dismissed using the keyboard.

**Evidence:** evidence/profile-no-action.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-044 Login and Create Account mode switch is not a keyboard control

**Defect | Medium | P2 | Open**

Module: Account  
Test: TC-044  
Location: https://forevermart.vercel.app/login  
Method: DOM and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open the account form.
2. Inspect and attempt keyboard activation of Login or Create Account.

**Expected:** The mode switch is an operable button or link.

**Actual:** The switch is a paragraph with an onClick handler and no keyboard control semantics.

**Impact:** Keyboard users cannot select the alternative authentication form.

**Recommended remedy:** Use a type=button mode switch or links to explicit account routes.

**Retest acceptance:** Enter and Space switch modes without submitting the form accidentally.

**Evidence:** evidence/login-form.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-045 Product gallery thumbnails are pointer-only controls

**Defect | Medium | P2 | Open**

Module: Product  
Test: TC-045  
Location: https://forevermart.vercel.app/product/68ee7c73675d613eba9e96c6  
Method: DOM and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open the product with multiple gallery images.
2. Inspect the thumbnail controls.

**Expected:** Each thumbnail is keyboard operable and identifies the image it selects.

**Actual:** Thumbnails are clickable images without button roles or tabindex.

**Impact:** Keyboard shoppers cannot inspect alternative product views.

**Recommended remedy:** Use named buttons around thumbnails, exposing selected state and a visible focus indicator.

**Retest acceptance:** All images can be selected using Tab and Enter; selected image state is announced.

**Evidence:** evidence/product-details.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-046 Remove cart item is an unnamed pointer-only image

**Defect | Medium | P2 | Open**

Module: Cart  
Test: TC-046  
Location: https://forevermart.vercel.app/cart  
Method: DOM and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Add one valid item.
2. Inspect the bin icon used to remove the row.

**Expected:** Removal is a named keyboard-operable button identifying its item.

**Actual:** The bin is an image click target without suitable alternative text or button semantics.

**Impact:** Keyboard and assistive-technology users cannot reliably remove a line item.

**Recommended remedy:** Use a button labelled Remove [product name] with a clear focus style.

**Retest acceptance:** The item is removable with the keyboard and focus moves to a sensible remaining control.

**Evidence:** evidence/cart-one-item.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-047 Cart product navigation is available only through a clickable image

**Defect | Medium | P2 | Open**

Module: Cart  
Test: TC-047  
Location: https://forevermart.vercel.app/cart  
Method: DOM and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Add one item.
2. Inspect its image-based route to the product.

**Expected:** An ordinary product link is available and identifies the destination.

**Actual:** The image uses a click handler rather than an anchor; the visible product name is also blank.

**Impact:** Keyboard users cannot use the cart shortcut back to product details.

**Recommended remedy:** Use an anchor containing an informative product name or image alternative.

**Retest acceptance:** Tab reaches a named product link and Enter opens the correct product.

**Evidence:** evidence/cart-one-item.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-048 Mobile menu opener has no button semantics

**Defect | Medium | P2 | Open**

Module: Shared layout  
Test: TC-048  
Location: https://forevermart.vercel.app/  
Method: Responsive DOM review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Use a 390 px viewport.
2. Inspect the menu icon.

**Expected:** Open menu is a named button with its expanded state exposed.

**Actual:** The visible opener is a clickable image without button semantics or aria-expanded.

**Impact:** Keyboard and assistive-technology users cannot reliably open mobile navigation.

**Recommended remedy:** Use a button with aria-expanded and aria-controls tied to the menu panel.

**Retest acceptance:** Keyboard activation opens the menu and the announced state changes.

**Evidence:** evidence/home-mobile.json, evidence/mobile-menu-open.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-049 Mobile menu Back affordance is not keyboard operable

**Defect | Medium | P2 | Open**

Module: Shared layout  
Test: TC-049  
Location: https://forevermart.vercel.app/  
Method: Responsive DOM review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open mobile navigation.
2. Inspect its Back image and text.

**Expected:** The visible closing control is a keyboard-operable, named button.

**Actual:** Back is implemented with a clickable div, image and paragraph rather than a button.

**Impact:** A keyboard user lacks a reliable explicit close control.

**Recommended remedy:** Use a Close menu button and return focus to the original opener.

**Retest acceptance:** Tab reaches Close menu; Enter or Space closes the panel and restores focus.

**Evidence:** evidence/mobile-menu-open.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-050 Closed mobile menu leaves offscreen links in the accessibility tree

**Defect | Medium | P2 | Open**

Module: Shared layout  
Test: TC-050  
Location: https://forevermart.vercel.app/  
Method: Responsive DOM and code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. At mobile width, close the menu.
2. Inspect the menu links and their hiding mechanism.

**Expected:** Collapsed navigation content is removed from interactive and accessibility navigation.

**Actual:** The panel is moved with translate-x-full; its links remain in the snapshot and are not inert or aria-hidden.

**Impact:** Assistive navigation can expose offscreen destinations unrelated to the visible interface.

**Recommended remedy:** Conditionally mount the closed panel or use an appropriate inert/hidden state, restoring it when opened.

**Retest acceptance:** Closed links are absent from the accessibility and tab sequence; opening makes them available.

**Evidence:** evidence/home-mobile.json, raw/app.js

Audit note: The observed accessibility-tree exposure is confirmed; individual assistive-technology behaviour was not separately tested.

Developer/client comments: not supplied. Close date: not closed.

## FM-051 Mobile menu does not manage focus or dismiss on Escape

**Defect | Medium | P2 | Open**

Module: Shared layout  
Test: TC-051  
Location: https://forevermart.vercel.app/  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open the mobile menu.
2. Press Escape while a navigation item is focused.
3. Inspect focus handling.

**Expected:** An overlay menu provides predictable focus and dismissal behaviour.

**Actual:** Escape leaves the menu open; no opening focus transfer or closing focus restoration is implemented.

**Impact:** Keyboard users can lose their position in navigation.

**Recommended remedy:** Choose a disclosure or dialog interaction model and implement its focus and Escape behaviour consistently.

**Retest acceptance:** Open, traverse, Escape and reopen the menu; focus remains predictable throughout.

**Evidence:** evidence/mobile-menu-escape.json, evidence/mobile-menu-open.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-052 Mobile filter disclosure is a paragraph rather than a control

**Defect | Medium | P2 | Open**

Module: Collection  
Test: TC-052  
Location: https://forevermart.vercel.app/collection  
Method: Responsive DOM review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Use mobile Collection.
2. Inspect the FILTERS toggle.

**Expected:** A button opens filters and exposes expanded or collapsed state.

**Actual:** The toggle is a clickable paragraph without button semantics or expanded-state metadata.

**Impact:** Keyboard and assistive users cannot reliably discover and operate filtering.

**Recommended remedy:** Use a button with aria-expanded and aria-controls for the filter group.

**Retest acceptance:** Keyboard opening works and the state is announced correctly.

**Evidence:** evidence/mobile-filters-open.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-053 Payment methods are not keyboard selectable radio controls

**Defect | Medium | P2 | Open**

Module: Checkout  
Test: TC-053  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: DOM and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Open checkout.
2. Traverse to the Stripe and Cash on Delivery choices.

**Expected:** Payment methods form a labelled radio group with keyboard selection and selected-state exposure.

**Actual:** The choices are clickable divs and decorative circles, with no radio or button semantics.

**Impact:** Keyboard customers cannot select a payment method reliably.

**Recommended remedy:** Use labelled radio inputs in a fieldset and expose the selected payment option.

**Retest acceptance:** Tab and arrow keys select each method; the selected method is announced.

**Evidence:** evidence/checkout-form-limitations.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-054 Stripe option has no accessible payment-provider name

**Defect | Medium | P2 | Open**

Module: Checkout  
Test: TC-054  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: DOM review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Inspect the Stripe choice in the checkout accessibility snapshot.

**Expected:** The provider name Stripe is available as text or an accessible label.

**Actual:** Only a logo with alt="" appears; the option has no text label and is absent as a named choice.

**Impact:** A screen-reader user cannot identify this visible payment option.

**Recommended remedy:** Add the text label Stripe to its radio option; retain the logo as decorative.

**Retest acceptance:** The provider is announced as Stripe together with its selected state.

**Evidence:** evidence/checkout-form-limitations.json, evidence/checkout-form-limitations.jpg

Audit note: This checks the accessible name, separately from the keyboard-selection defect.

Developer/client comments: not supplied. Close date: not closed.

## FM-055 Selected product size is communicated only by colour

**Defect | Medium | P2 | Open**

Module: Product  
Test: TC-055  
Location: https://forevermart.vercel.app/product/68ee7c73675d613eba9e96c6  
Method: DOM and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Select size M.
2. Inspect its button attributes before and after selection.

**Expected:** The selected variant has a programmatically exposed state.

**Actual:** Only the border/background classes change; no aria-pressed or radio checked state indicates the selected size.

**Impact:** Assistive users cannot determine which size will be added.

**Recommended remedy:** Use a labelled size radio group, or expose aria-pressed consistently on selection buttons.

**Retest acceptance:** Selecting M announces its state and clears the previous selection.

**Evidence:** evidence/related-size-carryover.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-056 Collection sort selector has no associated label

**Defect | Medium | P2 | Open**

Module: Collection  
Test: TC-056  
Location: https://forevermart.vercel.app/collection  
Method: DOM and code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect the sort select element and its labels or aria-label.

**Expected:** The control has a programmatic label explaining its purpose.

**Actual:** The select has no label, id association or aria-label; only option text contains Sort by.

**Impact:** The control purpose depends on selected option text rather than a stable accessible name.

**Recommended remedy:** Associate a Sort products label with the select.

**Retest acceptance:** The control is announced by its purpose with each available option.

**Evidence:** evidence/collection-loaded.jpg, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-057 Delivery fields rely on disappearing placeholders

**Defect | Medium | P2 | Open**

Module: Checkout  
Test: TC-057  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Inspect delivery inputs before entry.
2. Type values into first name, address and contact fields.

**Expected:** Persistent visible labels identify the fields after entry and provide programmatic associations.

**Actual:** There are no associated labels; placeholders disappear as values are entered. Numeric postal and phone controls appear unnamed in the snapshot.

**Impact:** Customers lose field context and assistive users encounter unnamed controls.

**Recommended remedy:** Add label elements linked to stable input IDs for every delivery field; keep placeholders as optional examples.

**Retest acceptance:** All nine fields retain visible and accessible names after entry.

**Evidence:** evidence/checkout-fields.json, evidence/checkout-form-limitations.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-058 Authentication fields have no persistent associated labels

**Defect | Medium | P2 | Open**

Module: Account  
Test: TC-058  
Location: https://forevermart.vercel.app/login  
Method: DOM and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open Signup or Login.
2. Fill username, email and password and inspect labels.

**Expected:** Each credential field retains a visible label and programmatic association.

**Actual:** Only placeholders identify the fields; no label associations are present.

**Impact:** Entered forms lose clear visual context and depend on placeholder interpretation.

**Recommended remedy:** Add associated Username, Email and Password labels to the account form.

**Retest acceptance:** Both modes keep field names visible and expose them correctly after entry.

**Evidence:** evidence/login-form.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-059 Personal-data inputs do not expose their autocomplete purposes

**Defect | Medium | P2 | Open**

Module: Checkout  
Test: TC-059  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: DOM review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Inspect autocomplete attributes on delivery name, address, email and phone inputs.

**Expected:** Known personal-data purposes are exposed using appropriate autocomplete tokens.

**Actual:** The fields do not specify purpose tokens such as given-name, street-address, postal-code or tel.

**Impact:** Assistive personalization and reliable browser autofill lack explicit field-purpose metadata.

**Recommended remedy:** Add correct autocomplete tokens for each supported personal-data field and authentication mode.

**Retest acceptance:** Inspect the corrected DOM and verify a test autofill preserves each field purpose.

**Evidence:** evidence/checkout-form-limitations.json, evidence/login-form.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-060 Muted home-page text has insufficient contrast

**Defect | Medium | P2 | Open**

Module: Home  
Test: TC-060  
Location: https://forevermart.vercel.app/  
Method: Computed-style measurement  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect policy and newsletter text rendered in gray-400 on white.
2. Calculate contrast from the observed computed colour.

**Expected:** Normal-size text meets a minimum 4.5:1 contrast ratio.

**Actual:** The computed colour is oklch(0.707 0.022 261.325) at 16 px on white, approximately RGB [153, 161, 175]. The calculated contrast ratio is 2.60:1, below 4.5:1.

**Impact:** Low-vision users may struggle to read service-policy and newsletter text.

**Recommended remedy:** Use a darker approved text colour and check all states against the real background.

**Retest acceptance:** The same text at 16 px measures at least 4.5:1 without relying on rounding.

**Evidence:** evidence/typography-semantics.json, evidence/contrast-measurement.json

Audit note: The exact converted sRGB colour and ratio are included in the evidence summary.

Developer/client comments: not supplied. Close date: not closed.

## FM-061 Newsletter input suppresses its visible keyboard focus

**Defect | Medium | P2 | Open**

Module: Home  
Test: TC-061  
Location: https://forevermart.vercel.app/  
Method: Keyboard test and style review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Focus SUBSCRIBE, then Shift+Tab into the email input.
2. Inspect the focus outline and screenshot.

**Expected:** Keyboard focus is visibly indicated on the input.

**Actual:** The input uses outline-none and no focus shadow; the observed focus has no visible outline or replacement.

**Impact:** Keyboard users cannot easily locate the active subscription field.

**Recommended remedy:** Provide a distinct focus-visible border or outline with sufficient contrast.

**Retest acceptance:** Tab and Shift+Tab clearly indicate focus without requiring pointer interaction.

**Evidence:** evidence/newsletter-focus.jpg, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-062 Meaningful product photographs have empty alternative text

**Defect | Medium | P2 | Open**

Module: Product  
Test: TC-062  
Location: https://forevermart.vercel.app/product/68ee7c73675d613eba9e96c6  
Method: DOM review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect the main product image and gallery alternatives.

**Expected:** Meaningful product views have concise text alternatives describing the item or view.

**Actual:** The product images use alt="" despite conveying garment identity and appearance.

**Impact:** Screen-reader users cannot obtain information conveyed by the product photography.

**Recommended remedy:** Provide accurate item and view alternatives; use empty alt only for genuinely decorative or fully redundant images.

**Retest acceptance:** The main image and each informative gallery view expose useful, non-duplicative alternatives.

**Evidence:** evidence/product-details.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-063 Visible page and section titles are not semantic headings

**Defect | Medium | P2 | Open**

Module: Shared layout  
Test: TC-063  
Location: https://forevermart.vercel.app/collection  
Method: DOM review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect Collection, Cart, Checkout, About and Contact heading outlines.

**Expected:** Page titles and major sections use a logical h1-h2 hierarchy.

**Actual:** The inspected pages have paragraph-based titles and no h1-h3 outline; the common title component renders a p.

**Impact:** Assistive heading navigation cannot follow the visible document structure.

**Recommended remedy:** Use semantic headings in the shared title component with context-appropriate levels.

**Retest acceptance:** Every page has a meaningful h1 and logical section headings without skipped structural levels.

**Evidence:** evidence/collection-reload.json, evidence/about-page.json, evidence/contact-page.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-064 Page content lacks main and footer landmarks

**Defect | Low | P3 | Open**

Module: Shared layout  
Test: TC-064  
Location: https://forevermart.vercel.app/  
Method: DOM review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect document landmarks on Home and Collection.

**Expected:** Main content and the site footer have suitable landmark semantics.

**Actual:** No main or contentinfo/footer landmarks are present; major regions are generic containers.

**Impact:** Assistive users have fewer efficient ways to navigate page regions.

**Recommended remedy:** Use one main element per page and a footer for shared closing content.

**Retest acceptance:** Landmark navigation identifies Navigation, Main and Content information in a sensible order.

**Evidence:** evidence/typography-semantics.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-065 Browser title does not identify the current page

**Defect | Low | P3 | Open**

Module: Shared layout  
Test: TC-065  
Location: https://forevermart.vercel.app/collection  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Navigate between Home, Collection, Product, About and Checkout.
2. Compare document.title.

**Expected:** Each title describes its page purpose and the store.

**Actual:** All inspected routes retain Forever Mart.

**Impact:** Tabs and assistive page announcements do not distinguish destinations.

**Recommended remedy:** Set route-specific titles such as Collection | ForeverMart and include product names on detail pages.

**Retest acceptance:** Each route and direct deep link exposes an accurate title.

**Evidence:** evidence/collection-reload.json, evidence/product-details.json, evidence/about-page.json, evidence/checkout-fields.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-066 Layout overflows horizontally at 320 CSS pixels

**Defect | Medium | P2 | Open**

Module: Shared layout  
Test: TC-066  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: Responsive measurement  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Set the viewport to 320 CSS px.
2. Inspect the header and checkout document width.

**Expected:** The page reflows without horizontal scrolling for ordinary content.

**Actual:** At 320 CSS px, the settled checkout document and body are both 352 px wide. The totals panel uses min-w-80 within the page margins.

**Impact:** Small-screen and zoomed users must pan horizontally to reach content.

**Recommended remedy:** Remove fixed minimum widths that exceed the available content area; wrap header controls and stacked form panels.

**Retest acceptance:** At 320 CSS px, document width is no greater than the viewport and all controls remain usable.

**Evidence:** evidence/checkout-320-verified.json, evidence/checkout-320-verified.jpg, raw/app.js

Audit note: Reproduced again at the stated viewport; a screenshot and the full DOM snapshot are retained.

Developer/client comments: not supplied. Close date: not closed.

## FM-067 Home-page hero misspells Arrivals

**Defect | Low | P3 | Open**

Module: Home  
Test: TC-067  
Location: https://forevermart.vercel.app/  
Method: Browser test  
Proposed owner: Content owner (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open Home and read the hero heading.

**Expected:** The heading reads Latest Arrivals.

**Actual:** The visible heading reads Latest Arivals.

**Impact:** The first impression contains a spelling mistake.

**Recommended remedy:** Correct the copy and add a content proofreading checklist.

**Retest acceptance:** The rendered heading and accessible heading text both read Latest Arrivals.

**Evidence:** evidence/home-desktop.jpg, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-068 Template filler text remains in customer-facing sections

**Defect | Low | P3 | Open**

Module: Shared layout  
Test: TC-068  
Location: https://forevermart.vercel.app/  
Method: Browser test  
Proposed owner: Content owner (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Read the home collection descriptions, newsletter copy and footer.

**Expected:** Public copy explains the store and each section.

**Actual:** Several visible paragraphs contain Lorem ipsum template text.

**Impact:** Customers see unfinished content instead of useful information.

**Recommended remedy:** Replace all placeholder paragraphs with approved store copy and search the production content for template text.

**Retest acceptance:** No Lorem ipsum remains on public routes; reviewed copy is meaningful.

**Evidence:** evidence/home-desktop.jpg, evidence/about-page.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-069 Contact details conflict between the footer and Contact page

**Defect | Medium | P2 | Open**

Module: Contact  
Test: TC-069  
Location: https://forevermart.vercel.app/contact  
Method: Browser test  
Proposed owner: Content owner (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Compare Contact page details with its footer.

**Expected:** The store publishes one verified contact set, or clearly labels different departments.

**Actual:** The footer shows +1-212-444-780 and contact@foreveryou.com; Contact shows (415) 555-0321 and admin@forever.com without an explanation.

**Impact:** Customers do not know which contact details belong to the store.

**Recommended remedy:** Centralize approved contact data and label any distinct support or administrative contacts.

**Retest acceptance:** Each route shows the same approved support contact or explains the difference.

**Evidence:** evidence/contact-page.json, evidence/contact-page.jpg

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-070 About page contains an incomplete support sentence

**Defect | Low | P3 | Open**

Module: About  
Test: TC-070  
Location: https://forevermart.vercel.app/about  
Method: Browser test  
Proposed owner: Content owner (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Read the support paragraph on About.

**Expected:** The sentence is complete and understandable.

**Actual:** The copy ends with assist you the way, leaving the intended meaning incomplete.

**Impact:** The About page communicates unfinished copy.

**Recommended remedy:** Rewrite the sentence and proofread the complete About page.

**Retest acceptance:** The paragraph is grammatically complete and approved by the content owner.

**Evidence:** evidence/about-page.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-071 Winterwear filter has no matching catalogue classification

**Observation | Low | P3 | Review required**

Module: Collection  
Test: TC-071  
Location: https://forevermart.vercel.app/collection  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Select winterwear and compare the public subCategory values.

**Expected:** Filter options reflect available classifications or explain an empty category.

**Actual:** winterwear returns an empty grid; the catalogue uses only Topwear and Bottomwear, including for jackets.

**Impact:** An apparently useful filter has no compatible records.

**Recommended remedy:** Align the taxonomy and product classification, or omit unavailable options until they contain products.

**Retest acceptance:** Every advertised filter is backed by the intended classification or has an explicit empty state.

**Evidence:** evidence/winterwear-filter.json, raw/products.json

Audit note: The intended garment taxonomy requires owner confirmation.

Developer/client comments: not supplied. Close date: not closed.

## FM-072 Empty cart has no explanatory state or shopping recovery

**Observation | Low | P3 | Review required**

Module: Cart  
Test: TC-072  
Location: https://forevermart.vercel.app/cart  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Open the cart with zero items.

**Expected:** The page states that the cart is empty and offers a clear shopping action.

**Actual:** There are no rows or empty-cart explanation, but checkout remains the main action.

**Impact:** Customers receive little guidance when nothing is selected.

**Recommended remedy:** Add an empty-cart message and a Continue shopping link; suppress checkout in that state.

**Retest acceptance:** A new or cleared cart has a clear recovery action.

**Evidence:** evidence/cart-empty.json, evidence/cart-empty.jpg

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-073 Checkout does not show the products being purchased

**Observation | Medium | P2 | Review required**

Module: Checkout  
Test: TC-073  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Open checkout after adding a valid item.
2. Inspect the review information.

**Expected:** A shopper can verify product, variant and quantity before submission.

**Actual:** Only monetary totals and address fields are shown; no item summary is presented.

**Impact:** The final screen does not help customers catch selection mistakes.

**Recommended remedy:** Include a concise order summary with item names, quantities, sizes and prices, with an edit-cart link.

**Retest acceptance:** The summary agrees with the cart and server-calculated final order.

**Evidence:** evidence/checkout-fields.json, evidence/checkout-fields.jpg

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-074 Order history omits order identifiers

**Observation | Medium | P2 | Review required**

Module: Orders  
Test: TC-074  
Location: https://forevermart.vercel.app/order  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Open own demo order history and compare it with the own-orders API.

**Expected:** Customers have a visible order reference for support.

**Actual:** The API has order IDs, but the interface does not display them.

**Impact:** A customer cannot cite an unambiguous order reference from the interface.

**Recommended remedy:** Show a safe order reference on each order group and use it in support or detail links.

**Retest acceptance:** Each displayed order has a unique visible reference matching its record.

**Evidence:** evidence/orders-validation-tests.json, raw/api-validation.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-075 Order history loses order-level grouping

**Observation | Medium | P2 | Review required**

Module: Orders  
Test: TC-075  
Location: https://forevermart.vercel.app/order  
Method: Browser and public code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Inspect the own order history and the public order-view component.

**Expected:** Line items are grouped under the order that owns them.

**Actual:** The component pushes all order items into one list and renders item rows without order containers.

**Impact:** Customers cannot clearly distinguish separate purchases with similar items.

**Recommended remedy:** Render order-level sections containing their line items, reference, date and total.

**Retest acceptance:** Two orders and a multi-item order are visually distinguishable; empty invalid records are not silently hidden.

**Evidence:** evidence/orders-validation-tests.json, raw/app.js

Audit note: The flattening implementation was inspected; a multi-item-order scenario was not executed.

Developer/client comments: not supplied. Close date: not closed.

## FM-076 Order history omits the final order total and shipping breakdown

**Observation | Medium | P2 | Review required**

Module: Orders  
Test: TC-076  
Location: https://forevermart.vercel.app/order  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Inspect the order priced $210 in the own-orders data and its visible row.

**Expected:** The customer can verify the stored final payable amount.

**Actual:** Only item price and quantity are shown; the stored order total and shipping breakdown are not displayed.

**Impact:** The view cannot serve as a complete order cost confirmation.

**Recommended remedy:** Show order subtotal, shipping, discounts where applicable, currency and final total from the validated order record.

**Retest acceptance:** The $200 test item plus $10 shipping displays a $210 final total.

**Evidence:** evidence/orders-validation-tests.json, raw/api-validation.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-077 Order history has no delivery-address review

**Observation | Low | P3 | Review required**

Module: Orders  
Test: TC-077  
Location: https://forevermart.vercel.app/order  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Open own order history after the test order.
2. Inspect the delivery information available to the customer.

**Expected:** An order detail view allows the customer to review the submitted delivery address safely.

**Actual:** The visible history provides no address or detail link for reviewing it.

**Impact:** A delivery-entry mistake cannot be checked from the current customer interface.

**Recommended remedy:** Provide an authenticated order-detail view with the delivery address and contact information.

**Retest acceptance:** Own order details show the stored address; another account cannot retrieve it.

**Evidence:** evidence/orders-validation-tests.json, raw/demo-orders.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-078 About page advertises product ranges absent from the inspected catalogue

**Observation | Low | P3 | Review required**

Module: About  
Test: TC-078  
Location: https://forevermart.vercel.app/about  
Method: Browser test  
Proposed owner: Content owner (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Read the advertised product ranges.
2. Compare with the 40 returned product records.

**Expected:** Marketing copy reflects the current offer or explicitly describes future ranges.

**Actual:** About mentions electronics, beauty and home essentials while the inspected catalogue contains apparel only.

**Impact:** The current copy can create expectations the store does not presently meet.

**Recommended remedy:** Align copy with the current catalogue or label future expansion clearly.

**Retest acceptance:** Each current-range claim is supported by published products.

**Evidence:** evidence/about-page.json, raw/products.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-079 Newsletter placeholder contains incorrect wording

**Defect | Low | P3 | Open**

Module: Home  
Test: TC-079  
Location: https://forevermart.vercel.app/  
Method: Browser test  
Proposed owner: Content owner (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect the newsletter email placeholder.

**Expected:** The field instruction is clear and correctly written.

**Actual:** The placeholder reads enter you email.

**Impact:** A visible entry instruction contains a grammar error.

**Recommended remedy:** Use a persistent Email address label and an optional example placeholder.

**Retest acceptance:** The form contains clear approved wording before and after entry.

**Evidence:** evidence/home-mobile.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-080 Copyright footer contains incomplete grammar and inconsistent branding

**Observation | Low | P3 | Review required**

Module: Shared layout  
Test: TC-080  
Location: https://forevermart.vercel.app/  
Method: Browser test  
Proposed owner: Content owner (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Read the copyright footer and compare its named domain with the store identity.

**Expected:** The notice is correctly written and uses the approved store or legal-owner identity.

**Actual:** The line reads Copyright 2025@ forever.com -All Right Reserved.; the store is presented as Forever Mart.

**Impact:** The footer appears unfinished and its ownership identity needs clarification.

**Recommended remedy:** Use the approved legal identity and All rights reserved wording. Verify the year policy rather than automatically replacing it.

**Retest acceptance:** The notice is grammatically correct and its owner is approved.

**Evidence:** evidence/home-mobile.json

Audit note: A 2025 year is not itself classified as a defect; it may identify the original publication year.

Developer/client comments: not supplied. Close date: not closed.

## FM-081 Public document has no Content Security Policy

**Observation | Medium | P2 | Review required**

Module: Platform  
Test: TC-081  
Location: https://forevermart.vercel.app/  
Method: HTTP configuration review  
Proposed owner: Platform developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect the saved response headers and public HTML head.

**Expected:** A production hardening policy limits script and other resource sources as appropriate to this app.

**Actual:** Neither a Content-Security-Policy response header nor a CSP meta policy is present in the inspected document.

**Impact:** The page lacks this defence-in-depth control; no script-injection exploit was demonstrated.

**Recommended remedy:** Develop a least-privilege CSP using report-only validation before enforcing it, including the actual API, image and payment dependencies.

**Retest acceptance:** The reviewed policy is present and all authorised app flows work without unexpected violations.

**Evidence:** raw/headers.json, raw/home.html

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-082 Public document lacks an explicit framing restriction

**Observation | Medium | P2 | Review required**

Module: Platform  
Test: TC-082  
Location: https://forevermart.vercel.app/  
Method: HTTP configuration review  
Proposed owner: Platform developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect frame-related response headers and policy directives.

**Expected:** The deployment restricts embedding to explicitly approved origins.

**Actual:** No X-Frame-Options or CSP frame-ancestors restriction is present in the inspected response.

**Impact:** Clickjacking defence is not configured in this response; an exploit was not attempted.

**Recommended remedy:** Set a suitable CSP frame-ancestors policy and, where appropriate, X-Frame-Options for older clients.

**Retest acceptance:** An unauthorised framing origin is blocked and approved integrations continue to work.

**Evidence:** raw/headers.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-083 Public responses omit the nosniff hardening header

**Observation | Low | P3 | Review required**

Module: Platform  
Test: TC-083  
Location: https://forevermart.vercel.app/  
Method: HTTP configuration review  
Proposed owner: Platform developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect X-Content-Type-Options in the saved public response.

**Expected:** Responses use correct content types and X-Content-Type-Options: nosniff.

**Actual:** The inspected response contains no X-Content-Type-Options header.

**Impact:** An additional browser MIME-sniffing defence is absent; no MIME-confusion exploit was demonstrated.

**Recommended remedy:** Configure nosniff consistently and verify asset MIME types.

**Retest acceptance:** HTML, script, stylesheet and image responses have correct types and the intended header.

**Evidence:** raw/headers.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-084 Public document has no explicit Referrer Policy

**Observation | Low | P3 | Review required**

Module: Platform  
Test: TC-084  
Location: https://forevermart.vercel.app/  
Method: HTTP configuration review  
Proposed owner: Platform developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect Referrer-Policy headers and meta tags in the document.

**Expected:** The application explicitly defines the referrer information it permits external destinations to receive.

**Actual:** No explicit policy is present; browser defaults determine behaviour.

**Impact:** The deployment leaves this privacy setting implicit; this finding does not claim a proven data leak.

**Recommended remedy:** Choose and configure an appropriate policy such as strict-origin-when-cross-origin after reviewing navigation needs.

**Retest acceptance:** Inspect same-origin and cross-origin navigation to confirm the intended information is sent.

**Evidence:** raw/headers.json, raw/home.html

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-085 Offscreen catalogue images are not marked for lazy loading

**Observation | Low | P3 | Review required**

Module: Collection  
Test: TC-085  
Location: https://forevermart.vercel.app/collection  
Method: DOM and code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Load the 40-product collection.
2. Inspect loading attributes on product images below the fold.

**Expected:** Non-critical offscreen images can defer loading while initial visible content remains prioritised.

**Actual:** The inspected image elements have no loading=lazy attribute.

**Impact:** The implementation misses a possible transfer-saving optimisation; no Core Web Vitals failure is claimed.

**Recommended remedy:** Lazy-load offscreen cards, keep initial visible images eager, and measure the impact on a representative device.

**Retest acceptance:** A network trace verifies deferred offscreen requests without delaying visible products.

**Evidence:** evidence/collection-reload.json, evidence/typography-semantics.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-086 Product images do not advertise responsive source variants

**Observation | Low | P3 | Review required**

Module: Collection  
Test: TC-086  
Location: https://forevermart.vercel.app/collection  
Method: DOM review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect catalogue image srcset and sizes attributes at desktop and mobile widths.

**Expected:** Image delivery can select a suitably sized source for the rendered card.

**Actual:** The inspected images use a single source with no srcset or sizes attributes.

**Impact:** Smaller screens cannot request a deliberately smaller variant through these attributes; actual speed impact was not measured.

**Recommended remedy:** Generate appropriate Cloudinary or equivalent variants and declare sizes and srcset.

**Retest acceptance:** Mobile and desktop request suitable image dimensions while retaining image quality.

**Evidence:** evidence/typography-semantics.json, evidence/collection-mobile.json

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-087 Public pages lack a page-specific meta description

**Observation | Low | P3 | Review required**

Module: Routing  
Test: TC-087  
Location: https://forevermart.vercel.app/collection  
Method: HTML and code review  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect the document head and route title updates.

**Expected:** Indexable store pages provide concise, page-specific descriptive metadata.

**Actual:** The inspected HTML has no meta description and the client does not populate a route-specific description.

**Impact:** Search and sharing systems have little authored summary information. This is an optimisation observation.

**Recommended remedy:** Add approved descriptions for indexable routes and product pages using a route-aware metadata strategy.

**Retest acceptance:** Rendered page heads contain distinct relevant descriptions without indexing private account routes.

**Evidence:** raw/home.html, evidence/typography-semantics.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-088 Footer email and telephone cannot be activated directly

**Observation | Low | P3 | Review required**

Module: Contact  
Test: TC-088  
Location: https://forevermart.vercel.app/contact  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Inspect and click the email and telephone strings in the footer and contact details.

**Expected:** Customers can activate an approved support email or phone link on compatible devices.

**Actual:** The details are static text without mailto or tel links.

**Impact:** Customers must manually copy contact information, especially awkward on phones.

**Recommended remedy:** After approving the contact values, provide mailto and tel links with meaningful accessible names.

**Retest acceptance:** The links invoke the corresponding device action without sending a message automatically.

**Evidence:** evidence/contact-page.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-089 Checkout does not state which dollar currency is used

**Observation | Low | P3 | Review required**

Module: Checkout  
Test: TC-089  
Location: https://forevermart.vercel.app/PlaceOrder  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Authenticated disposable demo account; cash on delivery; no real payment.

### Reproduction

1. Inspect the displayed prices and final checkout total.

**Expected:** The payable amount identifies its currency unambiguously.

**Actual:** Only $ is shown; no ISO currency label is displayed while the country field is unrestricted.

**Impact:** An international customer cannot distinguish USD from other dollar currencies from the checkout display.

**Recommended remedy:** Display the actual supported ISO currency next to the final total and align the payment configuration.

**Retest acceptance:** Cart, checkout and order confirmation use one consistent, explicit currency.

**Evidence:** evidence/checkout-fields.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## FM-090 Displayed return and exchange promises lack instructions

**Observation | Low | P3 | Review required**

Module: Home  
Test: TC-090  
Location: https://forevermart.vercel.app/  
Method: Browser test  
Proposed owner: Frontend developer (not assigned)

Preconditions: Public deployment available; use the stated page and test data.

### Reproduction

1. Read Easy Exchange Policy and 7 Days Return Policy.
2. Look for a working route to the policy details.

**Expected:** Customers can read the scope, conditions and procedure behind these service promises.

**Actual:** The promises are brief text only; the inspected interface provides no usable policy-detail route or procedure.

**Impact:** Customers cannot determine how to request the promised service.

**Recommended remedy:** Publish owner-approved policy details and link directly from the service summary.

**Retest acceptance:** A customer can find eligibility, timeframe, procedure and support contact from each summary.

**Evidence:** evidence/home-mobile.json, raw/app.js

Audit note: None

Developer/client comments: not supplied. Close date: not closed.

## Supporting references

- [W3C WCAG 2.2 Labels or Instructions](https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html)
- [W3C WCAG 2.2 Keyboard](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html)
- [W3C WCAG 2.2 Name Role Value](https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html)
- [W3C WCAG 2.2 Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- [W3C WCAG 2.2 Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)
- [OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
- [MDN Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy)